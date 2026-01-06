import sys
import traceback
from time import sleep
from datetime import datetime, timedelta

from dqt_graph import DQTGraph
from dqt_json import DQTJSON


class DayQualityTracker:
    """Track and visualize day quality ratings in a graph."""

    def __init__(self):
        """Load saved data, initialize settings and DQTGraph instance."""
        # Initialize settings
        self.min_time = 20  # Earliest hour the of day to enter rating
        self.min_rating = 1  # 1 recommended
        self.max_rating = 20
        self.median_rating = 10  # Rating for an average day
        self.rating_inp_dp = 3

        self.date_format = '%Y-%m-%d'
        self.date_format_print = "YYYY-MM-DD"
        # Format printed time using 12-hour clock if True
        self.clock_format_12 = True

        # JSON manager instance
        self.json = DQTJSON(self)

        # Graph manager instance
        self.graph = DQTGraph(self)

    def run(self):
        """Run Day Quality Tracker."""
        print("\n*--- Day Quality Tracker! ---*")
        sleep(1)

        if not self._today_rated():
            self._input_todays_rating()

        while True:
            self._check_missing_ratings()

            print("\nChoose what to do: ")
            print("1) [V]iew current ratings graph")
            print("2) [C]hange today's rating")
            print("3) Change previous rating...")
            print("4) [P]rint ratings here")
            print("5) E[x]it")

            match input("> ").lower().strip():
                case '1' | 'v':
                    self._view_ratings_graph()

                case '2' | 'c':
                    self._change_todays_rating()

                case '3':
                    self._change_previous_rating()

                case '4' | 'p':
                    self._print_ratings()

                case '5' | 'x':
                    print("\nBye!")
                    raise SystemExit()

                case _:
                    print("\nError: Only enter 1~5 or the given letters.")
                    sleep(1)

    # ######################################################## #
    # --------------------- MAIN METHODS --------------------- #
    # ######################################################## #

    def _input_todays_rating(self):
        """Get today's rating if it has not been provided yet.

        Reject if the specified earliest time to collect data has not
        passed yet.
        """
        if datetime.now().time().hour >= self.min_time:

            if self.json.saved_ratings:
                self._check_missing_ratings()

            if (input("\nWould you like to enter today's rating now? (y/n): ")
                    .strip().lower() != 'y'):
                print("\nRerun the program later to enter your rating!")
                return

            todays_rating = self._input_rating(
                f"Rate your day from {self.min_rating} to {self.max_rating}, "
                f"{self.median_rating} being an average day: ",
            )

            # Save data
            todays_date = datetime.today().strftime(self.date_format)
            self.json.saved_ratings[todays_date] = todays_rating
            self.json.update()
            print("Rating saved!")
            sleep(1)

        else:
            # Format time in 12-hour or 24-hour clock
            if self.clock_format_12:
                hour = self.min_time % 12 if self.min_time % 12 != 0 else 12
                suffix = 'AM' if self.min_time < 12 else 'PM'
                formatted_time = f"{hour} {suffix}"
            else:
                formatted_time = str(self.min_time)

            print(f"\nYou can only input a rating after {formatted_time}.")
            print("\nCome back later!")

    def _view_ratings_graph(self):
        self._check_missing_ratings()

        print("\nBuilding graph...")

        self.graph.build()

        print("\nDisplaying graph...")
        print("Close the graph window to proceed.")

        self.graph.show()

        print("\nGraph closed.")

    def _change_todays_rating(self):
        if self._today_rated():

            todays_date = datetime.today().strftime(self.date_format)
            print(
                f"Today's rating: ",
                self.json.saved_ratings[todays_date]
            )
            sleep(1)

            todays_rating = self._input_rating(
                "Change your rating for today "
                f"({self.min_rating}~{self.max_rating}): ",
            )

            # Save data
            todays_date = datetime.today().strftime(self.date_format)
            self.json.saved_ratings[todays_date] = todays_rating
            self.json.update()
            print("\nRating updated and saved!")
            sleep(1)

        else:
            print("\nYou haven't entered a rating yet today!")
            sleep(1)

    def _change_previous_rating(self):
        while True:
            inp = input("\nEnter the number of days ago or exact date "
                        f"('{self.date_format_print}'): ").strip()
            selected_date = None

            # If number of days ago specified, get date
            if inp.isdigit():
                inp = int(inp)
                today = datetime.today()
                selected_date = today - timedelta(days=inp)
                selected_date = selected_date.strftime(self.date_format)
                print(f"Date selected: {selected_date}")

            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.date_format)
                except ValueError:
                    print("\nError: Enter a valid date in the "
                          f"format {self.date_format_print}.")
                    sleep(1)
                    continue
                selected_date = inp

            # Check if date exists in saved ratings
            try:
                self.json.saved_ratings[selected_date]
            except KeyError:
                print("\nError: Rating for specified date not found.")
                print("Ensure you have already entered a "
                      "rating for that date.")
                print("\nTry again.")
                sleep(1)
                continue

            break

        print("\nUpdating:")
        print(f"Date: {selected_date}")
        print(f"Rating: {self.json.saved_ratings[selected_date]}"
              f"/{self.max_rating}")
        new_rating = self._input_rating(
            f"Enter new rating for {selected_date} "
            f"({self.min_rating}~{self.max_rating}): ",
        )

        # Save data
        self.json.saved_ratings[selected_date] = new_rating
        self.json.update()
        print("\nRating updated and saved!")
        sleep(1)

    def _print_ratings(self):
        print("\nRatings from the last 30 days: ")

        # Convert dictionary items to a list of tuples
        items_list = list(self.json.saved_ratings.items())

        # Get the last 30 items or all items if less than 30
        last_30_items = items_list[-30:]

        for d, q in last_30_items:
            print(f"{d}: {q}/{self.max_rating}")

    # ########################################################## #
    # --------------------- HELPER METHODS --------------------- #
    # ########################################################## #

    def _today_rated(self):
        """Check if a rating has been provided for today."""
        today = datetime.today().strftime(self.date_format)
        return today in self.json.saved_ratings

    def _check_missing_ratings(self):
        """Check if any previous days are missing ratings.

        User chooses to enter missing ratings or not. If they do,
        loop through each missing date and prompt rating.
        """
        if not self.json.saved_ratings:
            return

        last_date_str = max(self.json.saved_ratings.keys())
        last_date = datetime.strptime(last_date_str, self.date_format).date()
        todays_date = datetime.now().date()
        days_since_last = (todays_date - last_date).days

        # No missing ratings, return
        if days_since_last <= 1:
            return

        # Else:
        print(f"\nYou haven't entered a rating since {last_date}.")

        if input("Enter missing ratings now? [Y/N]: ").lower().strip() != 'y':
            return

        # Get list of missed dates
        missed_dates = []
        curr_loop_date = last_date + timedelta(days=1)
        while len(missed_dates) < days_since_last - 1:  # Exclude today
            missed_dates.append(curr_loop_date)
            curr_loop_date += timedelta(days=1)

        new_ratings = {}
        for date in missed_dates:
            rating = self._input_rating(
                f"Enter your rating for {date} "
                f"({self.min_rating}~{self.max_rating}): ",
            )
            new_ratings[datetime.strftime(date, self.date_format)] = rating

        self.json.saved_ratings.update(new_ratings)
        self.json.update()
        print("Rating saved!")
        sleep(1)

    def _input_rating(self, prompt: str) -> float:
        """Get and validate user float input."""
        error_msg = (f"Please enter a valid number from "
                     f"{self.min_rating} to {self.max_rating}.")
        while True:
            inp = input(f"\n{prompt}").strip()
            try:
                inp = float(inp)
            except ValueError:
                print(f"\nError: {error_msg}")
                sleep(1)
                continue

            if self.min_rating <= inp <= self.max_rating:
                break

            print(f"\nError: {error_msg}")
            sleep(1)
            continue
        return round(inp, self.rating_inp_dp)


if __name__ == '__main__':
    dqt = DayQualityTracker()

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
