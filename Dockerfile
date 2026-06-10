FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-hin tesseract-ocr-tam \
    tesseract-ocr-tel tesseract-ocr-kan tesseract-ocr-mal \
    tesseract-ocr-ben libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data/raw/hindi data/raw/tamil data/raw/telugu \
    data/raw/english data/processed data/vector_store
EXPOSE 8000 8501