import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "👋 Hello! Welcome to Sree Dattha. How can I help you today?",
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);

  // Reference to the bottom of the conversation
  const messagesEndRef = useRef(null);

  // Automatically scroll to the newest message
  useEffect(() => {
    if (isChatOpen) {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }
  }, [messages, isLoading, isChatOpen]);

  const sendMessage = async () => {
    if (!message.trim() || isLoading) {
      return;
    }

    const userMessage = message.trim();

    // Add user's message to the conversation
    setMessages((previousMessages) => [
      ...previousMessages,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    // Clear input
    setMessage("");

    // Show loading state
    setIsLoading(true);

    try {
      // Send question to FastAPI
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          message: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Server returned status ${response.status}`
        );
      }

      const data = await response.json();

      // Add chatbot answer
      setMessages((previousMessages) => [
        ...previousMessages,
        {
          sender: "bot",
          text:
            data.answer ||
            "I could not find an answer to that question.",
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          sender: "bot",
          text:
            "Sorry, I could not connect to the Sree Dattha assistant. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !isLoading) {
      sendMessage();
    }
  };

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <h1>Sree Dattha</h1>
        <p>Educational Institutions</p>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <h2>Welcome to Sree Dattha</h2>

        <p>
          Ask our virtual assistant about courses, admissions,
          placements, facilities, and more.
        </p>
      </main>

      {/* Chat Window */}
      {isChatOpen && (
        <div className="chat-window">

          {/* Chat Header */}
          <div className="chat-header">
            <div>
              <strong>🎓 Sree Dattha Assistant</strong>
              <span>Online</span>
            </div>

            <button
              className="close-button"
              onClick={() => setIsChatOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="chat-messages">

            {messages.map((chatMessage, index) => (
              <div
                key={index}
                className={
                  chatMessage.sender === "user"
                    ? "user-message"
                    : "bot-message"
                }
                style={{
                  whiteSpace: "pre-wrap",
                }}
              >
                {chatMessage.text}
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div
                className="bot-message"
                style={{
                  whiteSpace: "pre-wrap",
                }}
              >
                Thinking...
              </div>
            )}

            {/* Invisible element used for auto-scroll */}
            <div ref={messagesEndRef} />

          </div>

          {/* Input Area */}
          <div className="chat-input">

            <input
              type="text"
              placeholder="Ask about courses, admissions, placements..."
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />

            <button
              onClick={sendMessage}
              disabled={
                isLoading || !message.trim()
              }
              aria-label="Send message"
            >
              ➤
            </button>

          </div>
        </div>
      )}

      {/* Floating Chat Button */}
      {!isChatOpen && (
        <button
          className="chat-button"
          onClick={() => setIsChatOpen(true)}
        >
          💬 Chat with us
        </button>
      )}

    </div>
  );
}

export default App;