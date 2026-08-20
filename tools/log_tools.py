import time
from rich.console import Console

console = Console()

def log_write(message: str):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def log_clear():
    with open("log.txt", "w", encoding="utf-8") as f:
        f.write("")

def log_success(message: str):
    console.print(f"[bold green]{message}[/bold green]")
    log_write("[SUCCESS] " + message)

def log_warning(message: str):
    console.print(f"[bold yellow]{message}[/bold yellow]")
    log_write("[WARNING] " + message)

def log_error(message: str):
    console.print(f"[bold red]{message}[/bold red]")
    log_write("[ERROR] " + message)

def log_status(message: str):
    console.print(f"[bold cyan]{message}[/bold cyan]")
    log_write("[STATUS] " + message)

def log_output(message: str):
    log_write("[OUTPUT] " + message)