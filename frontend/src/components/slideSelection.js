import React, { useState, useEffect } from "react";
import { usePhase } from "../pages/context/phaseContext";
import GenereatedContent from "./generatedContent";
import DownloadButton from "./downloadOptions";
import Delete from "./deleteProject"; 
import { useNavigate } from "react-router-dom";
import { FaArrowRight } from "react-icons/fa";

const SlideSelection = () => {
  const slideOrder = [
    "Title",
    "Introduction",
    "Team",
    "Experience",
    "Problem",
    "Solution",
    "Revenue",
    "Go_to_market",
    "Demo",
    "Technology",
    "Pipeline",
    "Expansion",
    "Uniqueness",
    "Competition",
    "Traction",
    "Ask",
    "Use_of_funds",
  ];

  const requiredSlides = [
    "Title",
    "Introduction",
    "Problem",
    "Solution",
    "Ask",
    "Go_to_market",
  ];

  const optionalSlides = slideOrder.filter((slide) => !requiredSlides.includes(slide));

  const [selectedSlides, setSelectedSlides] = useState([]);
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const { setPhase, editMode, baseUrl, language , slides} = usePhase();
  const token = localStorage.getItem("authToken");
  const [isGenerationComplete, setIsGenerationComplete] = useState(false);
  const navigate = useNavigate()

  const languageTexts = {
    en: {
      createPitchDeck: "Create Your Pitch Deck",
    completeDocumentAnalysis: "Please complete the document analysis phase first.",
    goToDocumentSection: "Go to document section",
      requiredSlides: "Recommended Slides",
      optionalSlides: "Optional Slides",
      confirmSelection: "Confirm Slide Selection",
      processing: "Processing...",
      slideTitles: {
        Title: "Title",
        Introduction: "Introduction",
        Problem: "Problem",
        Solution: "Solution",
        Ask: "Ask",
        Go_to_market: "Go to Market",
        Team: "Team",
        Experience: "Experience",
        Revenue: "Revenue",
        Demo: "Demo",
        Technology: "Technology",
        Pipeline: "Pipeline",
        Expansion: "Expansion",
        Uniqueness: "Uniqueness",
        Competition: "Competition",
        Traction: "Traction",
        Use_of_funds: "Use of Funds",
      },
    },
    no: {
      createPitchDeck: "Lag din Pitch Deck",
    completeDocumentAnalysis: "Vennligst fullfør dokumentanalysen først.",
    goToDocumentSection: "Gå til dokumentseksjonen",
      requiredSlides: "Anbefalte lysbilder",
      optionalSlides: "Valgfrie Lysbilder",
      confirmSelection: "Bekreft Lysbildevalg",
      processing: "Behandler...",
      slideTitles: {
        Title: "Tittel",
        Introduction: "Introduksjon",
        Problem: "Problem",
        Solution: "Løsning",
        Ask: "Spørsmål",
        Go_to_market: "Gå til markedet",
        Team: "Team",
        Experience: "Erfaring",
        Revenue: "Inntekt",
        Demo: "Demo",
        Technology: "Teknologi",
        Pipeline: "Pipeline",
        Expansion: "Utvidelse",
        Uniqueness: "Unikhet",
        Competition: "Konkurranse",
        Traction: "Fremdrift",
        Use_of_funds: "Bruk av midler",
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

  // useEffect(() => {
  //   console.log("Current responses:", responses);
  // }, [responses]);

  if (slides === 0) {
    return (
      <div className="flex flex-col justify-center items-start h-screen w-full gap-6 py-20 px-8">
      <h1 className=" font-bold text-[#004F59] text-5xl my-7 ">{texts.createPitchDeck}</h1>
      <h2 className="text-xl bg-[#D3EC99] text-[#004F59] w-1/2 h-16 text-center flex items-center justify-center font-light">
       {texts.completeDocumentAnalysis}
      </h2>
        <button
        onClick={() => navigate("/upload")}
        className="bg-[#D3EC99] text-[#00383D] py-3 px-6 rounded-lg shadow-[50px] transition duration-300 text-xl font-normal my-6 flex items-center justify-center"
      >
        {
          texts.goToDocumentSection
        }
        <span className="ml-2">
          <FaArrowRight />
        </span>
      </button>

    </div>
    
    );
  }


  return (
    <div className="px-8  w-3/4   my-3">



      {!isGenerating ? (
        <div>

        <div className="bg-white rounded-3xl p-6 pl-10 shadow-md  flex-col justify-center items-center">
        <h1 className="text-4xl text-[#004F59] font-semibold pb-4">{texts.requiredSlides}</h1>
        <hr className="py-1"/>
        
        <div className="flex text-xl  text-gray-600 font-semibold justify-center items-center">
          <div className="flex-1 flex flex-col gap-4">
            {requiredSlides.slice(0, 3).map((slide, index) => (
              <div key={index} className="px-4 py-2 ">
                {texts.slideTitles[slide]} {/* Display slide title in the selected language */}
              </div>
            ))}
          </div>
          <div className="flex-1 flex flex-col gap-4">
            {requiredSlides.slice(3).map((slide, index) => (
              <div key={index} className="px-4 py-2  rounded-md">
                {texts.slideTitles[slide]} {/* Display slide title in the selected language */}
              </div>
            ))}
          </div>
        </div>
      </div>
      

       <div className="bg-white rounded-3xl p-6 pl-10 shadow-md my-4">
  <h1 className="text-4xl text-[#004F59] font-semibold pb-4">{texts.optionalSlides}</h1>
  <hr className="py-1"/>
  
  <div className="flex text-gray-600 font-semibold text-xl">
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
</div>


          <div className="flex justify-center mt-6">
            <button
              onClick={handleSubmit}
              className="bg-[#004F59] px-16 py-4 rounded-[60px] text-white "
              disabled={isProcessing}
            >
              {isProcessing ? texts.processing : texts.confirmSelection}
            </button>
            
            
          </div>
        </div>
      ) : (
        <GenereatedContent responses={responses} isGenerationComplete={isGenerationComplete} isProcessing={isProcessing}/>
      )}
    </div>
  );
};

export default SlideSelection;
