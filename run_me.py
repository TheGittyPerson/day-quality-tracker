import sys
import traceback

from day_quality_tracker import DayQualityTracker

if __name__ == '__main__':
    dqt = DayQualityTracker()

    # Customizations go here ↴

    # ------------------------ #

    try:
        dqt.run()
    except KeyboardInterrupt:
        print("\n\nUser interrupted the program.")
        print("\nSaving changes...")
        dqt.json.update()
        print("Success!")
        sys.exit()
    except Exception:
        print("\n❌ \033[1m\033[31mError!\033[0m")
        print(traceback.format_exc())
        sys.exit(1)
