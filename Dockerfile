FROM python:3.9-slim

# Install wget, gnupg, and Google Chrome for headless PDF generation
RUN apt-get update && apt-get install -y wget gnupg2 apt-transport-https ca-certificates curl
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Run gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "server:app"]
