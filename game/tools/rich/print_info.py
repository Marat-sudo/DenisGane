from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import tools.requests_funs.querys as  qu

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

    for step in steps:
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
    title += step["description"]

    if step["combo_count"] >= 3:
        title = title + f"\nТекущие комбо противника: {step["combo_count"]}, умножитель урона: {step["combo_bonus_damage"]}%"
    panel = Panel(
        title,
        width=80,
        style=title_style,
        border_style=border_style
    )

    console.print(panel)
    


def player_act_effect(act_effects: list):
    text = ""
    stats = {
        "hp_per_turn": "hp/ход",
        "attack": "атаки",
        "agility": "ловкости",
        "defense": "защиты",
    }
     
    for act_eff in act_effects:
        eff_type = qu.get_effect_info(act_eff["effect_type_id"])
        
        color = "green" if eff_type["type"]  == "buff" else "red" 
        
        eff = f"[{color}]{eff_type["name"]}[/{color}]   "
        eff += "+" if eff_type["type"]  == "buff" else " "
        eff += str(eff_type["modifier_value"])
        eff += "% " if eff_type["modifier_type"] == "percent" else " "
        eff += f"{stats[eff_type["affected_stat"]]}   ({act_eff["turns_remaining"]})\n"
        
        text += eff

    return text



def player_static_field_get_print(player, cur_hp, get=False):
    title = f"{player["nickname"]} \nHp: {cur_hp}/{player["max_hp"]}\n"
    title += f"attack: {player["attack"]}\n"
    title += f"defense: {player["defense"]}\n"
    title += f"agility: {player["agility"]}\n"
    title += f"mana: {player["max_mana"]}\n"

    if get:
        return title
    panel = Panel(
        title,
        expand=False
    )

    console.print(panel)


def player_info_get_print(player, pl_cur_hp, session, get=False):
    title = player_static_field_get_print(player, pl_cur_hp, True)
    title += "\nАктивные эффекты: \n"
    
    

    act_effects = qu.get_active_effect(session["id"], player["id"])["effects"]

   
    if act_effects:
        title += player_act_effect(act_effects)

    if get:
        return title
    
    panel = Panel(
        title,
        expand=False
    )

    console.print(panel)
    

def player_step(player, opponent, pl_cur_hp, opp_cur_hp, opp_old_hp, step, session, style):

    title = player_info_get_print(player, pl_cur_hp, session, True)
    title += "\n"
    match step["action_type"]:
        case "attack":
            act = f"Вы нанесли {step["damage_dealt"]} урона понизив хп противника с {opp_old_hp} до {opp_cur_hp}" 
        case "skill":
            skill_id = step["skill_id"]
            if skill_id:
                skill = qu.get_skill_info(skill_id)
            

            if skill["applies_effect_id"]:
                effect = qu.get_effect_info(skill["applies_effect_id"])


            match skill["skill_type"]:
                case "damage":
                    # TODO тут криво отображается олд хп  Вы нанесли 15.0 урона понизив хп противника с 66.0 до 66.0
                    act = f"Вы нанесли навыком {skill["name"]} {step["damage_dealt"]} урона понизив хп противника с {opp_old_hp} до {opp_cur_hp}"
                
                case "heal":
                     act = f"вы повысили своё здоровье с {pl_cur_hp - skill["damage"]} до {pl_cur_hp}"
                
                case "debuff":
                    act_eff = qu.get_active_effect_by_id(skill["applies_effect_id"], session["id"], opponent["id"])["effects"]  
                    print(act_eff)

                    if effect["affected_stat"] == "hp_per_turn":
                        act = f"вы нанесли дот на противника потребляющий {effect["modifier_value"]}hp/ход"
                    
                    else:
                        stat = player[effect["affected_stat"]]
                        act = f"вы нанесли дебафф понижающий характеристику врага {effect["affected_stat"]}, с {stat - act_eff[-1]["final_addition"]} {stat}"
            
                        
                        
                case "buff":
                    stat = player[effect["affected_stat"]]
                    act_eff = qu.get_active_effect_by_id(skill["applies_effect_id"], session["id"], player["id"])["effects"]
                    print(skill["applies_effect_id"], session["id"], opponent["id"])
                    print(act_eff)
                    
                    
                    act = f"вы нанесли бафф повышаюший вашу характеристику {effect["affected_stat"]}, с {stat - act_eff[-1]["final_addition"]} {stat}"
            


        case "dodge":
            act = f"{opponent["nickname"]} увернулся от вашей атаки не получим урон ({opp_old_hp} -> {opp_cur_hp})"
    
    title += act

    panel = Panel(
        title,
        expand=False
    )

    console.print(panel)


def fight_end(session, player_id):
    if session["winner_id"] == player_id:
        op_id = session["attacker_id"] if session["attacker_id"] != player_id else session["opponent_id"]
        opponent = qu.get_player_info(op_id)
        
        title = f"Вы одолели {opponent["nickname"]} {opponent["level"]} уровня" 

        title_style = "spring_green3"

        border_style = "green"
    else:
        op_id = session["attacker_id"] if session["attacker_id"] != player_id else session["opponent_id"]
        opponent = qu.get_player_info(op_id)
        
        title = f"Вы проиграли {opponent["nickname"]} {opponent["level"]} уровня" 

        title_style = "bright_red"

        border_style = "red1"
    panel = Panel(
        title,
        width=80,
        style=title_style,
        border_style=border_style
    )