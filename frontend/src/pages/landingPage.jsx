/* eslint-disable no-unused-vars */
import React, {useState} from 'react'
import { FaArrowRight } from "react-icons/fa";
import vbailogo from "../vbailogo.svg"
import { useSocket } from '../api/socket';

const LandingPage = () => {

  const [projectName, setProjectName] = useState('project')
  const { socket, isConnected, sendUsername } = useSocket();
  
  const handleSubmit = (e) => {
    e.preventDefault();  
    if (projectName) {
      socket.emit('set_project', { project_id: projectName }); 
      console.log("Project Name sent to backend:", projectName);
    } else {
      alert("Enter a project name");
    }
  };

  
  return (
    <div className='w-screen h-screen flex '>
    
    <div className='w-1/4 bg-[#004F59] flex flex-col gap-4 justify-center items-center px-3'>
        <img src={vbailogo} alt='vbai logo' />
        <h1 className='text-3xl font-normal text-white'>Pitch Deck Generator AI</h1>
    </div>
       
    <div className="w-3/4 flex flex-col py-20 px-56 gap-5">
        <h1 className='text-5xl text-[#004F59] font-semibold pb-3'>Pitch Deck Generator AI</h1>
        <h5 className='text-xl'>Enter your project name:</h5>
        <form onSubmit={handleSubmit}>
           <input className='w-96 h-7 border-2 p-3 py-4 mb-4' type='text' placeholder='Enter Project Name  '  value={projectName} onChange={(e) => setProjectName(e.target.value)}/>

        </form>
        <a href='/' >
            <button className='w-96  flex items-center justify-center py-4 px-44 gap-2 bg-[#D3EC99] rounded-3xl'>Next <span> <FaArrowRight/> </span></button> 
        </a>
    </div>
    
    </div>
  )
}

export default LandingPage