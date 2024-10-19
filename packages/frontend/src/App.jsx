import React from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Connect from './pages/Connect'
import Choose from './pages/Choose'
import Chat from './pages/Chat'

function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/connect" element={<Connect />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/choose" element={<Choose />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
