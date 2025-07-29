rich_logging = True

import logging
import rich.console
logging.basicConfig(level=logging.INFO)

class RichLogger():

    def __init__(self):
        self.logging = rich
        self.console = rich.console.Console()

    def getLogger(self,__name__: str):
        self.name = __name__
        return self
    
    def error(self,msg):
        self.console.print(f"[red]ERROR: {msg}[/red]")
    def warning(self,msg):
        self.console.print(f"[yellow]WARNING: {msg}[/yellow]")
    def info(self,msg):
        self.console.print(f"[green]INFO: [/green]{msg}")
    

logging = RichLogger()


