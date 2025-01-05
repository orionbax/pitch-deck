import React, { useState } from "react";
import axios from "axios";
import { usePhase } from "../pages/context/phaseContext";

const DownloadButton = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(""); // State to hold the success message
    const { phase, setPhase, baseUrl, language } = usePhase();
    const token = localStorage.getItem("authToken");
    // const tok = "rZOQf0wJ2xhtOg56h0HmilRAp-BIPfMzfuckGpA1vng"

    // Language-based text content
    const textContent = {
        buttonLabel: language === "no" ? "Eksporter som PDF" : "Export as PDF",
        loadingLabel: language === "no" ? "Eksporterer..." : "Exporting...",
        noTokenError: language === "no" 
            ? "Ingen autentiseringstoken funnet." 
            : "No authentication token found.",
        downloadStarted: language === "no" 
            ? "Nedlasting startet! Du finner filen i nedlastingsmappen din." 
            : "Download started! You can find the file in your Downloads folder.",
        downloadFailed: language === "no" 
            ? "Kunne ikke laste ned PDF. Prøv igjen." 
            : "Failed to download PDF. Please try again."
    };

    const handleDownload = async () => {
        if (!token) {
            setError(textContent.noTokenError);
            return;
        }

        setLoading(true);
        setError(null); // Clear previous errors
        setSuccessMessage(""); // Clear previous success messages

        // Log the base URL before making the request
        console.log("Base download URL:", baseUrl);

        try {
            // Fetch project data using the bearer token when the button is clicked
            const response = await axios.post(
                `${baseUrl}/download_pdf`, // Endpoint to get the PDF
                {},
                {
                    headers: {
                        Authorization: `Bearer ${token}`, // Send the bearer token
                    },
                    responseType: "blob", // Ensure the response is treated as a file
                }
            );

            // Create a link element and trigger download
            const blob = new Blob([response.data], { type: "application/pdf" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "project_slides.pdf"; // You can customize this filename as needed
            link.click(); // Trigger download

            // Show success message after download is triggered
            setSuccessMessage(textContent.downloadStarted);
        } catch (err) {
            console.log("Error occurred:", err);
            setError(textContent.downloadFailed);
        } finally {
            setLoading(false);
        }

        setPhase("download-pdf");
    };

    return (
        <div>
            <button
                className="text-[#004F59] bg-[#D3EC99] px-20 py-4 rounded-[50px]"
                onClick={handleDownload}
                disabled={loading}
            >
                {loading ? textContent.loadingLabel : textContent.buttonLabel}
            </button>
            {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
    );
};

export default DownloadButton;
