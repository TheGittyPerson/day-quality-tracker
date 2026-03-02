# Day Quality Tracker 5 <sub><sup>(v1.0.0)</sup></sub>

Day Quality Tracker (DQT) is a simple Python CLI that helps you record and track
daily “day quality” ratings and visualize them over time using the 
`matplotlib.pyplot` module.

It is designed to be lightweight, flexible, and reflective — combining numeric 
ratings with short memory entries so you can track both trends and moments.

---

## Installation

On the [GitHub page](https://github.com/TheGittyPerson/day-quality-tracker):
* Click the green "Code" button
* Select "Download ZIP"
* Unzip the ZIP file on your machine.

Or, to install the latest _stable_ version:
* Scroll down on the right column
* Under
  "[Releases](https://github.com/TheGittyPerson/day-quality-tracker/releases)", 
  select the option labeled "Latest"
* Scroll down to "Assets"
* Click on "Source code (zip)" (recommended for basic installation)
* Unzip the ZIP file on your machine.

---

## How to use

Before using the program, ensure you have a Python interpreter installed on your
system **(version 3.12+ required)**.

To start the program, **run `main.py`**, or initialize and run the tracker 
manually:

```python
from src.tracker import Tracker

dqt = Tracker()
dqt.run()
```

To set a configuration manually:

```python
# Example:
from src.tracker import Tracker

dqt = Tracker()
dqt.configure(
  enable_ansi=False,
)
dqt.run()
```

Or use `settings.py`:

```python
from src.tracker import Tracker
from settings import CONFIGS

dqt = Tracker()
dqt.configure(*CONFIGS['tracker'])
dqt.run()
```

---

### Ratings

Each day, if you have not yet entered a rating, the program will prompt you to 
do so. By default, the earliest time you can enter a rating is **8:00 PM** 
(configurable).

You may also enter a null rating, indicating that you are unable or unwilling to
rate your day at the moment. Ratings can be edited at any time.

---

### Memory entries

You may optionally add a memory entry alongside your rating. Memory entries 
function like short diary notes and can span a few lines.

You may enter anything you wish to remember for the future, or leave the entry 
empty if you do not wish to write one.

---

### Main menu

After entering your log for the day, you have a number of options:

#### View ratings graph

Visually display your ratings on a line graph.
The graph also shows your average, highest, and lowest ratings.

#### Edit today's log

Choose to edit the rating or memory (or both) you entered today.

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

#### Back up logs

Occasionally, errors or interruptions may corrupt or erase the JSON file where 
logs are stored. To prevent data loss, it is recommended to back up your logs 
periodically.

This option creates a copy of your log JSON file in a directory of your 
choosing.

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

To configure and customize DQT, open `settings.py`. Each configuration comes 
with a description, and to change a setting, simply change the value after the 
colon.

For example, to set the earliest hour of day a log entry is accepted to 
**10:00 PM**:
```python
# (Simplified)
CONFIGS: dict[str, dict[str, ...]] = {
    'tracker': {
        'min_time': 22,  # Earliest hour of day a log entry is accepted...
```

Feel free to experiment with each setting to tune DQT to your preferences.

---

## License

This project is licensed under the MIT License.
