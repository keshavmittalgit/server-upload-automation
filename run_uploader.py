"""
Server Upload Automation - Main Application Entrypoint
======================================================
Architecture:
- src.config            : Selectors, ports, file rules
- src.browser_launcher  : Real native browser manager (Chrome/Edge)
- src.file_scanner      : Strict .glb + MAIN validation & folder discovery
- src.portal_driver     : Web element interactions (select, upload, submit)
- src.logger            : Live console streaming and JSON audit report
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog
from playwright.sync_api import sync_playwright

from src.config import CDP_PORT
from src.browser_launcher import launch_native_browser
from src.file_scanner import validate_and_find_files, get_subfolders
from src.portal_driver import get_existing_portal_entries, upload_item
from src.logger import AuditLogger


def ask_folder_gui():
    """Opens native Windows folder chooser dialog."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_selected = filedialog.askdirectory(title="Select Data Folder containing item subfolders")
    root.destroy()
    return folder_selected


def main():
    print("\n" + "=" * 75)
    print("      SERVER UPLOAD AUTOMATOR - MODULAR PRODUCTION SYSTEM            ")
    print("=" * 75)

    # 1. Launch real native browser
    success, browser_path = launch_native_browser(CDP_PORT)
    if not success:
        print(f"[X] Error: {browser_path}")
        return

    print("\n" + "*" * 75)
    print(f"STEP 1: Your NATIVE browser is now OPEN ({os.path.basename(browser_path)}).")
    print("        - Go to your server portal URL.")
    print("        - Log in with your password normally.")
    print("        - Open the Upload page.")
    print("*" * 75)

    input("\n>>> Once on the Upload page, press [ENTER] here to continue... ")

    # 2. Folder picker
    print("\n" + "*" * 75)
    print("STEP 2: Please select your Data Folder in the folder popup window...")
    print("*" * 75)

    data_folder = ask_folder_gui()
    if not data_folder:
        print("[!] No folder selected. Exiting.")
        return

    logger = AuditLogger(data_folder)
    logger.log(f"Selected Data Folder: {data_folder}", "SUCCESS")

    current_dialog = {"message": None, "type": None}

    # 3. Playwright Controller
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
            contexts = browser.contexts
            if not contexts or not contexts[0].pages:
                logger.log("No active browser tabs found!", "ERROR")
                return

            # Find active portal tab
            target_page = None
            for p_tab in contexts[0].pages:
                url = p_tab.url.lower()
                title = p_tab.title().lower()
                if "image" in title or "museum" in title or "admin" in url or "upload" in url:
                    target_page = p_tab
                    break
            if not target_page:
                target_page = contexts[0].pages[0]

            logger.log(f"Connected to Tab: '{target_page.title()}' ({target_page.url})", "SUCCESS")
        except Exception as e:
            logger.log(f"Could not connect to browser: {e}", "ERROR")
            return

        # Native popup / alert listener
        def handle_dialog(dialog):
            msg = dialog.message
            d_type = dialog.type
            logger.log(f"Popup [{d_type.upper()}]: \"{msg}\"", "POPUP")
            current_dialog["message"] = msg
            current_dialog["type"] = d_type
            logger.record_popup(d_type, msg)
            dialog.accept()

        target_page.on("dialog", handle_dialog)

        # Live browser console listener
        def handle_console(msg):
            text = f"[{msg.type.upper()}] {msg.text}"
            logger.log(text, "BROWSER")
            logger.record_console(msg.type, msg.text)

        target_page.on("console", handle_console)

        # Scan existing items
        already_uploaded = get_existing_portal_entries(target_page)
        logger.log(f"Found {len(already_uploaded)} entries already recorded in portal.", "INFO")

        # Discover subfolders
        subfolders = get_subfolders(data_folder)
        logger.log(f"Found {len(subfolders)} folders to process.\n", "INFO")
        print("-" * 75)

        # 4. Process each subfolder
        for idx, folder_name in enumerate(subfolders, 1):
            folder_path = os.path.join(data_folder, folder_name)
            folder_key = folder_name.strip().lower()

            logger.log(f"[{idx}/{len(subfolders)}] Processing Folder: '{folder_name}'")

            # Skip check
            if folder_key in already_uploaded:
                logger.log(f"Skipping '{folder_name}': Already uploaded in portal.", "SKIP")
                logger.record_skip(folder_name)
                continue

            # Strict file validation
            glb_file, main_file, validation_error = validate_and_find_files(folder_path)
            if validation_error:
                logger.log(f"FAILED '{folder_name}': {validation_error} -> SKIPPING", "ERROR")
                logger.record_failure(folder_name, validation_error)
                continue

            files_to_upload = [glb_file, main_file]
            for f in files_to_upload:
                size_kb = round(os.path.getsize(f) / 1024, 1)
                logger.log(f"   -> Validated File: {os.path.basename(f)} ({size_kb} KB)")

            current_dialog["message"] = None
            current_dialog["type"] = None

            try:
                ok, msg = upload_item(target_page, folder_name, files_to_upload, current_dialog)
                if ok:
                    logger.log(f"SUCCESS '{folder_name}': {msg}", "SUCCESS")
                    logger.record_success(folder_name, files_to_upload, msg)
                    already_uploaded.add(folder_key)
                else:
                    logger.log(f"FAILED '{folder_name}': {msg}", "ERROR")
                    logger.record_failure(folder_name, msg)
            except Exception as err:
                logger.log(f"FAILED '{folder_name}': {err}", "ERROR")
                logger.record_failure(folder_name, str(err))

        # 5. Output Summary and JSON Report
        logger.generate_summary(len(subfolders))
        input("\n>>> Done! Press [ENTER] to exit... ")


if __name__ == "__main__":
    main()
