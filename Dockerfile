FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p static

COPY main.py .
COPY utils ./utils
COPY notes ./notes
COPY LICENSE .
COPY static/edit_image_handler.js ./static/
COPY static/image_handler.js ./static/
COPY static/text_formatter.js ./static/
COPY static/favicon.svg ./static/
COPY static/logo.webp ./static/

EXPOSE 9494

ENTRYPOINT ["python", "main.py"]

