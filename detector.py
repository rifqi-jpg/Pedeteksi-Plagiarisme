# Copyright (c) 2025 RifqiRabbani. All rights reserved.

import io
from typing import BinaryIO

import nltk
import PyPDF2
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_stopwords_ready = False


def _ensure_stopwords() -> None:
    global _stopwords_ready
    if _stopwords_ready:
        return
    try:
        stopwords.words("indonesian")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    _stopwords_ready = True


def extract_text_from_pdf(file_obj: BinaryIO) -> str:
    pdf_reader = PyPDF2.PdfReader(file_obj)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()


def extract_text_from_txt(file_obj: BinaryIO) -> str:
    content = file_obj.read()
    if isinstance(content, bytes):
        return content.decode("utf-8").strip()
    return str(content).strip()


def extract_text_from_upload(file_obj: BinaryIO, filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_obj)
    if name.endswith(".txt"):
        return extract_text_from_txt(file_obj)
    raise ValueError("Format file tidak didukung. Gunakan PDF atau TXT.")


def calculate_cosine_similarity(text1: str, text2: str) -> float:
    _ensure_stopwords()

    if not text1.strip() or not text2.strip():
        raise ValueError("Teks referensi dan teks uji tidak boleh kosong.")

    stopwords_indonesia = stopwords.words("indonesian")
    tfidf = TfidfVectorizer(stop_words=stopwords_indonesia)
    tfidf_matrix = tfidf.fit_transform([text1, text2])
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return float(similarity_matrix[0][0])


def analyze_similarity(reference_text: str, test_text: str) -> dict:
    score = calculate_cosine_similarity(reference_text, test_text)
    percentage = round(score * 100, 1)

    if score >= 0.8:
        level = "high"
        label = "Tinggi — Sangat Mirip"
        message = "Dokumen sangat mirip dengan referensi. Kemungkinan plagiarisme tinggi."
    elif score >= 0.5:
        level = "medium"
        label = "Sedang — Cukup Mirip"
        message = "Dokumen cukup mirip dengan referensi. Perlu ditinjau lebih lanjut."
    else:
        level = "low"
        label = "Rendah — Tidak Terlalu Mirip"
        message = "Dokumen tidak terlalu mirip dengan referensi."

    return {
        "similarity_score": round(score, 4),
        "similarity_percentage": percentage,
        "level": level,
        "label": label,
        "message": message,
        "reference_length": len(reference_text),
        "test_length": len(test_text),
    }


def resolve_text_input(text: str | None, file_bytes: bytes | None, filename: str | None) -> str:
    if text and text.strip():
        return text.strip()

    if file_bytes and filename:
        return extract_text_from_upload(io.BytesIO(file_bytes), filename)

    raise ValueError("Harap isi teks atau unggah file (PDF/TXT).")
