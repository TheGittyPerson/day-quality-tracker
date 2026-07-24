try:
    import sys
    import traceback

    from dqt.tracker import Tracker
    from dqt.settings import CONFIGS
    from dqt.ui_utils import *

    dqt: Tracker = Tracker()

    try:

        dqt.configure(**CONFIGS["tracker"])
        dqt.graph.configure(**CONFIGS["graph"])

    except ValueError as e:
        print("\n*!* —————————————————————————————— *!*")
        print(bol(red("\n❌ Error!")))
        print(f"{e}.")
        print("Ensure that you have passed valid configuration keys in "
              "`settings.py`.")
        sys.exit(1)

    try:
        dqt.run()

    except KeyboardInterrupt as e:
        print("\n\n*⎋* —————————————————————————————— *⎋*")
        print("\nProgram interrupted.")
        print("\nSaving changes...")
        dqt.json.update()
        print(bol(grn("Success!")))
        sys.exit()

except ModuleNotFoundError as e:
    print("\n*!* —————————————————————————————— *!*")
    print("\n❌ Error!")
    print(f"Could not import '{e.name}'")
    print("\nEnsure that you have installed all required dependencies before "
          "running DQT.")
except (SyntaxError, NameError, AttributeError) as e:
    print("\n*!* —————————————————————————————— *!*")
    print("\n❌ Error!")
    print(f"It seems some modules have been corrupted/changed.")
    print("\nTry reinstalling DQT and try again.")
except Exception:
    print("\n*!* —————————————————————————————— *!*")
    print("\n❌ Error!")
    print("An unexpected error occurred...")
    traceback.print_exc()
    sys.exit(1)
