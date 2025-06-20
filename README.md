# Welcome to kurup!
<div align="center">
  <img src="./static/logo.webp" alt="kurup logo" width="400"/>
  <br/>
  <br/>
  
  ![License](https://img.shields.io/badge/license-GPLv3.0-blue.svg)
  ![Version](https://img.shields.io/badge/version-0.1.1-orange.svg)
  ![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
  
  *A simple, markdown-based note-taking application*
</div>

## ✨ Features

- **Markdown Support** - Write notes using simple markdown formatting
- **Live Preview**: See your formatted content instantly as you type.
- **Quick Format** : Quick format buttons for easier writing in markdown format.
- **Tags** : Organize your notes with tags.
- **Note Management** : View, edit, delete and download saved notes from within the app.
- **Image Embedding** - Paste images directly from your clipboard
- **Search Functionality** - Filter notes with a search term.
- **Local Storage** - All notes are stored locally in plain-text, no database required.
- **Import** - Simply place markdown notes in kurup's notes folder
- **Export** - Download notes as zip files with images included
- **Simple Interface** - Simple, no-frills and lightweight

If you find this project helpful, please consider giving it a ⭐ to show your support.

## 📸 Screenshots

<!-- Add your screenshots here -->
<div align="center">
  <img src="./static/screenshot.webp" alt="kurup logo" width="1000"/>
</div>

## 💻 Usage

### Creating a Note

1. Open the "New" tab
2. Enter a title (optional)
3. Write your note content using markdown syntax and quick format buttons
    - Quick format :  Bold, Italic, Underline, Strikethrough, H1, H2, H3, code
4. Press the "Save" button

### Markdown Syntax Guide

| Syntax              | Output                   | Example                    |
|---------------------|--------------------------|----------------------------|
| `**bold**`          | **bold**                 | `**This is bold**`         |
| `*italic*`          | *italic*                 | `*This is italic*`         |
| `<u>underline</u>`     | <u>underline</u>  | `<u>This is underlined</u>`   |
| `<s>strike</s>`        | ~~strike~~               | `<s>This is struck</s>`       |
| `# Heading 1`       | Heading 1                | `# Heading 1`              |
| `## Heading 2`      | Heading 2                | `## Heading 2`             |
| `### Heading 3`     | Heading 3                | `### Heading 3`            |
| `` `inline code` `` | `inline code`            | `` `code` ``               |

For code blocks use : 

```markdown
```python
def hello_world():
  print('This is kurup.')
``` 
which renders to:

```python
def hello_world():
  print('This is kurup.')
```

### Embedding Images

Simply paste images from your clipboard directly into the note area. Images are automatically:
- Displayed in the preview
- Stored locally with your note
- Included when you export the note

#### Demo :

<div align="center">
  <img src="./static/gif1.gif" alt="notes-gif" width="1000"/>
</div>


### Managing Notes

In the "Saved" tab you can:
- **Search** - Search notes and its contents
- **Select** - Select saved notes to view from a dropdown
- **Preview** - Read your notes with formatted markdown, a small preview is also shown when hovered.
- **Raw** - View the raw markdown
- **Edit** - Make changes to existing notes
- **Delete** - Remove notes you no longer need (irreversible!)
- **Download** - Export individual notes as zip files (includes images)

#### Demo :

<div align="center">
  <img src="./static/gif2.gif" alt="managing_notes" width="1000"/>
</div>


## 🚀 Getting Started

This project is under active development. Please make a separate backup of your notes.

### Using Docker (Recommended)

#### 1. Make a directory for kurup and the notes

```bash
mkdir -p kurup/notes
mkdir -p kurup/temp
cd kurup
```

####  2. Make a docker-compose.yml file in the kurup folder with the following contents:
```bash
services:
  kurup:
    image: ghcr.io/davistdaniel/kurup:latest
    container_name: kurup
    ports:
      - "9494:9494"
    volumes:
      - ./notes:/app/notes # make sure the notes folder exists before running the container‚ otherwise the folder will be owned by root.
      - ./temp:/app/temp # make sure the notes temp folder exists
      # you can also use a custom path for the notes directory
      #- /home/yourusername/Documents/notes:/app/notes                        
    command: ["--notes_dir", "/app/notes"]
    user: "1000:1000" # set to your own local UID:GID, run `id -u` to find UID and run `id -g` to find GID
```

#### 3. Start the container

```bash
sudo docker compose up -d
```

#### 4. Open your web browser and navigate to:

http://localhost:9494

### Using Python (Tested on Linux, MacOS)

#### Prerequisites

- Python 3.11 or higher

```bash
# Clone the repository
git clone https://github.com/davistdaniel/kurup
cd kurup

# Install dependencies
python -m pip install "nicegui>=2.17.0"

# Run the application
python main.py

# Open your web browser and navigate to:
http://localhost:9494
```



## 🔄 Updating

> [!NOTE]  
> It is recommended to make a backup of your `notes` folder before updating.

### Python
```bash
# Pull the latest changes from the repository
git pull origin main

# (Optional) Reinstall dependencies in case of updates
python -m pip install -r requirements.txt

# Run the updated application
python main.py

# Open your web browser and navigate to:
http://localhost:9494
```

### Docker
```bash
# restart the container
sudo docker compose down
# pull the latest image
sudo docker compose pull
# start the container
sudo docker compose up -d

# Open your web browser and navigate to:
http://localhost:9494
```

## ⚙️ Configuration

Run with custom options:

```bash
python main.py --notes_dir 'custom_directory' --port 8080
```

Command-line arguments:
- `--notes_dir`: Specify where to store notes (default: "notes")
- `--port`: Set the app server port (default: 9494)

## 🔧 Project Structure

```
kurup/
├── main.py           # Main application file
├── static/           # Static assets (logo, favicon, JS etc.)
├── notes/            # Notes storage directory, contains an example note
└── utils/
    ├── fun.py                # Random label generation
    ├── image_handler.py      # Image processing module
    └── notes_handler.py      # Note management module
```

## 📝 Under the hood

kurup uses a simple approach to note management:

1. Notes are stored as markdown files in the `notes` directory
2. When images are pasted to clipboard, they are stored in the `temp` directory.
3. Images are copied from the `temp` directory to the `notes` directory when the note is saved.
4. A hidden `.kurup` metadata file tracks image references for each note.
5. The web interface is built with NiceGUI.

## 🤝 Contributing

Feel free to fork and contribute! Feature ideas or bug fixes are always welcome.

## 📜 License
This project is licensed under the terms of the GNU General Public License v3.0.

