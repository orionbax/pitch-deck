import React, { useState } from "react";
import axios from "axios";
import { usePhase } from "../pages/context/phaseContext";

const DownloadButton = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(""); // State to hold the success message
    const {phase, setPhase, baseUrl} = usePhase()
    const handleDownload = async () => {
        // Retrieve the bearer token from local storage
        const token = localStorage.getItem("authToken");
        console.log("downloadtoken", token);

        if (!token) {
            setError("No authentication token found.");
            return;
        }

        setLoading(true);
        setError(null);  // Clear previous errors
        setSuccessMessage("");  // Clear previous success messages

        try {
            // Fetch project data using the bearer token when the button is clicked
            const response = await axios.post(
                `${baseUrl}/download_pdf`, // Endpoint to get the PDF
                {},
                {
                    headers: {
                        Authorization: `Bearer ${token}`, // Send the bearer token
                    },
                    responseType: "blob", // This ensures the response is treated as a file
                }
            );

            // Create a link element and trigger download
            const blob = new Blob([response.data], { type: "application/pdf" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "project_slides.pdf";  // You can customize this filename as needed
            link.click(); // Trigger download

            // Show success message after download is triggered
            setSuccessMessage("Download started! You can find the file in your Downloads folder.");
        } catch (err) {
            setError("Failed to download PDF. Please try again.");
        } finally {
            setLoading(false);
        }
        setPhase("download-pdf")

    };

    return (
        <div>
            <button
                onClick={handleDownload}
                disabled={loading}
                style={{
                    padding: "10px 20px",
                    backgroundColor: "#4CAF50",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                }}
            >
                {loading ? "Exporting..." : "Export as PDF"}
            </button>
         {/*  {error && <p style={{ color: "red" }}>{error}</p>}
            {successMessage && <p style={{ color: "green" }}>{successMessage}</p>} {/* Display success message */}
        </div>
    );
};

export default DownloadButton;
