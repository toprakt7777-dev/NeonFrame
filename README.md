# NeonFrame

NeonFrame is a standalone, offline desktop review tool for user-selected screenshots and video recordings. It detects people in the opened media using OpenCV's built-in HOG person detector and draws configurable boxes on the preview. It does not capture the screen, interact with games, inject code, inspect process memory, or hide itself.

## Run on Windows

Download `NeonFrame-Windows-x64.zip` from the latest successful GitHub Actions run (Actions → Build Windows x64 → Artifacts). Extract the ZIP and launch `NeonFrame.exe`. Windows may show its normal SmartScreen prompt because the executable is unsigned. No Python installation is needed.

## Build from an Android tablet

1. Create a free GitHub account (GitHub may request verification according to its current policies), then create an empty repository.
2. Upload the contents of this folder using GitHub's website, preserving `.github/workflows/build.yml`.
3. Open the repository's Actions tab and enable Actions if prompted. The workflow builds on a GitHub-hosted Windows runner and publishes a ZIP artifact.
4. Download the artifact from the completed workflow run. A GitHub account is needed; Actions usage is subject to GitHub's free-tier limits.

## Features

- Dark cyberpunk interface, overlay enabled toggle, adjustable opacity and bounding-box color.
- Select an image or video (MP4/AVI/MOV/MKV); choose detection confidence and enable/disable detection.
- Start/Stop processing, progress and status display, and image export with drawn boxes.
- Settings persist in `%APPDATA%\NeonFrame\settings.json`.
- Preview-only visualization: no always-on-top transparent game overlay is created.

## Detection limitations

The included classic HOG detector identifies upright full-body people and is not a game-specific character classifier. It may miss small, distant, occluded, stylized, or seated characters and can return false positives. Video is sampled at a modest interval for responsiveness. Processing runs locally; no media is uploaded. OpenCV, PySide6 and PyInstaller are installed by the workflow.

## Development

Python 3.11 is recommended. `pip install -r requirements.txt`, then `python main.py`. Run tests with `python -m unittest discover -s tests`.
