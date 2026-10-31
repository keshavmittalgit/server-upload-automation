"""File scanning, identification and strict validation module."""

import os
from src.config import MAIN_IMAGE_EXTS, MODEL_EXTS


def validate_and_find_files(folder_path):
    """
    Scans a subfolder and validates:
    1. Model file (.glb) exists.
    2. MAIN file (MAIN.png, MAIN.jpg, MAIN.jpeg, etc.) exists.
    
    Returns:
        tuple: (glb_path, main_path, error_message)
        If any file is missing, error_message is populated and paths may be None.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return None, None, "Folder does not exist or is inaccessible"

    try:
        entries = os.listdir(folder_path)
    except Exception as e:
        return None, None, f"Cannot read directory: {e}"

    glb_file = None
    main_file = None

    # Pass 1: Exact matches
    for item in entries:
        full_path = os.path.join(folder_path, item)
        if not os.path.isfile(full_path):
            continue

        base, ext = os.path.splitext(item)
        ext_lower = ext.lower()

        if base.upper() == "MAIN" and ext_lower in MAIN_IMAGE_EXTS:
            main_file = full_path

        if ext_lower in MODEL_EXTS:
            glb_file = full_path

    # Pass 2: Fuzzy match for MAIN if needed (e.g. main_view.png)
    if not main_file:
        for item in entries:
            full_path = os.path.join(folder_path, item)
            if not os.path.isfile(full_path) or full_path == glb_file:
                continue
            base, ext = os.path.splitext(item)
            if "MAIN" in base.upper() and ext.lower() in MAIN_IMAGE_EXTS:
                main_file = full_path
                break

    # Determine missing status
    missing = []
    if not glb_file:
        missing.append(".glb 3D file")
    if not main_file:
        missing.append("MAIN image file")

    if missing:
        return glb_file, main_file, f"Missing required file(s): {', '.join(missing)}"

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

