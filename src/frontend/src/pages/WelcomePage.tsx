import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Common.css';
import './WelcomePage.css';

// 주제별 아이콘 및 라벨
const topics = [
  { key: 'festival', icon: '/fruit1.png', label: '축제' },
  { key: 'steam', icon: '/fruit2.png', label: '스팀게임' },
  { key: 'lineage', icon: '/fruit3.png', label: '리니지2M' },
  { key: 'stock', icon: '/fruit4.png', label: '주식' },
];
// 주제별 코멘트
const topicCommentMap: { [key: string]: string } = {
  festival: '축제봇입니다.',
  steam: '스팀게임봇입니다.',
  lineage: '리니지2M봇입니다.',
  stock: '주식봇입니다.',
};


const WelcomePage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [userInput, setUserInput] = useState('');

  // 아이콘 클릭 핸들러 
  const handleTopicClick = (topic: string) => {
    setSelectedTopic(prev => prev === topic ? null : topic);
  };

  // 주제별 코멘트 또는 공통 코멘트
  const comment = selectedTopic ? topicCommentMap[selectedTopic] : '하루하루봇입니다.';

  // 메시지 제출 시 실행되는 함수
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    const topic = selectedTopic || 'common';
    // ChatBotPage로 이동하면서 topic과 message를 함께 전달
    navigate(`/chat?msg=${encodeURIComponent(userInput)}&topic=${topic}`);
  };

  return (
    <div className="chatbot-container welcome-background">
      {/* 오른쪽 상단 로고 */}
      <img 
        src="/logo.png" 
        alt="hu 로고" 
        className="welcome-logo-inside"
        style={{ cursor: 'pointer' }}
        onClick={() => navigate('/topic-select')}
      />

      {/* 주제 선택 아이콘  */}
      <div className="fruit-center-box">
        <div className="fruit-wrapper">
          {topics.map((t) => (
            <img
              key={t.key}
              src={t.icon}
              alt={t.label}
              title={t.label}
              onClick={() => handleTopicClick(t.key)}   // topic 선택만 수행
              className={`fruit-icon ${selectedTopic === t.key ? 'selected' : ''}`}
            />
          ))}
        </div>
        {/* 말풍선 코멘트 (트리 중앙에 띄우기) */}
        <div className="comment-bubble">
          {comment}
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
          rows={1}
        />
        <button 
          type="submit" 
          className="chat-btn" 
          disabled={!userInput.trim()}
        >
          🌱
        </button>
      </form>
    </div>
  );
};

export default WelcomePage;
