import re
import random
import os
from django.db.models import Q
from .models import ServiceOrder, SiteSetting
from google import genai
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
from dotenv import load_dotenv
load_dotenv() # Ensure env vars are loaded

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to init Gemini Client: {e}")

class OisaAssistant:
    def __init__(self, user):
        self.user = user

    def respond(self, message):
        """
        Main entry point for Oisa's logic.
        """
        message = message.lower().strip()
        
        # --- Priority 1: Database Dependent Logic (Order Status) ---
        status_patterns = [
            r'status of my', r'my order', r'my project', r'track order', 
            r'project status', r'work update', r'how is my order'
        ]
        if self._check_intent(message, status_patterns):
             return self._order_status_response()

        # --- Priority 2: Gemini AI ---
        if client:
            try:
                ai_response = self._get_gemini_response(message)
                if ai_response:
                    return ai_response
            except Exception as e:
                logger.error(f"Gemini API Error: {e}")
                # Fall through to specific fallback logic

        # --- Priority 3: Simple Regex Fallback (If AI fails) ---
        # Identity
        if self._check_intent(message, [r'who are you', r'your name', r'real person']):
            return self._identity_response()
            
        # Greetings
        if self._check_intent(message, [r'\bhi\b', r'\bhello\b', r'\bhey\b', r'good morning']):
            return self._greeting_response()

        # Services
        if self._check_intent(message, [r'service', r'price', r'cost', r'do for me', r'offer']):
            return self._services_response()
            
        # Support
        if self._check_intent(message, [r'help', r'support', r'contact', r'human', r'phone']):
            return self._support_response()
            
        # Generic Fallback
        return self._fallback_response()

    def _get_gemini_response(self, user_message):
        """
        Calls Gemini API with system context.
        Tries multiple models in case of 404 or Rate Limits.
        """
        if not client:
            return None
        
        # List of models to try in order of preference/stability
        # Updated based on available models in the project (Gemini 2.x available, 1.5 missing)
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite',
            'gemini-flash-latest',
            'gemini-2.5-flash',
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash', # Kept just in case
        ]

        # Build System Context
        user_name = self.user.first_name if (self.user.is_authenticated and self.user.first_name) else "Guest"
        
        setting = SiteSetting.objects.first()
        contact_phone = setting.contact_phone if setting else "+91 8797456730"
        
        system_prompt = f"""
        You are Oisa, the advanced AI assistant for Hewor Agency (hewor.in).
        Your persona: Professional, friendly, helpful, and efficient. You are part of the Hewor team.
        User Name: {user_name}

        === ABOUT HEWOR AGENCY ===
        - Mission: "To let students and professors focus on research while we handle the grunt work."
        - Founder & CEO: Rajesh Kumar Mishra.
        - Stats: 34+ Projects Delivered, 23+ Active Professors, 24/7 Support.
        - Core Value: Trusted & Secure, On-Time Delivery, Expert Team.

        === SERVICES WE OFFER ===
        1. Thesis Formatting:
           - We ensure adherence to strict university guidelines (APA, MLA, IEEE, etc.).
           - Features: Table of Contents Automation, Reference Management, Layout Precision, Print-Ready PDF.
           - Case Study: Fixed a PhD thesis for a Delhi University scholar (100% compliance) in 48 hours.

        2. Premium PPT Design:
           - Transform boring slides into engaging, professional presentations.
           - Features: Modern layouts, Infographics, Custom Animations, Branding Integration.
           - Ideal for: International Conferences, Pitch Decks, Lectures.

        3. Book Typing:
           - Digitize handwritten notes or physical manuscripts into Word/LaTeX.
           - Features: High Accuracy (99%+), Multi-language Support, Secure & Confidential.

        4. Data Entry & Processing:
           - Excel/Google Sheets experts for bulk data processing.
           - Features: Data Cleaning, Formatting, Web Scraping.

        === NAVIGATION & PAGES ===
        - Home: Overview of everything.
        - Services: Detailed breakdown of offers. URL: /services/
        - Case Studies: Real success stories (PhD Thesis, Conference PPT, Survey Data). URL: /case-studies/
        - About Us: Meet the leadership and our vision. URL: /about/
        - Contact: Get in touch. URL: /contact/
        - FAQs: Common questions. URL: /faqs/
        - Pricing: Flexible plans available. Contact us for a quote.
        - Legal: Terms & Ethics (/terms/), Privacy Policy (/privacy/).

        === CONTACT SUPPORT ===
        - Phone: {contact_phone}
        - Hours: 9 AM - 6 PM IST.
        - Location: Online Premium Agency.

        === INSTRUCTIONS ===
        1. Answer ALL business-related questions (Services, Pricing, About Us, Policies) regardless of login status.
        2. If the user asks for "Order Status" or "My Projects":
           - If User Name is "Guest", nicely ask them to LOG IN first (provide /login/ link).
           - If logged in, you can't see the DB directly here, but the system handles specific status intents before reaching you. If it reached you, just guide them to the Dashboard (/dashboard/).
        3. Keep answers concise (2-4 sentences) unless asked for details.
        4. Use emojis to be friendly 😊.
        5. If asked about "Pricing", say it varies by project complexity and suggest they "Contact Us" or "Sign Up" for a quote.
        6. Do NOT mention being an AI model from Google. You are Oisa from Hewor.
        7. Format important terms in <b>bold</b>.
        """
        
        # Prepare prompt
        full_message = f"System: {system_prompt}\nUser: {user_message}"

        for model_name in models_to_try:
            try:
                # Create chat and send
                chat = client.chats.create(model=model_name)
                response = chat.send_message(message=full_message)
                
                # If successful, process and return
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response.text)
                return text
            except Exception as e:
                # Log error and try next model
                logger.warning(f"Gemini Model {model_name} failed: {e}")
                continue
        
        # If all failed
        logger.error("All Gemini models failed.")
        return None

    def _check_intent(self, message, patterns):
        """Helper to check if any regex pattern matches the message."""
        for pattern in patterns:
            if re.search(pattern, message):
                return True
        return False

    def _identity_response(self):
        return "I am <b>Oisa</b>, your personal AI assistant at Hewor! 🤖✨"

    def _greeting_response(self):
        return "Hello! Oisa here. How can I help you today? 😊"

    def _order_status_response(self):
        if not self.user.is_authenticated:
            return "I can't check your orders unless you're logged in! Please <a href='/login/'>login</a> to check your status."
            
        orders = ServiceOrder.objects.filter(user=self.user).order_by('-created_at')[:5]
        if not orders.exists():
            return "You don't have any active projects yet. Ready to start one? 🚀"
        
        response = "Here are your recent projects:<br><br>"
        for order in orders:
            status_map = {
                'pending': "🟠 Pending", 'contacted': "🔵 Contacted",
                'in_progress': "🟢 In Progress", 'completed': "✅ Delivered"
            }
            response += f"• {order.title}: {status_map.get(order.status, order.status)}<br>"
        return response

    def _services_response(self):
        return "We offer PPT Design, Book Typing, Data Entry, and Web Scraping. Check the Services page for more! 💼"

    def _support_response(self):
        return f"You can reach our human support team at <b>+91 8797456730</b> (9 AM - 6 PM). 📞"

    def _fallback_response(self):
        return "I'm not sure about that. Try asking about our services or your order status! 🤔"

def get_chatbot_response(user, message):
    assistant = OisaAssistant(user)
    return assistant.respond(message)
