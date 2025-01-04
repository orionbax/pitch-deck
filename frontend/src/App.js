import { Routes, Route, useLocation } from 'react-router-dom';
import { useState } from 'react';
import Home from './pages/landingPage.js';
import UploadDocument from './pages/uploadDocument.js';
import SelectSlide from './pages/selectSlide.js';
import Preview from './pages/preview.js';
import Sidebar from './components/statusSideBar.js';
import PreviewSlides from './components/previewSlide';

const Layout = ({ children }) => {
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Only apply layout changes if the path is not "/"
  const isHomePage = location.pathname === '/';

  const toggleSidebar = () => {
    setIsSidebarOpen(prevState => !prevState);
  };

  return (
    <div className="flex flex-col sm:flex-row h-screen bg-[#F1F1F1]">
      {/* Hamburger Menu for small screens */}
      {!isHomePage && (
        <button 
          className="sm:hidden fixed top-4 left-4 z-20"
          onClick={toggleSidebar}
        >
          <div className="w-6 h-0.5 bg-black mb-1"></div>
          <div className="w-6 h-0.5 bg-black mb-1"></div>
          <div className="w-6 h-0.5 bg-black"></div>
        </button>
      )}

      {/* Sidebar */}
      {!isHomePage && (
        <div
          className={`fixed sm:relative top-0 left-0 bottom-0 w-full sm:w-64 bg-[#004F59] z-10 ${isSidebarOpen ? 'block' : 'hidden'} sm:block`}
        >
          <Sidebar />
        </div>
      )}

      {/* Content area, adjust the margin-left for larger screens */}
      <div className={`flex-grow ${!isHomePage ? '' : ''} overflow-y-auto`}>
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<UploadDocument />} />
        <Route path="/slide" element={<SelectSlide />} />
        <Route path="/preview" element={<PreviewSlides />} />
      </Routes>
    </Layout>
  );
}

export default App;
