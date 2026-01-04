# Day Quality Tracker <sub><sup>v0.3.0</sup></sub>

This is a simple Python CLI that helps you track your day quality ratings and visualize them on a graph using the Matplotlib.pyplot module.

# How to use

Before using the program, ensure you have a Python interpreter installed on your system **(version 3.12+ recommended)**.

1. Download **`day_quality_tracker.py` AND `dqt_graph.py`** (`dqt_graph.py` is required if you wish to visually see your ratings in a graph)
2. To start the program, **run `day_quality_tracker.py`**, or
   
   ```
   from day_quality_tracker import DayQualityTracker
   
   dqt = DayQualityTracker()
   dqt.run()
   ```
   
3. A JSON file, **`dq_tracker.json`, is automatically generated on first run**. This file is used to record the ratings you enter.
4. Follow the instructions in the program. Simple!

# License

This project is licensed under the MIT License.
