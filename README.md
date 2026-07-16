# Day Quality Tracker 5 <sub><sup>(v1.4.0)</sup></sub>

Day Quality Tracker (DQT) is a simple Python CLI that helps you record and track
daily “day quality” ratings and visualize them over time using the 
`matplotlib.pyplot` module.

> By _[Morpheus][profile]_

---

## Table of Contents

- [Pre-installation Requirements](#pre-installation-requirements)
- [TL;DR](#tldr)
- [Installation](#installation)
- [Notes](#notes)
- [Installing Dependencies](#installing-dependencies)
- [How to use](#how-to-use)
  - [What happens on first run](#what-happens-on-first-run)
  - [Key files](#key-files)
  - [Logs](#logs)
    - [Ratings](#ratings)
    - [Memory entries](#memory-entries)
  - [Main menu](#main-menu)
    - [Write/Edit today's log](#writeedit-todays-log)
    - [Edit previous log](#edit-previous-log)
    - [View ratings graph](#view-ratings-graph)
    - [See stats](#see-stats)
    - [View logs](#view-logs)
    - [Open settings](#open-settings)
    - [Back up logs](#back-up-logs)
    - [Create Desktop Shortcut](#create-desktop-shortcut)
    - [Import logs](#import-logs)
  - [Missed logs](#missed-logs)
  - [Custom Configurations](#custom-configurations)
- [License](#license)

---

## Pre-installation Requirements

- Python 3.12 or later
- An internet connection (only for dependency installation)

[^ TOC](#table-of-contents)

---

## TL;DR

For a quick start:

1. Download and unzip the project from the latest release
2. Open a terminal window
3. Run:
```shell
cd <PATH/TO/FOLDER>  # Replace this with the path to the folder you installed
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m dqt
```

For your convenience, in the main menu:
- Select `10) More...`
- Select `1) Create Desktop Shortcut`
- Enter the name of the Desktop Shortcut script.

[^ TOC](#table-of-contents)

---

## Installation

On the [GitHub page][repo]:
- Scroll down on the right column
- Under "[Releases][releases]", select the option labeled "Latest"
- Scroll down to "Assets"
- Click on "Source code (zip)" (recommended for basic installation)
- Unzip the ZIP file on your machine to produce a new folder.

[^ TOC](#table-of-contents)

---

## Notes

**Before running any commands** from this guide in your terminal, ensure your
terminal is running from the correct directory. You can open a terminal window
from the new dqt folder:

- macOS:
  1. Open the folder in Finder
  2. Right-click the folder and select **"New Terminal at folder"**
- Windows (10/11):
  1. Click on the address bar in File Explorer (or press Alt + D), type `cmd` 
     or `powershell`, and **press Enter**. To use the Windows Terminal app 
     instead, **type `wt`**.
  2. **Hold the Shift key and right-click** on an empty space inside the folder
     or on the folder icon itself. Select "Open PowerShell window here" or 
     "Open Command Prompt here".
  - Windows 11 Context Menu: 
    - **Right-click an empty space** in the folder and select "Open in Terminal" 
      directly from the context menu.

Alternatively:
1. Open a new Terminal window
2. Run `cd <path/to/day_quality_tracker>`
   - Replace `path/to/day_quality_tracker` with the actual path to the DQT 
     folder

If the command `python` does not work on your system, try `python3` (common on 
macOS/Linux) or `py` (common on Windows).

You only have to do this once per Terminal session.

[^ TOC](#table-of-contents)

---

## Installing Dependencies

Run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

After the dependencies are installed, you can start using DQT.

[^ TOC](#table-of-contents)

---

## How to use

To start the program, run from the project directory:

```bash
python -m dqt
```

Directly opening and running `dqt/__main__.py` may not work.

Alternatively, create your own script:

```python
from dqt.tracker import Tracker

dqt = Tracker()
dqt.run()
```

### What happens on first run

On the first run, DQT will create its logs file automatically if it does not
already exist.

- If the `data/` directory does not exist yet, DQT will create it.
- Your logs are stored in `data/dqt_logs.json`

### Key files

- `dqt/settings.py`: user-editable configuration file
- `data/dqt_logs.json`: where your ratings and memory entries are stored
- `requirements.txt`: Python dependencies needed by the app

[^ TOC](#table-of-contents)

---

### Logs

Logs are a rating + a memory entry. You do not have to enter a log every day.
You can choose to skip them when DQT says you have logs missing.

Logs can be easily edited at any time.

#### Ratings

You can enter a rating every day by selecting `1) Write Today's log` from the 
Main menu. Ratings are from 1 to 20 by default. After entering a rating, you 
can choose to edit it by selecting the same option.

You may also enter a null rating if you don't want to rate your day yet. 

#### Memory entries

Memory entries can be diary/journal entries, notes, or anything you want to 
remember for the future. You can leave the entry empty if you do not want 
to write one.

When you want to write a new memory entry or edit an existing one, DQT
creates a new temporary text file in `data/` and opens it with your device's
default text editing application. Your memory entries are **NOT** permanently
saved in this file; it is just a temporary text file for an individual entry.

*Always remember to save the text file* before closing the window and 
returning to the terminal.

These temporary editor files use names like `MEM_ENTRY_EDIT_*.txt`. DQT creates
a fresh file for each edit so an older open editor window cannot overwrite a new
entry. Old temporary editor files are cleaned up automatically after a few days,
but your actual saved logs are stored in `data/dqt_logs.json`.

Do **NOT** use the temporary text files as your primary source of backup, as 
they are **deleted after 7 days** by default and can be unreliable. Always use 
the "Backup Logs" feature provided in the main menu.

If the memory editor fails or if your device is incompatible with this feature, 
DQT allows you to directly write your entry via terminal input.

[^ TOC](#table-of-contents)

---

### Main menu

This is the first thing you see when you run the program and is DQT's "Homepage"

#### Write/Edit today's log

Write a new log for the day. If you've already done this, this option 
instead allows you to edit your rating and/or memory entry.

#### Edit previous log

To choose the log to edit, the program will prompt you to enter either:
- The date of the log you wish to edit
  - By default, the format you must use is `DD-MM-YYYY` (e.g., `20-01-2026`)
- The number of days ago the log is for
  - e.g.: yesterday → `1`, last week → `7`

Then choose to edit the rating and/or memory you've written for that day.

#### View ratings graph

Visually display your ratings on a line graph.
The graph also shows your average, highest, and lowest ratings.
When the graph window opens, close it to return to the program.

[^ TOC](#table-of-contents)

#### See stats

View detailed statistics about your ratings, including averages, highs, lows, 
and more.

#### View logs

Choose either to:
- Search a log by date
- Print last 30 or all logs as standard output
- Open the file with your system's default application

#### Open settings

Open `dqt/settings.py` to customize your experience. See more 
[below](#custom-configurations).

#### Back up logs

Occasionally, errors or interruptions may corrupt or erase the JSON file where 
logs are stored. To prevent data loss, it is recommended to back up your logs 
periodically.

This option creates a copy of your log JSON file in a directory of your 
choosing.

[^ TOC](#table-of-contents)

#### Create Desktop Shortcut

You can create a shell script that acts as a shortcut to run DQT on your 
Desktop folder. Instead of running DQT manually from your Terminal every time, 
you can start DQT by simply double-clicking this shortcut file.

#### Import logs

You can easily migrate your logs between versions of DQT or between different 
devices.

The program reads and copies the data from a chosen JSON file over to the 
current JSON file used by the program.

---

### Missed logs

At the start of the program, DQT first checks if you've missed any prior logs.

You may choose to enter the missed logs immediately or skip them for later.

If you skip missed logs and write a new log, the missed logs must be entered 
manually at a later time, unless you rerun the program and enter the missing 
logs before creating a new one. This is because the program identifies missed 
logs by only looking at the date of the most recent log. This is good if you 
want to intentionally skip logging for a day.

[^ TOC](#table-of-contents)

---

### Custom Configurations

To configure and customize DQT, select `6) Open Settings` from the main menu.

Each configuration comes with a description, and to change a setting, simply 
change the value after the colon.

For example, to change the date format to YYYY/MM/DD:
```python
        "date_format": "%Y/%m/%d",  #          ★ Date format used
```

**Remember to save any changes made** and rerun the program for changes to take
effect.

Feel free to experiment with each setting to tune DQT to your preferences!

---

## License

This project is licensed under the [MIT License](LICENSE.txt).

---

🌟 Be an amazing person and [drop me a star][repo]!

[^ TOC](#table-of-contents)


[profile]: https://github.com/TheGittyPerson
[repo]: https://github.com/TheGittyPerson/day-quality-tracker
[releases]: https://github.com/TheGittyPerson/day-quality-tracker/releases
