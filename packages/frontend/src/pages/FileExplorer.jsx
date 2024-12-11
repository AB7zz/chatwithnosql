import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FileText, Image, Music, Video, Folder, 
  ChevronLeft, Grid, List, Download, Eye
} from 'lucide-react';

const FileExplorer = () => {
  const { chatId } = useParams();
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  const dummyFiles = [
    { 
      id: 1, 
      name: 'Project Documentation.pdf', 
      type: 'document', 
      size: '2.4 MB',
      modified: '2024-03-15',
      icon: <FileText className="w-8 h-8 text-orange-400" />
    },
    { 
      id: 2, 
      name: 'Meeting Recording.mp4', 
      type: 'video',
      size: '156 MB',
      modified: '2024-03-14',
      icon: <Video className="w-8 h-8 text-blue-400" />
    },
    { 
      id: 4, 
      name: 'Background Music.mp3', 
      type: 'audio',
      size: '6.8 MB',
      modified: '2024-03-12',
      icon: <Music className="w-8 h-8 text-green-400" />
    },
    { 
      id: 5, 
      name: 'Screenshot.png', 
      type: 'image',
      size: '1.2 MB',
      modified: '2024-03-11',
      icon: <Image className="w-8 h-8 text-purple-400" />
    },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800"
    >
      {/* Header */}
      <div className="border-b border-gray-700 bg-gray-800/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/chat"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <ChevronLeft className="w-6 h-6" />
              </Link>
              <h1 className="text-xl font-semibold text-white">
                Chat Files
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-blue-500/20 text-blue-400' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button 
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-blue-500/20 text-blue-400' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* File Grid/List */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className={`
          ${viewMode === 'grid' 
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4' 
            : 'space-y-2'
          }
        `}>
          {dummyFiles.map((file) => (
            <motion.div
              key={file.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ scale: 1.02 }}
              className={`
                bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700
                ${viewMode === 'grid' ? 'p-4' : 'p-3'}
              `}
            >
              <div className={`
                ${viewMode === 'grid' 
                  ? 'flex flex-col items-center text-center'
                  : 'flex items-center space-x-4'
                }
              `}>
                {file.icon}
                <div className={`
                  ${viewMode === 'grid' ? 'mt-3 w-full' : 'flex-1'}
                `}>
                  <p className="text-white font-medium truncate">
                    {file.name}
                  </p>
                  <p className="text-gray-400 text-sm">
                    {file.size || file.items}
                  </p>
                </div>
                <div className={`
                  flex items-center space-x-2
                  ${viewMode === 'grid' ? 'mt-4' : ''}
                `}>
                  <button className="p-2 text-gray-400 hover:text-white transition-colors">
                    <Eye className="w-5 h-5" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-white transition-colors">
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default FileExplorer;