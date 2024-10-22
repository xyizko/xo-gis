#####################################################
# Banner function that gets banner at initialization
####################################################

import logging
import requests as rq

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

install(show_locals=True)

console = Console()

# --- Code section below ---

# Banner url 
url = [
    "https://snips.sh/f/ZuwtQ3Pk0x?r=1",
]

# Grabs banner 
def banr() -> None:
    """
    Function for grabbing the banner via curl
    """
    logging.basicConfig(
        level="DEBUG",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    logger = logging.getLogger(__name__)

    for x in url:
        try:
            r = rq.get(x)
            r.raise_for_status()  # Raises an HTTPError for bad responses
            logger.info(f"Success: Status code {r.status_code}")
            print(r.text)  # This will print the response text to the console
        except rq.RequestException as e:
            logger.error(
                f"Failed to fetch {x}. Status code: {e.response.status_code if e.response else 'N/A'}. Error: {str(e)}"
            )
            console.rule(f"[bold red] {x} [/bold red]", style="bold red")
