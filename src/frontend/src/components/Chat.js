import React, { useState } from 'react';

function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ msg: input }),
      });

      const data = await res.json();
      const botMessage = { sender: 'bot', text: data.answer };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('서버 에러:', err);
    }
  };

  return (
    <div>
      <h2>챗봇</h2>
      <div style={{ minHeight: 200, border: '1px solid #ccc', padding: 10 }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <p><strong>{msg.sender === 'user' ? '나' : '봇'}:</strong> {msg.text}</p>
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        placeholder="메시지를 입력하세요"
        style={{ width: '80%', marginRight: 10 }}
      />
      <button onClick={handleSend}>전송</button>
    </div>
  );
}

export default Chat;
