import { useState, useEffect, useRef } from "react";
import {
  MessageSquare,
  PlusCircle,
  Settings,
  Loader,
  Send,
  Trash2,
} from "lucide-react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
// import { useNavigate, Link } from "react-router-dom";
import { Chart, registerables } from "chart.js";
import { db } from "../firebase/config";
import {
  collection,
  addDoc,
  getDocs,
  query,
  orderBy,
  doc,
  setDoc,
  deleteDoc,
} from "firebase/firestore";

// Register chart.js components
Chart.register(...registerables);

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isChatActive, setIsChatActive] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  // const [chatHistory, setChatHistory] = useState([
  //   { id: 1, title: "Previous Chat 1", timestamp: "2h ago", fileCount: 5 },
  //   { id: 2, title: "Previous Chat 2", timestamp: "1d ago", fileCount: 3 },
  // ]);
  const chartRefs = useRef({});
  const chatContainerRef = useRef(null);
  const [currentRoomId, setCurrentRoomId] = useState(null);
  const [chatRooms, setChatRooms] = useState([]);

  // const navigate = useNavigate();

  // Effect to scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Effect to render charts when messages change
  useEffect(() => {
    messages.forEach((message, index) => {
      if (message.chartData && chartRefs.current[index]) {
        const ctx = chartRefs.current[index].getContext("2d");

        // Destroy existing chart if it exists
        if (chartRefs.current[index].chart) {
          chartRefs.current[index].chart.destroy();
        }

        // Create new chart instance with the data
        chartRefs.current[index].chart = new Chart(ctx, {
          type: message.chartData.type,
          data: message.chartData.data,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "top",
                labels: {
                  color: "#fff",
                },
              },
            },
            scales: {
              y: {
                ticks: {
                  color: "#fff",
                },
                grid: {
                  color: "rgba(255, 255, 255, 0.1)",
                },
              },
              x: {
                ticks: {
                  color: "#fff",
                },
                grid: {
                  color: "rgba(255, 255, 255, 0.1)",
                },
              },
            },
          },
        });
      }
    });
  }, [messages]);

  // Fetch chat rooms on component mount
  useEffect(() => {
    fetchChatRooms();
  }, []);

  // Fetch messages when room changes
  useEffect(() => {
    if (currentRoomId) {
      fetchMessages(currentRoomId);
    }
  }, [currentRoomId]);

  const fetchChatRooms = async () => {
    try {
      const roomsRef = collection(db, "chatrooms");
      const roomsSnap = await getDocs(roomsRef);
      const roomsData = roomsSnap.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
        timestamp: doc.data().timestamp?.toDate().toLocaleString() || "Unknown",
      }));
      setChatRooms(roomsData);
    } catch (error) {
      console.error("Error fetching chat rooms:", error);
    }
  };

  const fetchMessages = async (roomId) => {
    try {
      const messagesRef = collection(db, `chatrooms/${roomId}/messages`);
      const q = query(messagesRef, orderBy("timestamp", "asc"));
      const messagesSnap = await getDocs(q);
      const messagesData = messagesSnap.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
        timestamp: doc.data().timestamp?.toDate(),
      }));
      setMessages(messagesData);
    } catch (error) {
      console.error("Error fetching messages:", error);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentRoomId) return;

    const newMessage = {
      text: input,
      sender: "user",
      timestamp: new Date(),
    };

    try {
      // Add message to Firebase
      const messagesRef = collection(db, `chatrooms/${currentRoomId}/messages`);
      await addDoc(messagesRef, newMessage);

      // Update UI
      setMessages((prev) => [...prev, newMessage]);
      setInput("");
      setIsTyping(true);

      // Process with AI
      const res = await axios.post("http://localhost:5000/api/process-query", {
        company_id: "makeaton",
        query: input,
      });

      // Save AI response to Firebase
      const aiResponse = {
        text:
          res.data.type === "graph"
            ? "Here's a visualization of the data:"
            : res.data.answer,
        sender: "ai",
        timestamp: new Date(),
        chartData: res.data.type === "graph" ? res.data.graphData : null,
      };

      await addDoc(messagesRef, aiResponse);

      // Update UI
      setIsTyping(false);
      setMessages((prev) => [...prev, aiResponse]);

      // Update room's last message
      const roomRef = doc(db, "chatrooms", currentRoomId);
      await setDoc(
        roomRef,
        {
          lastMessage: input,
          timestamp: new Date(),
        },
        { merge: true }
      );

      // Refresh chat rooms to update last message
      fetchChatRooms();
    } catch (error) {
      console.error("Error sending message:", error);
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          text: "Sorry, I encountered an error. Please try again.",
          sender: "ai",
          timestamp: new Date(),
          isError: true,
        },
      ]);
    }
  };

  const startNewChat = async () => {
    try {
      // Create new chat room
      const newRoomRef = await addDoc(collection(db, "chatrooms"), {
        title: `Chat ${new Date().toLocaleString()}`,
        timestamp: new Date(),
        lastMessage: null,
      });

      setCurrentRoomId(newRoomRef.id);
      setIsChatActive(true);
      setMessages([]);

      // Refresh chat rooms list
      fetchChatRooms();

      // Initialize data lake
      await axios.post("http://localhost:5000/api/data-lake", {
        company_id: "makeaton",
      });
    } catch (error) {
      console.error("Error creating new chat:", error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex min-h-screen bg-gradient-to-br from-gray-900 to-gray-800"
    >
      {/* Sidebar */}
      <motion.div
        initial={{ x: -50 }}
        animate={{ x: 0 }}
        className="w-64 bg-gray-800/50 backdrop-blur-xl text-gray-100 p-4 border-r border-gray-700"
      >
        <button
          className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-indigo-600 w-full p-3 rounded-lg mb-6 hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200"
          onClick={startNewChat}
        >
          <PlusCircle size={20} />
          <span>New chat</span>
        </button>

        <div className="space-y-2">
          {chatRooms.map((room) => (
            <motion.div
              key={room.id}
              whileHover={{ scale: 1.02 }}
              className="flex items-center space-x-3 p-3 hover:bg-gray-700/50 rounded-lg cursor-pointer group"
              onClick={() => {
                setCurrentRoomId(room.id);
                setIsChatActive(true);
              }}
            >
              <MessageSquare size={18} />
              <div className="flex-1">
                <p className="text-sm font-medium">{room.title}</p>
                <p className="text-xs text-gray-400">{room.timestamp}</p>
              </div>
              <Trash2
                size={16}
                className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-400 transition-opacity"
                onClick={async (e) => {
                  e.stopPropagation();
                  // Implement delete functionality
                  if (
                    window.confirm("Are you sure you want to delete this chat?")
                  ) {
                    try {
                      await deleteDoc(doc(db, "chatrooms", room.id));
                      fetchChatRooms();
                      if (currentRoomId === room.id) {
                        setCurrentRoomId(null);
                        setIsChatActive(false);
                        setMessages([]);
                      }
                    } catch (error) {
                      console.error("Error deleting chat:", error);
                    }
                  }
                }}
              />
            </motion.div>
          ))}
        </div>

        <div className="absolute bottom-4 left-4">
          <button className="hover:text-white flex items-center space-x-2 hover:bg-zinc-400 p-2 rounded">
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </div>
      </motion.div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <AnimatePresence mode="wait">
          {isChatActive ? (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1 flex flex-col h-screen"
            >
              <div
                ref={chatContainerRef}
                className="flex-1 overflow-y-auto p-6 space-y-6 mt-[100px]"
              >
                {messages.map((message, index) => (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    key={index}
                    className={`flex ${
                      message.sender === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`
                      max-w-xl p-4 rounded-2xl shadow-lg
                      ${
                        message.sender === "user"
                          ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white"
                          : "bg-gray-800/50 backdrop-blur-sm text-gray-100"
                      }
                      ${message.isError ? "border-red-500 border" : ""}
                    `}
                    >
                      {message.text}
                      <div className="text-xs opacity-50 mt-2">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                      {message.chartData && (
                        <div className="mt-4 h-[300px] w-[500px]">
                          <canvas
                            ref={(el) => (chartRefs.current[index] = el)}
                            className="w-full h-full"
                          />
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
                {isTyping && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center space-x-2 text-gray-400"
                  >
                    <Loader className="animate-spin" size={16} />
                    <span>AI is typing...</span>
                  </motion.div>
                )}
              </div>

              {/* Input Form */}
              <motion.form
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                onSubmit={handleSend}
                className="p-4 border-t border-gray-700 bg-gray-800/30 backdrop-blur-sm"
              >
                <div className="max-w-4xl mx-auto flex space-x-4">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="flex-1 bg-gray-700/50 text-gray-100 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder-gray-400"
                    placeholder="Type your message..."
                  />
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    type="submit"
                    className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2"
                  >
                    <Send size={18} />
                    <span>Send</span>
                  </motion.button>
                </div>
              </motion.form>
            </motion.div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-4xl font-ab7 font-bold mb-4 text-white">
                  Welcome to the Chat App
                </h1>
                <p className="text-xl mb-8 text-white">
                  Click new chat to start a conversation
                </p>
                <button
                  className="bg-zinc-700 hover:bg-zinc-600 text-white px-6 py-3 rounded-lg text-lg"
                  onClick={startNewChat}
                >
                  Start New Chat
                </button>
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default Chat;
