try:
    import sys
    import traceback

    from dqt.tracker import Tracker
    from dqt.settings import CONFIGS
    from dqt.styletext import StyleText as Txt

    dqt: Tracker = Tracker()

    try:

        dqt.configure(**CONFIGS['tracker'])
        dqt.graph.configure(**CONFIGS['graph'])

    except ValueError as e:
        print("\n*!* —————————————————————————————— *!*")
        print(Txt("\n❌ Error!").bold().red())
        print(f"{e}.")
        print("Ensure that you have passed valid configuration keys in "
              "`settings.py`.")
        sys.exit(1)

    try:
        dqt.run()

    except KeyboardInterrupt as e:
        print("\n\n*⎋* —————————————————————————————— *⎋*")
        print("\nUser interrupted the program.")
        print("\nSaving changes...")
        dqt.json.update()
        print(Txt("Success!").bold().green())
        sys.exit()
except Exception:
    print("\n*!* —————————————————————————————— *!*")
    print("\n❌ Error!")
    print("An unexpected error occurred...")
    traceback.print_exc()
    sys.exit(1)
