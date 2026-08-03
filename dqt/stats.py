from datetime import date, datetime, timedelta
from collections import defaultdict
from typing import TYPE_CHECKING

from .ui_utils import *

if TYPE_CHECKING:
    from .tracker import Tracker
    from .json_manager import JSONManager

_today: datetime = datetime.today()


class Stats:
    """A class to manage stats display."""

    def __init__(self, dqt: Tracker):
        """Initialize attributes."""
        self.dqt: Tracker = dqt
        self.json: JSONManager = dqt.json

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
        print(bol(cyn("\n📋📊 Day Quality Tracker Stats:\n")))

        rating_key = self.json.RATING_KYNAME
        logs = self.json.logs
        chronologically_sorted_logs: list[tuple[date, str, dict]] = sorted(
            (
                datetime.strptime(date_str, self.dqt.date_format).date(),
                date_str,
                log,
            )
            for date_str, log in logs.items()
        )

        datestr_to_ratings: list[tuple[str, float]] = [
            (date_str, log[rating_key])
            for _, date_str, log in chronologically_sorted_logs
            if log[rating_key] is not None
        ]
        dateobj_to_ratings: list[tuple[date, float]] = [
            (dateobj, log[rating_key])
            for dateobj, _, log in chronologically_sorted_logs
            if log[rating_key] is not None
        ]

        self._print_logging_streaks(chronologically_sorted_logs)
        print()

        self._print_days_rated(logs, dateobj_to_ratings)
        print()

        self._print_recent_average_ratings(chronologically_sorted_logs)

        if not datestr_to_ratings:
            print("Average rating: -")
            print("Highest rating: -")
            print("Lowest rating: -")
            print(f"Days rated over {self.dqt.neutral_rating}: 0")
            print(f"Days rated at {self.dqt.neutral_rating}: 0")
            print(f"Days rated under {self.dqt.neutral_rating}: 0")
            print("Day with longest memory entry: -")
            print("\nBest days of the week: -")
            return

        ratings_only = [r for _, r in datestr_to_ratings]

        self._print_avg_rating(ratings_only)
        self._print_highest_and_lowest_ratings(ratings_only, datestr_to_ratings)
        self._print_rating_distribution(datestr_to_ratings)
        self._print_longest_memory_day(chronologically_sorted_logs)
        print()

        self._print_weekdays_ranked(dateobj_to_ratings)

    def _print_logging_streaks(
            self,
            chronologically_sorted_logs: list[
                tuple[date, str, dict[str, float | None | str]]
            ]) -> None:
        """Print the current and longest streak of consecutive logged days."""
        current_streak = self._current_logging_streak(
            chronologically_sorted_logs
        )
        longest_streak = self._longest_logging_streak(
            chronologically_sorted_logs
        )

        current_unit = "day" if current_streak == 1 else "days"
        longest_unit = "day" if longest_streak == 1 else "days"

        print(
            f"{bol("Current logging streak:")} "
            f"{current_streak} {current_unit}"
        )
        print(
            f"{bol("Longest logging streak:")} "
            f"{longest_streak} {longest_unit}"
        )

    @staticmethod
    def _current_logging_streak(
            chronologically_sorted_logs: list[
                tuple[date, str, dict[str, float | None | str]]
            ]) -> int:
        """Return the ongoing streak ending today or yesterday."""
        if not chronologically_sorted_logs:
            return 0

        logged_dates = [
            log_date for log_date, _, _ in chronologically_sorted_logs
        ]
        latest_log_date = logged_dates[-1]
        if (_today.date() - latest_log_date).days > 1:
            return 0

        streak = 1
        for idx in range(len(logged_dates) - 1, 0, -1):
            if (logged_dates[idx] - logged_dates[idx - 1]).days == 1:
                streak += 1
                continue
            break

        return streak

    @staticmethod
    def _longest_logging_streak(
            chronologically_sorted_logs: list[
                tuple[date, str, dict[str, float | None | str]]
            ]) -> int:
        """Return the longest streak of consecutive logged days."""
        if not chronologically_sorted_logs:
            return 0

        logged_dates = [
            log_date for log_date, _, _ in chronologically_sorted_logs
        ]
        longest = 1
        current = 1

        for idx in range(1, len(logged_dates)):
            if (logged_dates[idx] - logged_dates[idx - 1]).days == 1:
                current += 1
            else:
                longest = max(longest, current)
                current = 1

        return max(longest, current)

    @staticmethod
    def _print_days_rated(logs: dict[str, dict[str, float | None | str]],
                          dateobj_to_ratings: list[tuple[date, float]]) -> None:
        """Print the number of days rated."""
        days_total = len(logs)
        days_rated = len(dateobj_to_ratings)
        output = f"{bol("Days rated:")} {bol(days_rated)} "
        if dateobj_to_ratings:
            first_rated_date = min(_date for _date, _ in dateobj_to_ratings)
            output += f"since {bol(first_rated_date)} "
        if not days_rated == days_total:
            output += f"({days_total} including null ratings)"

        print(output)

    def _print_recent_average_ratings(
            self,
            chronologically_sorted_logs: list[
                tuple[date, str, dict[str, float | None | str]]
            ]) -> None:
        """Print rolling rating averages for recent calendar windows."""
        for days in (7, 30, 365):
            avg = self._recent_average_rating(chronologically_sorted_logs, days)
            label = "1-year" if days == 365 else f"{days}-day"
            if avg is None:
                print(f"Last {label} average: -")
                continue
            print(
                f"{bol(f"Last {label} average:")} "
                f"{bol(f"{avg:g}")}/{self.dqt.max_rating}"
            )

    def _recent_average_rating(
            self,
            chronologically_sorted_logs: list[
                tuple[date, str, dict[str, float | None | str]]
            ], days: int
            ) -> float | None:
        """Return the average rating over the last ``days`` calendar days."""
        cutoff = _today.date() - timedelta(days=days - 1)
        ratings = [
            log[self.json.RATING_KYNAME]
            for log_date, _, log in chronologically_sorted_logs
            if (cutoff <= log_date <= _today.date()
                and log[self.json.RATING_KYNAME] is not None)
        ]

        if not ratings:
            return None

        ratings: list[float]
        return round(sum(ratings) / len(ratings), self.dqt.rating_inp_dp)

    def _print_avg_rating(self, ratings_only: list[float]) -> None:
        """Print average rating for each day of the week."""
        avg = round(
            sum(ratings_only) / len(ratings_only),
            self.dqt.rating_inp_dp
        )
        print(f"{bol("Average rating:")} "
              f"{bol(f"{avg:g}")}/{self.dqt.max_rating}")

    def _print_highest_and_lowest_ratings(
            self, ratings_only: list[float],
            dates_to_ratings: list[tuple[str, float]]) -> None:
        """Print highest and lowest ratings, and the date for each.

        Prints the dates of ALL days that share the highest/lowest rating.
        """
        highest = max(ratings_only)
        lowest = min(ratings_only)

        highest_dates = [
            _date for _date, rating in dates_to_ratings
            if rating == highest
        ]
        lowest_dates = [
            _date for _date, rating in dates_to_ratings
            if rating == lowest
        ]

        print(
            f"{bol("Highest rating:")} "
            f"{bol(f"{highest:g}")}/{self.dqt.max_rating} "
            f"on {self._format_dates(highest_dates)}"
        )
        print(
            f"{bol("Lowest rating:")} "
            f"{bol(f"{lowest:g}")}/{self.dqt.max_rating} "
            f"on {self._format_dates(lowest_dates)}"
        )

    def _print_rating_distribution(
            self, dates_to_ratings: list[tuple[str, float]]) -> None:
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

        print(bol(f"Days rated over {neutral_rat}: {over}"))
        print(bol(f"Days rated at {neutral_rat}: {at}"))
        print(bol(f"Days rated under {neutral_rat}: {under}"))

    def _print_longest_memory_day(
            self,
            chronologically_sorted_logs: list[
                tuple[date, str, dict[str, float | None | str]]
            ]) -> None:
        """Print the day or days with the longest non-empty memory entry."""
        # The below is because we're dealing with the memory entries.
        # But mostly because my type checker is complaining.
        chronologically_sorted_logs: list[tuple[date, str, dict[str, str]]]

        memory_entries: list[tuple[str, str]] = [
            (date_str, log[self.json.MEMORY_KYNAME].strip())
            for _, date_str, log in chronologically_sorted_logs
            if log[self.json.MEMORY_KYNAME].strip()
        ]

        if not memory_entries:
            print("Day with longest memory entry: -")
            return

        longest: str = max([mem for _, mem in memory_entries], key=len)
        max_length: int = len(longest)
        longest_dates = [
            date_str for date_str, memory in memory_entries
            if len(memory) == max_length
        ]

        label = (
            "Day with longest memory entry:"
            if len(longest_dates) == 1
            else "Days with longest memory entry:"
        )
        print(
            f"{bol(label)} {self._format_dates(longest_dates)} "
            f"({max_length} characters, {len(longest.split())} words)"
        )

    def _print_weekdays_ranked(
            self, dateobj_to_ratings: list[tuple[date, float]]) -> None:
        """Print the days of the week in rank order of highest avg rating"""
        weekday_scores: dict[str, list[float]] = defaultdict(list)

        for dateobj, rating in dateobj_to_ratings:
            weekday = dateobj.strftime("%A")
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

        print(f"{bol("Best days of the week")} "
              "(highest to lowest average rating):")
        counter = 0
        for day, value in ranked_days:
            counter += 1
            cleaned_avg = f"{round(value, self.dqt.rating_inp_dp):g}"
            print(f"  #{counter} {bol(day)}: "
                  f"{bol(cleaned_avg)}"
                  f"/{self.dqt.max_rating}")

    @staticmethod
    def _format_dates(dates: list[str]) -> str:
        """Format dates as a string, separated by commas."""
        return ", ".join(dates)
