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
import time
import logging
import argparse
import urllib
from datetime import datetime
from fastapi import UploadFile
from nicegui import app, ui
from pathlib import Path

# kurup
from utils.image_handler import TempImageHandler, get_image_refs, save_images
from utils.notes_handler import NotesHandler
from utils.fun import get_random_label
# from utils.walkthrough_handler import WalkthroughHandler


# logging setup
logger = logging.getLogger("kurup_logger")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():  

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s")    
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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

CURRENT_VERSION = "0.1.1"
UPDATE_BADGE = None
# Setup
BASE_DIR = Path(__file__).parent.resolve()
NOTES_DIR = BASE_DIR / args.notes_dir
TEMP_DIR = BASE_DIR / "temp"
STATIC_DIR = BASE_DIR / "static"

logger.info(f"Notes will be saved at {NOTES_DIR}")
logger.info(f"Temporary files will be saved at {TEMP_DIR}")

NOTES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# static filepaths
app.add_static_files(f"/{NOTES_DIR.name}", str(NOTES_DIR))
app.add_static_files(f"/{TEMP_DIR.name}", str(TEMP_DIR))
app.add_static_files("/static", str(STATIC_DIR))

# handlers for images and notes
temp_image_handler = TempImageHandler()
notes_handler = NotesHandler()
# walkthrough_handler = WalkthroughHandler(BASE_DIR)
note_area_labels = get_random_label("note")
heading_label = get_random_label("heading")
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
    heading_label = get_random_label("heading")
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
        logger.info("Set reference to MyNotes tab.")
        self.my_notes_reference = my_notes

    def validate_title(self, e):
        title = e.value.strip()
        if (
            title in [note["title"] for note in self.my_notes_reference.all_notes_cache]
            or len(title) > 99
            or not title
        ):
            self.save_button.disable()
        else:
            self.save_button.enable()

    def create_new_note_ui(self):
        """Create the UI for the new note tab"""
        global note_label
        self.save_button = (
            ui.button("Save", on_click=self.save_button_clicked)
            .classes("w-43")
            .props("id=save-note-button")
        )

        logger.info("Creating New Note tab")
        self.note_title = (
            ui.input(
                on_change=self.validate_title,
                placeholder="Type a unique title...",
                validation={
                    "Title too long": lambda value: len(value) <= 99,
                    "A note with this title already exists, choose a different title.": lambda value: value
                    not in [
                        note["title"]
                        for note in self.my_notes_reference.all_notes_cache
                    ],
                },
            )
            .props("maxlength=100")
            .classes("w-full")
        )

        with ui.column().classes("w-full"):
            # Add formatting toolbar
            with ui.row().classes("w-full q-mb-sm"):
                ui.button(
                    "",
                    icon="format_bold",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'bold')"
                    ),
                ).props("size=sm").tooltip("Bold (Ctrl+B)")

                ui.button(
                    "",
                    icon="format_italic",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'italic')"
                    ),
                ).props("size=sm").tooltip("Italic (Ctrl+I)")

                ui.button(
                    "",
                    icon="format_underlined",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'underline')"
                    ),
                ).props("size=sm").tooltip("Underline (Ctrl+U)")

                ui.button(
                    "",
                    icon="format_strikethrough",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'strikethrough')"
                    ),
                ).props("size=sm").tooltip("Strikethrough")

                ui.button(
                    "H1",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'h1')"
                    ),
                ).props("size=sm").tooltip("Heading 1")

                ui.button(
                    "H2",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'h2')"
                    ),
                ).props("size=sm").tooltip("Heading 2")

                ui.button(
                    "H3",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'h3')"
                    ),
                ).props("size=sm").tooltip("Heading 3")

                ui.button(
                    "{ }",
                    on_click=lambda: ui.run_javascript(
                        "toggleFormatting('noteTextarea', 'code')"
                    ),
                ).props("size=sm").tooltip("Code block")

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

        timestamp = str(int(time.time()))
        ui.add_body_html(
            f'<script src="./static/text_formatter.js?v={timestamp}"></script>'
        )
        ui.add_body_html('<script src="./static/image_handler.js"></script>')
        ui.add_body_html('<script src="./static/edit_image_handler.js"></script>')

    def update_markdown(self):
        """Update markdown preview and clean up unused temp images"""
        logger.debug("Markdown updated.")
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
                    logger.info(f"Removed temporary file which is not referenced: {img_path}")
                except Exception as e:
                    logger.error(f"Error removing temp image {img}: {e}")

    def save_button_clicked(self):
        """Save button click event"""

        if self.note_area.value == "":
            ui.notify("Nothing to save!", color="negative")
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
        logger.info(f"Saved note titled {filename}.")

        kurup_metadata = {filename: img_list}
        kurup_file_path = NOTES_DIR / f".{filename}.kurup"
        kurup_file_path.write_text(json.dumps(kurup_metadata), encoding="utf-8")
        logger.info(f"Saved kurup metadata for {filename}.")

        ui.notify(f"Saved as {filename}", color="positive")
        self._clean_all_temp_images()
        self.note_title.value = ""
        self.note_area.value = ""
        self.markdown_area.set_content("")

        if self.my_notes_reference:
            self.my_notes_reference.sort_notes()

        self.note_area.set_label(get_random_label("note"))
        set_heading_labels()

    def _clean_all_temp_images(self):
        """Clean up all temporary images"""
        for img in list(temp_image_handler.temp_images):
            try:
                img_path = TEMP_DIR / img
                if img_path.exists():
                    img_path.unlink()
                    logger.info(f"Removed temporary image file: {img_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temp image {img}: {e}")

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
            "Most recent",
            "Least recent",
            "Title (A–Z)",
            "Title (Z–A)",
        ]

        with ui.column().classes("w-full q-pa-md"):
            self.search_input = (
                ui.input(
                    placeholder="Search notes...",
                    on_change=lambda: self.on_search_input(
                        search_term=self.search_input.value
                    ),
                )
                .classes("w-full text-base")
                .props("id=search-notes")
            )
            self.notes_select = (
                ui.select(
                    options=[],
                    label="Select a note...",
                    on_change=self.on_note_selected,
                    with_input=True,
                    new_value_mode="add",
                    clearable=False,
                )
                .classes("w-full text-base")
                .props("id=select-notes use-input")
            )

            ui.button(
                "Refresh",
                on_click=lambda: self.sort_notes(sorting=self.sort_option.value),
                icon="refresh",
            ).props("id=refresh-notes")

            self.sort_option = ui.select(
                options=options,
                value="Most recent",
                on_change=lambda: self.sort_notes(sorting=self.sort_option.value),
            )
            self.sort_option.set_value("Most recent")

        self.notes_container = (
            ui.element("div").classes("w-full").props("id=notes-container")
        )
        self.refresh_notes()

    def on_search_input(self, search_term=""):
        """Handle search input - filter notes as user types"""
        if search_term is not None:
            search_term = search_term.lower()
        if not hasattr(self, "all_notes_cache"):
            return

        if search_term:
            filtered_notes = [
                note
                for note in self.all_notes_cache
                if search_term in note["title"].lower()
                or search_term in note["content"].lower()
            ]
        else:
            filtered_notes = self.all_notes_cache

        self.notes_container.clear()
        if not filtered_notes:
            with self.notes_container:
                ui.label(f"No notes found matching '{search_term}'").classes(
                    "text-h6 q-pa-md"
                )
        else:
            for note in filtered_notes:
                self._create_note_card(note)

    def refresh_notes_options(self, current_notes):
        """Refresh the notes selection dropdown options"""
        if not current_notes:
            self.notes_select.set_options([])
            return

        options = []
        self.notes_data = {}

        for note in current_notes:
            display_title = (
                note["title"]
                if note["title"] != "Untitled"
                else f"Untitled ({note['filename']})"
            )
            options.append(display_title)
            self.notes_data[display_title] = note

        self.notes_select.set_options(options)
        if options:
            self.notes_select.set_value(None)

    def on_note_selected(self):
        """Handle note selection from dropdown"""
        if (
            not self.notes_select.value
            or self.notes_select.value not in self.notes_data
        ):
            self.notes_container.clear()
            if hasattr(self, "current_notes_cache") and self.current_notes_cache:
                for note in self.current_notes_cache:
                    self._create_note_card(note)
            return
        selected_note = self.notes_data[self.notes_select.value]
        self.notes_container.clear()
        self._create_note_card(selected_note)

    def sort_notes(self, sorting=None, search_term=""):
        current_notes = notes_handler.update_notes_list(NOTES_DIR)
        options = [
            "Most recent",
            "Least recent",
            "Title (A–Z)",
            "Title (Z–A)",
        ]

        def natural_key(note):
            return [
                int(text) if text.isdigit() else text.lower()
                for text in re.split(r"([0-9]+)", note["filename"])
            ]

        if sorting is None:
            sorting = self.sort_option.value
        if sorting == options[0]:
            current_notes.sort(key=lambda note: note["modified"], reverse=True)
        elif sorting == options[1]:
            current_notes.sort(key=lambda note: note["modified"])
        elif sorting == options[2]:
            current_notes.sort(key=natural_key)
        elif sorting == options[3]:
            current_notes.sort(key=natural_key, reverse=True)
        else:
            current_notes.sort(key=lambda note: note["modified"], reverse=True)

        # self.refresh_notes(current_notes=current_notes,search_term=search_term)
        self.refresh_notes(current_notes=current_notes)
        if search_term == "":
            self.search_input.set_value(None)

    def refresh_notes(self, current_notes=None):
        """Refresh the notes list and dropdown options"""
        logger.info("Refreshing saved notes.")
        self.notes_container.clear()

        if not current_notes:
            current_notes = notes_handler.update_notes_list(NOTES_DIR)

        self.all_notes_cache = current_notes
        self.current_notes_cache = current_notes

        # Update dropdown options
        self.refresh_notes_options(current_notes)

        if not current_notes:
            with self.notes_container:
                ui.label("No notes found").classes("text-h6 q-pa-md")
            return

        for note in current_notes:
            self._create_note_card(note)

    def _create_note_card(self, note):
        """Create a card for a single note"""
        with self.notes_container:
            logger.info(f"Creating note card for {note['title']} in my notes.")
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
                edit_textarea_id = f"edit-textarea-{uuid.uuid4().hex[:8]}"
                with ui.row().classes("w-full q-mb-sm"):
                    ui.button(
                        "",
                        icon="format_bold",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'bold')"
                        ),
                    ).props("size=sm").tooltip("Bold (Ctrl/Cmd+B)")

                    ui.button(
                        "",
                        icon="format_italic",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'italic')"
                        ),
                    ).props("size=sm").tooltip("Italic (Ctrl/Cmd+I)")

                    ui.button(
                        "",
                        icon="format_underlined",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'underline')"
                        ),
                    ).props("size=sm").tooltip("Underline (Ctrl/Cmd+U)")

                    ui.button(
                        "",
                        icon="format_strikethrough",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'strikethrough')"
                        ),
                    ).props("size=sm").tooltip("Strikethrough")

                    ui.button(
                        "H1",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'h1')"
                        ),
                    ).props("size=sm").tooltip("Heading 1")

                    ui.button(
                        "H2",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'h2')"
                        ),
                    ).props("size=sm").tooltip("Heading 2")

                    ui.button(
                        "H3",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'h3')"
                        ),
                    ).props("size=sm").tooltip("Heading 3")

                    ui.button(
                        "{ }",
                        on_click=lambda id=edit_textarea_id: ui.run_javascript(
                            f"toggleFormatting('{id}', 'code')"
                        ),
                    ).props("size=sm").tooltip("Code block")

                edit_area = (
                    ui.textarea(value=note["content"], on_change=self.edit_area_change)
                    .classes("w-full")
                    .style("min-height: 100px")
                    .props(f"id={edit_textarea_id}")
                )

                with ui.row().classes("w-full justify-start q-mt-md"):
                    ui.button(
                        "Save Changes",
                        color="primary",
                        on_click=lambda: self.save_edits_click(edit_area, note),
                    )

    def delete_note_click(self, note):
        """Handle delete note button click"""
        notes_handler.delete_note(note, NOTES_DIR, self.sort_notes)

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
        logger.info(f"Downloaded note {note['filename']}")


def check_for_update():
    global UPDATE_BADGE
    try:
        with urllib.request.urlopen(
            "https://api.github.com/repos/davistdaniel/kurup/releases/latest"
        ) as response:
            data = json.loads(response.read())
            latest_version = data["tag_name"].lstrip("v")
            if latest_version != CURRENT_VERSION:
                ui.notify(
                    f"A new version of kurup is available: {latest_version}. Current version: {CURRENT_VERSION}"
                )
                if UPDATE_BADGE:
                    UPDATE_BADGE.set_text("!")
                    UPDATE_BADGE.style("display: block")
            else:
                ui.notify("You're using the latest version of kurup.", color="positive")
                if UPDATE_BADGE:
                    UPDATE_BADGE.style("display: none")
    except Exception as e:
        ui.notify("Error checking for updates.", color="negative")
        logger.error(f"Failed to check for updates: {e}")


def create_ui():
    """Create the main UI for the application"""
    global quote_label, UPDATE_BADGE
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
        ui.label("Welcome to kurup.").classes("text-2xl text-bold")
        ui.switch("⏾", value=False, on_change=toggle_dark_mode).props(
            "id=dark-mode-switch"
        )

    quote_label = ui.label(f"{heading_label}").classes("text-l text-italic")

    with ui.header().classes("bg-[#e9f5d0] dark:bg-[#3c542d]"):
        ui.image("./static/logo.webp").classes("w-64").props("id=kurup-logo")
        with ui.column():
            with (
                ui.button("", on_click=check_for_update, icon="system_update_alt")
                .classes("w-10 h-10")
                .tooltip("Check for a newer version of kurup")
            ):
                UPDATE_BADGE = (
                    ui.badge("", color="red").props("floating").style("display: none")
                )

            ui.button(
                "",
                on_click=lambda: ui.navigate.to(
                    "https://github.com/davistdaniel/kurup", new_tab=True
                ),
                icon="code",
            ).classes("w-10 h-10").tooltip("View on GitHub")

    with ui.tabs().classes("w-96") as tabs:
        new_note_tab = ui.tab("New").props("id=new-note-tab")
        my_notes_tab = ui.tab("Saved").props("id=my-notes-tab")

    with ui.tab_panels(tabs, value=new_note_tab).classes("w-full"):
        with ui.tab_panel(new_note_tab):
            new_note.create_new_note_ui()

        with ui.tab_panel(my_notes_tab):
            my_notes.create_my_notes_ui()


# walkthrough_handler.setup_walkthrough()

# create the UI and start the app
logger.info("Starting kurup: a simple markdown-based notes app")
create_ui()
# check_for_update()
ui.run(port=args.port, favicon=STATIC_DIR / "favicon.svg", title="kurup")
