"""Web portal automation driver interacting with page elements."""

import time
from src.config import SELECTORS, TIMEOUT_NETWORK_IDLE_MS
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def get_existing_portal_entries(page):
    """Scans portal table and records to detect already uploaded items."""
    js_code = f"""
    (() => {{
        const found = new Set();
        document.querySelectorAll('{SELECTORS["table_rows"]}').forEach(row => {{
            const cells = row.querySelectorAll('td');
            if (cells.length > 0) {{
                const entryVal = cells[0].textContent.trim().toLowerCase();
                if (entryVal) found.add(entryVal);
            }}
        }});
        if (window.mockImages && Array.isArray(window.mockImages)) {{
            window.mockImages.forEach(img => {{
                if (img.entry_no) found.add(img.entry_no.trim().toLowerCase());
            }});
        }}
        return Array.from(found);
    }})()
    """
    try:
        entries = page.evaluate(js_code)
        return set(entries or [])
    except Exception:
        return set()


def select_entry_dropdown(page, folder_name):
    """
    Finds and selects the entry in #entry_no_image dropdown.
    Triggers change event to populate portal metadata.
    """
    js_select = f"""
    (() => {{
        const target = '{folder_name}'.trim();
        const sel = $('{SELECTORS["entry_select"]}').length ? $('{SELECTORS["entry_select"]}') : $('{SELECTORS["entry_select_alt"]}');
        if (!sel.length) return {{ success: false, reason: "Select menu not found" }};

        let matchedVal = null;
        sel.find('option').each(function() {{
            const val = $(this).val().trim();
            const text = $(this).text().trim();
            if (val.toLowerCase() === target.toLowerCase() || text.toLowerCase() === target.toLowerCase() || text.toLowerCase().includes(target.toLowerCase())) {{
                matchedVal = val;
                return false;
            }}
        }});

        if (matchedVal !== null) {{
            sel.val(matchedVal).trigger('change');
            return {{ success: true, mode: "matched", value: matchedVal }};
        }} else {{
            const newOpt = new Option(target, target, true, true);
            sel.append(newOpt).trigger('change');
            return {{ success: true, mode: "created", value: target }};
        }}
    }})()
    """
    return page.evaluate(js_select)


def upload_item(page, folder_name, files_to_upload, current_dialog, timeout_seconds=120):
    """
    Automates uploading:
    1. Ensures Upload Tab is active.
    2. Selects the folder/entry in the menu first.
    3. Attaches .glb and MAIN files.
    4. Clicks the Upload button.
    5. WAITS for the server to finish and for the NATIVE BROWSER POPUP (alert/confirm) to appear.
    6. Reads the popup text to determine SUCCESS or FAILURE.
    7. Clicks OK on the popup, and proceeds to the next folder.
    """
    # 1. Ensure Upload tab is visible
    upload_tab = page.locator(SELECTORS["upload_tab"])
    if upload_tab.count() > 0:
        is_active = page.evaluate("el => el.classList.contains('active')", upload_tab.element_handle())
        if not is_active:
            upload_tab.click()
            page.wait_for_timeout(300)

    # 2. Select in menu first
    sel_res = select_entry_dropdown(page, folder_name)
    if not sel_res.get("success"):
        raise RuntimeError(f"Dropdown selection failed: {sel_res.get('reason')}")

    page.wait_for_timeout(400)

    # 3. Attach files
    file_input = page.locator(SELECTORS["file_input"])
    if file_input.count() == 0:
        file_input = page.locator(SELECTORS["file_input_alt"])
    if file_input.count() == 0:
        file_input = page.locator(SELECTORS["file_input_legacy"])

    file_input.set_input_files(files_to_upload)
    page.wait_for_timeout(400)

    # Reset dialog tracker for this upload
    current_dialog["message"] = None
    current_dialog["type"] = None
    current_dialog["received"] = False

    # 4. Click Submit / Upload Files button
    submit_btn = page.locator(SELECTORS["submit_btn"])
    if submit_btn.count() == 0:
        submit_btn = page.locator('button:has-text("Upload Files")')

    submit_btn.scroll_into_view_if_needed()
    submit_btn.click()

    # 5. DYNAMIC WAIT: Wait until the server finishes processing and the native popup appears!
    start_time = time.time()
    while not current_dialog.get("received"):
        page.wait_for_timeout(500)
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            return False, f"Upload timed out after {timeout_seconds}s waiting for server popup"

    popup_msg = current_dialog.get("message") or ""
    popup_lower = popup_msg.lower()

    # 6. Analyze popup message: determine if success or fail
    failure_keywords = ["error", "fail", "invalid", "not allowed", "already exists", "exceeded"]
    is_failure = any(keyword in popup_lower for keyword in failure_keywords)

    if is_failure:
        return False, f"Popup indicated failure: {popup_msg}"
    else:
        return True, f"Popup indicated success: {popup_msg}"
