from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


def fight_menu(total_mana, current_mana, total_hp, current_hp):
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


    console.print(
        Panel(
            main_content,
            title="ваши действия",
            width=80,
            padding=(0, 1),
            border_style="dim"))


def skill_menu(skills: list):
    table = Table()
    table.add_column("Название")
    table.add_column("номер")
    table.add_column("Тип")
    table.add_column("урон")
    table.add_column("увеличивает урон в Х раз")
    table.add_column("требует маны")
    table.add_column("откат в ходах")
    table.add_column("описание")

    for index, skill in enumerate(skills, start=1):
        tp = skill["name"], index, skill["skill_type"], skill["base_damage"], str(skill["damage_multiplier"] * 100), skill["mana_cost"], skill["cooldown"], skill["description"]
        strtp = tuple(str(x) for x in tp)

        table.add_row(*strtp)
        table.add_section()
    
    console.print(table)
    