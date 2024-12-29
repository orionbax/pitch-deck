import React from "react";
import { useNavigate } from "react-router-dom";
import { usePhase } from '../pages/context/phaseContext';

const Navigation = () => {
  const navigate = useNavigate();
  const { language } = usePhase(); // Get the current language state

  // Function to handle navigation to different paths
  const handleNavigation = (path) => {
    navigate(path); // Navigate to the desired path
  };

  // Define labels for navigation based on the language
  const labels = {
    en: {
      document: "Document",
      slides: "Slides",
      preview: "Preview"
    },
    no: {
      document: "Dokument",
      slides: "Lysbilder",
      preview: "Forhåndsvisning"
    }
  };

  // Get the appropriate labels based on the selected language
  const currentLabels = labels[language] || labels.en;

  return (
    <div className="my-3">
      <h1 className="text-lg font-normal mb-4 text-white">{language === "en" ? "Navigation" : "Navigasjon"}</h1>

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
            <span>{currentLabels.document}</span>
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
            <span>{currentLabels.slides}</span>
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
            <span>{currentLabels.preview}</span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
