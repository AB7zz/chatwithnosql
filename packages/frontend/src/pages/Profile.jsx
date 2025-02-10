import React from 'react'
import { motion } from 'framer-motion'
import { FaEnvelope, FaPhone, FaUsers, FaGlobe, FaComments } from 'react-icons/fa'

const Profile = () => {
  const dataCategories = [
    {
      name: 'CRM Data',
      icon: <FaUsers className="text-2xl" />,
      description: 'Customer relationship notes and interactions',
      color: 'from-blue-400 to-blue-600'
    },
    {
      name: 'Emails',
      icon: <FaEnvelope className="text-2xl" />,
      description: 'Email communications and snippets',
      color: 'from-green-400 to-blue-500'
    },
    {
      name: 'Phone Calls',
      icon: <FaPhone className="text-2xl" />,
      description: 'Call transcripts and recordings',
      color: 'from-purple-400 to-pink-600'
    },
    {
      name: 'Social Media',
      icon: <FaComments className="text-2xl" />,
      description: 'Social media interactions and posts',
      color: 'from-orange-400 to-red-600'
    },
    {
      name: 'Website Behavior',
      icon: <FaGlobe className="text-2xl" />,
      description: 'User activity and website interactions',
      color: 'from-teal-400 to-emerald-600'
    }
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
        Data Profile Overview
      </motion.h1>
      <motion.p 
        initial={{ y: -30 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100, delay: 0.1 }}
        className="text-gray-300 mb-12 text-center max-w-2xl"
      >
        Explore the different types of data being collected and analyzed
      </motion.p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
        {dataCategories.map((category, index) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2 }}
            key={category.name}
          >
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className={`bg-gradient-to-br ${category.color} rounded-xl shadow-xl p-6 h-full`}
            >
              <div className="bg-white/10 rounded-lg p-6 backdrop-blur-sm">
                <div className="bg-white rounded-full p-4 w-16 h-16 mx-auto mb-6 flex items-center justify-center text-gray-800">
                  {category.icon}
                </div>
                <h2 className="text-2xl font-bold text-white text-center mb-3">
                  {category.name}
                </h2>
                <p className="text-white/80 text-center">
                  {category.description}
                </p>
              </div>
            </motion.div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-12 text-center"
      >
        <p className="text-gray-400 text-sm">
          Want to manage your data preferences? 
          <a href="#" className="text-blue-400 ml-2 hover:text-blue-300">
            Update your settings
          </a>
        </p>
      </motion.div>
    </motion.div>
  )
}

export default Profile
