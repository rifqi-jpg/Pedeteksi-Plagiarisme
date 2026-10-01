# Copyright (c) 2026 Rifqi Rabbani. All rights reserved.
# Pendeteksi Plagiarisme — Aplikasi milik Rifqi Rabbani.

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from detector import analyze_similarity, resolve_text_input

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Pendeteksi Plagiarisme",
    description="Aplikasi web deteksi plagiarisme dengan TF-IDF dan Cosine Similarity",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(
    reference_text: str = Form(""),
    test_text: str = Form(""),
    reference_file: UploadFile | None = File(None),
    test_file: UploadFile | None = File(None),
):
    try:
        ref_bytes = await reference_file.read() if reference_file and reference_file.filename else None
        test_bytes = await test_file.read() if test_file and test_file.filename else None

        ref_filename = reference_file.filename if reference_file else None
        test_filename = test_file.filename if test_file else None

        reference = resolve_text_input(reference_text, ref_bytes, ref_filename)
        test = resolve_text_input(test_text, test_bytes, test_filename)

        result = analyze_similarity(reference, test)
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan saat menganalisis dokumen.") from exc
