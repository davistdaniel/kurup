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

from datetime import datetime
import json
import re
from nicegui import ui
import zipfile
import threading
import time
import logging

# kurup
from utils.image_handler import get_image_refs, save_images

# logging
logger = logging.getLogger("kurup_logger")


def delete_note_and_images(note, notes_dir):
    """    
    Deletes a note file, associated images, metadata from the specified directory.

    Parameters
    ----------
    note : dict
        A dictionary containing information about the note. The dictionary should include:
        - 'filename' (str): The filename of the note.
        - 'kurup_ref' (list or None): A reference to Kurup metadata, if present.
        - 'image_refs' (list of str): A list of image filenames associated with the note.
    notes_dir : str
        The directory where the note file, images, and metadata are stored.

    Returns
    -------
    bool
        True or False based on if the deletion was successful.
    """

    try:
        note_path = notes_dir / note['filename']
        note_path.unlink(missing_ok=True)

        if note.get('kurup_ref'):
            for img in note.get('image_refs', []):
                img_path = notes_dir / img
                img_path.unlink(missing_ok=True)

        kurup_path = notes_dir / f".{note['filename']}.kurup"
        kurup_path.unlink(missing_ok=True)
        logger.info(f"Deleted {note['filename']}")
        return True

    except Exception as e:
        print(f"Error deleting note {note['filename']}: {e}")
        return False
    
def create_zip_archive(note, notes_dir, temp_dir):
    """
    Creates a zip archive of a note and its associated images.

    Parameters
    ----------
    note : dict
        A dictionary containing information about the note. The dictionary should include:
        - 'filename' (str): The filename of the note.
        - 'image_refs' (list of str): A list of image filenames associated with the note.
    notes_dir : str
        The directory where the note file and images are located.
    temp_dir : str
        The directory where the zip archive should be saved temporarily.

    Returns
    -------
    zip_path : str
        The path to the created zip archive.
    zip_url : str
        A URL-style reference to the zip archive's location.
    """

    zip_filename = f"{note['filename'].replace('.md', '')}.zip"
    zip_path = temp_dir / zip_filename

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        note_path = notes_dir / note['filename']
        zipf.write(note_path, arcname=note['filename'])

        for img in note.get('image_refs', []):
            img_path = notes_dir / img
            if img_path.exists():
                zipf.write(img_path, arcname=img)

    return zip_path, f'/temp/{zip_filename}'

class NotesHandler():
    """
    A class for managing a collection of notes, including functionality to update note lists,
    delete notes, download notes as zip files, and save edited notes.

    Attributes
    ----------
    note_list : list of dict
        A list of dictionaries, each containing metadata and content of a note.

    Methods
    -------
    update_notes_list(notes_dir)
        Updates the note list by scanning the specified directory for markdown files.
    delete_note(note, notes_dir, callback=None)
        Deletes a specific note and its associated images, with an optional callback to execute after deletion.
    download_note(note, notes_dir, temp_dir)
        Downloads a note as a zip archive, including the note content and its associated images.
    save_note_edits(temp_image_handler, edit_area_val, note, notes_dir, temp_dir)
        Saves edited content for a note, including handling images and updating metadata.
    """
    
    def __init__(self):
        self.note_list = []
    
    def update_notes_list(self, notes_dir):
        """
        Scans the specified directory for markdown files and updates the note list with metadata.

        Parameters
        ----------
        notes_dir : str
            The directory where the markdown notes are stored.

        Returns
        -------
        list of dict
            A list of dictionaries containing metadata and content for each note.
        """
        self.note_list = []

        for filepath in notes_dir.iterdir():
            if filepath.suffix == '.md' and not filepath.name.startswith('.'):
                filename = filepath.name
                kr_filepath = notes_dir / f".{filename}.kurup"

                try:
                    content = filepath.read_text(encoding='utf-8')
                    #lines = content.splitlines()

                    title = filepath.stem.replace('_', ' ')
                    # if lines and lines[0].startswith('# '):
                    #     title = lines[0][2:]

                    modified_time = datetime.fromtimestamp(filepath.stat().st_mtime)

                    pattern = rf"!\[.*?\]\(/{notes_dir.name}/([^)]+)\)"
                    image_refs = list(set(re.findall(pattern, content)))

                    try:
                        kurup_data = json.loads(kr_filepath.read_text(encoding='utf-8'))
                        logger.info(f"kurup metadata file read from {str(kr_filepath.name)}")
                    except FileNotFoundError:
                        logger.warning(f"kurup metadata file not found at {str(kr_filepath.name)}")
                        logger.info(f"Creating kurup metadata file at {str(kr_filepath.name)}")
                        kurup_metadata = {filename: image_refs}
                        kr_filepath.write_text(json.dumps(kurup_metadata), encoding="utf-8")
                        kurup_data = json.loads(kr_filepath.read_text(encoding='utf-8'))

                    self.note_list.append({
                        'filename': filename,
                        'title': title,
                        'modified': modified_time,
                        'content': content,
                        'image_refs': image_refs,
                        'kurup_ref': kurup_data.get(filename)
                    })

                except Exception as e:
                    print(f"Error processing note {filename}: {e}")

        return self.note_list
    
    def delete_note(self, note, notes_dir, callback=None):
        """
        Deletes a note and its associated images from the specified directory.
        
        Parameters
        ----------
        note : dict
            The note to be deleted, containing 'filename', 'title', 'image_refs', and 'kurup_ref'.
        notes_dir : str
            The directory where the note and associated files are stored.
        callback : callable, optional
            An optional callback function to execute after the note is deleted.
        """
        def confirm_delete():
            if delete_note_and_images(note, notes_dir):
                ui.notify(f"Deleted {note['filename']}")
                if callback:
                    callback()
                logging.info(f"Deleted {note['filename']}")
            else:
                ui.notify(f"Failed to delete {note['filename']}", color='negative')
            dialog.close()

        
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                ui.label(f"Delete '{note['title']}'?").classes('text-h6 q-pa-md')
                if note['kurup_ref']:
                    ui.label(f"This will permanently delete the note and {len(note['image_refs'])} associated images.").classes('q-pa-md')
                else:
                    ui.label("This will permanently delete the note.")
                with ui.card_actions().classes('justify-end'):
                    ui.button('Cancel', on_click=dialog.close)
                    ui.button('Delete', color='negative', on_click=confirm_delete)
        dialog.open()

    def download_note(self, note, notes_dir, temp_dir):
        """
        Downloads a note and its associated images as a zip archive.

        Parameters
        ----------
        note : dict
            The note to be downloaded, containing 'filename' and 'image_refs'.
        notes_dir : str
            The directory where the note and images are stored.
        temp_dir : str
            The directory where the zip archive will be temporarily saved.
        """
        zip_path, zip_url = create_zip_archive(note, notes_dir, temp_dir)
        ui.download(zip_url)


        def cleanup():
            time.sleep(10)
            try:
                if zip_path.exists():
                    zip_path.unlink()
                    print(f"Deleted zip: {zip_path}")
            except Exception as e:
                print(f"Error deleting zip file: {e}")

        threading.Thread(target=cleanup, daemon=True).start()

    def save_note_edits(self, temp_image_handler, edit_area_val, note, notes_dir, temp_dir):

        """
        Saves the edited content of a note, including handling images and updating associated metadata.

        Parameters
        ----------
        temp_image_handler : object
            An object responsible for managing temporary image references.
        edit_area_val : str
            The updated content of the note, including any changes to image references.
        note : dict
            The note being edited, containing 'filename', 'image_refs', and other metadata.
        notes_dir : str
            The directory where the note and associated images are stored.
        temp_dir : str
            The directory where temporary images are stored.
        """

        try:
            old_image_refs = note['image_refs']
            temp_image_handler.temp_image_refs = get_image_refs(edit_area_val, temp_dir)

            for img_ref in temp_image_handler.temp_image_refs:
                img_file = img_ref.replace(f'/{temp_dir.name}/', '')
                img_path = temp_dir / img_file
                if not img_path.exists():
                    print(f"Warning: Referenced temp file does not exist: {img_path}")
                    edit_area_val = edit_area_val.replace(img_ref, '')

            updated_content, img_list = save_images(edit_area_val, notes_dir, temp_dir)

            note_path = notes_dir / note['filename']
            note_path.write_text(updated_content, encoding='utf-8')

            new_image_pattern = rf'!\[.*?\]\(/({notes_dir.name})/([^)]+)\)'
            new_image_refs = [match[1] for match in re.findall(new_image_pattern, updated_content)]

            for img in old_image_refs:
                if img not in new_image_refs:
                    img_path = notes_dir / img
                    try:
                        if img_path.exists():
                            img_path.unlink()
                    except Exception as e:
                        print(f"Error removing unused image {img}: {e}")

            kr_filepath = notes_dir / f".{note['filename']}.kurup"
            try:
                kurup_file_dict = json.loads(kr_filepath.read_text(encoding='utf-8'))
            except FileNotFoundError:
                kurup_file_dict = {}

            kurup_file_dict[note['filename']] = new_image_refs
            kr_filepath.write_text(json.dumps(kurup_file_dict), encoding='utf-8')

            # delete temp images afterwards, needs tests.
            for img in temp_image_handler.temp_images:
                img_path = temp_dir / img
                try:
                    if img_path.exists():
                        img_path.unlink()
                except Exception as e:
                    print(f"Error cleaning up temp image {img}: {e}")

            temp_image_handler.temp_images = []

            ui.notify(f"Saved changes to {note['filename']}")
            logging.info(f"Saved changes to {note['filename']}")

        except Exception as e:
            ui.notify(f"Error saving changes: {str(e)}", color='negative')
            print(f"Detailed error: {e}")

