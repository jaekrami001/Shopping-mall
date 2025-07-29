import React, { useState } from 'react';

const Chat = ({ user }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = (e) => {
    e.preventDefault();
    setMessages([...messages, { text: newMessage, sender: user.username }]);
    setNewMessage('');
  };

  return (
    <div className="chat">
      <h2>Chat with Seller</h2>
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender === user.username ? 'sent' : 'received'}`}>
            <p>{message.text}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleSendMessage}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default Chat;
