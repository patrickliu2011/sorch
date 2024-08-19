import glob
import os

def get_file_paths(root_dir: str):
    root_dir = os.path.abspath(os.path.expanduser(root_dir))
    paths = glob.iglob(os.path.join(root_dir, "**/*"), recursive=True)
    paths = list(filter(os.path.isfile, paths))
    return paths

INVALID_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "gif", "docx", "xlsx", "pem", "pub"}
VALID_EXTENSIONS = {"txt", "py", "json", "md", "html", "java"}

def is_unicode_file(path: str):
    try:
        with open(path, 'r') as f:
            f.read()
    except UnicodeDecodeError:
        return False
    return True

def is_indexable_file(
        path: str, 
        valid_extensions: set[str] = VALID_EXTENSIONS, 
        invalid_extensions: set[str] = INVALID_EXTENSIONS):
    if not os.path.isfile(path): # directory
        return False
    if os.path.getsize(path) == 0: # empty
        return False
    ext = os.path.splitext(path)[-1][1:].lower()
    if ext in invalid_extensions:
        return False
    if ext in valid_extensions:
        return True
    return False # is_unicode_file(path)