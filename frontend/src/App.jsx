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

  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    "What courses are offered?",
    "How can I get admission into Sree Dattha?",
    "Tell me about placements",
    "What facilities are available?",
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  const sendMessage = async (question = message) => {
    const userMessage = question.trim();

    if (!userMessage || isLoading) {
      return;
    }

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        sender: "user",
        text: userMessage,
      },
    ]);

    setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(
        "https://sreedattha-chatbot.onrender.com/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: userMessage,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Unable to get a response from the chatbot."
        );
      }

      const data = await response.json();

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
            "Sorry, I couldn't connect to the Sree Dattha assistant. Please try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="site-header">
        <div className="header-content">
          <h1>Sree Dattha Educational Institutions</h1>
        </div>
      </header>

      <main className="main-content">
        <div className="welcome-section">
          <h2>Welcome to Sree Dattha</h2>

          <p>
            Ask our virtual assistant about courses, admissions,
            placements, facilities, and more.
          </p>
        </div>
      </main>

      {!isChatOpen && (
        <button
          className="chat-launcher"
          onClick={() => setIsChatOpen(true)}
          aria-label="Open chatbot"
        >
          <span className="chat-launcher-icon">💬</span>
          <span>Chat with us</span>
        </button>
      )}

      {isChatOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="chat-avatar">SD</div>

              <div>
                <h3>Sree Dattha Assistant</h3>

                <div className="online-status">
                  <span className="online-dot"></span>
                  <span>Online</span>
                </div>
              </div>
            </div>

            <button
              className="close-button"
              onClick={() => setIsChatOpen(false)}
              aria-label="Close chatbot"
            >
              ×
            </button>
          </div>

          <div className="messages-container">
            {messages.map((chatMessage, index) => (
              <div
                key={index}
                className={`message-row ${
                  chatMessage.sender === "user"
                    ? "user-row"
                    : "bot-row"
                }`}
              >
                <div
                  className={`message-bubble ${
                    chatMessage.sender === "user"
                      ? "user-message"
                      : "bot-message"
                  }`}
                  style={{
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {chatMessage.text}
                </div>
              </div>
            ))}

            {messages.length === 1 && !isLoading && (
              <div className="suggested-questions">
                {suggestedQuestions.map(
                  (question, index) => (
                    <button
                      key={index}
                      className="suggested-question"
                      onClick={() => sendMessage(question)}
                    >
                      {question}
                    </button>
                  )
                )}
              </div>
            )}

            {isLoading && (
              <div className="message-row bot-row">
                <div className="message-bubble bot-message">
                  Thinking...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <textarea
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask about courses, admissions, placements..."
              rows="1"
              disabled={isLoading}
            />

            <button
              className="send-button"
              onClick={() => sendMessage()}
              disabled={!message.trim() || isLoading}
              aria-label="Send message"
            >
              {isLoading ? "..." : "Send"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;