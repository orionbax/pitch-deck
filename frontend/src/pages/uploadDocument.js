import React from 'react';
import { usePhase } from '../pages/context/phaseContext'; // Assuming this context holds language info
import Upload from '../components/upload';

const UploadDocument = () => {
  const { language } = usePhase(); 

  // Translations for the page content
  const content = {
    en: {
      title: 'Upload Document',
      description: 'Upload Company Document (optional)',
    },
    no: {
      title: 'Subir Documento',
      description: 'Subir Documento de la Empresa (opcional)',
    },
    // Add more languages here as needed
  };

  return (
    <div className="flex">
      <div className="p-16">

        <h1 className="text-5xl font-semibold text-[#004F59]">
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
