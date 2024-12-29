import React, { useState, useEffect } from "react";
import { usePhase } from "../pages/context/phaseContext";

const SlideSelection = () => {
  const requiredSlides = [
    "Title slide",
    "Introduction",
    "Problem Statement",
    "Solution",
    "Market Opportunity",
    "Ask",
  ];

  const slides = [
    "title",
    "introduction",
    "Team Members",
    "Revenue Models",
    "Market Analysis",
    "Business Strategy",
    "Technology Stack",
    "Project Timeline",
    "Marketing Plan",
    "Customer Acquisition",
    "Competitive Landscape",
    "Financial Projections",
    "Risk Management",
    "Investment Opportunity",
    "Conclusion",
  ];

  const [selectedSlides, setSelectedSlides] = useState([]);
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
   const { setPhase } = usePhase();
  const token = localStorage.getItem('authToken');
  console.log('Token:', token);  // Debug token

  useEffect(() => {
    setPhase("slide-selection")
  }, [setPhase]);
  

  const handleSlideSelection = (slide) => {
    setSelectedSlides((prevSelectedSlides) => {
      if (prevSelectedSlides.includes(slide)) {
        return prevSelectedSlides.filter((s) => s !== slide);
      } else {
        return [...prevSelectedSlides, slide];
      }
    });
  };

  const handleSubmit = async () => {
    setPhase("content-generating");
    setIsProcessing(true);
    setIsGenerating(true); // Show generating screen
    setResponses([]); // Reset previous responses

    // Loop through each selected slide
    for (const slide of selectedSlides) {
      try {
        const response = await fetch("http://127.0.0.1:5000/generate_slides", {
          method: "POST",
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
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
  };

  return (
    <div className="px-16 py-4 w-3/4">

      {!isGenerating ? (
        <div>
          <h1 className="text-4xl text-[#004F59] font-semibold pb-3">Required Slides</h1>
          <div className="flex text-xl gap-4 text-gray-600 my-3 font-semibold">
            {/* Left Column */}
            <div className="flex-1 flex flex-col gap-4">
              {requiredSlides.slice(0, 3).map((slide, index) => (
                <div key={index}>{slide}</div>
              ))}
            </div>

            {/* Right Column */}
            <div className="flex-1 flex flex-col gap-4">
              {requiredSlides.slice(3).map((slide, index) => (
                <div key={index}>{slide}</div>
              ))}
            </div>
          </div>

          <h1 className="text-4xl text-[#004F59] font-semibold pb-3">Optional Slides</h1>
          <div className="flex my-3 text-gray-600 font-semibold">
            {/* Left Column: First part of optional slides */}
            <div className="flex-1 flex flex-col gap-4">
              {slides.slice(0, Math.ceil(slides.length / 2)).map((slide, index) => (
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
            <div className="flex-1 flex flex-col gap-4">
              {slides.slice(Math.ceil(slides.length / 2)).map((slide, index) => (
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
            className="bg-[#004F59] px-16 py-3 rounded-[50px] text-white ml-32"
            disabled={isProcessing}
          >
            {isProcessing ? "Processing..." : "Confirm Slide Selection"}
          </button>

        </div>

      ) : (
        <div>
          <h2 className="text-3xl font-semibold text-[#004F59]">Generating Slide Content...</h2>
          <div className="space-y-4 mt-4 max-h-[400px] overflow-y-auto">
            {responses.map((item, index) => (
              <div key={index} className="bg-gray-100 p-4 rounded-md">
                <h3 className="text-2xl font-semibold">{item.slide}</h3>
                <p>{item.content}</p>
                <button className="text-blue-600 font-semibold mt-2">Edit</button>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>

  );
};

export default SlideSelection;
