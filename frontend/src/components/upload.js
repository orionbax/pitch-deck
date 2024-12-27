import React, { useState } from 'react';
import { useSocket } from '../api/socket';
import { FaDownload } from 'react-icons/fa'; // Import the download icon

const Upload = () => {
  const { socket, isConnected } = useSocket(); // Use the custom hook
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(null);
  const [fileError, setFileError] = useState('');

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);

      // Check for file size and type
      const validFiles = selectedFiles.filter(file => {
        const isValidSize = file.size <= 200 * 1024 * 1024; // 200 MB max
        const isValidType = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type);
        
        return isValidSize && isValidType;
      });

      if (validFiles.length !== selectedFiles.length) {
        setFileError('Some files are either too large or have unsupported formats.');
      } else {
        setFileError('');
      }

      setFiles(validFiles);
    }
  };

  // Handle file upload
  const handleUpload = () => {
    if (!isConnected) {
      alert('Not connected to the server. Please try again later.');
      return;
    }

    if (files.length === 0) {
      alert("Please select at least one valid file to upload.");
      return;
    }

    // Prepare files and filenames for the server
    const fileData = files.map((file) => {
      return {
        filename: file.name,
        file: file,
      };
    });

    // Emit the `upload_document` event
    socket.emit('upload_document', {
      file: fileData.map((f) => f.file),
      filename: fileData.map((f) => f.filename),
    });

    // Listen for server responses
    socket.on('document_upload_status', (data) => {
      if (data.status === 'success') {
        setStatus(`Successfully uploaded: ${data.filenames.join(', ')}`);
      } else {
        setStatus(`Error: ${data.message}`);
      }
    });
  };

  return (
    <div className="file-uploader max-w-lg mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Upload Files</h2>
    {/*   {isConnected ? (
        <p className="text-green-500">Connected to server</p>
      ) : (
        <p className="text-red-500">Disconnected from server</p>
      )}

      {/* White box for file upload */}
      <div
        className="upload-box border-2 border-dashed border-gray-300 p-6 text-center cursor-pointer bg-white"
        onClick={() => document.getElementById('file-input').click()}
      >
        <FaDownload size={40} color="#007bff" />
        <p className="mt-4 text-lg text-blue-600">
          Click to upload PDF, DOCX, or TXT files (Max 200MB)
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

      {/* Button to trigger upload */}
      {files.length > 0 && !fileError && (
        <button
          onClick={handleUpload}
          disabled={!isConnected || files.length === 0}
          className="mt-6 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300"
        >
          Upload
        </button>
      )}

      {/* Status message */}
      {status && <p className="mt-4">{status}</p>}
    </div>
  );
};

export default Upload;
