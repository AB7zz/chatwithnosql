import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, MessageSquare, Database, User, LogOut } from 'lucide-react';
import { auth } from '../../firebase/config.js';
import { useAuthState } from 'react-firebase-hooks/auth';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [user] = useAuthState(auth);

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/choose', icon: Database, label: 'Warehouse' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
  ];

  const handleLogout = async () => {
    try {
      await auth.signOut();
      navigate('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 bg-gradient-to-r from-gray-900/95 to-gray-800/95 backdrop-blur-sm border-b border-gray-700/50 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex-shrink-0"
          >
            <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 text-transparent bg-clip-text">
              DataLake
            </Link>
          </motion.div>

          {/* Navigation Items */}
          <div className="flex space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <motion.div
                  key={item.path}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Link
                    to={item.path}
                    className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200
                      ${isActive 
                        ? 'bg-gradient-to-r from-blue-500/20 to-indigo-500/20 text-blue-400' 
                        : 'text-gray-300 hover:bg-gray-700/50'
                      }`}
                  >
                    <Icon size={18} className="mr-2" />
                    {item.label}
                  </Link>
                </motion.div>
              );
            })}
          </div>

          {/* User Section */}
          <div className="flex items-center space-x-2">
            {user ? (
              <>
                <Link to="/profile">
                  <motion.div 
                    whileHover={{ scale: 1.05 }}
                    className="flex items-center"
                  >
                    <button className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-lg hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200">
                      <User size={18} className="mr-2" />
                      <span>Profile</span>
                    </button>
                  </motion.div>
                </Link>
                <motion.div 
                  whileHover={{ scale: 1.05 }}
                  className="flex items-center"
                >
                  <button 
                    onClick={handleLogout}
                    className="flex items-center space-x-2 bg-gray-700 text-gray-200 px-4 py-2 rounded-lg hover:bg-gray-600 transition-all duration-200"
                  >
                    <LogOut size={18} className="mr-2" />
                    <span>Logout</span>
                  </button>
                </motion.div>
              </>
            ) : (
              <Link to="/login">
                <motion.div 
                  whileHover={{ scale: 1.05 }}
                  className="flex items-center"
                >
                  <button className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-lg hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200">
                    <span>Login</span>
                  </button>
                </motion.div>
              </Link>
            )}
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
