"""Configuration settings for server upload automation."""

# Chrome DevTools Protocol debugging port
CDP_PORT = 9222

# Selectors on the web portal
SELECTORS = {
    "upload_tab": "#upload-tab",
    "entry_select": "#entry_no_image",
    "entry_select_alt": "select[name='entry_no_image']",
    "file_input": "#image_files",
    "file_input_alt": "input[name='image_files[]']",
    "file_input_legacy": "#image_files_input",
    "submit_btn": "#imageUploadForm button[type='submit']",
    "table_rows": "#imageTableBody tr, table tbody tr"
}

# Accepted file extensions
MAIN_IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp"]
MODEL_EXTS = [".glb"]

# Retry configuration
MAX_UPLOAD_RETRIES = 3
TIMEOUT_NETWORK_IDLE_MS = 3000

