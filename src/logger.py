"""Logger and JSON Audit Report generator."""

import os
import json
from datetime import datetime


class AuditLogger:
    def __init__(self, data_folder=""):
        self.report = {
            "start_time": datetime.now().isoformat(),
            "data_folder": data_folder,
            "successful": [],
            "failed": [],
            "skipped": [],
            "popups": [],
            "browser_console_logs": []
        }

    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[*]",
            "SUCCESS": "[+]",
            "WARN": "[!]",
            "ERROR": "[X]",
            "SKIP": "[-]",
            "BROWSER": "[BROWSER CONSOLE]",
            "POPUP": "[BROWSER POPUP]"
        }.get(level, "[*]")
        print(f"{prefix} [{timestamp}] {msg}")

    def record_success(self, folder, files, popup_message):
        self.report["successful"].append({
            "folder": folder,
            "files": [os.path.basename(f) for f in files],
            "popup_message": popup_message,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    def record_failure(self, folder, reason):
        self.report["failed"].append({
            "folder": folder,
            "reason": reason,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    def record_skip(self, folder, reason="Already exists in portal"):
        self.report["skipped"].append({
            "folder": folder,
            "reason": reason
        })

    def record_popup(self, d_type, msg):
        self.report["popups"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": d_type,
            "message": msg
        })

    def record_console(self, c_type, text):
        self.report["browser_console_logs"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": c_type,
            "text": text
        })

    def generate_summary(self, total_folders):
        self.report["end_time"] = datetime.now().isoformat()
        print("\n" + "=" * 75)
        print("                     UPLOAD SUMMARY REPORT                      ")
        print("=" * 75)
        self.log(f"Total Folders Scanned : {total_folders}")
        self.log(f"Successfully Uploaded : {len(self.report['successful'])}", "SUCCESS")
        self.log(f"Skipped (Already In)  : {len(self.report['skipped'])}", "SKIP")
        self.log(f"Failed (Missing/Err)  : {len(self.report['failed'])}", "ERROR" if self.report['failed'] else "INFO")
        self.log(f"Total Popups Handled  : {len(self.report['popups'])}", "INFO")
        self.log(f"Total Console Logs    : {len(self.report['browser_console_logs'])}", "INFO")
        print("=" * 75)

        if self.report["failed"]:
            print("\n" + "!" * 75)
            print("FAILED FOLDERS BREAKDOWN:")
            for item in self.report["failed"]:
                print(f"  - Folder [{item['folder']}]: {item['reason']}")
            print("!" * 75)

        # Save to JSON
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"upload_report_{date_str}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2)
        self.log(f"Audit log report saved to: {os.path.abspath(report_file)}", "SUCCESS")

