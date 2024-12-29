/* eslint-disable no-unused-vars */
import React from 'react'
import Upload from '../components/upload'
import SideBar from '../components/statusSideBar'



const uploadDocument = () => {

  
  return (
    <div className=' flex  '>
 {/*<StatusSideBar/> */}
      <div className='p-16'>
            <h1 className='text-5xl font-semibold text-[#004F59]'> Upload Document</h1>
            <h1 className='py-4 text-xl font-normal'>Upload Company Document(optional)</h1>
          
            <Upload/>
            
      </div>
      
    </div>
  )
}

export default uploadDocument