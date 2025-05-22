import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Common.css';
import './ChatBotPage.css';

const ChatBotPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const topic = new URLSearchParams(location.search).get('topic');
  const topicIconMap: { [key: string]: string } = {
    festival: '/fruit1.png',
    steam: '/fruit2.png',
    lineage: '/fruit3.png',
    etc: '/fruit4.png',
  };
  const initialMessage = new URLSearchParams(location.search).get('msg');
  const [messages, setMessages] = useState<{ type: 'user' | 'bot'; text: string }[]>([]);
  const [typingMessage, setTypingMessage] = useState('');
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBoxRef = useRef<HTMLDivElement>(null);
  const didRun = useRef(false);

  // 입력창 자동 높이 조절
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  };

  // 쿼리스트링 msg 삭제 함수
  const removeMsgQuery = () => {
    const newSearch = new URLSearchParams(location.search);
    newSearch.delete('msg');
    navigate({ search: newSearch.toString() }, { replace: true });
  };

  // 타자 효과 함수
  const showTypingEffect = (text?: string | null) => {
    if (!text) {
      setMessages(prev => [...prev, { type: 'bot', text: '오류가 발생했습니다.' }]);
      setTypingMessage('');
      return;
    }
    setTypingMessage('');
    let index = 0;
    const typeNextChar = () => {
      if (index < text.length) {
        setTypingMessage(prev => prev + text[index]);
        index++;
        setTimeout(typeNextChar, 40);
      } else {
        setMessages(prev => [...prev, { type: 'bot', text }]);
        setTypingMessage('');
      }
    };
    typeNextChar();
  };

  // 메시지 전송
  const sendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    setIsLoading(true);
    setMessages(prev => [...prev, { type: 'user', text: userInput }]);

    try {
      const res = await axios.post('/api/chat', { message: userInput });
      showTypingEffect(res.data?.response);
    } catch {
      showTypingEffect('오류가 발생했습니다.');
    } finally {
      setUserInput('');
      setIsLoading(false);
      removeMsgQuery();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }

  };

  // 초기 메시지 처리
  useEffect(() => {
    if (didRun.current) return;
    didRun.current = true;
    if (!initialMessage) return;

    const fetchBotResponse = async () => {
      setIsLoading(true);
      setMessages([{ type: 'user', text: initialMessage }]);
      try {
        const res = await axios.post('/api/chat', { message: initialMessage });
        showTypingEffect(res.data?.response);
      } catch {
        showTypingEffect('오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
        removeMsgQuery();
      }
    };
    fetchBotResponse();
    // eslint-disable-next-line
  }, []);

  // 스크롤 항상 하단 유지
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages, typingMessage]);

  return (
    <div className="chatbot-container">
      <div className="title-box">
        <div className="title-left" onClick={() => navigate('/')}>
          <img src="/logo_max.png" alt="로고" className="title-icon" />
          <span className="title-text">하루하루</span>
        </div>
        {topic && topicIconMap[topic] && (
          <img
            src={topicIconMap[topic]}
            alt="선택 주제 아이콘"
            className="title-topic-icon"
          />
        )}
      </div>

      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.type}`}>
            <b>{msg.type === 'user' ? '나' : '챗봇'}:</b> {msg.text}
          </div>
        ))}
        {typingMessage && (
          <div className="chat-message bot">
            <b>챗봇:</b> {typingMessage}
          </div>
        )}
      </div>
      <form
        className="chat-form"
        onSubmit={e => {
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
