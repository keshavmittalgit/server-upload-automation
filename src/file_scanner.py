"""File scanning, identification and strict validation module."""

import os
from src.config import MODEL_EXTS


def validate_and_find_files(folder_path):
    """
    Scans a subfolder and strictly validates:
    1. A 3D model (.glb) file.
    2. A file named 'MAIN' or 'main' (regardless of extension, e.g. .png, .jpg, .jpeg, .glb, etc.)
    
    Returns:
        tuple: (glb_path, main_path, error_message)
        If either file is missing, error_message is returned and the folder is skipped.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None, None, "Folder does not exist or is inaccessible"

    try:
        entries = os.listdir(folder_path)
    except Exception as e:
        return None, None, f"Cannot read directory: {e}"

    glb_file = None
    main_file = None

    # Step 1: Scan all files inside the subfolder
    for item in entries:
        full_path = os.path.join(folder_path, item)
        if not os.path.isfile(full_path):
            continue

        base_name, ext = os.path.splitext(item)
        ext_lower = ext.lower()

        # Find .glb file
        if ext_lower in MODEL_EXTS and not glb_file:
            glb_file = full_path

        # Find file named 'MAIN' or 'main' (case-insensitive)
        if base_name.strip().upper() == "MAIN" and not main_file:
            main_file = full_path

    # Step 2: Strict check - both must be present
    missing = []
    if not glb_file:
        missing.append("a .glb file")
    if not main_file:
        missing.append("a 'MAIN' / 'main' file")

    if missing:
        return glb_file, main_file, f"Missing required file: {', '.join(missing)}"

    return glb_file, main_file, None


def get_subfolders(data_dir):
    """Returns naturally sorted subfolder names from the target directory."""
    if not os.path.exists(data_dir):
        return []
    
    entries = os.listdir(data_dir)
    subfolders = [d for d in entries if os.path.isdir(os.path.join(data_dir, d))]
    # Natural sort: 1, 2, 10 instead of 1, 10, 2
    subfolders.sort(key=lambda s: int(s) if s.isdigit() else s)
    return subfolders
