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


def upload_item(page, folder_name, files_to_upload, current_dialog):
    """
    Automates:
    1. Ensure Upload Tab active
    2. Select in menu first
    3. Attach files
    4. Submit
    5. Await response/dialog
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

    # 4. Click Submit
    submit_btn = page.locator(SELECTORS["submit_btn"])
    if submit_btn.count() == 0:
        submit_btn = page.locator('button:has-text("Upload Files")')

    submit_btn.scroll_into_view_if_needed()
    submit_btn.click()

    # 5. Wait for network / popup
    page.wait_for_timeout(2000)

    popup_msg = current_dialog.get("message") or "Upload request sent"
    if current_dialog.get("message") and any(err in current_dialog["message"].lower() for err in ["error", "fail", "invalid"]):
        return False, f"Server popup error: {popup_msg}"

    return True, popup_msg

