import React from "react";
import { useNavigate } from "react-router-dom";

const Navigation = () => {
  const navigate = useNavigate();

  const handleNavigation = (path) => {
    navigate(path); // Navigate to the desired path
  };

  

  return (
    <div className="my-3">
      <h1 className="text-lg font-normal mb-4 text-white">Navigation</h1>

      <div className="space-y-4 text-white">
        {/* Document Navigation */}
        <div>
          <label htmlFor="document" className="flex items-center space-x-2">
            <input
              type="radio"
              id="document"
              name="navigation"
              onClick={() => handleNavigation("/upload")}
              className="accent-blue-500"
            />
            <span>Document</span>
          </label>
        </div>

        {/* Slides Navigation */}
        <div>
          <label htmlFor="slides" className="flex items-center space-x-2">
            <input
              type="radio"
              id="slides"
              name="navigation"
              onClick={() => handleNavigation("/slide")}
              className="accent-blue-500"
            />
            <span>Slides</span>
          </label>
        </div>

        {/* Preview Navigation */}
        <div>
          <label htmlFor="preview" className="flex items-center space-x-2">
            <input
              type="radio"
              id="preview"
              name="navigation"
              onClick={() => handleNavigation("/preview")}
              className="accent-blue-500"
            />
            <span>Preview</span>
          </label>
        </div>

        {/* Export Navigation */}
        <div>
          <label htmlFor="export" className="flex items-center space-x-2">
            <input
              type="radio"
              id="export"
              name="navigation"
              onClick={() => handleNavigation("/export")}
              className="accent-blue-500"
            />
            <span>Export</span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
