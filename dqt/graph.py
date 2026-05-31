import math
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from types import NoneType

from dqt.json_manager import JSONManager

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from dqt.tracker import Tracker


class Graph:
    """A class to manage graph plotting for day_quality_tracker."""
    
    _CONFIG_KEYS: dict[str, type | tuple[type, ...]] = {
        'graph_style': (str, NoneType),
        'graph_show_block': bool,
        'title': str,
        'title_fontsize': (float, int, str),
        'title_padding': (float, int),
        'xlabel_fontsize': (float, int, str),
        'ylabel_fontsize': (float, int, str),
        'tick_labels_fontsize': (float, int, str),
        'graph_date_format': str,
        'autofmt_xdates': bool,
        'year_labels_fontsize': (float, int, str),
        'year_labels_fontweight': (int, str),
        'line_width': (float, int),
        'line_color': (str, tuple, NoneType),
        'line_style': str,
        'marker': str,
        'marker_size': (float, int),
        'marker_face_color': (str, tuple, NoneType),
        'marker_edge_width': (float, int),
        'neutralline_width': (float, int),
        'neutralline_color': (str, tuple, NoneType),
        'neutralline_style': str,
        'averageline_width': (float, int),
        'averageline_color': (str, tuple, NoneType),
        'averageline_style': str,
        'highest_rating_point_size': (float, int),
        'highest_rating_point_color': (str, tuple, NoneType),
        'lowest_rating_point_size': (float, int),
        'lowest_rating_point_color': (str, tuple, NoneType),
        'legend_fontsize': (float, int),
        'legend_loc': (str, tuple),
        'legend_frameon': bool,
    }
    
    def __init__(self, dqt: Tracker):
        """Get required DQT attributes and initialize graph settings."""
        # DayQualityTracker attributes
        self.dqt: Tracker = dqt
        self.json: JSONManager = dqt.json
        
        # Graph settings
        self.graph_show_block: bool = True
        
        self.graph_style: str | None = 'ggplot'
        
        self.title: str = "Day Quality Ratings"
        self.title_fontsize: float | int | str = 20
        self.title_padding: float | int = 18
        
        self.xlabel: str = "Date"
        self.xlabel_fontsize: float | int | str = 14
        self.ylabel: str = "Rating"
        self.ylabel_fontsize: float | int | str = 14
        
        self.tick_labels_fontsize: float | int | str = 7
        self.max_xticks: int = 15  # None = no limit
        
        self.graph_date_format: str = '%a %b %d'
        self.autofmt_xdates: bool = True
        
        self.year_labels_fontsize: float | int | str = 9
        self.year_labels_fontweight: int | str = 'bold'
        
        self.line_label: str = "Ratings"
        self.line_width: float | int = 2
        self.line_color: str | tuple | None = None
        self.line_style: str = '-'
        
        self.marker: str = 'o'
        self.marker_size: float | int = 4
        self.marker_face_color: str | tuple | None = None
        self.marker_edge_width: float | int = 0
        
        self.neutralline_label: str = 'Neutral rating (baseline)'
        self.neutralline_width: float | int = 1
        self.neutralline_color: str | tuple | None = 'black'
        self.neutralline_style: str = '--'
        
        self.averageline_label: str = 'Average rating'
        self.averageline_width: float | int = 1
        self.averageline_color: str | tuple | None = 'red'
        self.averageline_style: str = '-.'
        
        self.highest_rating_label: str = 'Highest rating'
        self.highest_rating_point_size: float | int = 20
        self.highest_rating_point_color: str | tuple | None = 'green'
        self.highest_rating_point_zorder: int = 5
        
        self.lowest_rating_label: str = 'Lowest rating'
        self.lowest_rating_point_size: float | int = 20
        self.lowest_rating_point_color: str | tuple | None = 'orange'
        self.lowest_rating_point_zorder: int = 5
        
        self.legend_fontsize: float | int = 8
        self.legend_loc: str | tuple = 'upper right'
        self.legend_frameon: bool = True
    
    def view_ratings_graph(self) -> None:
        """Display current ratings graph."""
        print("\nBuilding graph...")
        self._build()
        print("\nDisplaying graph...")
        if self.graph_show_block:
            print("\n[Close the graph window to continue]")
        self._show()
        
    def _build(self) -> None:
        """Build the graph and initialize plt, fig, and ax properties."""
        logs = self.json.logs
        if self.json.no_logs():
            raise ValueError("No logs saved")
        
        dates, ratings = self._fill_missing(
            sorted(
                datetime.strptime(d, self.dqt.date_format)
                for d in self.json.logs.keys()
            )
        )
        
        # Close existing windows to prevent overlapping
        plt.close('all')
        
        if not logs:
            raise ValueError("No logs saved")
        
        if self.graph_style is None:
            plt.style.use('default')
        else:
            plt.style.use(self.graph_style)
        
        fig, ax = plt.subplots()
        
        self._set_title(ax)
        self._draw_xylabels(ax)
        self._set_ticks(fig, ax, dates)
        
        self._plot_ratings(ax, dates, ratings)
        self._draw_neutral_rating_line(ax)
        self._draw_average_rating_line(ax, ratings)
        self._plot_highest_lowest_ratings(ax, dates, ratings)
        
        self._draw_year_labels(ax, dates)
        
        self._set_ylimits(ax)
        
        self._draw_legend(ax)
        
    def _show(self) -> None:
        """Show the graph."""
        plt.show(block=self.graph_show_block)
        plt.pause(0.1)
    
    @staticmethod
    def close() -> None:
        """Close the graph."""
        plt.close('all')
        
    def configure(self, **configs: str | float | int | bool | tuple) -> None:
        """Update configuration options via keyword arguments.
        
        Must be called before `run()`.
        Raises:
            ValueError: Invalid configuration option
            TypeError: Incorrect type
        """
        for config_name, value in configs.items():
            if config_name not in self._CONFIG_KEYS:
                raise ValueError(
                    f"Invalid configuration option: '{config_name}'"
                )
            expected = self._CONFIG_KEYS[config_name]
            if not isinstance(value, expected):
                expected_name = (
                    expected.__name__
                    if isinstance(expected, type)
                    else " or ".join(t.__name__ for t in expected)
                )
                raise TypeError(
                    f"Expected {expected_name} for configuration "
                    f"'{config_name}', got {type(value).__name__} instead"
                )
            setattr(self, config_name, value)
        
    def _fill_missing(self, dates: list[datetime]) \
            -> tuple[list[datetime], list[float | None]]:
        """Fill in missing ratings with None."""
        start = dates[0]
        end = dates[-1]
        
        full_dates = []
        full_ratings = []
        
        current = start
        while current <= end:
            key = current.strftime(self.dqt.date_format)
            full_dates.append(current)
            full_ratings.append(
                self.json.logs.get(key, {}).get(self.json.RATING_KYNAME)
            )
            current += timedelta(days=1)
            
        return full_dates, full_ratings
    
    def _set_title(self, ax: plt.Axes) -> None:
        """Set the title of the graph."""
        ax.set_title(
            self.title,
            fontsize=self.title_fontsize,
            pad=self.title_padding,
        )
        
    def _draw_xylabels(self, ax: plt.Axes) -> None:
        """Draw x and y labels."""
        ax.set_xlabel(self.xlabel, fontsize=self.xlabel_fontsize)
        ax.set_ylabel(self.ylabel, fontsize=self.ylabel_fontsize)
        
    def _set_ticks(self,
                   fig: plt.Figure,
                   ax: plt.Axes,
                   dates: list[datetime]) -> None:
        """Set tick label sizes, format dates, and set y-tick increments."""
        ax.tick_params(labelsize=self.tick_labels_fontsize)
        
        # ---- x-ticks ----
        if not dates:
            return
        
        # Prevent date clustering by reducing shown dates
        shown_dates = dates
        if self.max_xticks is not None:
            if len(dates) > self.max_xticks:
                step = math.ceil(len(dates) / self.max_xticks)
                shown_dates = dates[::step]
        
        ax.set_xticks(shown_dates)
        ax.set_xticklabels(
            [d.strftime(self.graph_date_format) for d in shown_dates],
            fontsize=self.tick_labels_fontsize,
        )
        
        if self.autofmt_xdates and len(shown_dates) > 1:
            fig.autofmt_xdate()
        
        # ---- y-ticks ----
        ax.set_yticks(
            range(self.dqt.min_rating, self.dqt.max_rating + 1)
        )
    
    def _plot_ratings(self, ax: plt.Axes, dates: list[datetime],
                      ratings: list[float | None]) -> None:
        """Plot rating values."""
        ax.plot(
            dates,
            ratings,
            linewidth=self.line_width,
            linestyle=self.line_style,
            marker=self.marker,
            markersize=self.marker_size,
            markerfacecolor=self.marker_face_color,
            markeredgewidth=self.marker_edge_width,
            label=self.line_label,
        )
    
    def _draw_year_labels(self, ax: plt.Axes, dates: list[datetime]) -> None:
        """Draw year labels."""
        shown_years = set()
        for i, date in enumerate(dates):
            year = date.year
            
            if year not in shown_years:
                x = i / (len(dates) - 1) if len(dates) > 1 else 0.5
                ax.text(
                    x,
                    1,
                    str(year),
                    transform=ax.transAxes,
                    ha='center',
                    va='bottom',
                    fontsize=self.year_labels_fontsize,
                    fontweight=self.year_labels_fontweight
                )
                shown_years.add(year)
    
    def _draw_neutral_rating_line(self, ax: plt.Axes) -> None:
        """Draw horizontal neutral rating line."""
        ax.axhline(
            y=self.dqt.neutral_rating,
            color=self.neutralline_color,
            linewidth=self.neutralline_width,
            linestyle=self.neutralline_style,
            label=self.neutralline_label,
        )
        
    def _draw_average_rating_line(self, ax: plt.Axes,
                                  ratings: list[float | None]) -> None:
        """Draw horizontal average rating line."""
        avg = self._average_rating(ratings)
        if avg is None:
            return
        ax.axhline(
            y=round(avg, self.dqt.rating_inp_dp),
            color=self.averageline_color,
            linewidth=self.averageline_width,
            linestyle=self.averageline_style,
            label=self.averageline_label,
        )
    
    def _average_rating(self, ratings: list[float | None]) -> float | None:
        """Return average rating."""
        clean = [r for r in ratings if r is not None]
        if not clean:
            return None
        return round(sum(clean) / len(clean), self.dqt.rating_inp_dp)
    
    def _plot_highest_lowest_ratings(self,
                                     ax: plt.Axes,
                                     dates: list[datetime],
                                     ratings: list[float | None]) -> None:
        """Plot highest and lowest rating values as points."""
        indexed = [(i, r) for i, r in enumerate(ratings) if r is not None]
        if not indexed:
            return
        
        values = [r for _, r in indexed]
        max_val = max(values)
        min_val = min(values)
        
        max_indices = [i for i, r in indexed if r == max_val]
        min_indices = [i for i, r in indexed if r == min_val]
        
        ax.scatter(
            [dates[i] for i in max_indices],
            [max_val] * len(max_indices),
            label=self.highest_rating_label,
            s=self.highest_rating_point_size,
            color=self.highest_rating_point_color,
            zorder=self.highest_rating_point_zorder,
        )
        
        ax.scatter(
            [dates[i] for i in min_indices],
            [min_val] * len(min_indices),
            label=self.lowest_rating_label,
            s=self.lowest_rating_point_size,
            color=self.lowest_rating_point_color,
            zorder=self.lowest_rating_point_zorder,
        )
    
    def _set_ylimits(self, ax: plt.Axes) -> None:
        """Set y-limits."""
        ax.set_ylim(self.dqt.min_rating, self.dqt.max_rating + 1)
    
    def _draw_legend(self, ax: plt.Axes) -> None:
        """Draw legend."""
        ax.legend(
            fontsize=self.legend_fontsize,
            loc=self.legend_loc,
            frameon=self.legend_frameon,
        )
