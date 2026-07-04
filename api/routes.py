from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db
from services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])
chat_service = ChatService()


# Pydantic Models
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse


class CreateConversationRequest(BaseModel):
    title: str = None


def serialize_message(message) -> MessageResponse:
    """Convert an ORM message to the API response model."""
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role.value if hasattr(message.role, "value") else message.role,
        content=message.content,
        created_at=message.created_at.isoformat() if hasattr(message.created_at, "isoformat") else str(message.created_at),
    )


# API Routes
@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    try:
        conversation = chat_service.create_conversation(
            db=db,
            title=request.title
        )
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation with all messages"""
    try:
        conversation = chat_service.get_conversation(db, conversation_id)
        messages = [serialize_message(msg) for msg in conversation.messages]
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=messages
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse
)
def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """Send a message to the chatbot and get response"""
    try:
        # Get conversation
        conversation = chat_service.get_conversation(db, conversation_id)
        
        # Get all messages (including the new user message)
        from models import Message
        user_message = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).first()
        
        # Send message and get response
        ai_response_text = chat_service.send_message(
            db=db,
            conversation_id=conversation_id,
            user_message=request.message
        )
        
        # Get the saved messages
        user_msg = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).offset(1).first()
        
        ai_msg = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).first()
        
        return SendMessageResponse(
            user_message=serialize_message(user_msg),
            assistant_message=serialize_message(ai_msg)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
