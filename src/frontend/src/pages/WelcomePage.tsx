import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Common.css';
import './WelcomePage.css';

// 선택 가능한 주제 아이콘 목록
const topics = [
  { key: 'festival', icon: '/fruit1.png', label: '축제' },
  { key: 'steam', icon: '/fruit2.png', label: '스팀게임' },
  { key: 'lineage', icon: '/fruit3.png', label: '리니지2M' },
  { key: 'etc', icon: '/fruit4.png', label: '주식' },
];

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [userInput, setUserInput] = useState('');

  // 메시지 제출 시 실행되는 함수
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !selectedTopic) return;

    // ChatBotPage로 이동하면서 topic과 message를 함께 전달
    navigate(`/chat?msg=${encodeURIComponent(userInput)}&topic=${selectedTopic}`);
  };

  return (
    <div className="chatbot-container welcome-background">
      {/* 오른쪽 상단 로고 */}
      <img src="/logo.png" alt="hu 로고" className="welcome-logo-inside" />

      {/* 중간에 아이콘 선택 표시 */}
      <div className="fruit-center-box">
        <div className="fruit-wrapper">
          {topics.map((t) => (
            <img
              key={t.key}
              src={t.icon}
              alt={t.label}
              title={t.label}
              onClick={() => setSelectedTopic(t.key)}   // topic 선택만 수행
              className={`fruit-icon ${selectedTopic === t.key ? 'selected' : ''}`}
            />
          ))}
        </div>
      </div>


      {/* 하단 입력창 */}
      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          className="chat-input"
          placeholder="주제를 선택 후 알고싶은 정보를 물어보세요"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();     // 줄바꿈 방지
              handleSubmit(e as any); // 제출 함수 호출
            }
          }}
          disabled={!selectedTopic}
          rows={1}
        />
        <button 
          type="submit" 
          className="chat-btn" 
          disabled={!selectedTopic || !userInput.trim()}
        >
          🌱
        </button>
      </form>
    </div>
  );
};

export default WelcomePage;
