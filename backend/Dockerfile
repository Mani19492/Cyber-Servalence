FROM nvidia/cuda:13.0.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv ffmpeg libgl1 libglib2.0-0 git build-essential \
  && rm -rf /var/lib/apt/lists/*

# Ensure python3 is default
RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt

# Copy app
COPY app /app/app

# Expose port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
