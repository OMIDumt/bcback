# معماری سیستم

## 🏗️ نمای کلی

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Tauri/Lovable)                 │
│                                                             │
│                   ┌─────────────────────┐                  │
│                   │  React Components   │                  │
│                   │  Chat Interface     │                  │
│                   └──────────┬──────────┘                  │
│                              │ HTTP                        │
│                              ▼                              │
└─────────────────────────────────────────────────────────────┘
                              │
                      ┌───────▼────────┐
                      │   CORS Layer   │
                      └───────┬────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                     FastAPI Backend                           │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              API Routes (/api/chat)                    │  │
│  │  ┌─────────────────────┐  ┌─────────────────────────┐ │  │
│  │  │ POST /conversations │  │ POST /messages/{conv_id}│ │  │
│  │  │ GET  /conversations │  │ GET  /health            │ │  │
│  │  └─────────────────────┘  └─────────────────────────┘ │  │
│  └──────────┬────────────────────────────┬────────────────┘  │
│             │                            │                   │
│  ┌──────────▼───────────┐  ┌─────────────▼────────────────┐  │
│  │   ChatService        │  │   Database Operations        │  │
│  │  - send_message()    │  │   - Save messages            │  │
│  │  - get_history()     │  │   - Fetch history            │  │
│  │  - format_prompt()   │  │   - Create conversations     │  │
│  └──────────┬───────────┘  └──────────────────────────────┘  │
│             │                                                 │
│  ┌──────────▼─────────────────────────────┐                 │
│  │     Google Gemini API                  │                 │
│  │  - Generate response with history      │                 │
│  │  - System prompt for business coaching │                 │
│  └──────────┬─────────────────────────────┘                 │
│             │ Response                                       │
└─────────────┼──────────────────────────────────────────────────┘
              │
       ┌──────▼──────┐
       │ PostgreSQL  │
       │ Database    │
       └─────────────┘
```

## 🔄 جریان پردازش پیام

### مرحله 1: دریافت پیام

```
Frontend → POST /api/chat/conversations/{id}/messages
         → {"message": "سؤال کاربر"}
```

### مرحله 2: ذخیره پیام کاربر

```python
# در database.py
message = Message(
    conversation_id=id,
    role=MessageRole.USER,
    content=user_message
)
db.add(message)
db.commit()
```

### مرحله 3: بازیابی تاریخچه

```python
# دریافت تمام پیام‌های قبلی
history = db.query(Message).filter(
    Message.conversation_id == id
).order_by(Message.created_at).all()
```

### مرحله 4: ساخت Prompt

```python
full_prompt = f"""
{SYSTEM_PROMPT}

مکالمه تا اینجا:
user: پیام اول
assistant: پاسخ
user: پیام دوم
assistant: پاسخ
...
user: {new_message}
"""
```

### مرحله 5: درخواست از AI

```python
response = genai.GenerativeModel('gemini-pro').generate_content(full_prompt)
ai_response = response.text
```

### مرحله 6: ذخیره پاسخ

```python
message = Message(
    conversation_id=id,
    role=MessageRole.ASSISTANT,
    content=ai_response
)
db.add(message)
db.commit()
```

### مرحله 7: بازگشت به Frontend

```json
{
  "user_message": {...},
  "assistant_message": {...}
}
```

## 💾 ساختار Database

### جدول Conversations
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### جدول Messages
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER FOREIGN KEY,
    role ENUM('user', 'assistant'),
    content TEXT,
    created_at TIMESTAMP
);
```

## 🧠 حافظه و Context

### چگونه حافظه کار می‌کند:

1. **ذخیره کامل**: تمام پیام‌ها (اول تا آخر) در database ذخیره می‌شود
2. **بازیابی خودکار**: برای هر پیام جدید، تمام history بازیابی می‌شود
3. **Context بهتر**: AI تمام مکالمه‌های قبلی را می‌بیند
4. **بهتر شدن پاسخ**: هر پاسخ بر اساس درک کامل از مکالمه است

### مثال:

```
Msg 1: User → "میخوام کسب و کار شروع کنم"
Response → "خوب است. کدام زمینه؟"

Msg 2: User → "تکنولوژی"
Response → "تکنولوژی خوبی است. بودجه‌ی چند دارید؟"
    ↑ AI می‌دانند کاربر "کسب و کار" می‌خواهد نه "تکنولوژی" در کل

Msg 3: User → "۱۰۰ میلیون"
Response → "برای ۱۰۰ میلیون تومان در تکنولوژی، ۳ گزینه دارید..."
    ↑ AI همه قسمت‌های قبلی را می‌داند
```

## ⚙️ Configuration

### System Prompt برای AI

```python
SYSTEM_PROMPT = """شما یک مشاور تجاری حرفه‌ای و متخصص هستید.

شما باید:
1. به مسائل کسب و کار پاسخ دهید
2. راهکارهای عملی ارائه دهید
3. سؤالات پیگیری کنید
4. صادق و سازنده باشید
"""
```

### توسعه System Prompt

می‌توانید system prompt را برای نیازهای خاص تغییر دهید:

```python
# برای مشاور فروش
SYSTEM_PROMPT = """شما مشاور فروش ماهر هستید...

شما باید:
- تکنیک فروش بهتر تدریس دهید
- استراتژی فروش بسازید
- نتایج فروش بهتر کنید
"""

# برای مشاور مالی
SYSTEM_PROMPT = """شما مشاور مالی متخصص هستید...

شما باید:
- بودجه‌بندی کنید
- سرمایه‌گذاری تجویز دهید
- خطرات مالی کاهش دهید
"""
```

## 🚀 عملکرد و بهینه‌سازی

### نکاتی برای بهتر شدن:

1. **Caching**: برای صحبت‌های تکراری، نتایج cache کنید
2. **Vector Database**: برای conversation similarity search استفاده کنید
3. **Batch Processing**: چند پیام را یکجا پردازش کنید
4. **Async**: requests ناهمزمان برای سرعت بیشتر

### مثال Caching:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(conversation_id, hash(messages)):
    # Generate response only if cache miss
    ...
```

## 🔐 امنیت

### نکاتی برای امنیت:

1. **Input Validation**: تمام input را validate کنید
2. **Rate Limiting**: برای جلوگیری از abuse
3. **Authentication**: برای conversations (در آینده)
4. **Encryption**: برای messages حساس

### مثال Rate Limiting:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/messages")
@limiter.limit("10/minute")
def send_message(...):
    ...
```

## 📈 مراقبت و Monitoring

### Logs:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Message sent: {conversation_id}")
logger.error(f"API Error: {str(e)}")
```

### Metrics:

- تعداد conversations
- میانگین response time
- تعداد errors
- استفاده از API quota

## 🔄 Deployment

### Development:
```bash
python main.py
```

### Production with Docker:
```bash
docker-compose up
```

### Database Backup:
```bash
pg_dump business_coaching_db > backup.sql
psql business_coaching_db < backup.sql
```
