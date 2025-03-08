const API_URL = "http://127.0.0.1:8000"; // Change to your Render app URL when deployed

async function downloadVideo() {
    const videoUrl = document.getElementById("videoUrl").value;
    if (!videoUrl) {
        showError("Please enter a valid YouTube URL.");
        return;
    }

    showStatus("Fetching video metadata...");

    try {
        // Fetch video metadata
        const response = await fetch(`${API_URL}/metadata/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ video_url: videoUrl }),
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        // Display metadata
        document.getElementById("download-status").innerHTML = `
            <div class="metadata">
                <img src="${data.thumbnail}" alt="Thumbnail">
                <h2>${data.title}</h2>
                <p><i class="far fa-clock"></i> Duration: ${Math.floor(data.duration / 60)}:${String(data.duration % 60).padStart(2, '0')}</p>
                <button class="download-button" onclick="startDownload('${videoUrl}')">
                    <i class="fas fa-download"></i> Start Download
                </button>
            </div>
        `;
    } catch (error) {
        showError("Error fetching metadata.");
        console.error(error);
    }
}

function showStatus(message) {
    document.getElementById("download-status").innerHTML = `
        <div class="metadata">
            <p><i class="fas fa-spinner fa-spin"></i> ${message}</p>
        </div>
    `;
}

function showError(message) {
    document.getElementById("download-status").innerHTML = `
        <div class="metadata">
            <p style="color: #ff6666;"><i class="fas fa-exclamation-circle"></i> ${message}</p>
        </div>
    `;
}

async function startDownload(videoUrl) {
    document.getElementById("download-status").innerHTML += "<p>Downloading...</p>";

    try {
        const downloadResponse = await fetch(`${API_URL}/download/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ video_url: videoUrl }),
        });

        const downloadData = await downloadResponse.json();

        if (downloadData.error) {
            document.getElementById("download-status").innerHTML = "Error: " + downloadData.error;
            return;
        }

        // Provide a download link
        document.getElementById("download-status").innerHTML += `
            <p>Download Complete!</p>
            <a class="download-link" href="${API_URL}/download-file/${downloadData.filename}" download>Click here to download</a>
        `;
    } catch (error) {
        document.getElementById("download-status").innerHTML = "Error starting download.";
        console.error(error);
    }
}

function pasteFromClipboard() {
    navigator.clipboard.readText().then((text) => {
        document.getElementById("videoUrl").value = text;
    }).catch((err) => {
        console.error("Failed to read clipboard: ", err);
    });
}
