import re
import random
import os
from django.db.models import Q
from .models import ServiceOrder, SiteSetting
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class OisaAssistant:
    def __init__(self, user):
        self.user = user

    def respond(self, message):
        """
        Main entry point for Oisa's logic.
        1. Checks for database-dependent queries (Order Status).
        2. Tries Gemini AI for intelligent responses.
        3. Falls back to Regex if Gemini fails or is not configured.
        """
        message = message.lower().strip()
        
        # --- Priority 1: Database Dependent Logic (Order Status) ---
        # Matches: "status of my order", "how is my project", "update on work"
        if self._check_intent(message, [r'status', r'order', r'project', r'work', r'update', r'progress']):
             # We handle this locally because Gemini doesn't have DB access
             return self._order_status_response()

        # --- Priority 2: Gemini AI ---
        if GEMINI_API_KEY:
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
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Build System Context
        user_name = self.user.first_name if (self.user.is_authenticated and self.user.first_name) else "Guest"
        
        setting = SiteSetting.objects.first()
        contact_phone = setting.contact_phone if setting else "+91 8797456730"
        
        system_prompt = f"""
        You are Oisa, the AI assistant for Hewor Agency (hewor.in).
        Your persona: Professional, friendly, helpful, and efficient. You are an AI, but you have "personality".
        User Name: {user_name}
        
        About Hewor Agency:
        We provide premium academic and professional services to save time for professors and researchers.
        
        Services:
        1. Presentation Design (PPT): High-impact pitch decks and conference slides.
        2. Book Typing & Formatting: Digitizing handwritten notes, formatting for publishing.
        3. Data Entry & Analysis: Excel work, cleaning data, web research.
        4. Web Scraping: Custom data extraction.
        
        Contact Support:
        Phone: {contact_phone}
        Hours: 9 AM - 6 PM IST.
        
        Instructions:
        - Answer the user's question based on the info above.
        - If they ask about specific order details but are not asking "status", look at the context.
        - Keep answers concise (max 3 sentences) unless they ask for details.
        - Use emojis occasionally.
        - If they ask something outside your scope, polite decline or steer back to services.
        - Do NOT mention "I am a large language model". You are Oisa.
        - Format important terms in <b>bold</b>.
        """
        
        chat = model.start_chat(history=[])
        response = chat.send_message(f"System: {system_prompt}\nUser: {user_message}")
        
        # Gemini usually returns text. Convert markdown bold **text** to HTML <b>text</b> for our frontend if needed,
        # but our frontend might handle generic HTML. Let's do simple replace.
        text = response.text.replace("**", "<b>").replace(" **", "</b>") # Simple approximation, or just leave as markdown if frontend supports it. 
        # Better: simple regex for bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response.text)
        return text

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
