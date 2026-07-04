# Best Practices و نکات مهم

## ✅ کد Quality

### Type Hints
```python
# ✅ خوب
def send_message(
    db: Session,
    conversation_id: int,
    user_message: str
) -> str:
    ...

# ❌ بد
def send_message(db, conv_id, msg):
    ...
```

### Error Handling
```python
# ✅ خوب
try:
    response = chat_service.send_message(db, id, message)
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal error")

# ❌ بد
try:
    response = chat_service.send_message(db, id, message)
except:
    return None
```

### Database Transactions
```python
# ✅ خوب - auto-rollback on error
try:
    db.add(message)
    db.commit()
    db.refresh(message)
except Exception:
    db.rollback()
    raise

# ❌ بد - manual management
db.add(message)
db.commit()
```

## 🔐 امنیت

### API Key Management
```python
# ✅ خوب - از environment variable استفاده
api_key = settings.google_api_key

# ❌ بد - hardcoded
api_key = "AIzaSy..."
```

### Input Validation
```python
# ✅ خوب - Pydantic validation
class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

# ❌ بد - no validation
message = request.message
```

### CORS Security
```python
# ✅ خوب - specific origins
allow_origins = [settings.frontend_url, "http://localhost:3000"]

# ❌ بد - allow all
allow_origins = ["*"]
```

## 📊 Performance

### Query Optimization
```python
# ✅ خوب - eager loading
conversation = db.query(Conversation).options(
    joinedload(Conversation.messages)
).filter(Conversation.id == id).first()

# ❌ بد - N+1 query problem
conversation = db.query(Conversation).get(id)
for msg in conversation.messages:  # Extra query per message
    print(msg.content)
```

### Connection Pooling
```python
# ✅ خوب - در database.py
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Check connection validity
    pool_recycle=3600,   # Recycle connections
)

# ❌ بد - no pooling
engine = create_engine(settings.database_url)
```

### Caching
```python
# ✅ خوب - cache frequent queries
@lru_cache(maxsize=100)
def get_system_prompt() -> str:
    return SYSTEM_PROMPT

# ❌ بد - regenerate every time
def get_system_prompt() -> str:
    # Complex computation every time
    ...
```

## 📝 Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ خوب
logger.info(f"Conversation created: {conversation.id}")
logger.warning(f"API rate limit approaching: {usage}/1000")
logger.error(f"Database connection failed: {str(e)}", exc_info=True)

# ❌ بد
print(f"Conv: {conversation.id}")
print("Error!")
```

## 🧪 Testing

### Unit Test Example
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/chat/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_conversation():
    response = client.post(
        "/api/chat/conversations",
        json={"title": "Test"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
```

## 🚀 Deployment

### Environment Variables
```bash
# ✅ خوب - .env.production
DATABASE_URL=postgresql://prod_user:strong_password@prod.db.com/db
GOOGLE_API_KEY=secure_key
FRONTEND_URL=https://yourdomain.com
DEBUG=False

# ❌ بد - hardcoded or missing
```

### Database Migrations
```bash
# برای future: استفاده از Alembic
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

## 📱 API Design

### Naming Conventions
```python
# ✅ خوب
@router.post("/conversations")
@router.post("/conversations/{conversation_id}/messages")
@router.get("/conversations/{conversation_id}")

# ❌ بد
@router.post("/conv")
@router.post("/msg")
@router.get("/getConv")
```

### Response Format
```python
# ✅ خوب - consistent
{
    "id": 1,
    "title": "...",
    "created_at": "2024-01-01T12:00:00",
    "messages": [...]
}

# ❌ بد - inconsistent
{
    "conversation_id": 1,
    "conv_title": "...",
    "created": "2024-01-01"
}
```

### Error Responses
```python
# ✅ خوب
{
    "detail": "Conversation not found",
    "status_code": 404
}

# ❌ بد
{
    "error": "Not Found"
}
```

## 🔄 Version Control

### Commit Messages
```bash
# ✅ خوب
git commit -m "feat: add message history to chat service"
git commit -m "fix: handle database connection timeout"
git commit -m "refactor: extract chat logic to service"

# ❌ بد
git commit -m "update"
git commit -m "fixes"
git commit -m "wip"
```

## 📚 Documentation

### Docstrings
```python
# ✅ خوب
def send_message(
    db: Session,
    conversation_id: int,
    user_message: str
) -> str:
    """
    Process user message and return AI response.
    
    Maintains full conversation history for context.
    
    Args:
        db: Database session
        conversation_id: ID of the conversation
        user_message: User's message text
        
    Returns:
        AI-generated response text
        
    Raises:
        ValueError: If conversation not found
    """
    ...

# ❌ بد
def send_message(db, cid, msg):
    # Send message
    ...
```

## ⚡ Optimization Checklist

- [ ] Database indexes on frequently queried fields
- [ ] Connection pooling enabled
- [ ] Response compression (gzip)
- [ ] API rate limiting
- [ ] Message caching
- [ ] Async database operations
- [ ] Query optimization (no N+1)
- [ ] Proper error handling
- [ ] Logging and monitoring
- [ ] Input validation

## 🐛 Debugging Tips

### Local Development
```bash
# Enable debug mode in .env
DEBUG=True

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check database
psql business_coaching_db
SELECT * FROM conversations;
SELECT * FROM messages ORDER BY created_at DESC;
```

### Common Issues

**Issue**: CORS error
```
Fix: Check FRONTEND_URL in .env matches actual frontend URL
```

**Issue**: Database connection error
```
Fix: Verify DATABASE_URL and PostgreSQL is running
pg_isready -h localhost -p 5432
```

**Issue**: Google API error
```
Fix: Verify GOOGLE_API_KEY is correct and API is enabled
```

**Issue**: Slow responses
```
Fix: Check query performance with EXPLAIN
EXPLAIN ANALYZE SELECT * FROM messages WHERE conversation_id = 1;
```
