from datetime import datetime
from collections import defaultdict
from typing import TYPE_CHECKING

from dqt.json_manager import DQTJSON
from dqt.styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker


class Stats:
    """A class to manage stats display."""
    
    def __init__(self, dqt: Tracker):
        """Initialize attributes."""
        self.dqt: Tracker = dqt
        self.json: DQTJSON = dqt.json
        
    def show_stats(self) -> None:
        """Show day quality rating stats.

        Print:
            - Number of days rated
            - Ratings distribution
            - Average rating
            - Highest rating
            - Lowest rating
            - Days of the week ranked from best to worst
        """
        print(Txt("\nDay Quality Ratings Stats:\n").bold().cyan().underline())
        
        rating_key = self.json.rating_kyname
        logs = self.json.logs
        
        dates_to_ratings: list[tuple[str, float]] = [
            (date, log[rating_key])
            for date, log in logs.items()
            if log[rating_key] is not None
        ]
        
        self._prnt_days_rated(logs, dates_to_ratings)
        
        if not dates_to_ratings:
            print("Average rating: -")
            print("Highest rating: -")
            print("Lowest rating: -")
            print(f"Days rated over {self.dqt.neutral_rating}: 0")
            print(f"Days rated at {self.dqt.neutral_rating}: 0")
            print(f"Days rated under {self.dqt.neutral_rating}: 0")
            print("Best days of the week: -")
            return
        
        ratings_only = [r for _, r in dates_to_ratings]
        
        self._prnt_avg_rat(ratings_only)
        self._prnt_hghst_lwst_rat(ratings_only, dates_to_ratings)
        self._prnt_rats_dstrb(dates_to_ratings)
        self._prnt_weekdays_rnked(dates_to_ratings)
    
    @staticmethod
    def _prnt_days_rated(logs: dict[str, dict[str, float | None | str]],
                         dates_to_ratings: list[tuple[str, float]]) -> None:
        """Print the number of days rated."""
        days_total = len(logs)
        days_rated = len(dates_to_ratings)
        output = f"{Txt("Days rated:").bold()} {Txt(days_rated).bold()} "
        if dates_to_ratings:
            output += f"since {Txt(str(dates_to_ratings[0][0])).bold()} "
        if not days_rated == days_total:
            output += f"({days_total} including null ratings)"
        
        print(output)
        
    def _prnt_rats_dstrb(self,
                         dates_to_ratings: list[tuple[str, float]]) -> None:
        """Print the distribution of ratings.
        
        Show number of ratings over, at, and under the neutral rating.
        """
        neutral_rat = self.dqt.neutral_rating
        
        over = at = under = 0
        
        for _, rating in dates_to_ratings:
            if rating > neutral_rat:
                over += 1
            elif rating < neutral_rat:
                under += 1
            else:
                at += 1
        
        print(Txt(f"Days rated over {neutral_rat}: {over}").bold())
        print(Txt(f"Days rated at {neutral_rat}: {at}").bold())
        print(Txt(f"Days rated under {neutral_rat}: {under}").bold())
    
    def _prnt_avg_rat(self, ratings_only: list[float]) -> None:
        """Print average rating for each day of the week."""
        avg = round(
            sum(ratings_only) / len(ratings_only),
            self.dqt.rating_inp_dp
        )
        print(f"{Txt("Average rating:").bold()} "
              f"{Txt(f"{avg:g}").bold()}/{self.dqt.max_rating}")
    
    def _prnt_hghst_lwst_rat(self,
                             ratings_only: list[float],
                             dates_to_ratings: list[tuple[str, float]]) -> None:
        """Print highest and lowest ratings, and the date for each.
        
        Prints the dates of ALL days that share the highest/lowest rating.
        """
        highest = max(ratings_only)
        lowest = min(ratings_only)
        
        highest_dates = [
            date for date, rating in dates_to_ratings
            if rating == highest
        ]
        lowest_dates = [
            date for date, rating in dates_to_ratings
            if rating == lowest
        ]
        
        print(
            f"{Txt("Highest rating:").bold()} "
            f"{Txt(f"{highest:g}").bold()}/{self.dqt.max_rating} "
            f"on {self._format_dates(highest_dates)}"
        )
        print(
            f"{Txt("Lowest rating:").bold()} "
            f"{Txt(f"{lowest:g}").bold()}/{self.dqt.max_rating} "
            f"on {self._format_dates(lowest_dates)}"
        )
    
    def _prnt_weekdays_rnked(self,
                             dates_to_ratings: list[tuple[str, float]]) -> None:
        """Print the days of the week in rank order of highest avg rating"""
        weekday_scores: dict[str, list[float]] = defaultdict(list)
        
        for date_str, rating in dates_to_ratings:
            date = datetime.strptime(date_str, self.dqt.date_format)
            weekday = date.strftime("%A")
            weekday_scores[weekday].append(rating)
        
        weekday_averages = {
            day: sum(vals) / len(vals)
            for day, vals in weekday_scores.items()
        }
        
        ranked_days = sorted(
            weekday_averages.items(),
            key=lambda item: item[1],
            reverse=True
        )
        
        print(f"\n{Txt("Best days of the week").bold()} "
              "(highest to lowest average rating):")
        counter = 0
        for day, value in ranked_days:
            counter += 1
            cleaned_avg = f"{round(value, self.dqt.rating_inp_dp):g}"
            print(f"  #{counter} {Txt(day).bold()}: "
                  f"{Txt(cleaned_avg).bold()}"
                  f"/{self.dqt.max_rating}")
    
    @staticmethod
    def _format_dates(dates: list[str]) -> str:
        """Format dates as a string, separated by commas."""
        return ", ".join(dates)

    