import re
import shutil
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    force=True,
)

def get_image_refs(note_area_val, directory):
    """    
    Extracts image references from markdown text that point to a specific directory.

    Parameters
    ----------
    note_area_val : str
        The markdown text containing image references.
    directory : str
        The directory to search for in image references.

    Returns
    -------
    refs : list of str
        A list of image filenames referenced in the markdown text, with the directory portion removed.
    """
    pattern = rf"!\[.*?\]\((\/{directory}\/[^)]+)\)"
    refs = [match.replace(f'/{directory}/', '') for match in re.findall(pattern, note_area_val)]
    return refs

def save_images(current_note_area_val, notes_dir, temp_dir):
    """
    Saves images from a temp_dir to a notes_dir and updates image references in the entered text.

    Parameters
    ----------
    current_note_area_val : str
        The text containing image references in markdown format.
    notes_dir : str
        The directory where images should be permanently saved.
    temp_dir : str
        The directory where images are temporarily saved.

    Returns
    -------
    updated_text : str
        The text with updated image references pointing to the permanent location.
    img_list : list of str
        A list of filenames of the images that were moved.
    """
    pattern = rf"!\[(.*?)\]\(/({temp_dir.name})/([^)]+)\)"
    img_list = []
    updated_text = current_note_area_val

    for match in re.finditer(pattern, current_note_area_val):
        alt_text = match.group(1)
        #temp_subdir = match.group(2) # same as temp_dir
        filename = match.group(3)

        source = temp_dir / filename
        destination = notes_dir / filename

        logging.info(f"Moving {filename} from {source} to {destination}")
        shutil.move(source, destination)

        old_ref = match.group(0)
        new_ref = f"![{alt_text}](/{notes_dir.name}/{filename})"

        img_list.append(filename)
        updated_text = updated_text.replace(old_ref, new_ref)

    return updated_text, img_list

class TempImageHandler():
    def __init__(self):
        self.temp_images = []
        self.temp_image_refs = []