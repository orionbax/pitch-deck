import React, {useEffect} from 'react';
import { usePhase } from '../pages/context/phaseContext'; // Assuming this context holds language info
import Upload from '../components/upload';
import { useNavigate } from 'react-router-dom';


const UploadDocument = () => {


  const navigate = useNavigate()

   useEffect(() => {
      const token = localStorage.getItem('authToken'); // Get the token from localStorage
      if (!token) {
        navigate('/project'); // Redirect to home if no token is found
      }
    }, );

  const { language } = usePhase(); 

  // Translations for the page content
  const content = {
    en: {
      title: 'Upload Document',
      description: 'Upload Company Document',
    },
    no: {
      title: 'Subir Documento',
      description: 'Subir Documento de la Empresa',
    },
    // Add more languages here as needed
  };

  return (
    <div className="flex justify-center items-center min-h-screen"> {/* Centers content vertically and horizontally */}
      <div className="flex flex-col items-start "> {/* Align content to the start but within the centered area */}
        <h1 className="text-5xl font-semibold text-[#004F59] my-6">
          {content[language]?.title || content.en.title}
        </h1>

        <h1 className="py-4 text-xl font-normal">
          {content[language]?.description || content.en.description}
        </h1>

        <Upload />
      </div>
    </div>
  );
};

export default UploadDocument;
