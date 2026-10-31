# 🛠️ Step-by-Step Setup Guide

This guide will walk you through setting up and running the automation tool on any Windows PC or server from scratch.

---

## 📋 Prerequisites Checklist

Before running the tool, make sure you have:
1. **Windows 10 / 11 or Windows Server**
2. **Google Chrome** or **Microsoft Edge** installed.
3. **Python 3.10+** installed.
   - If not installed, download it from [python.org](https://www.python.org/downloads/).
   - ⚠️ **Important during installation:** Check the box that says **"Add Python to PATH"**.

---

## ⚡ Step 1: Install Playwright (One-Time Only)

1. Open **Command Prompt** (Press `Win + R`, type `cmd`, and press Enter).
2. Type or paste the following command and hit Enter:

```cmd
pip install playwright
```

*Wait 10–20 seconds until it says `Successfully installed playwright`.*

---

## 🚀 Step 2: Running the Automation

1. Open your terminal inside this project folder:
   ```cmd
   cd C:\Users\Asus\server-upload-automation
   ```

2. Run the main script:
   ```cmd
   python run_uploader.py
   ```

---

## 🖥️ Step 3: What You Will See On Screen

1. **Browser Opens Automatically:**
   - Your actual Chrome or Edge browser window will open up.
   - Navigate to your server upload page.
   - Enter your login credentials and sign in.
   - Make sure you are on the **Upload** page.

2. **Press Enter in Terminal:**
   - Go back to your Command Prompt window.
   - Press **ENTER**.

3. **Select Your Data Folder:**
   - A standard Windows folder selector window will open.
   - Click on your folder containing all the subfolders.
   - Click **Select Folder**.

---

## 🤖 Step 4: Sit Back and Relax!

The script will now do the rest automatically:
- Checks the folder for a `.glb` model and a `MAIN` or `main` file.
- If any file is missing, it skips it and logs it as **FAILED**.
- Selects the item from the dropdown menu.
- Uploads the two files.
- Waits for the server's native popup (Alert/Confirm).
- Automatically clicks **OK** on the popup.
- Moves on to the next folder.
- Generates a timestamped summary log file: `upload_report_YYYYMMDD_HHMMSS.json`.

---

## 🆘 Troubleshooting

- **Error: `ModuleNotFoundError: No module named 'playwright'`**
  - Run: `pip install playwright`
- **Browser didn't open?**
  - Ensure you have either Google Chrome or Microsoft Edge installed on the PC.
- **Want to cancel?**
  - Press `Ctrl + C` in the Command Prompt window.
