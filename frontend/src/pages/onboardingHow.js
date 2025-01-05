import React from "react";
import { useNavigate } from "react-router-dom";

const OnboardingStep = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate('/how'); // Navigate to /how route
  };

  return (
    <div className="flex flex-col sm:flex-row h-screen items-center justify-center bg-white w-screen">
      {/* Left Section */}
      <div className="w-full sm:w-1/2 h-full flex flex-col items-center justify-center bg-white p-10 px-4">
        <img
          src='/vbaiLogo.svg' // Use the imported logo
          alt="VBAI logo"
          className="w-3/4 sm:w-2/3 lg:w-1/2"
        />
        <h1 className="text-4xl font-normal text-gray-800">Pitch Deck AI</h1>
      </div>

      <div className="border-l-4 border-[#00383D] w-full sm:h-[80%] sm:border-l-4 sm:border-b-0 border-b-4 sm:w-px"></div>

      {/* Right Section */}
      <div className="w-full sm:w-1/2 py-10 flex flex-col items-center justify-center px-4 sm:px-10">
        <h2 className="mb-2 text-2xl font-semibold text-gray-800 text-center sm:text-left">
          Welcome to Pitch Deck AI 🚀
        </h2>
        <p className="mb-6 text-gray-600 text-center sm:text-left">
          Create professional pitch decks in minutes
        </p>

        <div className="shadow-xl shadow-slate-400 py-10 px-6 rounded-[20px] flex justify-center flex-col items-center w-full max-w-lg">
          <h3 className="mb-4 text-lg font-semibold text-gray-700 text-center sm:text-left">Features</h3>
          <ul className="space-y-4">
            <li className="flex items-start shadow-md py-2 rounded-[20px] px-4">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Our AI transforms your business info into pitch decks.
            </li>
            <li className="flex items-start shadow-md py-2 rounded-[20px] px-4">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Professional templates designed for investor presentations.
            </li>
            <li className="flex items-start shadow-md py-2 rounded-[20px] px-4">
              <span className="mr-2 text-yellow-500">&#9733;</span>
              Customizable slides with smart content suggestions.
            </li>
          </ul>
        
        </div>
        <button
        onClick={handleClick}
        className="mt-6 px-14 w-[60%] py-4 rounded-[50px] bg-[#D3EC99] text-[#002C31] font-bold text-xl"
      >
        Next →
      </button>
      </div>
    </div>
  );
};

export default OnboardingStep;
