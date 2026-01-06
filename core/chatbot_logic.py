from django.db.models import Q
from .models import ServiceOrder, SiteSetting

def get_chatbot_response(user, message):
    """
    Simple Rule-Based + Database Retrieval Chatbot.
    Acts as a placeholder for a real LLM.
    """
    message = message.lower()
    
    # 1. Greeting & Identity
    if any(x in message for x in ['who are you', 'your name', 'what is your name']):
        return "I am <b>Oisa</b>, your AI project assistant. I am here to help you with your orders and services."

    if any(x in message for x in ['hi', 'hello', 'hey']):
        return f"Hello {user.first_name}! I am Oisa. How can I help you with your project today?"

    # 2. Order Status Queries
    if 'status' in message or 'order' in message or 'project' in message or 'work' in message:
        if not user.is_authenticated:
            return "Please login to check your order status."
            
        orders = ServiceOrder.objects.filter(user=user).order_by('-created_at')[:3]
        if not orders.exists():
            return "You don't have any active projects yet. You can start a new project from the dashboard."
        
        response = "Here are your recent projects:<br>"
        for order in orders:
            status_emoji = "🟢" if order.status == 'completed' else "🔵" if order.status == 'in_progress' else "🟠"
            response += f"{status_emoji} <b>{order.title}</b>: {order.get_status_display()}<br>"
        return response

    # 3. Service Inquiries
    if 'service' in message or 'price' in message or 'cost' in message or 'make' in message or 'create' in message:
        return (
            "We offer premium digital services:<br>"
            "1. <b>PPT Design</b><br>"
            "2. <b>Book Typing</b><br>"
            "3. <b>Data Entry</b><br>"
            "Please visit the 'New Project' page to detail your requirements."
        )

    # 4. Contact/Support
    if 'contact' in message or 'call' in message or 'email' in message or 'number' in message:
        setting = SiteSetting.objects.first()
        phone = setting.contact_phone if setting else "+91 8797456730"
        return f"You can reach our support team at <b>{phone}</b>."

    # Default Fallback (Strict Scope)
    return "I am here to assist you regarding the project. Please ask about your Order Status, Services, or Support."
