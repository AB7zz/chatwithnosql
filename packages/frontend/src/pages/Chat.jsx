import React, { useState } from 'react';
import { MessageSquare, PlusCircle, Settings } from 'lucide-react';
import axios from 'axios'

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isChatActive, setIsChatActive] = useState(false);

  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
      // Simulate AI response
      setTimeout(() => {
        setMessages(prev => [...prev, { text: "This is a sample AI response.", sender: 'ai' }]);
      }, 1000);
    }
  };

  const startNewChat = async() => {
    setIsChatActive(true);
    setMessages([]);
    await axios.get('http://localhost:6000/api/data-lake')
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-gray-200 text-gray-800 p-4">
        <button 
          className="flex items-center space-x-2 bg-zinc-700 hover:bg-zinc-600 w-full p-2 rounded mb-4"
          onClick={startNewChat}
        >
          <PlusCircle className='text-white' size={20} />
          <span className='text-white'>New chat</span>
        </button>
        <div className="space-y-2">
          <div className="hover:text-white flex items-center space-x-2 p-2 hover:bg-zinc-400 rounded cursor-pointer">
            <MessageSquare size={20} />
            <span className=''>Chat 1</span>
          </div>
          <div className="hover:text-white flex items-center space-x-2 p-2 hover:bg-zinc-400 rounded cursor-pointer">
            <MessageSquare size={20} />
            <span className=''>Chat 2</span>
          </div>
        </div>
        <div className="absolute bottom-4 left-4">
          <button className="hover:text-white flex items-center space-x-2 hover:bg-zinc-400 p-2 rounded">
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Chat interface or Welcome screen */}
      <div className="flex-1 flex flex-col">
        {isChatActive ? (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-sm p-2 rounded ${message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                    {message.text}
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={handleSend} className="p-4 border-t">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="flex-1 p-2 border rounded"
                  placeholder="Type your message..."
                />
                <button type="submit" className="bg-black text-white px-4 py-2 rounded">
                  Send
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold mb-4">Welcome to the Chat App</h1>
              <p className="text-xl mb-8">Click "New chat" to start a conversation</p>
              <button 
                className="bg-zinc-700 hover:bg-zinc-600 text-white px-6 py-3 rounded-lg text-lg"
                onClick={startNewChat}
              >
                Start New Chat
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;