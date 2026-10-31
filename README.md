# 🚀 Server Upload Automator

A simple, automated tool to upload **3D Model (`.glb`)** and **`MAIN` preview files** to your museum server portal without manually clicking through hundreds of folders.

---

## 📌 How It Works (In Simple Terms)

1. You start the tool.
2. It automatically opens your real **Google Chrome** (or **Microsoft Edge**) browser.
3. You log in to your portal and go to the Upload page.
4. You press **ENTER** on your keyboard, and a window pops up asking you to **select your Data Folder**.
5. The tool takes over and automatically:
   - Checks every subfolder.
   - Finds the `.glb` file and the `MAIN` (or `main`) file.
   - Skips any folder that was already uploaded.
   - Skips and marks as **FAILED** any folder where a file is missing.
   - Automatically clicks **Upload**.
   - Listens for the server's popup message (Alert/Confirm) and automatically clicks **OK**.
   - Shows you live progress and saves a summary report at the end.

---

## 🛠️ One-Time Setup (First Time Only)

Make sure you have **Python** installed on your computer.

Open your **Command Prompt** (CMD) and run this single command to install Playwright:

```cmd
pip install playwright
```

*That's it! No extra browser downloads or complex installations needed.*

---

## 🏃 How to Run the Tool

### Step 1: Start the script
Open Command Prompt in this folder and run:

```cmd
python run_uploader.py
```

### Step 2: Log in to your portal
- Your normal Chrome / Edge browser will pop up automatically.
- Type your username and password, and log in to your website.
- Navigate to the **Upload** page.

### Step 3: Tell the tool to start
- Go back to your Command Prompt window and press **ENTER**.
- A folder selection window will appear on your screen.
- Click on your **Data Folder** (the folder that has all your numbered folders inside it) and click **Select Folder**.

### Step 4: Watch it work
The tool will now do all the work automatically:
- It uploads each folder one by one.
- You will see live logs on your screen.
- When an upload finishes and the server popup appears, it clicks **OK** for you and moves to the next folder.
- At the end, it will show you:
  - ✅ **Successfully Uploaded**
  - ⏭️ **Skipped** (already uploaded before)
  - ❌ **Failed** (e.g. missing `.glb` or `MAIN` file)
- A detailed file named `upload_report_YYYYMMDD_HHMMSS.json` will be saved with the full log.

---

## 📂 Folder Rules

Inside your data folder, each item must be in its own subfolder:

```text
My_Data_Folder/
│
├── 101/                  <-- (Subfolder)
│   ├── statue.glb        <-- Any .glb 3D file
│   └── MAIN.png          <-- File named 'MAIN' or 'main' (png, jpg, etc.)
│
├── 102/                  <-- (Subfolder)
│   ├── vase.glb
│   └── main.jpg
│
└── 103/                  <-- If this folder has no .glb, it will be skipped
    └── main.png              and marked as FAILED in the log.
```

---

## ❓ Frequently Asked Questions

**Q: Does the tool know my password?**  
No. You log in yourself manually using your own hands. The tool only takes control after you are logged in.

**Q: What if the internet or server is slow?**  
The tool patiently waits for the server to finish and for the popup to show before it moves to the next item.

**Q: Can I stop it midway?**  
Yes, simply press `Ctrl + C` in your Command Prompt window to stop at any time.

