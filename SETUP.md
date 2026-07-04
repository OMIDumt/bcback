# Setup Instructions

## خطوات نصب سریع

### Windows

```powershell
# 1. ایجاد virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. نصب وابستگی‌ها
pip install -r requirements.txt

# 3. ساخت .env
cp .env.example .env

# 4. ویرایش .env - اضافه کردن:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/business_coaching_db
# GOOGLE_API_KEY=your_api_key
# FRONTEND_URL=http://localhost:5173

# 5. اجرای سرور
python main.py
```

### PostgreSQL Setup (اگر نصب نشده)

**Windows:**
1. دانلود از https://www.postgresql.org/download/windows/
2. نصب PostgreSQL
3. دریافت password برای کاربر `postgres`
4. ایجاد database:

```bash
createdb business_coaching_db
```

### Google API Key

1. رفتن به: https://aistudio.google.com/apikey
2. کلیک روی "Create API Key"
3. کپی کردن کلید
4. اضافه کردن در .env

### اتصال Frontend

Frontend یا Tauri app باید به این endpoints درخواست بفرستد:

```javascript
// مثال برای JavaScript
const API_URL = "http://localhost:8000/api/chat";

// ایجاد مکالمه
const res = await fetch(`${API_URL}/conversations`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "مشاوره جدید" })
});
const conversation = await res.json();

// ارسال پیام
const messageRes = await fetch(
  `${API_URL}/conversations/${conversation.id}/messages`,
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "سؤال من چیست؟" })
  }
);
const result = await messageRes.json();
```

## 🔧 Development

برای development mode:

```bash
# .env میں تغییر دهید:
DEBUG=True

# سپس سرور اجرا کنید
python main.py
```

## ✅ تست سرور

```bash
# Health check
curl http://localhost:8000/api/chat/health

# ایجاد مکالمه
curl -X POST http://localhost:8000/api/chat/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```
