import React from "react";

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

  // Split the slides into two parts (left and right columns)
  const leftColumnSlides = slides.slice(0, Math.ceil(slides.length / 2));
  const rightColumnSlides = slides.slice(Math.ceil(slides.length / 2));

  return (
    <div className="px-16 py-4 w-3/4">
      <h1 className="text-4xl text-[#004F59] font-semibold pb-3">Required Slides</h1>
      <div className="flex  text-xl gap-4 text-gray-600 my-3  font-semibold">
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

      <div className="flex my-3 text-gray-600  font-semibold">
        {/* Left Column: First part of optional slides */}
        <div className="flex-1 flex flex-col gap-4">
          {leftColumnSlides.map((slide, index) => (
            <div key={index} className="flex items-center gap-2">
              <input type="checkbox" id={`optional-slide-left-${index}`} />
              <label htmlFor={`optional-slide-left-${index}`} className="font-semibold">
                {slide}
              </label>
            </div>
          ))}
        </div>

        {/* Right Column: Remaining slides */}
        <div className="flex-1 flex flex-col gap-4">
          {rightColumnSlides.map((slide, index) => (
            <div key={index} className="flex items-center gap-2">
              <input type="checkbox" id={`optional-slide-right-${index}`} />
              <label htmlFor={`optional-slide-right-${index}`} className="font-semibold">
                {slide}
              </label>
            </div>
          ))}
        </div>
      </div>

      <button className="bg-[#004F59] px-16 py-3 rounded-[50px] text-white ml-32 ">Confirm Slide Selection</button>
    </div>
  );
};

export default SlideSelection;
