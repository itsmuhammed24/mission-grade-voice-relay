
FROM python:3.10-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*



WORKDIR /app


COPY backend/ ./backend/
COPY backend/requirements.txt ./backend/requirements.txt



RUN pip install --no-cache-dir -r backend/requirements.txt


RUN git clone https://github.com/ggerganov/llama.cpp.git \
    && cd llama.cpp \
    && make -j4


RUN mkdir -p backend/models


EXPOSE 8000


CMD bash -c "\
    if [ ! -f backend/models/model.gguf ]; then \
        echo 'ERROR: backend/models/model.gguf missing!'; \
        echo 'Please copy your GGUF model into backend/models/'; \
        exit 1; \
    fi; \
    ./llama.cpp/llama-server -m backend/models/model.gguf --host 0.0.0.0 --port 9999 & \
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 \
"
