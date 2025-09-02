# ✅ Latest stable base image use करें
FROM python:3.10-slim-bullseye

# ✅ System update + dependencies install
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends gcc libffi-dev musl-dev ffmpeg aria2 python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ App directory
WORKDIR /app

# ✅ Requirements install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy source code
COPY . .

# ✅ Run your bot
CMD ["python3", "main.py"]
