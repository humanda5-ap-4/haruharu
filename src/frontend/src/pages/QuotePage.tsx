import React, { useState } from 'react';
import './QuotePage.css';

const QuotePage: React.FC = () => {
  const [quotes] = useState([
    { text: "행복은 결코 외부에서 오지 않는다. 그것은 우리 내면의 상태다.", author: "달라이 라마" },
    { text: "성공의 비결은 목적의 일관성에 있다.", author: "벤자민 디즈레일리" },
    { text: "실패는 성공으로 가는 가장 빠른 길이다.", author: "토마스 왓슨" },
    { text: "작은 기회로부터 종종 위대한 업적이 시작된다.", author: "데모스테네스" },
    { text: "자신을 믿어라. 당신이 할 수 있다고 생각하든 할 수 없다고 생각하든, 당신 말이 맞다.", author: "헨리 포드" }
  ]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextQuote = () => {
    setCurrentIndex((currentIndex + 1) % quotes.length);
  };

  return (
    <div className="quote-container">
      <h1>오늘의 명언</h1>
      <button onClick={() => (window.history.back())} className="chat-btn" style={{ marginBottom: '16px' }}>
        챗봇가기
      </button>
      <blockquote className="quote">
        "{quotes[currentIndex].text}"
      </blockquote>
      <p className="author">- {quotes[currentIndex].author}</p>
      <button onClick={nextQuote} className="next-btn">다음 명언 보기</button>
    </div>
  );
};

export default QuotePage;
