import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FiServer, FiDatabase, FiUser, FiLock } from 'react-icons/fi'
import { motion } from 'framer-motion'

const Connect = () => {
  const navigate = useNavigate()
  const [config, setConfig] = useState({
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setConfig(prevConfig => ({ ...prevConfig, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Here you would typically send the config to your backend or store it securely
    console.log('Configuration submitted:', config)
    // Redirect to chat interface
    navigate('/chat')
  }

  const inputFields = [
    { 
      icon: <FiServer className="text-lg font-satoshi" />, 
      label: 'Host', 
      name: 'host', 
      type: 'text',
      placeholder: 'e.g., your-instance.warehouse.com'
    },
    { 
      icon: <FiServer className="text-lg" />, 
      label: 'Port', 
      name: 'port', 
      type: 'number',
      placeholder: 'e.g., 5439'
    },
    { 
      icon: <FiDatabase className="text-lg" />, 
      label: 'Database', 
      name: 'database', 
      type: 'text',
      placeholder: 'e.g., analytics_db'
    },
    { 
      icon: <FiUser className="text-lg" />, 
      label: 'Username', 
      name: 'username', 
      type: 'text',
      placeholder: 'Enter your username'
    },
    { 
      icon: <FiLock className="text-lg" />, 
      label: 'Password', 
      name: 'password', 
      type: 'password',
      placeholder: 'Enter your password'
    },
  ]

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-8"
    >
      <motion.h1 
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
        className="text-4xl font-bold mb-4 text-white text-center"
      >
        Connect Your Warehouse
      </motion.h1>
      
      <motion.p 
        initial={{ y: -30 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100, delay: 0.1 }}
        className="text-gray-300 mb-12 text-center max-w-2xl"
      >
        Enter your credentials to establish a secure connection
      </motion.p>

      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-xl p-1 max-w-md w-full"
      >
        <div className="bg-gray-900/90 backdrop-blur-xl rounded-lg p-8">
          {error && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg relative mb-6"
            >
              {error}
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {inputFields.map((field, index) => (
              <motion.div 
                key={field.name}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  <div className="flex items-center gap-2">
                    {field.icon}
                    {field.label}
                  </div>
                </label>
                <div className="relative">
                  <input
                    className="w-full bg-gray-800/50 border border-gray-700 text-gray-100 rounded-lg py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-200 placeholder-gray-500"
                    placeholder={field.placeholder}
                    id={field.name}
                    type={field.type}
                    name={field.name}
                    value={config[field.name]}
                    onChange={handleChange}
                    required
                  />
                  {config[field.name] && (
                    <motion.div 
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute right-3 top-3 text-green-400"
                    >
                      ✓
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`
                w-full mt-6 bg-gradient-to-r from-blue-500 to-indigo-600 
                text-white font-medium py-3 px-6 rounded-lg focus:outline-none 
                focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2 
                focus:ring-offset-gray-900 transition-all duration-200
                ${isLoading ? 'cursor-not-allowed opacity-80' : 'hover:shadow-lg hover:shadow-blue-500/25'}
              `}
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  />
                  <span>Establishing Connection...</span>
                </div>
              ) : (
                'Connect Now'
              )}
            </motion.button>
          </form>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-8 text-center"
      >
        <p className="text-gray-400 text-sm">
          Having trouble connecting? 
          <a href="#" className="text-blue-400 ml-2 hover:text-blue-300">
            View our documentation
          </a>
        </p>
      </motion.div>
    </motion.div>
  )
}

export default Connect
