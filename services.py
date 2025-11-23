from config import Config

def get_ai_response(message, logger=None):
    """
    Get AI response for a chat message.
    Uses OpenAI API if available, otherwise falls back to rule-based responses.
    """
    assistant_reply = None
    
    # Try OpenAI API if key is configured
    if Config.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful medical clinic assistant. Provide helpful, professional responses to patient inquiries."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            assistant_reply = response.choices[0].message.content.strip()
            
        except Exception as e:
            if logger:
                logger.warning(f"OpenAI API call failed: {e}")
            assistant_reply = None
    
    # Fallback to rule-based responses
    if not assistant_reply:
        assistant_reply = get_rule_based_response(message)
    
    return assistant_reply

def get_rule_based_response(message):
    """
    Generate a rule-based response based on keywords in the message.
    """
    message_lower = message.lower()
    
    # Greetings
    if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return "Hello! Welcome to our clinic. How can I help you today?"
    
    # Pain or symptoms
    elif any(word in message_lower for word in ["pain", "hurt", "ache", "sick", "symptom"]):
        return "I'm sorry to hear that you're not feeling well. Can you describe where it hurts and when the symptoms started? This will help us assist you better."
    
    # Appointments
    elif any(word in message_lower for word in ["appointment", "book", "schedule", "visit"]):
        return "I can help you schedule an appointment. Which date and time would work best for you? Please also let me know if you have a preferred doctor."
    
    # Prescriptions
    elif any(word in message_lower for word in ["prescription", "medication", "medicine", "refill"]):
        return "For prescription refills or medication questions, please provide your patient ID and the medication name. A clinician will review your request shortly."
    
    # Test results
    elif any(word in message_lower for word in ["test", "result", "lab", "report"]):
        return "Test results are typically available within 2-3 business days. You can check your patient portal or we'll contact you when they're ready."
    
    # Emergency
    elif any(word in message_lower for word in ["emergency", "urgent", "bleeding", "chest pain", "can't breathe"]):
        return "⚠️ If this is a medical emergency, please call 911 or go to the nearest emergency room immediately. For urgent but non-emergency issues, please call our clinic directly."
    
    # Insurance
    elif any(word in message_lower for word in ["insurance", "billing", "payment", "cost"]):
        return "For insurance and billing questions, please contact our billing department. They can help you with coverage questions, payment plans, and cost estimates."
    
    # Default response
    else:
        return "Thank you for your message. A member of our clinical team will review your inquiry and get back to you shortly. If you need immediate assistance, please call our clinic."