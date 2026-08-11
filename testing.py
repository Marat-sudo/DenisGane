import tools.rich.game_menus as gm
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time
cs = Console()


def skill_menu(skills):
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
    
    cs.print(table)
    
    
a = {"skills": [
    {
      "name": "firebool",
      "hero_id": 1,
      "damage_multiplier": 1.2,
      "base_damage": 20,
      "mana_cost": 60,
      "cooldown": 4,
      "skill_type": "damage",
      "description": "наносит горящий bool урон",
      "id": 1
    },

    {
      "name": "острый меч",
      "hero_id": 2,
      "damage_multiplier": 1.5,
      "base_damage": 10,
      "mana_cost": 5,
      "cooldown": 3,
      "skill_type": "damage",
      "description": "заостряет меч на один удар",
      "id": 2
    }
  ]
}





panel = Panel(
        "aaaaasd12",
        width=80,
        style="spring_green3",
        border_style="green"
    )




cs.print(panel)