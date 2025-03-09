from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import glob

app = FastAPI()

# Allow requests from both Live Server & Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "https://mypogidownloader.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root `/`
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

# Ensure downloads folder exists
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Path to cookies.txt
COOKIES_FILE = "cookies.txt"

class VideoRequest(BaseModel):
    video_url: str

def get_metadata(url: str):
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
        "cookies": COOKIES_FILE,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
        }

def get_next_filename():
    """Finds the next available sequential filename."""
    existing_files = glob.glob(f"{DOWNLOAD_FOLDER}/videoplayback*.mp4")
    numbers = sorted(
        [int(f.replace(f"{DOWNLOAD_FOLDER}/videoplayback", "").replace(".mp4", "")) for f in existing_files if f[-5].isdigit()]
    ) or [0]
    return f"videoplayback{numbers[-1] + 1}.mp4"

def download_video(url: str):
    filename = get_next_filename()
    output_path = os.path.join(DOWNLOAD_FOLDER, filename)
    
    ydl_opts = {
        "format": "best",
        "outtmpl": output_path,
        "quiet": True,
        "noplaylist": True,
        "cookies": COOKIES_FILE,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3",
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return {"title": info["title"], "filename": filename, "path": output_path}

@app.post("/metadata/")
def get_video_metadata(request: VideoRequest):
    try:
        return get_metadata(request.video_url)
    except Exception as e:
        return {"error": str(e)}

@app.post("/download/")
def download_video_api(request: VideoRequest):
    try:
        return download_video(request.video_url)
    except Exception as e:
        return {"error": str(e)}

@app.get("/download-file/{filename}")
def serve_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    # Delete file after serving
    background_tasks.add_task(lambda: os.remove(file_path))

    return FileResponse(file_path, media_type="video/mp4", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
