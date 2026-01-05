# Day Quality Tracker <sub><sup>v0.4.0</sup></sub>

This is a simple Python CLI that helps you track your day quality ratings and visualize them on a graph using the 
Matplotlib.pyplot module.

## How to use

Before using the program, ensure you have a Python interpreter installed on your system **(version 3.12+ recommended)**.

1. To start the program, **run `day_quality_tracker.py`**, or
   
   ```python
   from day_quality_tracker import DayQualityTracker
   
   dqt = DayQualityTracker()
   dqt.run()
   ```
   
2. A JSON file, **`dq_ratings.json`, is automatically generated on first run**. This file is used to record the ratings
   you enter
3. Follow the instructions in the program.
   1. Enter day quality ratings as either an integer or float (e.g., 12 or 5.2).
   2. All ratings are automatically rounded to 3 decimal places (by default)
   3. You can always change your ratings at any time.

## License

This project is licensed under the MIT License.
