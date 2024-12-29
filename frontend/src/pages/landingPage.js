import React, { useState } from 'react';
import { FaArrowRight } from "react-icons/fa";
import vbailogo from "../vbailogo.svg";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const [projectName, setProjectName] = useState('project');
  const [projectData, setProjectData] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleCreateProject = async () => {
    if (!projectName) {
      setError('Project ID is required');
      return;
    }

    try {
      console.log('Sending request with project name:', projectName); // Log the project name
      const response = await axios.post('http://127.0.0.1:5000/create_project', {
        project_id: projectName,
      });
      console.log('Response received:', response.data); // Log the response data
      setProjectData(response.data);
      const token = response.data.token; // Assuming the token is in the `token` field.
      console.log('Token received:', token);
      localStorage.setItem('authToken', token); 
      setError('');
      navigate('/upload', { state: { projectData: response.data } });
    } catch (err) {
      console.error('Error occurred:', err); // Log the error if there's an issue
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <div className='w-screen h-screen flex'>
      <div className='w-1/4 bg-[#004F59] flex flex-col gap-4 justify-center items-center px-3'>
        <img src={vbailogo} alt='vbai logo' />
        <h1 className='text-3xl font-normal text-white'>Pitch Deck Generator AI</h1>
      </div>

      <div className="w-3/4 flex flex-col py-20 px-56 gap-5">
        <h1 className='text-5xl text-[#004F59] font-semibold pb-3'>Pitch Deck Generator AI</h1>
        <h5 className='text-xl'>Enter your project name:</h5>
        <form>
          <input
            className='w-96 h-7 border-2 p-3 py-4 mb-4'
            type='text'
            placeholder='Enter Project Name'
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
          />
        </form>
        <button
          onClick={handleCreateProject}
          className='w-96 flex items-center justify-center py-4 px-44 gap-2 bg-[#D3EC99] rounded-3xl'
        >
          Next <span><FaArrowRight /></span>
        </button>

        {error && <p className="text-red-500">{error}</p>}
      </div>
    </div>
  );
}

export default LandingPage;
