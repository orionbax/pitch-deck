import React, { useState, useEffect } from "react";
import { usePhase } from "../pages/context/phaseContext";
import { useNavigate } from "react-router-dom";


const DeleteProjectComponent = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const { project_id , baseUrl, language} = usePhase(); // Get project_id from context
  const [status, setStatus] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    console.log(project_id, "project id"); // Debug: log the project ID
  }, [project_id]); // Only run when project_id changes

  const handleDelete = async () => {
    if (!project_id) {
      setMessage("Project not found.");
      return;
    }

    setLoading(true);
    setMessage(""); // Clear previous message

    try {
      const token = localStorage.getItem("authToken"); // Assuming token is stored in localStorage
     console.log("Token:", token); // Check if the token is retrieved correctly

      if (!token) {
        setMessage("Authorization token is missing.");
        setLoading(false);
        return;
      }

      const response = await fetch(`${baseUrl}/delete_project`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ project_id: project_id }), 
      });

      const result = await response.json();
      console.log(result, "deletresult")
      console.log("delete result", result)

      if (response.ok) {
        setMessage(`Project with ID "${project_id}" deleted successfully.`);
        localStorage.removeItem("authToken");
        setStatus(true)
        navigate('/')
      } else {
        setMessage(`Error: ${result.error || "Failed to delete project."}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className=" ">
      <div className="flex items-center justify-center gap-4">
        <button
          onClick={handleDelete}
          className="bg-[#C0D78C] text-[#00383D] font-bold text-opacity-[60%] py-2 px-10 rounded-lg"
          disabled={loading} // Disable button while loading
        >
          {loading ? "Deleting..." : "Yes, Delete"} 
        </button>
        {message && <p className="mt-4 text-black">{message}</p>} {/* Show message */}
      </div>
    </div>
  );
};

export default DeleteProjectComponent;
