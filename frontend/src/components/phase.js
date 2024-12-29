import React from "react";
import { usePhase } from "../pages/context/phaseContext";

const PhaseIndicator = () => {
  const { phase } = usePhase(); // `phase` holds the current phase string like "document-uploading"

  const phases = {
    "document-uploading": "Phase 1: Document Uploading",
    "slide-selection": "Phase 2: Slide Selection",
    "content-generating": "Phase 3: Content Generating",
    "preview-slide": "Phase 4: Preview Slide",
  };

  // Get the index of the current phase (1-based index)
  const currentPhaseIndex = Object.keys(phases).indexOf(phase) + 1;

  // Calculate progress percentage
  const progressPercentage = (currentPhaseIndex / Object.keys(phases).length) * 100;

  return (
    <div className="text-white my-3">
      <h1 className="text-lg font-normal mb-4">Current Phase</h1>

      {/* Progress Bar */}
      <div className="w-full bg-gray-600 rounded-full h-2 overflow-hidden">
        <div
          className="bg-[#D3EC99] h-2 rounded-full"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>

      {/* Current Phase Text */}
      <p className="mt-4">
        <strong></strong> {phases[phase] || "Unknown Phase"}
      </p>
    </div>
  );
};

export default PhaseIndicator;
