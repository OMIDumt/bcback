import google.generativeai as genai
from sqlalchemy.orm import Session
from models import Conversation, Message, MessageRole
from config import get_settings

settings = get_settings()

# Configure Gemini API or fall back to mock mode for local smoke tests
self_model = None
self_use_mock = False
try:
    if settings.use_mock_ai or not settings.google_api_key or settings.google_api_key.lower().startswith("your"):
        self_use_mock = True
    else:
        genai.configure(api_key=settings.google_api_key)
        self_model = genai.GenerativeModel('gemini-pro')
except Exception:
    self_use_mock = True


SYSTEM_PROMPT = """شما یک مشاور تجاری حرفه‌ای و متخصص هستید.

شما باید:
1. به مسائل کسب و کار کاربران پاسخ دهید
2. راهکارهای عملی و قابل اجرا ارائه دهید
3. بر اساس تجربه و بهترین شیوه‌های صنعت مشاوره دهید
4. سؤالات پیگیری کنید تا موضوع را بهتر درک کنید
5. توجه به جزئیات داشته باشید و مشاوره شخصی‌سازی شده دهید
6. صادق و سازنده باشید

تن صحبت شما باید حرفه‌ای، دوستانه و حمایتی باشد."""


class ChatService:
    def __init__(self):
        self.model = self_model
        self.use_mock = self_use_mock

    def build_mock_response(self, user_message: str, history_text: str) -> str:
        """Return a deterministic local response for smoke testing."""
        return (
            "این پاسخ تستی است. سیستم چت بات با موفقیت اجرا شد و پیام شما دریافت شد. "
            "برای استفاده با مدل واقعی Gemini، کلید API را در فایل .env تنظیم کنید."
        )
    
    def get_conversation_history(self, db: Session, conversation_id: int) -> list:
        """Get all messages from a conversation"""
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        return messages
    
    def format_messages_for_api(self, messages: list) -> str:
        """Format messages for API call"""
        formatted = ""
        for msg in messages:
            role = msg.role.value
            content = msg.content
            formatted += f"{role}: {content}\n"
        
        return formatted
    
    def send_message(
        self,
        db: Session,
        conversation_id: int,
        user_message: str
    ) -> str:
        """
        Process user message and return AI response.
        Maintains full conversation history.
        """
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        
        # Get full conversation history
        history = self.get_conversation_history(db, conversation_id)
        
        # Build context for API
        history_text = self.format_messages_for_api(history)
        
        # Call Gemini API or use a local fallback response for smoke tests
        full_prompt = f"""{SYSTEM_PROMPT}

مکالمه تا اینجا:
{history_text}

حالا لطفاً پاسخ دهید."""

        if self.use_mock or self.model is None:
            ai_response = self.build_mock_response(user_message, history_text)
        else:
            response = self.model.generate_content(full_prompt)
            ai_response = response.text
        
        # Save AI response
        ai_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=ai_response
        )
        db.add(ai_msg)
        
        # Update conversation updated_at
        conversation.updated_at = __import__('datetime').datetime.utcnow()
        
        db.commit()
        db.refresh(ai_msg)
        
        return ai_response
    
    def create_conversation(self, db: Session, title: str = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(title=title or "New Conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return conversation
    
    def get_conversation(self, db: Session, conversation_id: int) -> Conversation:
        """Get conversation with all messages"""
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        return conversation
