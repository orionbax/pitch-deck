import React, {useEffect} from 'react'
import StatusSideBar from '../components/statusSideBar'
import PreviewSlide from '../components/previewSlide'
import { useNavigate } from 'react-router-dom'

const preview = () => {

  const token = localStorage.getItem('authToken');
  console.log("preview token ", token)
  return (
    <div className='flex'>

      {/*<StatusSideBar/> */}
      <PreviewSlide/>
    
    </div>
  )
}

export default preview