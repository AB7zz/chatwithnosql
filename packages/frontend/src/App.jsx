import React from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Connect from './pages/Connect'
import Choose from './pages/Choose'
import Chat from './pages/Chat'
import FileExplorer from './pages/FileExplorer'
import Navbar from './components/Navbar/Navbar'
import Home from './pages/Home'
import Profile from './pages/Profile'
function App() {

  return (
    <>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/connect" element={<Connect />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/choose" element={<Choose />} />
          <Route path="/files/:chatId" element={<FileExplorer />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
