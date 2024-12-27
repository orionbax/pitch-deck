/* eslint-disable no-unused-vars */
import { Routes, Route } from 'react-router-dom';
import Home from './pages/landingPage.jsx';
import UploadDocument from './pages/uploadDocument.js';
import './App.css';

function App() {
  return (
   
    <Routes>
      <Route path='/' element={<Home />}  />
      <Route path='/upload' element={<UploadDocument />}  />
    </Routes>

  );
}

export default App;
