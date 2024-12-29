import React, { useState, useEffect } from 'react';
import { FiX } from 'react-icons/fi';
import { SlCloudUpload } from "react-icons/sl";
import { useNavigate } from 'react-router-dom';
import { usePhase } from '../pages/context/phaseContext';

const Upload = () => {
  const { setPhase, language } = usePhase(); // Get current language and phase
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]); // Keep track of uploaded files
  const [status, setStatus] = useState(null);
  const [fileError, setFileError] = useState('');
  const token = localStorage.getItem('authToken');
  const navigate = useNavigate();

  useEffect(() => {
    setPhase("document-uploading");
  }, [setPhase]);

  // Define text for English and Norwegian
  const text = {
    en: {
      uploadBoxTitle: 'Supported formats: PDF, DOCX, DOC, TXT (Max 200MB)',
      selectedFiles: 'Selected Files:',
      uploadButton: 'Upload',
      status: 'Status:',
      uploadedFiles: 'Uploaded Documents:',
      nextButton: 'Next',
      fileError: 'Some files are either too large or have unsupported formats.',
      fileTooLarge: 'File size should not exceed 200MB.',
      fileFormatError: 'Unsupported file format. Please upload a PDF, DOCX, DOC, or TXT.',
    },
    no: {
      uploadBoxTitle: 'Støttede formater: PDF, DOCX, DOC, TXT (Maks 200MB)',
      selectedFiles: 'Valgte Filer:',
      uploadButton: 'Last opp',
      status: 'Status:',
      uploadedFiles: 'Opplastede Dokumenter:',
      nextButton: 'Neste',
      fileError: 'Noen filer er enten for store eller har ikke støttede formater.',
      fileTooLarge: 'Filstørrelse kan ikke overskride 200MB.',
      fileFormatError: 'Ikke-støttet filformat. Vennligst last opp en PDF, DOCX, DOC eller TXT.',
    },
  };

  const currentText = text[language] || text.en; // Use selected language or default to English

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);

      // Check for file size and type
      const validFiles = selectedFiles.filter((file) => {
        const isValidSize = file.size <= 200 * 1024 * 1024; // 200 MB max
        const isValidType = [
          'application/pdf',
          'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'text/plain',
        ].includes(file.type);

        return isValidSize && isValidType;
      });

      if (validFiles.length !== selectedFiles.length) {
        setFileError(currentText.fileError);
      } else {
        setFileError('');
      }

      setFiles(validFiles); // Update selected files state
    }
  };

  // Handle file upload
  const handleUpload = () => {
    if (files.length === 0) {
      alert(currentText.fileFormatError);
      return;
    }

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('documents', file);
    });

    // Log token in console for debugging
    console.log('Sending token with the request:', token);

    fetch('http://127.0.0.1:5000/upload_documents', {
      method: 'POST',
      body: formData,
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`, // Include token in Authorization header
      },
      credentials: 'include', // Ensure the session is sent correctly
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setStatus(data.message);
          setUploadedFiles((prev) => [...prev, ...files.map((file) => file.name)]); // Append new files to uploadedFiles state
          setFiles([]); // Clear selected files for the next upload
        } else {
          setStatus(`Error: ${data.error}`);
        }
      })
      .catch((err) => {
        setStatus(`Error: ${err.message}`);
      });
  };

  // Handle sending data to backend on "Next"
  const handleNext = () => {
    setPhase("slide-selection");
    navigate('/slide');
  };

  // Handle removing selected file
  const handleRemoveFile = (fileName) => {
    setFiles(files.filter((file) => file.name !== fileName)); // Remove file from selected files
  };

  return (
    <div className="file-uploader p-4">
      <div
        className="upload-box border-2 border-dashed flex flex-col justify-center items-center border-gray-300 p-10 text-center cursor-pointer bg-white"
        onClick={() => document.getElementById('file-input').click()}
      >
        <SlCloudUpload size={40} color="#004F59" />
        <p className="mt-4 text-base text-[#676767]">
          {currentText.uploadBoxTitle}
        </p>
        <input
          type="file"
          id="file-input"
          accept=".pdf,.docx,.txt"
          multiple
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {/* File error message */}
      {fileError && <p className="text-red-500 mt-2">{fileError}</p>}

      {/* Display selected files before upload */}
      {files.length > 0 && (
        <div className="selected-files mt-4">
          <h3 className="text-lg font-normal mb-2">{currentText.selectedFiles}</h3>
          <ul className="list-disc list-inside">
            {files.map((file) => (
              <li key={file.name} className="flex justify-between items-center mb-2">
                <span>{file.name}</span>
                <button
                  onClick={() => handleRemoveFile(file.name)}
                  className="text-red-500 ml-2"
                  aria-label="Remove file"
                >
                  <FiX className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Button to trigger upload */}
      {files.length > 0 && !fileError && (
        <button
          onClick={handleUpload}
          className="mt-6 bg-[#004F59] text-white py-2 px-4 rounded-md"
        >
          {currentText.uploadButton}
        </button>
      )}

      {/* Status message */}
      {status && <p className="mt-4">{status}</p>}

      {/* Display uploaded files */}
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files mt-6">
          <h3 className="text-lg font-semibold mb-2">{currentText.uploadedFiles}</h3>
          <ul className="list-disc list-inside">
            {uploadedFiles.map((file, index) => (
              <li key={index}>{file}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Next button */}
      {uploadedFiles.length > 0 && (
        <button
          onClick={handleNext}
          className="mt-6 bg-[#D3EC99] text-[#00383D] py-4 px-36 rounded-3xl hover:bg-[#b1d362]"
        >
          {currentText.nextButton}
        </button>
      )}
    </div>
  );
};

export default Upload;
