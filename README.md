# KRITA Reset and Backup Tool

A Python Tkinter GUI utility for easily resetting or backing up Krita's configuration and resource files.

English | [简体中文](./README-ZH.md)

---

## Foreword

As a programming beginner, my code might be a bit messy. This is my first completed project.

![screenshot](./assets/44788d3173643ec7c40dde7b4b1e01eafe92ece1.png)

---

## Language Support

- ​**Language Localization**: All GUI display text is dynamically loaded from `./language/*.json`. `ZH.json` serves as the default fallback file. If `./language/ZH.json` is missing, it will be created automatically. Currently included is `EN.json`. If your language is unavailable, you may edit/create one and submit it.

---

## Planned Features

- [ ] Cross-platform: Currently only supports Windows due to lack of devices for other platforms and uncertainty about Krita's behavior on them. Platform-specific code is centralized in the `./platform_dependence` package. Contributions are welcome!
  
  - [x] Windows
  - [ ] Mac OS
  - [ ] Linux

- [x] Correctly reset Krita

- [x] Create Krita configuration backups with switching capability

- [x] Detect if Krita is running

- [x] Import/export Krita backups as ZIP files

- [x] Properly handle non-default Krita resource paths

---

## How to Use

The functionality is straightforward:

- Click the `+` or `-` buttons at the bottom-left to create/manage configuration groups
- Click "Apply" to switch Krita configurations
- Use the `Settings` button (top-right) to configure the tool and view about information
- Use `Import/Export` buttons for configuration sharing

---

## Development Notes

Install dependencies:

```
pip install sv_ttk pywinstyles pillow darkdetect
```

​**For packaging**​ (using `pyinstaller`/`nuitka` etc.):  
After packaging, copy the `./resources` and `./language` folders to the root directory (alongside the `.exe` file).

Windows-specific packaging command with icons using `pyinstaller`:

```
pyinstaller main.spec
```
