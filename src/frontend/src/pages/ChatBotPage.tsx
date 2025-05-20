import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatBotPage.css';

const ChatBotPage: React.FC = () => {
  const [messages, setMessages] = useState<{ type: 'user' | 'bot'; text: string }[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBoxRef = useRef<HTMLDivElement>(null);


  // 입력창 자동 높이 조절
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = e.target.scrollHeight + "px";
  };

  // 메시지 전송
  const sendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    setIsLoading(true);
    setMessages(prev => [...prev, { type: 'user', text: userInput }]);

    try {
      const res = await axios.post('/api/chat', { message: userInput });
      setMessages(prev => [...prev, { type: 'bot', text: res.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { type: 'bot', text: '오류가 발생했습니다.' }]);
    } finally {
      setUserInput('');
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();      // 기본 줄바꿈 막기
      sendMessage();           // 메시지 전송 함수 호출
    }
    // Shift+Enter는 아무 처리 안 하면 줄바꿈이 됨
  };


  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chatbot-container">
      <div className="title-box">
        <img src="/logo_max.png" alt="로고" className="title-icon" />
        <span className="title-text">하루하루</span>
      </div>

      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.type}`}>
            <b>{msg.type === 'user' ? '나' : '챗봇'}:</b> {msg.text}
          </div>
        ))}
      </div>
      <form
          className="chat-form"
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
        >
          <textarea
            className="chat-input"
            placeholder="알고싶은 정보를 물어보세요"
            value={userInput}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            style={{ resize: "none" }}
          />
          <button type="submit" className="chat-btn" disabled={isLoading}>
            전송
          </button>
        </form>
    </div>
  );
};

export default ChatBotPage;
