# Business Coaching Chatbot - Backend API

API سرور برای چت بات مشاوره‌ای بیزینس با حافظه کامل.

## 🎯 ویژگی‌ها

- ✅ مشاور AI با حافظه کامل مکالمات
- ✅ ذخیره‌سازی تاریخچه چت در PostgreSQL
- ✅ استفاده از Google Gemini API (رایگان)
- ✅ REST API سریع و محکم
- ✅ پشتیبانی CORS برای frontend

## 📋 پیش‌نیازها

- Python 3.8+
- PostgreSQL 12+

## 🚀 نحوه استفاده

### 1. Setup محیط

```bash
# ایجاد virtual environment
python -m venv venv

# فعال کردن
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 2. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 3. پیکربندی

```bash
# کپی کردن .env.example به .env
cp .env.example .env

# ویرایش .env و اضافه کردن:
# - DATABASE_URL: اتصال PostgreSQL
# - GOOGLE_API_KEY: کلید Gemini API
# - FRONTEND_URL: آدرس frontend
```

### 4. دریافت Google API Key

1. برو به [Google AI Studio](https://aistudio.google.com/apikey)
2. دکمه "Create API Key" کلیک کن
3. کلید رو در .env اضافه کن

### 5. ایجاد Database

```bash
# PostgreSQL
createdb business_coaching_db
```

### 6. اجرای سرور

```bash
python main.py
```

سرور در `http://localhost:8000` اجرا می‌شود.

## 📚 API Endpoints

### Health Check
```
GET /api/chat/health
```

### ایجاد مکالمه جدید
```
POST /api/chat/conversations
Content-Type: application/json

{
  "title": "مشاوره جدید"
}
```

### دریافت یک مکالمه
```
GET /api/chat/conversations/{conversation_id}
```

### ارسال پیام
```
POST /api/chat/conversations/{conversation_id}/messages
Content-Type: application/json

{
  "message": "سوال یا نظر کاربر"
}
```

Response:
```json
{
  "user_message": {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "سوال",
    "created_at": "2024-01-01T12:00:00"
  },
  "assistant_message": {
    "id": 2,
    "conversation_id": 1,
    "role": "assistant",
    "content": "پاسخ مشاور",
    "created_at": "2024-01-01T12:00:01"
  }
}
```

## 🏗️ ساختار پروژه

```
backend/
├── main.py                 # نقطه ورود
├── config.py              # پیکربندی
├── database.py            # اتصال DB
├── models.py              # مدل‌های SQLAlchemy
├── requirements.txt       # وابستگی‌ها
├── .env.example          # متغیرهای محیط
├── services/
│   └── chat_service.py    # منطق چت
└── api/
    └── routes.py          # API endpoints
```

## 🔄 جریان کار

1. **ایجاد مکالمه**: Frontend به `/conversations` درخواست POST می‌فرستد
2. **ارسال پیام**: Frontend پیام کاربر به `/conversations/{id}/messages` می‌فرستد
3. **حفظ حافظه**: سرور تمام پیام‌های قبلی را بازیابی می‌کند
4. **ارسال به AI**: تمام history با prompt سیستمی به Gemini API می‌رود
5. **ذخیره نتیجه**: پاسخ AI و پیام کاربر در DB ذخیره می‌شود

## 🔐 نکات امنیتی

- CORS فقط از آدرس frontend مجاز است
- API Keys در .env محفوظ است
- Database connection secure است

## 📝 توسعه

برای محیط development:
```bash
# .env میں DEBUG=True کنید
# سرور با hot reload اجرا خواهد شد
```

## 🐛 Troubleshooting

**خطای Database Connection:**
- DATABASE_URL صحیح است؟
- PostgreSQL در حال اجرا است؟

**خطای API Key:**
- GOOGLE_API_KEY در .env صحیح است؟
- API Key مفعل است؟

**خطای CORS:**
- FRONTEND_URL در .env منطبق است؟
