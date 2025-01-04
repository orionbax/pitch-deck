import React, { useState } from 'react';
import axios from 'axios';
import DownloadButton from './downloadOptions';
import { usePhase } from '../pages/context/phaseContext';
import Delete from './deleteProject';
import { useNavigate } from 'react-router-dom';

const GeneratedContent = ({ responses = [], isGenerationComplete, isProcessing }) => {
  const [slides, setSlides] = useState(responses);
  const [editingSlide, setEditingSlide] = useState(null); // Tracks the currently editing slide
  const [editRequest, setEditRequest] = useState(''); // Tracks the user's input for the edit request
  const [editedContent, setEditedContent] = useState({}); // Store edited content per slide
  const [preview, setPreview] = useState(false);
  const [loadingSlide, setLoadingSlide] = useState(null); // Tracks which slide is being edited
  const { phase, setPhase, baseUrl } = usePhase();
  const navigate = useNavigate();
  const shouldShowMessage = responses.length === 0 || !isGenerationComplete;


  const token = localStorage.getItem('authToken');

  const handleModify = () => {
    console.log("clicked")
  
    navigate('/slide');

  };

  const handleEditRequest = async (slide) => {
    setLoadingSlide(slide.slide); // Set the slide as loading
    try {
      const updatedContent = await editSlide(slide.slide, editRequest);

      // Update only the content for the edited slide
      setSlides((prevSlides) =>
        prevSlides.map((item) =>
          item.slide === slide.slide
            ? { ...item, content: updatedContent.content }
            : item
        )
      );

      // Update edited content to store per slide
      setEditedContent((prevEditedContent) => ({
        ...prevEditedContent,
        [slide.slide]: updatedContent.content,
      }));

      setEditingSlide(null); // Close the text box after editing
      setEditRequest(''); // Reset the input field
    } catch (error) {
      console.error('Failed to edit slide:', error);
    } finally {
      setLoadingSlide(null); // Reset loading state
    }
  };

  const handlePreview = () => {
    setPreview(true);
    setPhase('preview-slide');
  };

  const editSlide = async (slide, editRequest) => {
    console.log('slidetoedi', slide, 'editrequest', editRequest);
    try {
      const response = await axios.post(
        `${baseUrl}/edit_slide`,
        {
          slide,
          edit_request: editRequest,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.status === 'completed') {
        return response.data.content;
      } else {
        console.error('Failed to edit slide content');
      }
    } catch (error) {
      console.error('Error editing slide:', error);
      throw error;
    }
  };

  return (
    <div>
      <h2 className="text-5xl text-[#004F59] my-10 px-2 flex justify-center font-semibold">Create your pitch deck</h2>

      <div className="bg-white my-10 py-10">
        {shouldShowMessage && (
          <div className="py-8 text-xl font-medium text-[#004F59]">
            AI is analyzing your documents and generating pitch deck content...
          </div>
        )}

        <div className="overflow-y-auto max-h-[400px] py-10 px-8"> {/* Set a max height for the scrollable content */}
          {responses.map((item, index) => (
            <div key={index} className="bg-white p-4">
              <h3 className="text-2xl font-semibold mb-2">{item.slide}</h3>
              <p>
                {(editedContent[item.slide] || item.content).split('\n').map((line, index) => (
                  <React.Fragment key={index}>
                    {line}
                    <br />
                  </React.Fragment>
                ))}
              </p>
              {editingSlide === item.slide ? (
                <div className="mt-2 space-y-2">
                  <textarea
                    value={editRequest}
                    onChange={(e) => setEditRequest(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder="Enter your edit request here..."
                  />
                  <div className="flex space-x-2">
                    <button
                      className="text-white bg-[#004F59] px-4 py-2 rounded-md disabled:opacity-50"
                      onClick={() => handleEditRequest(item)}
                      disabled={loadingSlide === item.slide} // Disable button while loading
                    >
                      {loadingSlide === item.slide ? 'Editing...' : 'Save'}
                    </button>

                    <button
                      className="text-white bg-[#548062] px-4 py-2 rounded-md"
                      onClick={() => {
                        setEditingSlide(null); // Cancel editing
                        setEditRequest('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                // Only show Edit button if not in Preview mode
                !preview && (
                  <button
                    className="text-[#004F59] bg-[#D3EC99] py-2 px-5 rounded-lg font-semibold mt-2"
                    onClick={() => setEditingSlide(item.slide)}
                  >
                    Edit
                  </button>
                )
              )}
            </div>
          ))}
        </div>
      </div>

      <div>
        {isGenerationComplete && (
          <div className="flex justify-between mt-3">
            {preview && (
              <div className="flex w-full justify-between items-center">
                <DownloadButton />
                <Delete />
              </div>
            )}

            {!preview && (
              <div className="flex gap-16 w-full">
                <button
                  className="bg-[#D3EC99] text-[#004F59] py-4 rounded-[50px] px-16"
                  onClick={handleModify}
                >
                  Modify section
                </button>

                <button
                  className="bg-[#004F59] py-4 rounded-[50px] px-16 text-white"
                  onClick={handlePreview}
                >
                  Go to preview
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GeneratedContent;
