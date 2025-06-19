FROM python:3.12-slim-bookworm

# Change the working directory to the `app` directory
WORKDIR /app

# Copy only the files needed for dependency installation
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p static

COPY main.py .
COPY utils ./utils
COPY temp ./temp
COPY notes ./notes
COPY LICENSE .
COPY static/edit_image_handler.js ./static/
COPY static/images_handler.js ./static/
COPY static/favicon.svg ./static/

# Document default port
EXPOSE 9494

# Let users pass args like --notes_dir, --port
ENTRYPOINT ["python", "main.py"]

