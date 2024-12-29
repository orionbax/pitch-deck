import React, { useState, useEffect } from "react";
import { usePhase } from "../pages/context/phaseContext";
import GenereatedContent from "./generatedContent";
import DownloadButton from "./downloadOptions";

const SlideSelection = () => {
  // Define the fixed order of all slides
  const slideOrder = [
    "title",
    "introduction",
    "team",
    "experience",
    "problem",
    "solution",
    "revenue",
    "go_to_market",
    "demo",
    "technology",
    "pipeline",
    "expansion",
    "uniqueness",
    "competition",
    "traction",
    "ask",
    "use_of_funds",
  ];

  // Define the required slides that must always be included
  const requiredSlides = [
    "title",
    "introduction",
    "problem",
    "solution",
    "ask",
    "go_to_market",
  ];

  // Calculate the optional slides (everything in slideOrder except the required ones)
  const optionalSlides = slideOrder.filter(slide => !requiredSlides.includes(slide));

  const [selectedSlides, setSelectedSlides] = useState([]);
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const { setPhase, editMode } = usePhase();
  const token = localStorage.getItem("authToken");
  const [isGenerationComplete, setIsGenerationComplete] = useState(false);

  useEffect(() => {
    // If there are already responses, directly go to content-generating state
    if (responses.length > 0) {
      setPhase("content-generating");
      setIsGenerating(true);
    } else {
      setPhase("slide-selection");
    }
  }, [responses, setPhase]);

  const handleSlideSelection = (slide) => {
    setSelectedSlides((prevSelectedSlides) => {
      const updatedSlides = prevSelectedSlides.includes(slide)
        ? prevSelectedSlides.filter((s) => s !== slide)
        : [...prevSelectedSlides, slide];

      return updatedSlides;
    });
  };

  const handleSubmit = async () => {
    setPhase("content-generating");
    setIsProcessing(true);
    setIsGenerating(true); // Show generating screen
    setResponses([]); // Reset previous responses
    setIsGenerationComplete(false);

    // Combine required slides with selected slides, maintaining the predefined order
    const slidesToGenerate = [
      ...requiredSlides,  // Include the required slides first
      ...selectedSlides,  // Then add the selected optional slides
    ];

    // Loop through each slide to generate content
    for (const slide of slidesToGenerate) {
      try {
        const response = await fetch("http://127.0.0.1:5000/generate_slides", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ slide: slide }),
        });

        const data = await response.json();

        if (data.content) {
          // Add the response content to the list of responses
          setResponses((prevResponses) => [
            ...prevResponses,
            { slide, content: data.content },
          ]);
        } else if (data.error) {
          console.error(`Error for slide: ${slide}: ${data.error}`);
        }
      } catch (error) {
        console.error("Error processing slide:", slide, error);
      }
    }

    setIsProcessing(false);
    setIsGenerationComplete(true);
  };

  return (
    <div className="px-6 sm:px-12 lg:px-16 w-full md:w-3/5 py-4">
      {!isGenerating ? (
        <div>
          <h1 className="text-3xl sm:text-4xl text-[#004F59] font-semibold pb-3">Required Slides</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xl text-gray-600 my-3 font-semibold">
            {/* Left Column */}
            <div className="flex flex-col gap-4">
              {requiredSlides.slice(0, 3).map((slide, index) => (
                <div key={index}>{slide}</div>
              ))}
            </div>

            {/* Right Column */}
            <div className="flex flex-col gap-4">
              {requiredSlides.slice(3).map((slide, index) => (
                <div key={index}>{slide}</div>
              ))}
            </div>
          </div>

          <h1 className="text-3xl sm:text-4xl text-[#004F59] font-semibold pb-3">Optional Slides</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-gray-600 font-semibold">
            {/* Left Column: First part of optional slides */}
            <div className="flex flex-col gap-4">
              {optionalSlides.slice(0, Math.ceil(optionalSlides.length / 2)).map((slide, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedSlides.includes(slide)}
                    onChange={() => handleSlideSelection(slide)}
                  />
                  <label className="font-semibold">{slide}</label>
                </div>
              ))}
            </div>

            {/* Right Column: Remaining slides */}
            <div className="flex flex-col gap-4">
              {optionalSlides.slice(Math.ceil(optionalSlides.length / 2)).map((slide, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedSlides.includes(slide)}
                    onChange={() => handleSlideSelection(slide)}
                  />
                  <label className="font-semibold">{slide}</label>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={handleSubmit}
            className="bg-[#004F59] px-8 sm:px-16 py-3 mt-4 rounded-full text-white w-full sm:w-auto"
            disabled={isProcessing}
          >
            {isProcessing ? "Processing..." : "Confirm Slide Selection"}
          </button>
        </div>
      ) : (
        <GenereatedContent responses={responses} isGenerationComplete={isGenerationComplete} />
      )}
    </div>
  );
};

export default SlideSelection;
