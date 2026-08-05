import tools.rich.game_menus as gm
from rich.console import Console
from rich.table import Table
import time


cs = Console()
table = Table(title="asd", title_style="bright_cyan", style="cyan")
table.add_column("атакующий")
table.add_column("тип атаки")
table.add_column("всего нанёс урона")
table.add_column("описание")
cs.print("[blink]123[/blink]\n[italic]123[/italic]")

table.add_row("1", "2","3", "4")

cs.print(table)
    