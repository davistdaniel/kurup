# kurup - A simple, markdown-based note taking application
# Copyright (C) 2025 Davis Thomas Daniel
#
# This file is part of kurup.
#
# kurup is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kurup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kurup. If not, see <https://www.gnu.org/licenses/>.


import uuid
import shutil
import json
import re
import logging
import sys
import argparse
from datetime import datetime
from fastapi import UploadFile
from nicegui import app, ui
from pathlib import Path

# kurup
from utils.image_handler import TempImageHandler, get_image_refs, save_images
from utils.notes_handler import NotesHandler
from utils.fun import get_random_label
#from utils.walkthrough_handler import WalkthroughHandler

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    force=True,
)

parser = argparse.ArgumentParser(
    description="kurup : a simple markdown-based note taking app"
)
parser.add_argument(
    "--notes_dir",
    type=str,
    default="notes",
    help="directory where notes and files should be saved",
)

parser.add_argument(
    "--port",
    type=int,
    default=9494,
    help="Port to serve the app",
)


args = parser.parse_args()


# Setup
BASE_DIR = Path(__file__).parent.resolve()
NOTES_DIR = BASE_DIR / args.notes_dir
TEMP_DIR = BASE_DIR / "temp"
STATIC_DIR = BASE_DIR / "static"

logging.info(f"Notes will be saved at {NOTES_DIR}")
logging.info(f"Temporary files will be saved at {TEMP_DIR}")

NOTES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# static filepaths
app.add_static_files(f"/{NOTES_DIR.name}", str(NOTES_DIR))
app.add_static_files(f"/{TEMP_DIR.name}", str(TEMP_DIR))
app.add_static_files("/static", str(STATIC_DIR))

# handlers for images and notes
temp_image_handler = TempImageHandler()
notes_handler = NotesHandler()
#walkthrough_handler = WalkthroughHandler(BASE_DIR)
# global, so that it can be updated 
note_area_labels = get_random_label('note')
heading_label = get_random_label('heading')
quote_label = None 

# pasted images handling
@app.post("/upload_image")
async def upload_image(file: UploadFile):
    """Handle image uploads and store them in temp directory"""
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = TEMP_DIR / file_name
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    temp_image_handler.temp_images.append(file_name)
    return {"url": f"/{TEMP_DIR.name}/{file_name}"}

def set_heading_labels():
    global quote_label
    heading_label = get_random_label('heading')
    quote_label.set_text(heading_label)

# new note tab
class NewNote:
    """Class to handle creation of new notes"""

    def __init__(self):
        self.note_title = None
        self.note_area = None
        self.markdown_area = None
        self.save_button = None
        self.my_notes_reference = None

    def set_my_notes_reference(self, my_notes):
        """Set reference to MyNotes to allow refreshing list after save"""
        logging.info("Set reference to MyNotes tab.")
        self.my_notes_reference = my_notes

    def create_new_note_ui(self):
        """Create the UI for the new note tab"""
        global note_label
        self.save_button = (
            ui.button("Save", on_click=self.save_button_clicked)
            .classes("w-43")
            .props("id=save-note-button")
            
        )

        logging.info("Creating New Note tab")
        self.note_title = ui.input(placeholder="Title").classes("w-full")

        with ui.column().classes("w-full"):
            self.note_area = (
                ui.textarea(label=note_area_labels, on_change=self.update_markdown)
                .classes("w-full")
                .props("id=noteTextarea")
            )

        with ui.column().classes("w-full"):
            with ui.element("div").classes("w-full"):
                self.markdown_area = (
                    ui.markdown("").classes("w-full").props("id=markdownPreview")
                )

        # script for pasted images handling
        ui.add_body_html('<script src="./static/image_handler.js"></script>')
        ui.add_body_html('<script src="./static/edit_image_handler.js"></script>')

    def update_markdown(self):
        """Update markdown preview and clean up unused temp images"""
        logging.debug("Markdown updated.")
        self.markdown_area.set_content(self.note_area.value)

        temp_image_handler.temp_image_refs = get_image_refs(
            self.note_area.value, TEMP_DIR
        )

    def _clean_unused_temp_images(self):
        """Remove temporary images that are no longer referenced"""
        for img in list(temp_image_handler.temp_images):
            if img not in temp_image_handler.temp_image_refs:
                try:
                    img_path = TEMP_DIR / img
                    if img_path.exists():
                        img_path.unlink()
                    temp_image_handler.temp_images.remove(img)
                    logging.info(f"Removed temporary file not referenced: {img_path}")
                except Exception as e:
                    logging.error(f"Error removing temp image {img}: {e}")

    def save_button_clicked(self):
        """Save button click event"""

        if self.note_area.value == "":
            ui.notify("Nothing to save!")
            return

        if self.note_title.value:
            filename = f"{self.note_title.value.replace(' ', '_')}.md"
        else:
            filename = f"untitled_{datetime.now().strftime('%d%m%Y%H%M%S')}.md"

        # save note content and move images
        updated_content, img_list = save_images(
            self.note_area.value, NOTES_DIR, TEMP_DIR
        )

        note_path = NOTES_DIR / filename
        note_path.write_text(updated_content, encoding="utf-8")
        logging.info(f"Saved note titled {filename}.")

        kurup_metadata = {filename: img_list}
        kurup_file_path = NOTES_DIR / f".{filename}.kurup"
        kurup_file_path.write_text(json.dumps(kurup_metadata), encoding="utf-8")
        logging.info(f"Saved kurup metadata for {filename}.")

        ui.notify(f"Saved as {filename}")
        self._clean_all_temp_images()
        self.note_title.value = ""
        self.note_area.value = ""
        self.markdown_area.set_content("")

        if self.my_notes_reference:
            self.my_notes_reference.sort_notes()

        self.note_area.set_label(get_random_label('note'))
        set_heading_labels()

    def _clean_all_temp_images(self):
        """Clean up all temporary images"""
        for img in list(temp_image_handler.temp_images):
            try:
                img_path = TEMP_DIR / img
                if img_path.exists():
                    img_path.unlink()
                    logging.info(f"Removed temporary image file: {img_path}")
            except Exception as e:
                logging.error(f"Error cleaning up temp image {img}: {e}")

        temp_image_handler.temp_images = []


# my note tab
class MyNotes:
    """Class to handle viewing and managing existing notes"""

    def __init__(self):
        self.notes_container = None
        self.edit_area = None

    def create_my_notes_ui(self):
        """Create the UI for the my notes tab"""

        options = [
            'Most recent',
            'Least recent',
            'Title (A–Z)',
            'Title (Z–A)',
        ]
        with ui.column().classes("w-full q-pa-md"):
            self.search_input = ui.input(placeholder="Type to search notes...",on_change=lambda: self.refresh_notes(search_term=self.search_input.value)).classes("w-full").props("id=search-notes")
            ui.button(
                "Refresh",
                on_click=lambda: self.sort_notes(sorting=self.sort_option.value,search_term=self.search_input.value),
                icon="refresh",
            ).props("id=refresh-notes")
        
            self.sort_option = ui.select(options=options,value='Most recent',on_change=lambda: self.sort_notes(sorting=self.sort_option.value))
            self.sort_option.set_value('Most recent')

        self.notes_container = ui.element("div").classes("w-full").props("id=notes-container")
        self.refresh_notes()

    def sort_notes(self,sorting=None,search_term=""):
        current_notes = notes_handler.update_notes_list(NOTES_DIR)
        options = [
            'Most recent',
            'Least recent',
            'Title (A–Z)',
            'Title (Z–A)',
        ]
        def natural_key(note):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split(r'([0-9]+)', note['filename'])]
        
        if sorting is None:
            sorting = self.sort_option.value
        if sorting==options[0]:
            current_notes.sort(key=lambda note: note['modified'],reverse=True)
        elif sorting==options[1]:
            current_notes.sort(key=lambda note: note['modified'])
        elif sorting==options[2]:
            current_notes.sort(key=natural_key)        
        elif sorting==options[3]:
            current_notes.sort(key=natural_key,reverse=True)
        else:
            current_notes.sort(key=lambda note: note['modified'],reverse=True)
        
        self.refresh_notes(current_notes=current_notes,search_term=search_term)

    def refresh_notes(self, current_notes=None,search_term=""):
        """Refresh the notes list with search"""
        logging.info("Refreshing saved notes.")
        self.notes_container.clear()
        if not current_notes:
            current_notes = notes_handler.update_notes_list(NOTES_DIR)

        if not current_notes:
            with self.notes_container:
                ui.label("No notes found").classes("text-h6 q-pa-md")
                return

        if search_term:
            search_term = search_term.lower()
            current_notes = [
                note
                for note in current_notes
                if search_term in note["title"].lower()
                or search_term in note["content"].lower()
            ]

            if not current_notes:
                with self.notes_container:
                    ui.label(f"No notes found matching '{search_term}'").classes(
                        "text-h6 q-pa-md"
                    )
                return

        for note in current_notes:
            self._create_note_card(note)

    def _create_note_card(self, note):
        """Create a card for a single note"""
        with self.notes_container:
            logging.info("Creating note card in my notes.")
            with ui.card().classes("q-mb-md"):
                with ui.card_section():
                    ui.label(note["title"]).classes("text-h6")
                    ui.label(
                        f"Modified: {note['modified'].strftime('%Y-%m-%d %H:%M')}"
                    ).classes("text-caption")

                note_content_id = f"note-content-{uuid.uuid4()}"

                with ui.card_section().classes("w-full").props(f"id={note_content_id}"):
                    self._create_note_tabs(note)

                with ui.card_actions():
                    ui.button(
                        "Delete",
                        color="negative",
                        on_click=lambda: self.delete_note_click(note),
                    )
                    ui.button(
                        "Download",
                        color="primary",
                        on_click=lambda: self.download_note_click(
                            note, NOTES_DIR, TEMP_DIR
                        ),
                    )

    def _create_note_tabs(self, note):
        """Create the preview/raw/edit tabs for a note"""
        with ui.tabs().classes("w-96") as note_tabs:
            preview_tab = ui.tab("Preview")
            raw_tab = ui.tab("Raw")
            edit_tab = ui.tab("Edit")

        with ui.tab_panels(note_tabs, value=preview_tab).classes("w-full"):
            with ui.tab_panel(preview_tab):
                ui.markdown(note["content"])

            with ui.tab_panel(raw_tab):
                ui.code(note["content"], language="markdown").classes("w-full")

            with ui.tab_panel(edit_tab):
                edit_area = (
                    ui.textarea(value=note["content"], on_change=self.edit_area_change)
                    .classes("w-full")
                    .style("min-height: 100px")
                    .props("id=EditNoteTextarea")
                )

                with ui.row().classes("w-full justify-start q-mt-md"):
                    ui.button(
                        "Save Changes",
                        color="primary",
                        on_click=lambda: self.save_edits_click(edit_area, note),
                    )

    def delete_note_click(self, note):
        """Handle delete note button click"""
        notes_handler.delete_note(note, NOTES_DIR,self.sort_notes)

    def save_edits_click(self, edit_area, note):
        """Handle save edits button click"""
        notes_handler.save_note_edits(
            temp_image_handler, edit_area.value, note, NOTES_DIR, TEMP_DIR
        )
        self.sort_notes(sorting=self.sort_option.value)

    def edit_area_change(self):
        """Handle edit area change event"""
        if hasattr(self, "edit_area") and self.edit_area:
            temp_image_handler.temp_image_refs = get_image_refs(
                self.edit_area.value, TEMP_DIR
            )

    def download_note_click(self, note, NOTES_DIR, TEMP_DIR):
        notes_handler.download_note(note, NOTES_DIR, TEMP_DIR)
        logging.info(f"Downloaded note {note['filename']}")

def create_ui():
    """Create the main UI for the application"""
    global quote_label
    my_notes = MyNotes()
    new_note = NewNote()

    # this is needed for refreshing the my_notes tab when a new note is saved
    new_note.set_my_notes_reference(my_notes)
    dark = ui.dark_mode()
    
    def toggle_dark_mode(e):
        if e.value:
            dark.enable()
        else:
            dark.disable()

    with ui.grid(columns=2):
        ui.label('Welcome to kurup.').classes("text-2xl text-bold")
        ui.switch("⏾", value=False, on_change=toggle_dark_mode).props("id=dark-mode-switch")

    quote_label = ui.label(f'{heading_label}').classes("text-l text-italic")


    with ui.header().classes("bg-[#e9f5d0] dark:bg-[#3c542d]"):
        ui.image("./static/logo.webp").classes("w-64").props("id=kurup-logo")
        with ui.link(target='https://github.com/davistdaniel/kurup', new_tab=True):
            ui.image('https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png') \
                .classes("w-8").tooltip("View on GitHub")

    with ui.tabs().classes("w-96") as tabs:
        new_note_tab = ui.tab("New").props("id=new-note-tab")
        my_notes_tab = ui.tab("Saved").props("id=my-notes-tab")

    with ui.tab_panels(tabs, value=new_note_tab).classes("w-full"):
        with ui.tab_panel(new_note_tab):
            new_note.create_new_note_ui()

        with ui.tab_panel(my_notes_tab):
            my_notes.create_my_notes_ui()
    
#walkthrough_handler.setup_walkthrough()

# create the UI and start the app
logging.info("Starting kurup: a simple markdown-based notes app")
create_ui()
ui.run(port=args.port,favicon=STATIC_DIR / 'favicon.ico',title='kurup')


