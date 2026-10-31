"""Browser launcher and manager for native Chrome / Edge."""

import os
import time
import subprocess


def get_native_browser_path():
    """Locates the installed Google Chrome or Microsoft Edge executable."""
    candidates = [
        # Google Chrome
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        # Microsoft Edge
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def launch_native_browser(port=9222):
    """
    Launches the real, native installed browser with remote debugging port.
    Uses dedicated session profile to avoid automation banner or test mode warning.
    """
    browser_exe = get_native_browser_path()
    if not browser_exe:
        return False, "Could not find native Google Chrome or Edge installed"

    profile_dir = os.path.join(os.path.expanduser("~"), ".native_browser_session")
    os.makedirs(profile_dir, exist_ok=True)

    cmd = [
        browser_exe,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        "--disable-blink-features=AutomationControlled"
    ]

    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    return True, browser_exe

