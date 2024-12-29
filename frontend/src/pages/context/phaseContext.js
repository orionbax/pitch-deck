import React , { createContext, useContext, useState } from "react";

const PhaseContext = createContext();

export const PhaseProvider = ({ children }) => {
    const [phase, setPhase] = useState("document-uploading"); // Default phase
  
    return (
      <PhaseContext.Provider value={{ phase, setPhase }}>
        {children}
      </PhaseContext.Provider>
    );
  };
  
  // Hook to use the context
  export const usePhase = () => {
    return useContext(PhaseContext);
  };