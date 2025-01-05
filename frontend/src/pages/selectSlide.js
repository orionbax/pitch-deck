

/* eslint-disable no-unused-vars */
import React, {useEffect} from 'react'
import SideBar from '../components/sideBar'
import SlideSelection from '../components/slideSelection'
import StatusSideBar from '../components/statusSideBar'
import { useNavigate } from 'react-router-dom'


const SelectSlide = () => {

  const navigate = useNavigate()

   useEffect(() => {
      const token = localStorage.getItem('authToken'); // Get the token from localStorage
      if (!token) {
        navigate('/'); // Redirect to home if no token is found
      }
    }, [navigate]);

  return (
    <div className='flex  justify-center items-center'>
        {/*<StatusSideBar/> */}
        <SlideSelection/>
        
         
    </div>
  )
}

export default SelectSlide;