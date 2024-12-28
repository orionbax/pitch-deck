/* eslint-disable no-unused-vars */
import { Routes, Route } from 'react-router-dom';
import Home from './pages/landingPage.js';
import UploadDocument from './pages/uploadDocument.js';
import SelectSlide from './pages/selectSlide.js';
import './App.css';

function App() {
  return (
   
    <Routes>
      <Route path='/' element={<Home />}  />
      <Route path='/upload' element={<UploadDocument />}  />
      <Route path='/slide'  element={<SelectSlide />} />
    </Routes>

  );
}

export default App;
