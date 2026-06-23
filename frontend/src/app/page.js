"use client";

import { useState, useRef, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const clearChat = () => {
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const currentMessage = message;

    const userMessage = {
      role: "user",
      text: currentMessage,
    };

    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setMessage("");
    setLoading(true);

    try {
      const conversationHistory = updatedMessages.map((msg) => ({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: msg.text,
      }));

      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: conversationHistory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail || `Server error (${response.status})`
        );
      }

      const data = await response.json();

      const aiMessage = {
        role: "assistant",
        text: data.response || "No response received.",
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);

      const errorText =
        error.message === "Failed to fetch"
          ? "Unable to connect to backend."
          : error.message || "Something went wrong.";

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `Error: ${errorText}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="h-screen bg-black text-white flex flex-col items-center p-4">

      {/* Header */}
      <div className="w-full max-w-5xl flex justify-between items-center mb-4">
        <h1 className="text-5xl font-bold text-blue-400">
           🤖 Rohith AI Chatbot
        </h1>

        <button
          onClick={clearChat}
          className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg"
        >
          Clear Chat
        </button>
      </div>

      {/* Chat Container */}
      <div className="w-full max-w-5xl flex flex-col h-[80vh]">

        {/* Messages */}
        <div className="flex-1 bg-gray-900 border border-gray-700 rounded-lg p-4 overflow-y-auto">

          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-10">
              Start a conversation...
            </div>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`mb-4 flex ${
                msg.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >
              <div
                className={`max-w-[75%] p-4 rounded-xl whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-blue-600"
                    : "bg-gray-700"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-700 p-4 rounded-xl text-gray-300">
                AI is typing...
              </div>
            </div>
          )}

          <div ref={bottomRef}></div>
        </div>

        {/* Input Area */}
        <div className="flex gap-3 mt-4">

          <input
            type="text"
            value={message}
            placeholder="Type your question..."
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
            className="flex-1 p-4 rounded-lg bg-gray-800 text-white placeholder-gray-400 border border-gray-600 focus:outline-none focus:border-blue-500"
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            className={`px-8 rounded-lg font-semibold ${
              loading
                ? "bg-gray-600 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "..." : "Send"}
          </button>

        </div>

      </div>

    </main>
  );
}