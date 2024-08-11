"""
A small module to store functions used to process data in this 
repo

"""

from datetime import datetime

import altair as alt
from IPython.display import HTML, display




def load_poppins_font():
    """Load the Poppins font from Google Fonts."""
    display(HTML('<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet">'))

def poppins_theme():
    """Define the custom Poppins theme for Altair."""
    return {
        'config': {
            'title': {
                'fontSize': 20,
                'font': 'Poppins',
                'anchor': 'start',
                'color': 'black',
                'anchor': 'middle', # centered
                'fontWeight': 400,
                'dy': -20,
                'dx': 10
            },
            'axis': {
                'labelFontSize': 12,
                'titleFontSize': 14,
                'titleFont': 'Poppins',
                'labelFont': 'Poppins',
                'labelFontSize': 14, 
            },
            'axisX': {  # Configuration specifically for the x-axis
                'labelAngle': 0},
            'legend': {
                'labelFontSize': 12,
                'titleFontSize': 14,
                'titleFont': 'Poppins',
                'labelFont': 'Poppins'
            },
            'bar': {
                'color': 'purple',
                'fill': 'purple'
            },
            'line': {
                'color': 'purple'
            },
            'view': {
                'height': 300,
                'width': 600,  # Default chart width
                'padding': {"top": 190, "left": 10, "right": 10, "bottom": 90}
            }
        }
    }

def register_and_enable_poppins_theme():
    """Register and enable the Poppins theme in Altair."""
    alt.themes.register('poppins_theme', poppins_theme)
    alt.themes.enable('poppins_theme')




# TODO: delete this?
def parse_single_issue(issue) -> dict:
    """
    Parse a single issue from the GitHub API response.

    Parameters
    ----------
    issue : dict
        Dictionary containing information about a single issue.

    Returns
    -------
    dict
        Dictionary containing parsed information about the issue.
    """
    parsed_issue = {}

    # Extract labels
    parsed_issue["labels"] = [
        label["name"] for label in issue.get("labels", [])
    ]

    # Extract header text (title of the issue)
    parsed_issue["header_text"] = issue.get("title", "")

    # Extract date opened
    parsed_issue["date_opened"] = datetime.strptime(
        issue.get("created_at"), "%Y-%m-%dT%H:%M:%SZ"
    )

    # Extract date closed (if available)
    if issue.get("closed_at"):
        parsed_issue["date_closed"] = datetime.strptime(
            issue.get("closed_at"), "%Y-%m-%dT%H:%M:%SZ"
        )
        # Calculate total time issue was open
        time_open = parsed_issue["date_closed"] - parsed_issue["date_opened"]
        parsed_issue["days_open"] = time_open.total_seconds() / (60 * 60 * 24)
    else:
        parsed_issue["date_closed"] = None
        # calculate time delta
        delta = datetime.now() - parsed_issue["date_opened"]
        parsed_issue["days_open"] = delta.days

    return parsed_issue
