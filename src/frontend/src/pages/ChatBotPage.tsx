import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatBotPage.css';

const ChatBotPage: React.FC = () => {
  const [messages, setMessages] = useState<{ type: 'user' | 'bot'; text: string }[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBoxRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chatbot-container">
      <h1>하루하루</h1>
      <button className="tree-btn" onClick={() => (window.location.href = '/QuotePage')}>
        오늘의 명언
      </button>
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
        <input
          type="text"
          className="chat-input"
          placeholder="알고싶은 정보를 물어보세요"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" className="chat-btn" disabled={isLoading}>
          보내기
        </button>
      </form>
    </div>
  );
};

export default ChatBotPage;
