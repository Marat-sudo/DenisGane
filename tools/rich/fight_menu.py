from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.text import Text
from rich.console import Console, Group
from rich.progress import Progress, BarColumn, MofNCompleteColumn, TextColumn
console = Console()


def fight_menu(total_mana, total_hp, current_mana, current_hp):
    buttons = [
        Panel("[1] обычная атака", padding=(0, 1)),
        Panel("[2] навыки", padding=(0, 1)),
        Panel("[3] персонаж", padding=(0, 1)),
        Panel("[4] уклонение", padding=(0, 1)),
        
    ]
    centered_content = Align.center(
        Columns(buttons, padding=1)
    )

    progress = Progress(
        TextColumn("Мана"),
        BarColumn(bar_width=30, complete_style="blue", finished_style="blue"),
        MofNCompleteColumn(),
    )
    task_id = progress.add_task("Прогресс:", total=total_mana, completed=current_mana)


    progress_hp = Progress(
        TextColumn(" hp "),
        BarColumn(bar_width=30, complete_style="red", finished_style="red"),
        MofNCompleteColumn(),   # для точных чисел
    )
    task_hp = progress_hp.add_task("hp:", total=total_hp, completed=current_hp)


    pr_bar_centered = Align.center(
        Group(progress_hp, progress)
    )

    main_content = Group(
        centered_content,
        Text(""),
        pr_bar_centered
    )


    console.print(Panel(
        main_content,
        width=80,
        padding=(0, 1),
        border_style="dim"))

