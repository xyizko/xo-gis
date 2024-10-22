########################
# Entry Point
########################

import asyncio

from rich.console import Console
from rich.traceback import install

from src.banner import banr
from src.scraper import gis

install(show_locals=True)
console = Console()

# --- Code section below ---


def main():
    banr() # Banner Function
    asyncio.run(gis()) # Call to scraping function
    console.rule(f"[green]DONE[/green]", style="green")


if __name__ == "__main__":
    main()
