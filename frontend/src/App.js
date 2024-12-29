import { Routes, Route, useLocation } from 'react-router-dom';
import Home from './pages/landingPage.js';
import UploadDocument from './pages/uploadDocument.js';
import SelectSlide from './pages/selectSlide.js';
import Preview from './pages/preview.js';
import Sidebar from './components/statusSideBar.js';

const Layout = ({ children }) => {
  const location = useLocation();

  // Only apply layout changes if the path is not "/"
  const isHomePage = location.pathname === '/';

  return (
    <div className="flex h-screen">
      {/* Sidebar should not display on the Home page */}
      {!isHomePage && (
        <div className="fixed top-0 left-0 bottom-0 w-64 bg-[#004F59] z-10">
          <Sidebar />
        </div>
      )}
      <div className={`flex-grow ${!isHomePage ? 'ml-64' : ''} overflow-y-auto`}>
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
        <Route path="/preview" element={<Preview />} />
      </Routes>
    </Layout>
  );
}

export default App;
