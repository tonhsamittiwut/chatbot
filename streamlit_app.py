import React, { useState, useEffect } from 'react';

const SmartChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const generateSmartReply = (userMessage) => {
    // ตัวอย่างการสร้างคำตอบ
    if (userMessage.includes('ดวง')) {
      return 'ดวงของคุณในวันนี้เป็นไปในทางที่ดี!';
    } else if (userMessage.includes('ชื่อ')) {
      return 'ชื่อของคุณมีความหมายว่า...';
    } else {
      return 'ขอโทษค่ะ ฉันไม่เข้าใจคำถามของคุณ';
    }
  };

  const handleSend = () => {
    const userMessage = input.trim();
    if (userMessage) {
      setMessages([...messages, { text: userMessage, sender: 'user' }]);
      const reply = generateSmartReply(userMessage);
      setMessages((prevMessages) => [...prevMessages, { text: reply, sender: 'bot' }]);
      setInput('');
    }
  };

  useEffect(() => {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }, [messages]);

  return (
    <div>
      <div id="chat-container" style={{ height: '400px', overflowY: 'scroll' }}>
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender}>
            <strong>{msg.sender === 'user' ? 'คุณ' : 'บอท'}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
      />
      <button onClick={handleSend}>ส่ง</button>
    </div>
  );
};

export default SmartChatbot;
