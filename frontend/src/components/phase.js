import React from "react";
import { usePhase } from "../pages/context/phaseContext";

const PhaseIndicator = () => {
  const { phase, language } = usePhase(); // Get current phase and language

  // Define phase labels in English and Norwegian
  const phases = {
    en: {
      "document-uploading": "Phase 1: Document Uploading",
      "slide-selection": "Phase 2: Slide Selection",
      "content-generating": "Phase 3: Content Generating",
      "preview-slide": "Phase 4: Preview Slide",
      "download-pdf": "Phase 5: Download",
    },
    no: {
      "document-uploading": "Fase 1: Dokumentopplasting",
      "slide-selection": "Fase 2: Lysbildevalg",
      "content-generating": "Fase 3: Innholdsgenerering",
      "preview-slide": "Fase 4: Lysbildesjekk",
      "download-pdf": "Fase 5: laste ned",
    },
  };

  // Get the appropriate phase texts based on the selected language
  const currentPhases = phases[language] || phases.en;

  // Get the index of the current phase (1-based index)
  const currentPhaseIndex = Object.keys(currentPhases).indexOf(phase) + 1;

  // Calculate progress percentage
  const progressPercentage = (currentPhaseIndex / Object.keys(currentPhases).length) * 100;

  return (
    <div className="text-white my-3">
      <h1 className="text-lg font-normal mb-4">
        {language === "en" ? "Current Phase" : "Nåværende Fase"}
      </h1>

      {/* Progress Bar */}
      <div className="w-full bg-gray-600 rounded-full h-2 overflow-hidden">
        <div
          className="bg-[#D3EC99] h-2 rounded-full"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>

      {/* Current Phase Text */}
      <p className="mt-4">
        <strong>{currentPhases[phase] || "Unknown Phase"}</strong>
      </p>
    </div>
  );
};

export default PhaseIndicator;
