import React from "react";
import { useNavigate } from "react-router-dom";


const OnboardingHowItWorks = () => {

    const navigate = useNavigate()
    const handleClick = () => {
        navigate('/tips')
    }

    const handleBack = () => {
        navigate('/')
    }


  return (
    <div className="flex flex-col sm:flex-row h-screen items-center justify-center bg-teal-900">
      {/* Left Section */}
      <div className="w-full sm:w-1/2 h-1/2 sm:h-full flex flex-col items-center justify-center bg-white p-6 sm:p-10">
        <img
          src="/vbaiLogo.svg" // Use the imported logo
          alt="VBAI logo"
          className="w-3/4 sm:w-2/3 lg:w-1/2"
        />
        <h1 className="text-3xl sm:text-4xl font-normal text-gray-800 mt-4">
          Pitch Deck AI
        </h1>
      </div>

      {/* Divider */}
      <div className="w-full h-2 sm:h-3/4 sm:w-px bg-white sm:border-l-4 border-t-4 border-[#00383D] sm:border-t-0"></div>

      {/* Right Section */}

      <div className="w-full sm:w-1/2 h-1/2 sm:h-full bg-white p-6 sm:p-10 flex flex-col items-center justify-center">
      
        <div className="w-full sm:w-3/4 flex flex-col items-center">
          <button onClick={handleBack} className="mb-6 flex items-center justify-center text-teal-600 self-start bg-[#D3EC99] w-10 h-10 rounded-full ">
            <span className="text-xl">&#8592;</span>
          </button>
          <div className="flex flex-col items-center shadow-lg py-10 px-6 w-full rounded-[20px]">
            <h2 className="mb-6 text-2xl sm:text-3xl font-semibold text-[#004F59] text-center">
              How it works.
            </h2>
            <ul className="space-y-4 w-full">
              <li className="flex items-center shadow-md shadow-slate-400 rounded-3xl pl-4 pr-6 py-3">
                <span className="mr-2 text-yellow-500">&#9733;</span>
                Create Project
              </li>
              <li className="flex items-center shadow-md shadow-slate-400 rounded-3xl pl-4 pr-6 py-3">
                <span className="mr-2 text-yellow-500">&#9733;</span>
                Upload Documents
              </li>
              <li className="flex items-center shadow-md shadow-slate-400 rounded-3xl pl-4 pr-6 py-3">
                <span className="mr-2 text-yellow-500">&#9733;</span>
                Select & Customize Slides
              </li>
            </ul>
          </div>
          <button
            onClick={handleClick}
            className="mt-8 px-10 sm:px-14 w-full py-4 rounded-[50px] bg-[#D3EC99] text-[#002C31] font-bold text-lg sm:text-xl"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingHowItWorks;
