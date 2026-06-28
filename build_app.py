# build_app.py — PyInstaller Packaging Script for DocuMind AI
"""
Run this script once to compile the application into a single .exe installer:

    python build_app.py

The output will be placed in:
    dist/DocuMind AI/DocuMind AI.exe   (folder distribution — fast startup)

Requirements:
    pip install pyinstaller
"""

import subprocess
import sys
import os

APP_NAME    = "DocuMind AI"
ENTRY_POINT = "main.py"
ICON_PATH   = os.path.join("assets", "icon.ico")

args = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",                          # Overwrite output without asking
    "--onedir",                             # Folder-based output (fast cold start)
    "--windowed",                           # No console window on Windows
    f"--name={APP_NAME}",
    "--add-data=ui;ui",                     # Include UI package
    "--add-data=core;core",                 # Include core package
    "--add-data=storage;storage",           # Include storage package
    "--hidden-import=customtkinter",
    "--hidden-import=langchain_google_genai",
    "--hidden-import=langchain_community.vectorstores.chroma",
    "--hidden-import=chromadb",
    "--hidden-import=fitz",
    "--hidden-import=docx",
    "--hidden-import=langgraph",
    "--hidden-import=openpyxl",
    "--hidden-import=sqlalchemy",
    "--hidden-import=pandas",
    "--hidden-import=PIL",
]

# Include icon if it exists
if os.path.exists(ICON_PATH):
    args.append(f"--icon={ICON_PATH}")

args.append(ENTRY_POINT)

print(f"[BUILD] Compiling {APP_NAME} with PyInstaller...")
print(f"[BUILD] Command:\n  {' '.join(args)}\n")

result = subprocess.run(args, check=False)

if result.returncode == 0:
    print(f"\n[SUCCESS] Build complete!")
    print(f"  → Executable: dist/{APP_NAME}/{APP_NAME}.exe")
    print(f"  → You can zip the entire 'dist/{APP_NAME}/' folder for distribution.")
else:
    print(f"\n[ERROR] Build failed with code {result.returncode}.")
    print("  → Make sure PyInstaller is installed: pip install pyinstaller")
    sys.exit(result.returncode)
