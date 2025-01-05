import React from 'react';
import { MdClose } from 'react-icons/md'; // Importing MdClose icon
import { AiOutlineWarning } from 'react-icons/ai'; // Importing Warning icon
import Delete from './deleteProject';

const Modal = ({ message, onConfirm, onCancel }) => {
  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg w-[30%] relative">
        {/* Close Button */}
        <button
          className="absolute top-2 right-2 text-white bg-[#C0D78C] rounded-full"
          onClick={onCancel}
        >
          <MdClose className="h-6 w-6" />
        </button>

        {/* Warning Icon */}
        <div className="  flex justify-center  my-3 text-[#C0D78C] ">
          <AiOutlineWarning className="h-8 w-8" />
        </div>

        {/* Modal Message */}
        <h2 className="text-xl mb-6 flex justify-center py-2">{message}</h2>

        {/* Delete Button */}
        <div className="flex justify-center space-x-4 px-10">
          <Delete onConfirm={onConfirm} />
        </div>
      </div>
    </div>
  );
};

export default Modal;
