FROM python:3.11

RUN apt-get update && \
    apt-get install -y ffmpeg libsodium-dev build-essential && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
