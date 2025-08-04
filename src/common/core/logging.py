rich_logging = True

import logging as logging
import rich.console
logging.basicConfig(level=logging.INFO)

class RichLogger():

    def __init__(self):
        self.console: rich.console.Console = rich.console.Console()

    def getLogger(self,__name__: str):
        return self
    
    def error(self,msg: str):
        self.console.print(f"[red]ERROR: {msg}[/red]")
    def warning(self,msg: str):
        self.console.print(f"[yellow]WARNING: {msg}[/yellow]")
    def info(self,msg: str):
        self.console.print(f"[green]INFO: [/green]{msg}")
    

logging = RichLogger()


