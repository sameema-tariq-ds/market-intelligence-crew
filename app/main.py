from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uuid
import os

from app.crew_runner import run_market_intel_crew

app = FastAPI()

# FIX: ensure folder exists
os.makedirs("static", exist_ok=True)
os.makedirs("output", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    with open("app/static/index.html", "r") as f:
        return f.read()


@app.post("/generate")
def generate(industry: str = Form(...)):
    try:
        file_id = str(uuid.uuid4())
        output_path = f"output/market_analyst_{industry}.md"

        run_market_intel_crew(industry, output_path)

        return {
            "message": "Report generated successfully",
            "download_url": f"/download/{output_path}"
        }

    except Exception as e:
        return {
            "error": str(e)
        }


@app.get("/download/{file_path:path}")
def download(file_path: str):

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(path=file_path, filename="report.md")