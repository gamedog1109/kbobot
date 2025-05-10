FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip fonts-liberation libnss3 libgconf-2-4 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxi6 libxtst6 libxrandr2 xdg-utils \
    libasound2 libatk-bridge2.0-0 libgtk-3-0 libgbm1 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask gunicorn playwright beautifulsoup4 pandas requests \
    && playwright install --with-deps

WORKDIR /app
COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers=1"]