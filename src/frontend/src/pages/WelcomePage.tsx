import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ChatBotPage.css';

const WelcomePage: React.FC = () => {
  const [userInput, setUserInput] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent | React.KeyboardEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    const message = userInput;
    setUserInput('');
    navigate(`/chat?msg=${encodeURIComponent(message)}`);
  };

  return (
    <div className="chatbot-container welcome-background">
      {/* 오른쪽 상단 로고 */}
      <img src="/logo.png" alt="hu 로고" className="welcome-logo-inside" />

      <div className="welcome-spacer" />  {/* 빈 공간 확보 */}

      {/* 하단 입력창 */}
      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          className="chat-input"
          placeholder="알고싶은 정보를 물어보세요"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault(); // 줄바꿈 방지
              // 제출 함수 호출
              handleSubmit(e as any);
            }
          }}
          rows={1}
        />
        <button type="submit" className="chat-btn">🌱</button>
      </form>
    </div>
  );
};

export default WelcomePage;
