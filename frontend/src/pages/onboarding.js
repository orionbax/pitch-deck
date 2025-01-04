import React from "react";
import { useNavigate } from "react-router-dom";

const Onboarding = () => {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col sm:flex-row h-screen items-center justify-center bg-white">
      {/* Left Section */}
      <div className="w-full sm:w-1/2 h-1/2 sm:h-full flex flex-col items-center justify-center bg-white p-6 sm:p-10">
        <img
          src="/vbaiLogo.svg" // Replace with your logo image
          alt="Venture Builder AI"
          className="mb-6 w-1/2 sm:w-3/4 "
        />
        <h1 className="text-lg sm:text-2xl font-bold text-gray-800 text-center">
          Pitch Deck AI
        </h1>
      </div>

      {/* Divider */}
      <div className="h-2 sm:h-3/4 sm:w-px sm:border-l-4 border-t-4 sm:border-t-0 border-teal-900 rounded-md"></div>

      {/* Right Section */}
      <div className="w-full sm:w-1/2 h-1/2 sm:h-full bg-white p-6 sm:p-10 flex flex-col justify-center">
        <button
          className="mb-6 flex items-center justify-center text-teal-600 bg-[#D3EC99] w-10 h-10 rounded-full"
          onClick={() => {
            navigate("/how");
          }}
        >
          <span className="text-xl">&#8592;</span> {/* Back Arrow */}
        </button>
        <div className="flex flex-col items-center w-full shadow-md shadow-gray-400 rounded-lg p-4 sm:p-10 bg-white">
          {/* Tips Section */}
          <h2 className="mb-4 text-lg sm:text-2xl font-semibold text-gray-800 text-center">
            Tips for Best Result
          </h2>
          <ul className="space-y-4 w-full sm:w-3/4 text-sm sm:text-base">
            <li className="flex items-start p-2 pr-6 shadow-md rounded-[20px]">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Begin with a clear project name that reflects your business.
            </li>
            <li className="flex items-start p-2 pr-6 shadow-md rounded-[20px]">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Upload business documents for improved AI content.
            </li>
            <li className="flex items-start p-2 pr-6 shadow-md rounded-[20px]">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Review and edit slides to keep your brand voice.
            </li>
            <li className="flex items-start p-2 pr-6 shadow-md rounded-[20px]">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Use preview to ensure a professional presentation.
            </li>
            <li className="flex items-start p-2 pr-6 shadow-md rounded-[20px]">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Save your progress regularly as you customize your deck.
            </li>
          </ul>
        </div>

        {/* Get Started Button */}
        <button
          onClick={() => {
            navigate("/project");
          }}
          className="mt-6 w-full sm:w-3/4 self-center bg-[#D3EC99] py-3 text-[#002C31] text-base sm:text-lg font-bold rounded-[50px] shadow-md hover:shadow-lg"
        >
          Get Started →
        </button>
      </div>
    </div>
  );
};

export default Onboarding;
