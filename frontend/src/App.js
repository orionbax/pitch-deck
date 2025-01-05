import { Routes, Route, useLocation } from 'react-router-dom';
import { useState } from 'react';
import Home from './pages/landingPage.js';
import UploadDocument from './pages/uploadDocument.js';
import SelectSlide from './pages/selectSlide.js';
import Preview from './pages/preview.js';
import Sidebar from './components/statusSideBar.js';
import PreviewSlides from './components/previewSlide';
import Onboarding from './pages/onboarding.js';
import OnboardingStep from './pages/onboardingHow.js';
import OnboardingHowItWorks from './pages/onboardingTips.js';

const App = () => {
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Routes where the sidebar should not be visible
  const noSidebarRoutes = ['/', '/how', '/tips', '/project'];
  const isNoSidebarPage = noSidebarRoutes.includes(location.pathname);

  const toggleSidebar = () => {
    setIsSidebarOpen((prevState) => !prevState);
  };

  return (
    <div className="flex flex-col sm:flex-row h-screen bg-[#F1F1F1]">
      {/* Hamburger Menu for small screens */}
      {!isNoSidebarPage && (
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
      {!isNoSidebarPage && (
        <div
          className={`fixed sm:relative top-0 left-0 bottom-0 w-full sm:w-64 bg-[#004F59] z-10 ${
            isSidebarOpen ? 'block' : 'hidden'
          } sm:block`}
        >
          <Sidebar />
        </div>
      )}

      {/* Content area */}
      <div className={`flex-grow ${isNoSidebarPage ? 'w-full' : ''} overflow-y-auto`}>
        <Routes>
          <Route path="/project" element={<Home />} />
          <Route path="/upload" element={<UploadDocument />} />
          <Route path="/slide" element={<SelectSlide />} />
          <Route path="/preview" element={<PreviewSlides />} />
          <Route path="/tips" element={<Onboarding />} />
          <Route path="/" element={<OnboardingStep />} />
          <Route path="/how" element={<OnboardingHowItWorks />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
