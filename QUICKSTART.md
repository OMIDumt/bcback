# 🚀 Quick Start

## 5 دقیقه برای اجرا کردن

### Step 1: Setup (2 دقیقه)

```powershell
# 1. باز کردن PowerShell و رفتن به پوشه backend
cd backend

# 2. ایجاد virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. نصب وابستگی‌ها
pip install -r requirements.txt
```

### Step 2: Setup Database (2 دقیقه)

```powershell
# 1. اگر PostgreSQL نصب نشده:
# دانلود و نصب از https://www.postgresql.org/download/windows/

# 2. ایجاد database
createdb business_coaching_db

# 3. ایجاد .env file
copy .env.example .env

# 4. ویرایش .env و اضافه کردن:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/business_coaching_db
# GOOGLE_API_KEY=your_google_api_key
```

### Step 3: API Key (1 دقیقه)

1. رفتن به: https://aistudio.google.com/apikey
2. کلیک "Create API Key"
3. کپی کردن کلید و اضافه کردن در .env

### Step 4: اجرا (فوری)

```powershell
python main.py
```

✅ **Done!** سرور اجرا شد: `http://localhost:8000`

---

## 🧪 تست کردن

### Health Check
```bash
curl http://localhost:8000/api/chat/health
```

### ایجاد مکالمه
```bash
curl -X POST http://localhost:8000/api/chat/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'

# Response:
# {
#   "id": 1,
#   "title": "Test",
#   "created_at": "2024-01-01T12:00:00",
#   ...
# }
```

### ارسال پیام
```bash
curl -X POST http://localhost:8000/api/chat/conversations/1/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "سلام، میخواهم یک کسب و کار شروع کنم"}'
```

---

## 📱 اتصال به Frontend

### JavaScript/React
```javascript
const response = await fetch('http://localhost:8000/api/chat/conversations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: 'My Chat' })
});

const conversation = await response.json();
console.log(conversation.id); // Use this ID for messaging
```

---

## 📁 ساختار پروژه

```
backend/
├── main.py              ← اجرا کردن: python main.py
├── config.py            ← تنظیمات و environment variables
├── database.py          ← اتصال PostgreSQL
├── models.py            ← جداول database
├── requirements.txt     ← وابستگی‌ها
├── .env.example         ← متغیرهای محیط
├── api/
│   └── routes.py        ← API endpoints
└── services/
    └── chat_service.py  ← منطق چت و AI
```

---

## 🔑 مهمترین فایل‌ها

| فایل | توضیح |
|------|--------|
| `main.py` | نقطه ورود - FastAPI app |
| `services/chat_service.py` | منطق چت، اتصال به Gemini AI |
| `api/routes.py` | API endpoints برای frontend |
| `models.py` | جداول: Conversation, Message |
| `.env` | کلیدها و تنظیمات |

---

## 🐛 مشکلات عام و حل‌شان

### مشکل: "ModuleNotFoundError"
```powershell
# حل: مطمئن شوید venv فعال است
.\venv\Scripts\activate
```

### مشکل: "Database connection error"
```powershell
# حل: PostgreSQL اجرا می‌شود؟
# اگر کاربر/رمز اشتباه: تغییر DATABASE_URL در .env
```

### مشکل: "API Key not found"
```powershell
# حل: GOOGLE_API_KEY در .env صحیح است؟
# از https://aistudio.google.com/apikey دریافت کنید
```

### مشکل: "CORS error" در frontend
```python
# حل: FRONTEND_URL در .env منطبق با frontend است
FRONTEND_URL=http://localhost:5173  # برای Tauri/Lovable
```

---

## 📖 مستندات بیشتر

- **[README.md](./README.md)** - توضیح کامل
- **[SETUP.md](./SETUP.md)** - setup تفصیلی
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - معماری سیستم
- **[FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md)** - اتصال frontend
- **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** - بهترین شیوه‌ها

---

## ⚙️ Production Deployment

### با Docker
```bash
docker-compose up
```

### بدون Docker
```bash
# Setup PostgreSQL
# تغییر DATABASE_URL برای production DB
# تغییر DEBUG=False در .env
python main.py
```

### نکات امنیتی
- [ ] GOOGLE_API_KEY محفوظ است
- [ ] DATABASE_URL رمز قوی دارد
- [ ] DEBUG=False است
- [ ] FRONTEND_URL به production URL تغییر کرد

---

## 💡 بعدی چیست؟

✅ Backend آماده است!

حالا می‌توانید:
1. ✅ Frontend رو با Tauri/Lovable بسازید
2. ✅ API endpoints رو در frontend فراخوانی کنید
3. ✅ Chat interface رو طراحی کنید
4. ✅ Features اضافی اضافه کنید (auth, user profiles, etc.)

---

## 🎓 یادگیری

### فایل‌های مهم برای درک:
1. `services/chat_service.py` - چگونه حافظه کار می‌کند
2. `api/routes.py` - API چگونه طراحی شده
3. `ARCHITECTURE.md` - جریان کامل سیستم

### تغییرات سادگی:
- **System Prompt**: تغییر در `services/chat_service.py`
- **Database Fields**: تغییر در `models.py` + migration
- **API Response**: تغییر در `api/routes.py`

---

**Happy Coding! 🚀**
