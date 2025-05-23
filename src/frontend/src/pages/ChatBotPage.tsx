import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Common.css';
import './ChatBotPage.css';

const ChatBotPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const topic = new URLSearchParams(location.search).get('topic') || 'default';
  const LOCAL_STORAGE_KEY = `chatbot_messages_${topic}`;

  // 1. localStorage에서 불러오기
  const getInitialMessages = () => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  };

  const topicIconMap: { [key: string]: string } = {
    festival: '/fruit1.png',
    steam: '/fruit2.png',
    lineage: '/fruit3.png',
    etc: '/fruit4.png',
  };
  
  const initialMessage = new URLSearchParams(location.search).get('msg');


  // 2. 상태 정의
  const [messages, setMessages] = useState<{ type: 'user' | 'bot'; text: string }[]>(getInitialMessages);
  const [typingMessage, setTypingMessage] = useState('');
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBoxRef = useRef<HTMLDivElement>(null);
  const didRun = useRef(false);

  // 3. messages가 바뀔 때마다 localStorage에 저장
  useEffect(() => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(messages));
  }, [messages, LOCAL_STORAGE_KEY]);

  // 4. 입력창 자동 높이 조절
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  };

  // 5. 쿼리스트링 msg 삭제 함수
  const removeMsgQuery = () => {
    const newSearch = new URLSearchParams(location.search);
    newSearch.delete('msg');
    navigate({ search: newSearch.toString() }, { replace: true });
  };

  // 6. 타자 효과 함수
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

  // 7. 메시지 전송
  const sendMessage = async () => {
    if (!userInput.trim() || isLoading) return;

    setIsLoading(true);
    setMessages(prev => [...prev, { type: 'user', text: userInput }]);

    try {
      const res = await axios.post('http://localhost:8000/chat', { msg: userInput });
      showTypingEffect(res.data?.answer);
    } catch {
      showTypingEffect('오류가 발생했습니다.');
    } finally {
      setUserInput('');
      setIsLoading(false);
      removeMsgQuery();
    }
  };

  // 8. 엔터키 적용
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 9. 대화초기화 함수
  const handleClearChat = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    setMessages([]);
  };

  

  // 초기 메시지 처리
  useEffect(() => {
    if (didRun.current) return;
    didRun.current = true;
    if (!initialMessage) return;

    const fetchBotResponse = async () => {
      setIsLoading(true);
      setMessages(prev => [...prev, { type: 'user', text: initialMessage }]);
      try {
        const res = await axios.post('http://localhost:8000/chat', { msg: initialMessage });
        showTypingEffect(res.data?.answer);
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
        <button
          className="chat-clear-btn"
          onClick={handleClearChat}
          style={{
            background: "#fff",
            border: "1px solid rgb(211, 49, 0)",
            borderRadius: "70px",
            padding: "4px 8px",
            cursor: "pointer",
            marginLeft: "0px"
          }}
        >
          대화초기화
        </button>
        {topic && topicIconMap[topic] && (
          <img
            src={topicIconMap[topic]}
            alt="선택 주제 아이콘"
            className="title-topic-icon"
          />
        )}
      </div>

      {/* 채팅 메시지 */}
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
