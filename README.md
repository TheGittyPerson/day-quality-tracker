# Day Quality Tracker 5 <sub><sup>(v1.3.0)</sup></sub>

Day Quality Tracker (DQT) is a simple Python CLI that helps you record and track
daily “day quality” ratings and visualize them over time using the 
`matplotlib.pyplot` module.

> By _[Morpheus][profile]_

---

## Pre-installation Requirements

- Python 3.12 or later
- An internet connection (only for dependency installation)

---

## Quick Start

If you want the shortest path to running DQT:

1. Download and unzip the project from the latest release
2. Open a terminal in the project folder
3. Install dependencies with `python -m pip install -r requirements.txt`
4. Start the program with `python -m dqt`

---

## Installation

On the [GitHub page][repo]:
- Scroll down on the right column
- Under "[Releases][releases]", select the option labeled "Latest"
- Scroll down to "Assets"
- Click on "Source code (zip)" (recommended for basic installation)
- Unzip the ZIP file on your machine to produce a new folder.

---

## Notes

Before running any commands from this guide in your terminal, ensure your
terminal is running from the correct directory. You can open a terminal window
from the new dqt folder:

- macOS:
  1. Open the folder in finder
  2. Right-click the folder and select **"New Terminal at folder"**
- Windows (10/11):
  1. Click on the address bar in File Explorer (or press Alt + D), type `cmd` 
     or `powershell`, and **press Enter**. To use the Windows Terminal app, 
     **type `wt` instead**.
  2. **Hold the Shift key and right-click** on an empty space inside the folder
     or on the folder icon itself. Select "Open PowerShell window here" or 
     "Open Command Prompt here".
  - Windows 11 Context Menu: 
    - **Right-click an empty space** in the folder and select "Open in Terminal" 
      directly from the context menu.

Alternatively:
1. Open a new Terminal window
2. Run `cd path/to/day_quality_tracker`
   - Replace `path/to/day_quality_tracker` with the actual path to the DQT 
     folder

If the command `python` does not work on your system, try `python3` (common on 
macOS/Linux) or `py` (common on Windows).

---

## Creating a Shortcut Executable File

Instead of having to open Terminal or navigate into the project directory 
every time you want to start DQT, you can create an executable file that you 
can double-click and run DQT with instantly.

You can run `scripts/package_installer.py` to create this file for you. You 
will need to enter the name and directory for the executable file.

---

## Installing Dependencies

Then, from the project directory, install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Alternatively, run `scripts/package_installer.py` to install everything listed
in `requirements.txt` for you:

```bash
python scripts/package_installer.py
```

After the dependencies are installed, you can [start DQT](#how-to-use).

---

## How to use

To start the program from the project directory, run:

```bash
python -m dqt
```

You can also initialize and run the tracker manually by opening and running 
`dqt/__main__.py` with an editor.

```python
from dqt.tracker import Tracker

dqt = Tracker()
dqt.run()
```

### What happens on first run

On the first run, DQT will create its logs file automatically if it does not
already exist.

- If the `data/` directory does not exist yet, DQT will create it.
- Your logs are stored in `data/dq_logs.json`

You usually do not need to create this file manually.

### Useful files

- `dqt/settings.py`: user-editable configuration file
- `data/dq_logs.json`: where your ratings and memory entries are stored
- `requirements.txt`: Python dependencies needed by the app

---

### Ratings

Each day, if you have not yet entered a rating, the program will prompt you to 
do so. By default, the earliest time you can enter a rating is **8:00 PM** 
(configurable).

You may also enter a null rating, indicating that you are unable or unwilling to
rate your day at the moment. Ratings can be edited at any time.

---

### Memory entries

You may optionally add a memory entry alongside your rating. Memory entries can
be diary/journal entries, notes, or anything you wish to remember for the 
future. You can leave the entry empty if you do not want to write one.

When you want to write a new memory entry or edit an existing one, DQT
creates a new temporary text file in `data/` and opens it with your device's
default text editing application. Your memory entries are **NOT** permanently
saved in this file; it is just a temporary text file for an individual entry.

*Always remember to save the text file* before closing the window and 
returning to the terminal.

These temporary editor files use names like `MEM_ENTRY_EDIT_*.txt`. DQT creates
a fresh file for each edit so an older open editor window cannot overwrite a new
entry. Old temporary editor files are cleaned up automatically after a few days,
but your actual saved logs are stored in `data/dq_logs.json`.

Do **NOT** use the temporary text files as your primary source of backup, as 
they are **deleted after 7 days** by default and can be unreliable. Always use 
the "Backup Logs" feature provided in the main menu.

If the memory editor fails or if your device is incompatible for this feature, 
DQT allows you to directly write your entry via terminal input.

---

### Main menu

After entering your log for the day, you have a number of options:

#### View ratings graph

Visually display your ratings on a line graph.
The graph also shows your average, highest, and lowest ratings.
When the graph window opens, close it to return to the program.

#### Edit today's log

Choose to edit the rating or memory (or both) you entered today. If you 
haven't entered a log for today yet, this option creates a new log.

#### Edit previous log

To choose the log to edit, the program will prompt you to enter either:
* The date of the log you wish to edit
    * By default, the format you must use is `YYYY-MM-DD` (e.g., `2026-01-20`)
* The number of days ago the log is for
    * e.g.: yesterday → `1`, last week → `7`

Choose to edit the rating or memory (or both) you entered for that day.

#### See stats

View detailed statistics about your ratings, including averages, highs, lows, 
and more.

#### View all logs

Choose either to:
* Print logs as standard output
* Open the file with your system's default application

#### Open settings

Open `dqt/settings.py` to customize your experience. See more 
[below](#custom-configurations).

#### Back up logs

Occasionally, errors or interruptions may corrupt or erase the JSON file where 
logs are stored. To prevent data loss, it is recommended to back up your logs 
periodically.

This option creates a copy of your log JSON file in a directory of your 
choosing.

#### Import logs

You can easily migrate your logs between versions of DQT or between different 
devices.

The program reads and copies the data from a chosen JSON file over to the 
current JSON file used by the program.

---

### Missed logs

After running the program, it first checks if you've missed any prior logs.

You may choose to enter the missed logs immediately or skip them for later.

If you skip missed logs, they must be entered manually at a later time (unless 
the program is exited before entering today’s log). This is because the program 
determines missed logs by comparing dates against the most recent recorded 
entry.

---

### Custom Configurations

To configure and customize DQT, open `dqt/settings.py` (the main menu provides
an option to do this).

Each configuration comes with a description, and to change a setting, simply 
change the value after the colon.

For example, to set the earliest hour of day a log entry is accepted to 
**10:00 PM**:
```python
# (Simplified)
CONFIGS: dict[str, dict[str, ...]] = {
    'tracker': {
        'min_time': 22,  # Earliest hour of day a log entry is accepted...
```

**Remember to save any changes made** and rerun the program for changes to take
effect.

Feel free to experiment with each setting to tune DQT to your preferences.

---

## License

This project is licensed under the MIT License.

---

Like my project? [Drop me a star][repo]!


[profile]: https://github.com/TheGittyPerson
[repo]: https://github.com/TheGittyPerson/day-quality-tracker
[releases]: https://github.com/TheGittyPerson/day-quality-tracker/releases
