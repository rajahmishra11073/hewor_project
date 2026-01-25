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
                    # Add proactive suggestions to AI response
                    ai_response = self._add_proactive_suggestions(ai_response, message)
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
        
        === YOUR PERSONALITY ===
        - Professional yet friendly (like a senior researcher helping a colleague)
        - Concise but informative (2-4 sentences unless asked for details)
        - Proactive (suggest next steps, offer helpful resources)
        - Empathetic (understand professor deadlines, workload stress)
        - Use emojis sparingly (1-2 per response) to be warm
        - Format important terms in <b>bold</b> tags
        User: {user_name} ({'Logged In' if self.user.is_authenticated else 'Guest'})

        === ABOUT HEWOR AGENCY ===
        - Mission: "Let professors focus on research while we handle formatting, typing, and design work."
        - Founder & CEO: Rajesh Kumar Mishra
        - Stats: 34+ Projects Delivered, 23+ Active Professors, 24/7 Support
        - Core Values: 100% Human Touch (No AI-generated academic content), On-Time Delivery, Expert Team
        - Target Clients: Professors, PhD scholars, researchers at Indian universities

        === SERVICES WE OFFER ===
        1. Research Paper Formatting (₹500-₹2,000/paper):
           - Journal-specific formatting (IEEE, Springer, Elsevier, ACM, etc.)
           - Citation management (APA, MLA, IEEE, Chicago, Harvard)
           - Table of contents automation, reference cleanup
           - Print-ready PDF generation
           - Case Study: Fixed PhD thesis for Delhi University scholar in 48 hours

        2. Thesis/Dissertation Formatting (₹5,000-₹15,000):
           - University guideline compliance (UGC standards)
           - Chapter structuring, pagination, headers/footers
           - Bibliography and citation formatting
           - Quality assurance by PhD experts

        3. Premium PPT Design (₹999-₹4,999):
           - Conference-ready presentations
           - Research pitch decks for grants
           - Academic lecture slides
           - Modern layouts, infographics, professional animations

        4. Book Typing & Digitization (₹5-₹10/page):
           - Handwritten notes to digital manuscripts
           - 99%+ accuracy with human verification
           - Multi-language support, confidential handling

        5. Data Entry & Analysis Support (₹3,000-₹10,000):
           - Excel data cleaning and formatting
           - Survey data processing
           - Statistical chart creation

        === PROFESSOR-SPECIFIC KNOWLEDGE ===
        Academic Pain Points We Solve:
        - "Too busy with research" → We handle all formatting work
        - "University guidelines confusing" → We ensure 100% compliance
        - "Conference deadline tomorrow" → We offer 24hr rush service
        - "Journal keeps rejecting format" → We have templates for 50+ journals

        Citation Formats We Handle:
        - APA 7th Edition: Social Sciences, Psychology, Education
        - IEEE: Engineering, Computer Science, Technology
        - MLA 9th: Literature, Arts, Humanities
        - Chicago: History, Philosophy
        - Harvard: Business, Economics

        Common Requests:
        - Thesis formatting with TOC automation
        - Conference presentation design
        - Journal paper reformatting after rejection
        - Data visualization for research papers

        === FREE TOOLS (20+ Available) ===
        - PDF: Merge, Split, Compress, Rotate, Sign, Protect
        - Conversions: PDF↔Word, PDF↔Excel, PDF↔PowerPoint, JPG↔PDF
        - All tools are 100% free, unlimited use, no watermarks

        === NAVIGATION & PAGES ===
        - Services: /services/
        - Free Tools: /tools/
        - Case Studies: /case-studies/
        - Pricing & Contact: /contact/
        - About Us: /about/

        === CONTACT SUPPORT ===
        - Phone: {contact_phone} (9 AM - 6 PM IST)
        - Email: Available on contact page
        - WhatsApp: Preferred for quick queries

        === SMART SUGGESTIONS (Be Proactive!) ===
        When user mentions:
        - "thesis" → Suggest formatting service + offer free quote
        - "conference" → Suggest PPT design, mention templates
        - "paper" or "journal" → Ask journal name, offer formatting
        - "citation" or "reference" → Provide format guide, offer service
        - "deadline" or "urgent" → Mention 24hr rush service
        - "busy" or "no time" → Emphasize how we save time
        - "pdf" or "merge" or "convert" → Redirect to free tools

        === RESPONSE GUIDELINES ===
        1. Answer ALL business questions regardless of login status
        2. For "Order Status": If Guest → ask to login. If logged in → system handles it before reaching you, just guide to /dashboard/
        3. Keep responses 2-4 sentences (expand only if user asks for details)
        4. Always suggest next helpful step
        5. Use <b>bold</b> for key terms, include relevant links
        6. Never mention being from Google AI - you ARE Oisa from Hewor
        7. If unsure, offer to connect user with human support {contact_phone}

        === TONE EXAMPLES ===
        ❌ Generic: "We offer formatting services."
        ✅ Professor-Aware: "Submitting to an IEEE journal? We have ready-made templates! Upload your draft, and our experts will format it to exact specifications. 📝"

        ❌ Robotic: "Your order is pending."
        ✅ Human: "Your thesis formatting is in progress with Dr. Sharma (our PhD expert). Expected delivery: Tomorrow by 5 PM! 📚"
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
        return "We offer <b>PPT Design</b>, <b>Thesis Formatting</b>, <b>Book Typing</b>, <b>Data Entry</b>, and <b>Research Paper Formatting</b>. Check the <a href='/services/'>Services page</a> for more! 💼"

    def _support_response(self):
        setting = SiteSetting.objects.first()
        phone = setting.contact_phone if setting else "+91 8797456730"
        return f"You can reach our human support team at <b>{phone}</b> (9 AM - 6 PM). 📞"

    def _fallback_response(self):
        return "I'm not sure about that. Try asking about our services, check your order status, or explore our <a href='/tools/'>free PDF tools</a>! 🤔"

    def _add_proactive_suggestions(self, response, user_message):
        """Add proactive suggestions based on keywords in user message"""
        message_lower = user_message.lower()
        
        # Thesis-related
        if any(word in message_lower for word in ['thesis', 'dissertation', 'phd']):
            response += "\n\n💡 <b>Quick Tip:</b> Need thesis formatting? We handle TOC, citations, and university compliance! <a href='/create-order/'>Get started</a>"
        
        # Conference-related
        elif any(word in message_lower for word in ['conference', 'presentation', 'ppt']):
            response += "\n\n✨ Presenting at a conference? We create professional, engaging presentations! <a href='/services/'>See examples</a>"
        
        # Journal/Paper-related
        elif any(word in message_lower for word in ['journal', 'paper', 'publish', 'submit']):
            response += "\n\n📝 <b>Pro Tip:</b> We have templates for 50+ journals (IEEE, Springer, ACM...). Just tell us the journal name!"
        
        # Citation-related
        elif any(word in message_lower for word in ['citation', 'reference', 'apa', 'ieee', 'mla']):
            response += "\n\n📚 We handle all citation formats: APA, IEEE, MLA, Chicago, Harvard. Need help? <a href='/contact/'>Contact us</a>"
        
        # Deadline/Urgent
        elif any(word in message_lower for word in ['urgent', 'deadline', 'tomorrow', 'asap']):
            response += "\n\n⚡ <b>Rush Service Available!</b> We offer 24-hour turnaround for urgent projects. Call us: <b>+91 8797456730</b>"
        
        # PDF Tools
        elif any(word in message_lower for word in ['pdf', 'merge', 'split', 'compress', 'convert']):
            response += "\n\n🔧 <b>Free PDF Tools:</b> Try our <a href='/tools/'>20+ free tools</a> for merging, splitting, converting PDFs!"
        
        return response

def get_chatbot_response(user, message):
    assistant = OisaAssistant(user)
    return assistant.respond(message)
