import React, { useState, useEffect } from "react";
import { usePhase } from "../pages/context/phaseContext";
import GenereatedContent from "./generatedContent";
import DownloadButton from "./downloadOptions";
import Delete from "./deleteProject";

const SlideSelection = () => {
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

  const requiredSlides = [
    "title",
    "introduction",
    "problem",
    "solution",
    "ask",
    "go_to_market",
  ];

  const optionalSlides = slideOrder.filter((slide) => !requiredSlides.includes(slide));

  const [selectedSlides, setSelectedSlides] = useState([]);
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const { setPhase, editMode, baseUrl, language } = usePhase();
  const token = localStorage.getItem("authToken");
  const [isGenerationComplete, setIsGenerationComplete] = useState(false);

  const languageTexts = {
    en: {
      requiredSlides: "Required Slides",
      optionalSlides: "Optional Slides",
      confirmSelection: "Confirm Slide Selection",
      processing: "Processing...",
      slideTitles: {
        title: "Title",
        introduction: "Introduction",
        problem: "Problem",
        solution: "Solution",
        ask: "Ask",
        go_to_market: "Go to Market",
        team: "Team",
        experience: "Experience",
        revenue: "Revenue",
        demo: "Demo",
        technology: "Technology",
        pipeline: "Pipeline",
        expansion: "Expansion",
        uniqueness: "Uniqueness",
        competition: "Competition",
        traction: "Traction",
        use_of_funds: "Use of Funds",
      },
    },
    no: {
      requiredSlides: "Påkrevde Lysbilder",
      optionalSlides: "Valgfrie Lysbilder",
      confirmSelection: "Bekreft Lysbildevalg",
      processing: "Behandler...",
      slideTitles: {
        title: "Tittel",
        introduction: "Introduksjon",
        problem: "Problem",
        solution: "Løsning",
        ask: "Spørsmål",
        go_to_market: "Gå til markedet",
        team: "Team",
        experience: "Erfaring",
        revenue: "Inntekt",
        demo: "Demo",
        technology: "Teknologi",
        pipeline: "Pipeline",
        expansion: "Utvidelse",
        uniqueness: "Unikhet",
        competition: "Konkurranse",
        traction: "Fremdrift",
        use_of_funds: "Bruk av midler",
      },
    },
  };

  const texts = languageTexts[language] || languageTexts.en;

  useEffect(() => {
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
    setIsGenerating(true);
    setResponses([]); 
    setIsGenerationComplete(false);

    const slidesToGenerate = [...requiredSlides, ...selectedSlides];

    for (const slide of slidesToGenerate) {
      try {
        const response = await fetch(`${baseUrl}/generate_slides`, {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ slide: slide }), // Always send slide name in English
        });

        const data = await response.json();
        console.log("Response for slide:", slide, data);

        if (data.content) {
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

  useEffect(() => {
    console.log("Current responses:", responses);
  }, [responses]);

  return (
    <div className="px-16 py-4 w-3/4">
      {!isGenerating ? (
        <div>
          <h1 className="text-4xl text-[#004F59] font-semibold pb-3">{texts.requiredSlides}</h1>
          <div className="flex text-xl gap-4 text-gray-600 my-3 font-semibold">
            <div className="flex-1 flex flex-col gap-4">
              {requiredSlides.slice(0, 3).map((slide, index) => (
                <div key={index}>{texts.slideTitles[slide]}</div> // Display slide title in the selected language
              ))}
            </div>
            <div className="flex-1 flex flex-col gap-4">
              {requiredSlides.slice(3).map((slide, index) => (
                <div key={index}>{texts.slideTitles[slide]}</div> // Display slide title in the selected language
              ))}
            </div>
          </div>

          <h1 className="text-4xl text-[#004F59] font-semibold pb-3">{texts.optionalSlides}</h1>
          <div className="flex my-3 text-gray-600 font-semibold">
            <div className="flex-1 flex flex-col gap-4">
              {optionalSlides.slice(0, Math.ceil(optionalSlides.length / 2)).map((slide, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedSlides.includes(slide)}
                    onChange={() => handleSlideSelection(slide)}
                  />
                  <label className="font-semibold">{texts.slideTitles[slide]}</label> {/* Display title based on language */}
                </div>
              ))}
            </div>

            <div className="flex-1 flex flex-col gap-4">
              {optionalSlides.slice(Math.ceil(optionalSlides.length / 2)).map((slide, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={selectedSlides.includes(slide)}
                    onChange={() => handleSlideSelection(slide)}
                  />
                  <label className="font-semibold">{texts.slideTitles[slide]}</label> {/* Display title based on language */}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between mt-6">
            <button
              onClick={handleSubmit}
              className="bg-[#004F59] px-16 py-1 rounded-[40px] text-white "
              disabled={isProcessing}
            >
              {isProcessing ? texts.processing : texts.confirmSelection}
            </button>
            
            <Delete />
          </div>
        </div>
      ) : (
        <GenereatedContent responses={responses} isGenerationComplete={isGenerationComplete} />
      )}
    </div>
  );
};

export default SlideSelection;
