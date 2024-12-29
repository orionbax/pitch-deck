import React from 'react';
import { useLocation } from 'react-router-dom';

const PreviewSlides = () => {
  const location = useLocation();
  const slides = location.state?.slides || []; // Get slides passed from the previous page

  return (
    <div>
      <h2 className="text-3xl font-semibold text-[#004F59]">Preview Slides</h2>
      <div className="space-y-4 mt-4 max-h-[400px] overflow-y-auto">
        {slides.map((item, index) => (
          <div key={index} className="bg-gray-100 p-4 rounded-md">
            <h3 className="text-2xl font-semibold">{item.slide}</h3>
            <p>{item.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PreviewSlides;
