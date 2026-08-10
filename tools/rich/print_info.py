from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def user_hero(players: list):
    table = Table(
                title="Персонажи",
                show_header=False,
                show_edge=True,
                show_lines=True,
                box=box.ROUNDED,
                padding=(0, 1)  )
  
    for index, player in enumerate(players):
        text = ""

        text += f"nickname: {player["nickname"]}\n"
        text += f"id героя: {player["hero_id"]}\n"
        text += f"уровнь игрока: {player["level"]}\n"
        text += f"количество опыта игрока: {player["exp"]}"

        table.add_row(text)

    
    console.print(table)

def all_heroes(heroes: list):
    table = Table(
                title="Персонажи",
                show_header=False,
                show_edge=True,
                show_lines=True,
                box=box.ROUNDED,
                padding=(0, 1))

    for index, hero in enumerate(heroes):
        text = ""
        text += f"название героя: {hero["name"]}\n"
        text += f"номер героя: {index + 1}"
        table.add_row(text)

       
    console.print(table)



def all_locations(locs: list):
    table = Table(title="локации")

    table.add_column("название")
    table.add_column("описание")
    table.add_column("минимальный уровень")
    table.add_column("номер")
    
        
    for loc in locs:
        table.add_row(loc["name"], loc["didescription"], str(loc["min_level"]), str(loc["id"]))


    console.print(table)

def user_statistics(data, player_id):
    table = Table(title="[bold]статистика", show_lines=True)

    table.add_column("[green]айди победителя[/green]")
    table.add_column("[red]айди проиграшего[/red]")
    table.add_column("[cyan]дата[/cyan]")

    win_count = 0
    los_count = 0
    for fight in data:
        if fight["winner_id"] == player_id:
            table.add_row(str(fight["winner_id"]), str(fight["loser_id"]), str(fight["fight"]), style="green")
            win_count += 1
        else:
            table.add_row(str(fight["winner_id"]), str(fight["loser_id"]), str(fight["fight"]), style="red")
            los_count += 1
    
    
    console.print(table)

    console.print("[bolt]ИТОГ")
    console.print(f"[green]{win_count} побед")
    console.print(f"[red]{los_count} поражений")
    console.print(f"[magenta]в процентах {(win_count / (win_count + los_count)) * 100}% побед")


def player_steps(steps: list, att_player: dict, def_player: dict):
    table = Table(title="[bold]Логи битвы")
    table.add_column("атакующий")
    table.add_column("тип атаки")
    table.add_column("всего нанёс урона")
    table.add_column("описание")

    for step in steps["steps"]:
        if step["attacker_id"] == att_player["id"]:
            player = att_player
        else:
            player = def_player

        table.add_row(player["nickname"], step["action_type"],str( step["damage_dealt"]), step["description"])
        table.add_section()
    console.print(table)


def step_last(step: dict, title: str, title_style: str, border_style: str):
    """
    при крит ударе
    red1 - для заголовка
    dark_red - для рамки 

    если не крит урон
    red3 - для рамки и заголовка

    уворот 
    bright_cyan - заголовок
    cyan - рамки
    """
    panel = Panel(
        title,
        width=80,
        style=title_style,
        border_style=border_style
    )
    
    
    console.print(panel)