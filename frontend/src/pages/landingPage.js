import React, { useState } from 'react';
import { FaArrowRight } from "react-icons/fa";
import vbailogo from "../vbailogo.svg";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { usePhase } from './context/phaseContext';


const LandingPage = () => {
  const [projectName, setProjectName] = useState('project');
  const [projectData, setProjectData] = useState(null);
  const [error, setError] = useState('');
  const {setProject_id, baseUrl, setSlides}  = usePhase()
  const navigate = useNavigate();

  const handleCreateProject = async () => {
    if (!projectName) {
      setError('Project ID is required');
      return;
    }
  // `${baseUrl}/edit_slide`
    try {
      console.log('Sending request with project name:', projectName); // Log the project name
      const response = await axios.post( `${baseUrl}/create_project`, {
        project_id: projectName,
      });
      console.log('Response received:', response.data); // Log the response data
      setProjectData(response.data);
      const token = response.data.token; // Assuming the token is in the `token` field.
      console.log('Token received:', token);
      if (token) {
        // localStorage.setItem('token', token);
        localStorage.setItem('authToken', token);

        console.log('Token saved to localStorage', token);
      } else {
        console.log('No token received in response');
      }

      
      setError('');
      setProject_id(projectName)
      setSlides(Object.keys(response.data.state.slides).length)
      navigate('/upload', { state: { projectData: response.data } });
    } catch (err) {
      console.error('Error occurred:', err); // Log the error if there's an issue
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <div className='w-screen h-screen flex flex-col md:flex-row'>
      <div className='w-full md:w-1/4 bg-[#004F59] flex flex-col gap-4 justify-center items-center px-3 py-10 md:py-0'>
        <img src={vbailogo} alt='vbai logo' className="w-24 md:w-40" />
        <h1 className='text-3xl font-normal text-white text-center md:text-left'>Pitch Deck Generator AI</h1>
      </div>

      <div className="w-full md:w-3/4 flex flex-col py-10 md:py-20 px-10 md:px-56 gap-5">
        <h1 className='text-3xl md:text-5xl text-[#004F59] font-semibold pb-3'>Pitch Deck Generator AI</h1>
        <h5 className='text-lg md:text-xl'>Enter your project name:</h5>
        <form>
          <input
            className='w-full md:w-96 h-7 border-2 p-3 py-4 mb-4'
            type='text'
            placeholder='Enter Project Name'
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
          />
        </form>
        <button
          onClick={handleCreateProject}
          className='w-full md:w-96 flex items-center justify-center py-4 px-8 gap-2 bg-[#D3EC99] rounded-3xl'
        >
          Next <span><FaArrowRight /></span>
        </button>

        {error && <p className="text-red-500 text-center">{error}</p>}
      </div>
    </div>
  );
}

export default LandingPage;
