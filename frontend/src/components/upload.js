/* eslint-disable no-unused-vars */
import React, {useState} from 'react'
import { useSocket } from '../api/socket'
import { IoCloudUploadOutline } from "react-icons/io5";

const Upload = () => {

  const { socket, isConnected } = useSocket();
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };


  const handleUpload = () => {

    if (!isConnected) {
        alert('Not connected to the server. Please try again later.');
        return;
      }

      if (files.length === 0) {
        alert("Please select at least one file to upload.");
        return;
      }

      const fileData = files.map((file) => {
        return {
          filename: file.name,
          file: file,
        };
      });



      socket.emit('upload_document', {
        file: fileData.map((f) => f.file),
        filename: fileData.map((f) => f.filename),
      });

      socket.on('document_upload_status', (data) => {
        if (data.status === 'success') {
          setStatus(`Successfully uploaded: ${data.filenames.join(', ')}`);
        } else {
          setStatus(`Error: ${data.message}`);
        }
      });



  }
  
  return (
    <div>

    </div>
  )
}

export default Upload;