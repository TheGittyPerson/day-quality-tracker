import sys
from subprocess import check_call
from datetime import datetime
from typing import TYPE_CHECKING

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("\nA python package 'matplotlib' is required before running.")
    if input("Install now? [y/n]: ").lower() != 'y':
        raise SystemExit()
    check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib'])
    print("\nInstallation complete!")
    print("Resuming program...\n")
    import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from day_quality_tracker import DayQualityTracker


class DQTGraph:
    """Manage graph plotting for day_quality_tracker."""

    def __init__(self, dqt: DayQualityTracker):
        """Get required DQT attributes and initialize graph settings."""
        # Get DayQualityTracker attributes
        self.dqt = dqt
        self.date_format = dqt.date_format
        self.min_rating = dqt.min_rating
        self.max_rating = dqt.max_rating

        # Graph settings
        self.graph_date_format = '%a %b %d'

        self.graph_style = 'ggplot'

        self.line_width = 3

        self.title_fontsize = 20
        self.title_padding = 18

        self.xlabel_fontsize = 14
        self.ylabel_fontsize = 14

        self.tick_params_fontsize = 7
        self.yticks_steps = 2

        self.year_labels_fontsize = 10
        self.year_labels_fontweight = 'bold'

    def build(self):
        """Initialize graph properties."""
        # Close existing windows to prevent overlapping
        plt.close('all')

        dates = list(self.dqt.json.saved_ratings.keys())
        ratings = list(self.dqt.json.saved_ratings.values())

        formatted_dates = [
            datetime.strptime(date, self.date_format)
            .strftime(self.graph_date_format)
            for date in dates
        ]

        # Initialise properties
        plt.style.use(self.graph_style)
        fig, ax = plt.subplots()
        ax.plot(formatted_dates, ratings, linewidth=self.line_width)

        # Set chart title and label axes
        ax.set_title(
            "Day Quality Ratings",
            fontsize=self.title_fontsize,
            pad=self.title_padding,
        )
        ax.set_xlabel("Date", fontsize=self.xlabel_fontsize)
        ax.set_ylabel("Rating", fontsize=self.ylabel_fontsize)

        # Set size of tick labels
        ax.tick_params(labelsize=self.tick_params_fontsize)

        fig.autofmt_xdate()

        # Set y-axis ticks to increment by 2
        ax.set_yticks(range(0, self.max_rating + 1, self.yticks_steps))

        shown_years = set()

        # Draw year labels on the top of the graph
        for i, date_str in enumerate(dates):
            date = datetime.strptime(date_str, self.date_format)
            year = date.year

            if year not in shown_years:
                ax.text(
                    i,
                    ax.get_ylim()[1],
                    str(year),
                    ha='center',
                    va='bottom',
                    fontsize=self.year_labels_fontsize,
                    fontweight=self.year_labels_fontweight
                )
                shown_years.add(year)

    @staticmethod
    def show():
        """Show the graph."""
        plt.show()
