# Frontend Integration Guide

## React/JavaScript Example

```typescript
// chatClient.ts
const API_URL = "http://localhost:8000/api/chat";

export class ChatClient {
  private conversationId: number | null = null;

  async createConversation(title: string = "New Conversation") {
    const response = await fetch(`${API_URL}/conversations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error("Failed to create conversation");
    }

    const data = await response.json();
    this.conversationId = data.id;
    return data;
  }

  async sendMessage(message: string) {
    if (!this.conversationId) {
      throw new Error("No active conversation");
    }

    const response = await fetch(
      `${API_URL}/conversations/${this.conversationId}/messages`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to send message");
    }

    return await response.json();
  }

  async getConversation() {
    if (!this.conversationId) {
      throw new Error("No active conversation");
    }

    const response = await fetch(
      `${API_URL}/conversations/${this.conversationId}`
    );

    if (!response.ok) {
      throw new Error("Failed to get conversation");
    }

    return await response.json();
  }

  setConversationId(id: number) {
    this.conversationId = id;
  }

  getConversationId() {
    return this.conversationId;
  }
}
```

## React Hook Example

```typescript
// useChat.ts
import { useState, useCallback } from "react";
import { ChatClient } from "./chatClient";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatClient] = useState(() => new ChatClient());

  const startConversation = useCallback(async (title?: string) => {
    try {
      setLoading(true);
      setError(null);
      await chatClient.createConversation(title);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [chatClient]);

  const sendMessage = useCallback(
    async (userMessage: string) => {
      try {
        setLoading(true);
        setError(null);

        const result = await chatClient.sendMessage(userMessage);

        setMessages([
          ...messages,
          result.user_message,
          result.assistant_message,
        ]);

        return result.assistant_message.content;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [chatClient, messages]
  );

  return {
    messages,
    loading,
    error,
    startConversation,
    sendMessage,
  };
}
```

## React Component Example

```tsx
// ChatComponent.tsx
import { useChat } from "./useChat";
import { useState } from "react";

export function ChatComponent() {
  const { messages, loading, startConversation, sendMessage } = useChat();
  const [input, setInput] = useState("");

  const handleStart = async () => {
    await startConversation("Business Coaching");
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const message = input;
    setInput("");

    try {
      await sendMessage(message);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="chat-container">
      <button onClick={handleStart} disabled={loading}>
        Start New Conversation
      </button>

      <div className="messages">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message message-${msg.role}`}
          >
            <strong>{msg.role === "user" ? "You" : "Coach"}</strong>
            <p>{msg.content}</p>
            <small>{new Date(msg.created_at).toLocaleTimeString()}</small>
          </div>
        ))}
      </div>

      <form onSubmit={handleSendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}
```

## Tauri (Desktop) Example

```typescript
// src-tauri/src/main.rs (if using Tauri's HTTP client)
// یا در JavaScript side:

import { http } from "@tauri-apps/api";

const API_URL = "http://localhost:8000/api/chat";

export async function createConversation(title: string) {
  const response = await http.post(`${API_URL}/conversations`, {
    body: http.Body.json({ title }),
  });
  return response.data;
}

export async function sendMessage(
  conversationId: number,
  message: string
) {
  const response = await http.post(
    `${API_URL}/conversations/${conversationId}/messages`,
    {
      body: http.Body.json({ message }),
    }
  );
  return response.data;
}
```

## CORS Configuration

API automatically allows:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React dev server)
- URL from `FRONTEND_URL` env variable

If you need to add more origins, update in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://your-production-url.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
