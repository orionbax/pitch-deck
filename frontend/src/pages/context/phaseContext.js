import React , { createContext, useContext, useState } from "react";

const PhaseContext = createContext();

export const PhaseProvider = ({ children }) => {
    const [phase, setPhase] = useState("document-uploading"); // Default phase
    const [editMode, setEditMode] = useState("structured-editing");
    const [language, set_language] = useState("en")
    const baseUrl = "http://127.0.0.1:5000"
    const [project_id, setProject_id] = useState('')
  
    return (
      <PhaseContext.Provider value={{ phase, setPhase,editMode, setEditMode,language, set_language,baseUrl, project_id, setProject_id}}>
        {children}
      </PhaseContext.Provider>
    );
  };
  
  // Hook to use the context
  export const usePhase = () => {
    return useContext(PhaseContext);
  };