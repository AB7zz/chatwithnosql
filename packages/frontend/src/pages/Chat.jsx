import React, { useState } from 'react';
import { MessageSquare, PlusCircle, Settings } from 'lucide-react';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

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

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-gray-200 text-gray-800 p-4">
        <button className="flex items-center space-x-2 bg-zinc-700 hover:bg-zinc-600 w-full p-2 rounded mb-4">
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

      {/* Chat interface */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-sm p-2 rounded ${message.sender === 'user' ? 'bg-blue-500 text-gray-800' : 'bg-gray-200'}`}>
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
      </div>
    </div>
  );
};

export default Chat;