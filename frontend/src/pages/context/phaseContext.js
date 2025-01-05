import React, { createContext, useContext, useState, useEffect } from "react";

const PhaseContext = createContext();

export const PhaseProvider = ({ children }) => {
  const [phase, setPhase] = useState(() => {
    // Retrieve from localStorage, or default to 'document-uploading'
    return localStorage.getItem('phase') || "document-uploading";
  });

  const [editMode, setEditMode] = useState(() => {
    return localStorage.getItem('editMode') || "structured-editing";
  });

  const [language, set_language] = useState(() => {
    return localStorage.getItem('language') || "en";
  });

  const [slides, setSlides] = useState(() => {
    return Number(localStorage.getItem('slides')) || 0;
  });

  const [project_id, setProject_id] = useState(() => {
    return localStorage.getItem('project_id') || '';
  });

  const baseUrl = "http://127.0.0.1:5000";

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('phase', phase);
    localStorage.setItem('editMode', editMode);
    localStorage.setItem('language', language);
    localStorage.setItem('slides', slides);
    localStorage.setItem('project_id', project_id);
  }, [phase, editMode, language, slides, project_id]);

  return (
    <PhaseContext.Provider value={{ phase, setPhase, editMode, setEditMode, language, set_language, baseUrl, project_id, setProject_id, slides, setSlides }}>
      {children}
    </PhaseContext.Provider>
  );
};

export const usePhase = () => {
  return useContext(PhaseContext);
};
