import React, { useState, useEffect } from 'react';
import vbailogo from "../vbailogo.svg";
import Phase from './phase';
import Navigation from './navigation';
import { usePhase } from '../pages/context/phaseContext';
import translations from './translation'; // Import the translations

const StatusSideBar = () => {
  const token = localStorage.getItem('authToken');
  const [selectedLanguage, setSelectedLanguage] = useState("en"); // default to English
  const [selectedOption, setSelectedOption] = useState("structured-editing"); // Default to structured-editing
  const { setEditMode, language, set_language } = usePhase();

  // Syncing local state with phase context
  useEffect(() => {
    setEditMode(selectedOption);
    set_language(selectedLanguage);
    console.log("lang", language);
  }, [selectedOption, setEditMode, selectedLanguage, set_language, language]);

  const handleOptionChange = (option) => {
    if (selectedOption === option) {
      setSelectedOption(null); // Deselect if the same option is clicked
    } else {
      setSelectedOption(option); // Select the clicked option
    }
  };

  const handleLanguageChange = async (event) => {
    const newLanguage = event.target.value;
    setSelectedLanguage(newLanguage);

    try {
      const response = await fetch('http://127.0.0.1:5000/set_language', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ language: newLanguage }),
        credentials: 'include',
      });

      const data = await response.json();

      if (data.status === 'success') {
        console.log(`${translations.languageSuccessMessage[newLanguage]}: ${newLanguage}`);
      } else {
        console.error(`${translations.languageErrorMessage[newLanguage]}: ${data.error}`);
      }
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  return (
    <div className="w-full sm:w-64 h-full bg-[#004F59] flex flex-col py-5">
      <div className="px-4 sm:px-10">
        <img src={vbailogo} alt="logo" className="w-36 sm:w-40 mx-auto sm:mx-0" />

        <div className="my-3">
          <h1 className="text-[#548062] text-base font-semibold my-1">{translations.languageLabel[selectedLanguage]}</h1>
          <select
            className="bg-[#004F59] text-white w-full sm:w-auto"
            value={selectedLanguage}
            onChange={handleLanguageChange}
          >
            <option value="en">English</option>
            <option value="no">Norwegian</option>
          </select>
        </div>

        <div className="my-3">
          <h1 className="text-base text-white font-normal mb-4">{translations.editModeLabel[selectedLanguage]}</h1>

          <div className="mb-2">
            <label
              htmlFor="structured-editing"
              className={`flex items-center space-x-2 cursor-pointer ${selectedOption === 'structured-editing' ? 'text-[#D3EC99]' : 'text-white'}`}
            >
              <input
                type="radio"
                id="structured-editing"
                name="editing-option"
                className="hidden"
                onChange={() => handleOptionChange('structured-editing')}
                checked={selectedOption === 'structured-editing'}
              />
              <div className={`w-5 h-5 border rounded-full flex items-center justify-center ${selectedOption === 'structured-editing' ? 'bg-[#D3EC99]' : 'bg-transparent'}`}>
                {selectedOption === 'structured-editing' && (
                  <div className="w-3 h-3 rounded-full bg-black"></div>
                )}
              </div>
              <span>{translations.structuredEditing[selectedLanguage]}</span>
            </label>
          </div>

          <div>
            <label
              htmlFor="guided-feedback"
              className={`flex items-center space-x-2 cursor-pointer font-normal ${selectedOption === 'guided-feedback' ? 'text-[#D3EC99]' : 'text-white'}`}
            >
              <input
                type="radio"
                id="guided-feedback"
                name="editing-option"
                className="hidden"
                onChange={() => handleOptionChange('guided-feedback')}
                checked={selectedOption === 'guided-feedback'}
              />
              <div className={`w-5 h-5 border rounded-full flex items-center justify-center ${selectedOption === 'guided-feedback' ? 'bg-[#D3EC99]' : 'bg-transparent'}`}>
                {selectedOption === 'guided-feedback' && (
                  <div className="w-3 h-3 rounded-full bg-black"></div>
                )}
              </div>
              <span>{translations.guidedFeedback[selectedLanguage]}</span>
            </label>
          </div>
        </div>

        {/* Phase indication */}
        <Phase />
        <Navigation />
      </div>
    </div>
  );
};

export default StatusSideBar;
