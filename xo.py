from rich.traceback import install
import asyncio
from rich.console import Console
from src.banner import banr
from src.scraper import gis

install(show_locals=True)
console = Console()

### Code ###


def main():
    banr()
    asyncio.run(gis())
    console.rule(f"[green]DONE[/green]", style="green")


if __name__ == "__main__":
    main()
