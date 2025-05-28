import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Common.css';
import './TopicSelectPage.css';

const topics = [
  { key: 'festival', icon: '/fruit1.png', label: '축제' },
  { key: 'steam', icon: '/fruit2.png', label: '스팀게임' },
  { key: 'lineage', icon: '/fruit3.png', label: '리니지2M' },
  { key: 'stock', icon: '/fruit4.png', label: '주식' },
];

const topicCommentMap: { [key: string]: string } = {
  festival: '축제봇입니다.',
  steam: '스팀게임봇입니다.',
  lineage: '리니지2M봇입니다.',
  stock: '주식봇입니다.',
};

const TopicSelectPage: React.FC = () => {
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const navigate = useNavigate();

  // 아이콘 클릭
  const handleTopicClick = (topic: string) => {
    setSelectedTopic(topic);
  };

  // 저장소 가기 버튼 클릭
  const handleGoToChatBot = () => {
    if (selectedTopic) {
        navigate(`/chat?topic=${selectedTopic}`);
    }
  };


  return (
    <div className="chatbot-container topic-select-background">
      {/* 오른쪽 상단 로고 */}
      <img
        src="/logo.png"
        alt="hu"
        className="topic-select-logo"
        onClick={() => navigate('/')}
      />
    <div className="nonnn"> 

    </div>


      {/* 주제 아이콘 */}
      <div className="topic-select-icons-wrapper">
        <div className="topic-select-icons">
            {topics.map((t) => (
            <img
                key={t.key}
                src={t.icon}
                alt={t.label}
                className={`topic-icon${selectedTopic === t.key ? ' selected' : ''}`}
                onClick={() => handleTopicClick(t.key)}
            />
            ))}
        </div>

        {/* 코멘트 말풍선 */}
        <div className="topic-comment-bubble">
            {selectedTopic ? topicCommentMap[selectedTopic] : '주제를 선택하세요.'}
        </div>

        {/* 저장소 가기 버튼 */}
        <button
            className="go-storage-btn"
            onClick={handleGoToChatBot}
            disabled={!selectedTopic}
        >
            저장소 가기
        </button>
        </div>
    </div>
  );
};

export default TopicSelectPage;
