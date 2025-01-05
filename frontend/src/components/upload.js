import React, { useState, useEffect } from 'react';
import { FiX } from 'react-icons/fi';
import { SlCloudUpload } from "react-icons/sl";
import { useNavigate } from 'react-router-dom';
import { usePhase } from '../pages/context/phaseContext';

const Upload = () => {
  const { setPhase, language, baseUrl, setSlides } = usePhase();
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [status, setStatus] = useState(null);
  const [fileError, setFileError] = useState('');
  const [isUploading, setIsUploading] = useState(false); // Track uploading state
  const token = localStorage.getItem('authToken');
  console.log("token downlaod", token)
  const navigate = useNavigate();

  useEffect(() => {
    setPhase("document-uploading");
  }, [setPhase]);

  const text = {
    en: {
      uploadBoxTitle: 'Supported formats: PDF, DOCX, DOC, TXT (Max 200MB)',
      selectedFiles: 'Selected Files:',
      uploadButton: 'Upload',
      uploadingButton: 'Uploading...', // Add uploading state text
      status: 'Status:',
      uploadedFiles: 'Uploaded Documents:',
      nextButton: 'Next',
      fileError: 'Some files are either too large or have unsupported formats.',
      fileTooLarge: 'File size should not exceed 200MB.',
      fileFormatError: 'Unsupported file format. Please upload a PDF, DOCX, DOC, or TXT.',
      uploadHere:"Click here to browse files"
    },
    no: {
      uploadBoxTitle: 'Støttede formater: PDF, DOCX, DOC, TXT (Maks 200MB)',
      selectedFiles: 'Valgte Filer:',
      uploadButton: 'Last opp',
      uploadingButton: 'Laster opp...', // Add uploading state text
      status: 'Status:',
      uploadedFiles: 'Opplastede Dokumenter:',
      nextButton: 'Neste',
      fileError: 'Noen filer er enten for store eller har ikke støttede formater.',
      fileTooLarge: 'Filstørrelse kan ikke overskride 200MB.',
      fileFormatError: 'Ikke-støttet filformat. Vennligst last opp en PDF, DOCX, DOC eller TXT.',
      uploadHere:"Klikk her for å bla gjennom filer"
    },
  };

  const currentText = text[language] || text.en;

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      const validFiles = selectedFiles.filter((file) => {
        const isValidSize = file.size <= 200 * 1024 * 1024;
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

      setFiles(validFiles);
    }
  };

  const handleUpload = () => {
    if (files.length === 0) {
      alert(currentText.fileFormatError);
      return;
    }

    setIsUploading(true); // Set uploading state to true

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('documents', file);
    });

    fetch(`${baseUrl}/upload_documents`, {
      method: 'POST',
      body: formData,
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setStatus(data.message);
          setUploadedFiles((prev) => [...prev, ...files.map((file) => file.name)]);
          setFiles([]);
          console.log("uploaded data", data)
        } else {
          console.log("token check", token)
          setStatus(`Error msg: ${data.error}`);
        }
      })
      .catch((err) => {
        setStatus(`Error: ${err.message}`);
      })
      .finally(() => {
        setIsUploading(false); // Reset uploading state after request completes
      });
  };

  const handleNext = () => {
    setSlides(1)
    setPhase("slide-selection");
    navigate('/slide');
  };

  const handleRemoveFile = (fileName) => {
    setFiles(files.filter((file) => file.name !== fileName));
  };

  return (
    <div className="file-uploader py-4">
      <div
        className="upload-box border-2 border-dashed flex flex-col justify-center items-center border-gray-300 p-10 text-center cursor-pointer bg-white"
        onClick={() => document.getElementById('file-input').click()}
      >
        <SlCloudUpload size={40} color="#004F59" />
        <p className="mt-4 text-base text-[#676767]">{currentText.uploadHere}</p>
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

      {fileError && <p className="text-red-500 mt-2">{fileError}</p>}

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

      {files.length > 0 && !fileError && (
        <button
          onClick={handleUpload}
          className="mt-6 bg-[#004F59] text-white py-2 px-4 rounded-md"
          disabled={isUploading} // Disable button while uploading
        >
          {isUploading ? currentText.uploadingButton : currentText.uploadButton}
        </button>
      )}

      {status && <p className="mt-4">{status}</p>}

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

      {uploadedFiles.length > 0 && (
        <button
  onClick={handleNext}
  className="mt-6 bg-[#D3EC99] text-[#00383D] py-4 px-36 rounded-3xl text-xl font-bold hover:bg-[#b1d362] flex items-center justify-center space-x-2"
>
  <span>{currentText.nextButton}</span>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth="2"
    stroke="currentColor"
    className="w-5 h-5"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M13.5 4.5L20.5 11.5L13.5 18.5"
    />
  </svg>
</button>

      )}
    </div>
  );
};

export default Upload;
