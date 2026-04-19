"""Customize DQT behavior and settings here.

Make sure to enter values with the right data type. Incorrect data types will
raise an error. You will be notified to fix the issue before proceeding.

Adding unknown configurations will raise an error. You will be notified to fix
the issue before proceeding.

If any configuration is removed, the default value will be used.
"""

from typing import Any

CONFIGS: dict[str, dict[str, Any]] = {
    
    # UI BEHAVIOR & SETTINGS
    #                                          CONFIGURATION DESCRIPTION:
    'tracker': {
        'min_time': 20,  #                     Earliest hour of day a log entry is accepted (0 = no limit)
        'min_rating': 1,  #                    Minimum day quality rating (1 recommended)
        'max_rating': 20,  #                   Maximum day quality rating (even number recommended)
        'rating_inp_dp': 2,  #                 Number of decimal units ratings are rounded to
        'linewrap_maxcol': 70,  #              Line width at which long lines are wrapped
        'date_format': '%Y-%m-%d',  #          ★ Date format used
        'date_format_print': 'YYYY-MM-DD',  #  Date format represented as a user-friendly string
        'clock_format_12': True,  #            Whether time will be printed in 12-hour clock format (24-hour otherwise)
        'enable_ansi': None,  #                Whether to enable ANSI escape codes for text coloring and styling (`None`
        #                                          = automatically detect terminal compatibility, not so reliable)
        'autofill_json': True,  #              Whether the program should silently fill in missing values in the JSON
        #                                          file where possible. If `True`, ratings will be set to `None` if
        #                                          not found, and memory entries will be set to an empty string. If
        #                                          `False`, an error will be raised instead.
    },
    
    # GRAPH APPEARANCE & SETTINGS
    
    'graph': {
        'graph_style': 'ggplot',  #                * Graph style (None = default style)
        'graph_show_block': True,  #               Whether the program should pause while the graph is open (`True`
        #                                              recommended for macOS, based on what I have tested)
        'title': 'Day Quality Ratings',  #         Graph title text
        'title_fontsize': 20,  #                   Title font size (pt, 1 point = 1/72 inches)
        'title_padding': 18,  #                    Title padding (pt)
        'xlabel_fontsize': 14,  #                  X-axis label font size (pt)
        'ylabel_fontsize': 14,  #                  Y-axis label font size (pt)
        'tick_labels_fontsize': 7,  #              Tick labels fontsize (pt)
        'graph_date_format': '%a %b %d',  #        ★ Date format shown on graph (see matplot)
        'autofmt_xdates': True,  #                 Whether to rotate date labels to prevent clustering
        'year_labels_fontsize': 9,  #              Year labels font size (pt)
        'year_labels_fontweight': 'bold',  #       Year labels font weight (pt)
        'line_width': 2,  #                        Ratings line width (pt)
        'line_color': None,  #                     Ratings line color (None = default color)
        'line_style': '-',  #                      * Ratings line style
        'marker': 'o',  #                          * Rating points marker style
        'marker_size': 4,  #                       Rating points size (pt)
        'marker_face_color': None,  #              Rating points color (None = default color)
        'marker_edge_width': 0,  #                 Rating points edge width (pt)
        'neutralline_width': 1,  #                 Neutral rating line width (pt)
        'neutralline_color': 'black',  #           Neutral rating line color
        'neutralline_style': '--',  #              * Neutral rating line style
        'averageline_width': 1,  #                 Average rating line width (pt)
        'averageline_color': 'red',  #             Average rating line color
        'averageline_style': '-.',  #              * Average rating line style
        'highest_rating_point_size': 20,  #        Highest rating point size (pt)
        'highest_rating_point_color': 'green',  #  Highest rating point color (None = default color)
        'lowest_rating_point_size': 20,  #         Lowest rating point size (pt)
        'lowest_rating_point_color': 'orange',  #  Lowest rating point color (None = default color)
        'legend_fontsize': 8,  #                   Legend text font size (pt)
        'legend_loc': 'upper right',  #            Location of legend on graph
        'legend_frameon': True,  #                 Whether to show the legend in a box
    }
    
    # * = See more options in the official Matplotlib documentation
    #     at https://matplotlib.org/stable
    # ★ = See more information on date format codes in the official Python documentation at
    #     https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
}
