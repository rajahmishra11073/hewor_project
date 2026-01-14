import re
import random
from django.db.models import Q
from .models import ServiceOrder, SiteSetting

class OisaAssistant:
    def __init__(self, user):
        self.user = user

    def respond(self, message):
        """
        Main entry point for Oisa's logic.
        Detects intent and routes to the appropriate handler.
        """
        message = message.lower().strip()
        
        # Priority 1: Identity & Greetings
        if self._check_intent(message, [r'who are you', r'your name', r'real person']):
            return self._identity_response()
            
        if self._check_intent(message, [r'\bhi\b', r'\bhello\b', r'\bhey\b', r'good morning', r'good evening']):
            return self._greeting_response()

        # Priority 2: Order Status (Most common user query)
        # Matches: "status of my order", "how is my project", "update on work"
        if self._check_intent(message, [r'status', r'order', r'project', r'work', r'update', r'progress']):
            return self._order_status_response()

        # Priority 3: Services & Pricing
        if self._check_intent(message, [r'service', r'price', r'cost', r'do for me', r'offer', r'make']):
            return self._services_response()
            
        # Priority 4: Support / Handover to Human
        if self._check_intent(message, [r'help', r'support', r'contact', r'human', r'phone', r'call', r'speak']):
            return self._support_response()
            
        # Priority 5: Small Talk
        if self._check_intent(message, [r'how are you', r'doing well']):
            return "I am functioning at 100% capacity and ready to assist! 🚀 How can I help you today?"
        
        if self._check_intent(message, [r'thank', r'thx']):
            return "You are very welcome! Let me know if you need anything else. 😊"

        # Priority 6: Fallback
        return self._fallback_response()

    def _check_intent(self, message, patterns):
        """Helper to check if any regex pattern matches the message."""
        for pattern in patterns:
            if re.search(pattern, message):
                return True
        return False

    def _identity_response(self):
        return (
            "I am <b>Oisa</b>, your personal AI assistant at Hewor. "
            "I help manage your projects, answer questions, and keep things organized while our human experts build your dreams! 🤖✨"
        )

    def _greeting_response(self):
        if self.user.is_authenticated and self.user.first_name:
            name = self.user.first_name
        else:
            name = "there"
            
        greetings = [
            f"Hello {name}! Oisa here. How can I help you with your project today?",
            f"Hi {name}! Ready to get to work? Ask me about your order status or our services.",
            f"Greetings! I'm Oisa. What can I do for you right now?"
        ]
        return random.choice(greetings)

    def _order_status_response(self):
        if not self.user.is_authenticated:
            return "I'd love to give you an update, but I need to know who you are first! Please <b>login</b> to check your order status."
            
        orders = ServiceOrder.objects.filter(user=self.user).order_by('-created_at')[:5]
        if not orders.exists():
            return (
                "I looked through our records, but I don't see any active projects for you yet. 📂<br>"
                "Would you like to start a new one? Just visit the <b>New Project</b> page!"
            )
        
        response = "Here is the latest status on your projects:<br><br>"
        for order in orders:
            # Emoji mapping for status
            status_map = {
                'pending': "🟠 <b>Pending Review</b>",
                'contacted': "🔵 <b>Client Contacted</b>",
                'in_progress': "🟢 <b>Work in Progress</b>",
                'completed': "✅ <b>Delivered</b>"
            }
            status_text = status_map.get(order.status, f"<b>{order.get_status_display()}</b>")
            
            response += f"• {order.title}: {status_text}<br>"
            
        response += "<br>Let me know if you need specific details on any of these!"
        return response

    def _services_response(self):
        return (
            "We offer a suite of premium digital services to help you scale:<br><br>"
            "1. <b>Presentation Design (PPT)</b> - Professional, high-impact pitch decks.<br>"
            "2. <b>Book Typing & Formatting</b> - For authors and publishers.<br>"
            "3. <b>Data Entry & Analysis</b> - Accurate and fast.<br>"
            "4. <b>Web Scraping</b> - Custom data extraction solutions.<br><br>"
            "You can start any of these from your Dashboard."
        )

    def _support_response(self):
        setting = SiteSetting.objects.first()
        phone = setting.contact_phone if setting else "+91 8797456730"
        return (
            "Sometimes you just need a human touch! 🧑‍💻<br>"
            f"You can contact our support team directly at <b>{phone}</b>.<br>"
            "They are available from 9 AM to 6 PM to handle complex queries."
        )

    def _fallback_response(self):
        return (
            "I'm still learning and didn't quite catch that. 🤔<br><br>"
            "You can ask me things like:<br>"
            "• <i>'What is the status of my order?'</i><br>"
            "• <i>'What services do you offer?'</i><br>"
            "• <i>'I need to talk to support'</i>"
        )

def get_chatbot_response(user, message):
    """
    Wrapper function to maintain compatibility with views.py
    """
    assistant = OisaAssistant(user)
    return assistant.respond(message)
