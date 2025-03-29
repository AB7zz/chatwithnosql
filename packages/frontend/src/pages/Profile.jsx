import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaEnvelope, FaPhone, FaUsers, FaGlobe, FaComments, FaFile, FaImage, FaMusic, FaVideo } from 'react-icons/fa';
import axios from 'axios';
import { getAuth, onAuthStateChanged } from 'firebase/auth';

const Profile = () => {
  const [fileData, setFileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const auth = getAuth();
        
        // Wait for auth state to be ready
        await new Promise((resolve) => {
          const unsubscribe = onAuthStateChanged(auth, (user) => {
            unsubscribe();
            resolve(user);
          });
        });

        const currentUser = auth.currentUser;
        console.log(currentUser, "currentUser");

        if (!currentUser) {
          setError('No authenticated user found');
          setLoading(false);
          return;
        }

        const response = await axios.post('http://localhost:5000/api/profile/files', {
          company_id: currentUser.uid
        });
        console.log(response.data, "response.data"); 
        setFileData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  const fileCategories = [
    {
      name: 'PDF Documents',
      icon: <FaFile className="text-2xl" />,
      type: 'pdf',
      color: 'from-red-400 to-red-600'
    },
    {
      name: 'Images',
      icon: <FaImage className="text-2xl" />,
      type: 'image',
      color: 'from-blue-400 to-blue-600'
    },
    {
      name: 'Audio Files',
      icon: <FaMusic className="text-2xl" />,
      type: 'audio',
      color: 'from-green-400 to-green-600'
    },
    {
      name: 'Video Files',
      icon: <FaVideo className="text-2xl" />,
      type: 'video',
      color: 'from-purple-400 to-purple-600'
    }
  ];

  if (loading) return <div className="text-center p-8">Loading...</div>;
  if (error) return <div className="text-center text-red-500 p-8">Error: {error}</div>;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-8"
    >
      <motion.h1 
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        className="text-4xl font-bold mb-4 text-white text-center"
      >
        Storage Overview
      </motion.h1>

      {fileData && (
        <div className="w-full max-w-6xl">
          {/* Statistics Summary */}
          <div className="bg-gray-800/50 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400">Total Files</p>
                <p className="text-2xl text-white">{fileData.statistics.total_files}</p>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400">Total Size</p>
                <p className="text-2xl text-white">{Math.round(fileData.statistics.total_size / 1024 / 1024)} MB</p>
              </div>
            </div>
          </div>

          {/* File Categories */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {fileCategories.map((category) => (
              <motion.div
                key={category.type}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`bg-gradient-to-br ${category.color} rounded-xl p-6`}
              >
                <div className="bg-white/10 rounded-lg p-6">
                  <div className="bg-white rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    {category.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-white text-center mb-2">
                    {category.name}
                  </h3>
                  <p className="text-white/80 text-center">
                    {fileData.files[category.type].length} files
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* File Lists */}
          <div className="mt-8 space-y-6">
            {fileCategories.map((category) => (
              <div key={category.type} className="bg-gray-800/50 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4">{category.name}</h3>
                <div className="space-y-2">
                  {fileData.files[category.type].map((file, index) => (
                    <div key={index} className="bg-gray-700/50 rounded-lg p-4 flex justify-between items-center">
                      <span className="text-white">{file.name}</span>
                      <span className="text-gray-400">{Math.round(file.size / 1024)} KB</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Profile;
