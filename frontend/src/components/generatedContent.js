import React, { useState } from 'react';
import axios from 'axios';
import DownloadButton from './downloadOptions';
import { usePhase } from '../pages/context/phaseContext';
import Delete from './deleteProject';
import { useNavigate } from 'react-router-dom';
import Modal from './modal';

const GeneratedContent = ({ responses = [], isGenerationComplete, isProcessing }) => {
  const [slides, setSlides] = useState(responses);
  const [editingSlide, setEditingSlide] = useState(null); // Tracks the currently editing slide
  const [editRequest, setEditRequest] = useState(''); // Tracks the user's input for the edit request
  const [editedContent, setEditedContent] = useState({}); // Store edited content per slide
  const [preview, setPreview] = useState(false);
  const [loadingSlide, setLoadingSlide] = useState(null); // Tracks which slide is being edited
  const { phase, setPhase, baseUrl, language } = usePhase();
  const navigate = useNavigate();
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const token = localStorage.getItem('authToken');

  const textContent = {
    heading: language === 'no' ? 'Lag din presentasjonsdekke' : 'Create your pitch deck',
    processingMessage: language === 'no'
      ? 'AI analyserer dokumentene dine og genererer innhold til presentasjonsdekke...'
      : 'AI is analyzing your documents and generating pitch deck content...',
    modifyButton: language === 'no' ? 'Endre seksjon' : 'Modify section',
    previewButton: language === 'no' ? 'Gå til forhåndsvisning' : 'Go to preview',
    editPlaceholder: language === 'no' ? 'Skriv inn redigeringsforespørselen her...' : 'Enter your edit request here...',
    editButton: language === 'no' ? 'Lagre' : 'Save',
    cancelButton: language === 'no' ? 'Avbryt' : 'Cancel',
    deleteButton: language === 'no' ? 'Slett' : 'Delete',
    deleteMessage: language === 'no'
      ? 'Er du sikker på at du vil slette dette prosjektet?'
      : 'Are you sure you want to delete this Project?',
  };

  const handleModify = () => {
    setPhase(2);
  };

  const handleEditRequest = async (item) => {
    setLoadingSlide(item.slide);

    try {
      const response = await fetch(`${baseUrl}/api/v1/content/edit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          slide: item.slide,
          content: item.content,
          editRequest: editRequest,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to edit content');
      }

      const data = await response.json();

      setEditedContent((prev) => ({ ...prev, [item.slide]: data.editedContent }));
      setEditingSlide(null);
      setEditRequest('');
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingSlide(null);
    }
  };

  const handlePreview = () => {
    setPreview(!preview);
  };

  const handleDeleteClick = () => {
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/v1/projects/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete project');
      }

      navigate('/dashboard');
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
  };

  return (
    <div>
      <h2 className="text-5xl text-[#004F59] my-10 px-2 flex justify-center font-semibold">
        {textContent.heading}
      </h2>

      <div className="bg-white my-10 py-10">
        {responses.length === 0 && (
          <div className="py-8 pl-3 text-xl font-medium text-[#004F59]">
            {textContent.processingMessage}
          </div>
        )}

        <div className="overflow-y-auto max-h-[400px] py-10 px-8">
          {responses.map((item, index) => (
            <div key={index} className="bg-white p-4">
              <h3 className="text-2xl font-semibold mb-2">{item.slide}</h3>
              <p>
                {(editedContent[item.slide] || item.content)
                  .split('\n')
                  .map((line, idx) => (
                    <li key={idx} className="list-none pl-5 flex items-center">
                      <span className="before:content-['•'] before:text-black before:text-2xl before:mr-2">
                        {line.trim().startsWith('-') ? line.trim().slice(1).trim() : line}
                      </span>
                    </li>
                  ))}
              </p>
              {editingSlide === item.slide ? (
                <div className="mt-2 space-y-2">
                  <textarea
                    value={editRequest}
                    onChange={(e) => setEditRequest(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-md"
                    placeholder={textContent.editPlaceholder}
                  />
                  <div className="flex space-x-2">
                    <button
                      className="text-white bg-[#004F59] px-4 py-2 rounded-md disabled:opacity-50"
                      onClick={() => handleEditRequest(item)}
                      disabled={loadingSlide === item.slide}
                    >
                      {loadingSlide === item.slide ? `${textContent.editButton}...` : textContent.editButton}
                    </button>

                    <button
                      className="text-[#004F59] bg-[#D3EC99] px-4 py-2 rounded-md"
                      onClick={() => {
                        setEditingSlide(null);
                        setEditRequest('');
                      }}
                    >
                      {textContent.cancelButton}
                    </button>
                  </div>
                </div>
              ) : (
                !preview && (
                  <button
                    className="text-[#004F59] bg-[#D3EC99] py-2 px-5 rounded-lg font-semibold mt-2"
                    onClick={() => setEditingSlide(item.slide)}
                  >
                    {textContent.editButton}
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
                <button
                  className="text-red-500 py-2 px-5 rounded-lg"
                  onClick={handleDeleteClick}
                >
                  {textContent.deleteButton}
                </button>
              </div>
            )}

            {!preview && (
              <div className="flex gap-16 w-full">
                <button
                  className="bg-[#D3EC99] text-[#004F59] py-4 rounded-[50px] px-16"
                  onClick={handleModify}
                >
                  {textContent.modifyButton}
                </button>

                <button
                  className="bg-[#004F59] py-4 rounded-[50px] px-16 text-white"
                  onClick={handlePreview}
                >
                  {textContent.previewButton}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {showDeleteModal && (
        <Modal
          message={textContent.deleteMessage}
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
        />
      )}
    </div>
  );
};

export default GeneratedContent;

