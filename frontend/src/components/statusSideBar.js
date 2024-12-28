import React from 'react'

const statusSideBar = () => {
  return (
    <div className='w-1/5 h-screen bg-[#004F59] flex flex-col '>

    <div>
        <h1>Language</h1>
        <select className='bg-[#004F59] text-white'>
            <option value="en">English</option>
            <option value="no">Norwegian</option>
        </select>
    </div>
    

    <div>
        <h1>Editing Options</h1>
        
        

        <div>
            <label for="structured-editing">
                <input type="checkbox" id="structured-editing" name="structured-editing"/>
                Structured Editing
            </label>
        </div>

        <div>
            <label for="guided-feedback">
                <input type="checkbox" id="guided-feedback" name="guided-feedback"/>
                Guided Feedback
            </label>
        </div>
        
    </div>

    
    </div>
  )
}

export default statusSideBar