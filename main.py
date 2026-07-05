import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.routes import router
from database import init_db
from config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Business Coaching Chatbot API",
    description="API for AI-powered business coaching chatbot",
    version="1.0.0"
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# Initialize database immediately for local smoke tests and simple runs.
init_db()


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Business Coaching Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/chat-test", response_class=HTMLResponse)
def chat_test_page():
    """Simple browser-based chat tester for Railway deployment."""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Railway Chat Tester</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
    input, button, textarea { font-size: 16px; padding: 10px; margin: 6px 0; width: 100%; box-sizing: border-box; }
    button { cursor: pointer; }
    .box { border: 1px solid #ddd; padding: 12px; margin-top: 12px; border-radius: 8px; }
    .msg { margin: 8px 0; padding: 10px; border-radius: 6px; background: #f7f7f7; }
    .assistant { background: #eef6ff; }
  </style>
</head>
<body>
  <h1>Railway Chat Tester</h1>
  <p>Open this page on your Railway deployment to test the chatbot directly.</p>
  <button id="createBtn">Create conversation</button>
  <div id="status" class="box">Status: waiting</div>
  <div class="box">
    <label>Message</label>
    <textarea id="messageInput" rows="3" placeholder="Type your message here"></textarea>
    <button id="sendBtn">Send message</button>
  </div>
  <div id="messages" class="box"></div>

  <script>
    const apiBase = window.location.origin + '/api/chat';
    let conversationId = null;

    async function parseResponse(res) {
      const text = await res.text();
      try { return text ? JSON.parse(text) : {}; } catch { return { raw: text }; }
    }

    function showError(message) {
      setStatus('Error: ' + message);
      renderMessage('System', 'Error: ' + message);
    }

    async function createConversation() {
      setStatus('Creating conversation...');
      try {
        const res = await fetch(apiBase + '/conversations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'Railway Test' })
        });
        const data = await parseResponse(res);
        if (!res.ok) throw new Error(data.detail || data.raw || 'Failed to create conversation');
        conversationId = data.id;
        setStatus('Conversation created: ' + conversationId);
        renderMessage('System', 'Conversation ready.');
        return true;
      } catch (error) {
        showError(error.message || 'Unknown error');
        return false;
      }
    }

    async function sendMessage() {
      try {
        if (!conversationId) {
          const created = await createConversation();
          if (!created) return;
        }
        const message = document.getElementById('messageInput').value.trim();
        if (!message) return;
        setStatus('Sending message...');
        const res = await fetch(apiBase + '/conversations/' + conversationId + '/messages', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });
        const data = await parseResponse(res);
        if (!res.ok) throw new Error(data.detail || data.raw || 'Failed to send message');
        renderMessage('You', message);
        renderMessage('Assistant', data.assistant_message?.content || 'No response');
        setStatus('Message sent');
        document.getElementById('messageInput').value = '';
      } catch (error) {
        showError(error.message || 'Unknown error');
      }
    }

    function renderMessage(role, text) {
      const div = document.createElement('div');
      div.className = 'msg' + (role === 'Assistant' ? ' assistant' : '');
      div.innerHTML = '<strong>' + role + ':</strong> ' + String(text).replace(/\n/g, '<br>');
      document.getElementById('messages').appendChild(div);
    }

    function setStatus(text) {
      document.getElementById('status').innerText = 'Status: ' + text;
    }

    document.getElementById('createBtn').onclick = createConversation;
    document.getElementById('sendBtn').onclick = sendMessage;
  </script>
</body>
</html>
""")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.debug
    )
