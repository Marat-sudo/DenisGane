import requests
from rich import print
from rich.table import Table

import tools.requests_funs.querys as qu
import tools.rich.game_menus as gm
import tools.rich.print_info as pf

API_URL = "http://127.0.0.1:8000"
USER_ID = None
PLAYER_ID = None
STEP_COLORS = {
    "крит урон": {
        "text": "Нанесён критический урон",
        "title": "red1",
        "border": "dark_red"
    },
    "обычный урон": {
        "text": "Нанесён урон",
        "title": "red3",
        "border": "red3"
    },
    "уворот": {
        "text": "Вы увернулись и не получили урон",
        "title": "bright_cyan",
        "border": "cyan"
    }
}

def fight(max_mana: int, cur_mana: int, max_hp: int, cur_hp: int, skills: list):
        while True:
            gm.fight_menu(
                    max_mana,
                    cur_mana,
                    max_hp,
                    cur_hp
                )

            choise = int(input("действие: "))
            
            if choise not in (1, 2):
                print("неверный ввод")
                continue

            if choise == 2:
                print("0 - вернуться назад")
                sk = select_skill(skills)
            
            if sk:
                return choise, sk


            return choise, None


def select_skill(skills: list):
    while True:
        gm.skill_menu(
                skills
            )

        choise = int(input("действие: "))
            
        if choise > len(skills):
            print("неверный ввод")
            continue

        if choise != 0 :
            return skills[choise - 1]
            
        return None


def game():
    global USER_ID 
    
    def get_user_hero():
        data = qu.get_user_info(USER_ID)

        players = data["players"]

  
        if len(players) > 0:
            pf.user_hero(players)            

        else:
            print("Нет персонажей")


    def select_player(player_id: int):
        data = qu.get_user_info(USER_ID)

        players = data["players"]
    
        if player_id -1 >= len(players) or player_id < 0:
            return -1 
        
        return players[player_id -1]["id"]

    def create_player():
        data = qu.get_heroes()
        heroes = data["heroes"]
        
        pf.all_heroes(heroes)
            
        choise = int(input("\nВыбор номера героя: ")) - 1
        
        hero_id = heroes[choise]["id"]
        nickname = input("Введите nickname вашего персонажа: ")
        data = {
            "nickname" : nickname,
            "hero_id" : hero_id,
            "user_id" : USER_ID
        }

        response = qu.post_create_player(data)
        if response.status_code == 201:
            print(f"Ваш персонаж {nickname} : {heroes[choise]["name"]} успено создан")


    
    def start_fight():
        get_user_hero()
        choise_id = int(input("выберите своего героя из спика: "))
        PLAYER_ID = choise_id


        
        data = qu.get_locations()

        pf.all_locations(data["locations"])
        
        choise_loc = int(input("введите номер локации, 0 - остаться на прежней\nвыберите локацию: "))

        if choise_loc != 0:
            qu.put_update_player_loc(PLAYER_ID, choise_loc)
        
        qu.post_start_fight(PLAYER_ID)


        response = qu.get_player_active_fight(PLAYER_ID)
        if response.status_code != 200:
            print("какая-то ошибка")
            return
        data = response.json()
        fight_id = data["id"]
        session = qu.get_session_info(fight_id)

        player = qu.get_player_info(session[str(PLAYER_ID)])

        act_type, skill = fight(
            max_mana=player["max_mana"],
            cur_mana=session["attacker_mana"],
            max_hp=player["max_hp"],
            cur_hp=session["attacker_current_hp"]    
        )

        skills = qu.get_player_skills(PLAYER_ID)["skills"]


        match act_type:
            case 1:
                qu.post_fight_step(session["id"])
            case 2:
                qu.post_fight_step(session["id"], skill["id"])
                
                
                
    

        # if data["detail"] == "вы уже находитесь в бою":
        #     print("вы уже находитесь в бою")
        #     return

        # if data["detail"]["winner"]["id"] == PLAYER_ID:
        #     title = "[green][bold]Выигрыш[/bold][/green]"
        #     color = "green"
        # else:
        #     title = "[red][bold]Проигрыш[/bold][/red]"
        #     color = "red"

        # detail = data["detail"]
        # mes = f"""
        # attacker: {detail["attacker"]["nickname"]} {detail["attacker"]["level"]}
        # opponent: {detail["opponent"]["nickname"]} {detail["opponent"]["level"]}
        # message: {detail["message"]}
        # """
        # res = Panel(mes, title=title, border_style=color)
        # # print(data)
        # print(res)
        

    def user_statistics():
        get_user_hero()
        choise_id = int(input("выберите своего героя из спика: "))
        PLAYER_ID = select_player(choise_id)

        
        res = qu.get_player_fight_history(PLAYER_ID)
        
        data = res["fights"]


        if data == []:
            print("нет статистики")
            return

        pf.user_statistics(data, PLAYER_ID)

    def fight_step():
        """отображает все ходы текущей битвы"""
        get_user_hero()
        choise_id = int(input("выберите своего героя из спика: "))
        PLAYER_ID = select_player(choise_id)
        
 
        response = qu.get_player_active_fight(PLAYER_ID)
        if response.status_code != 200:
            print("нет активных боёв")
            return
        data = response.json()
        fight_id = data["id"]

        
        steps = qu.get_session_steps(fight_id)

        print(steps)
        last_step = steps["steps"][-1]
        

        session = qu.get_session_info(fight_id)

        att_player = qu.get_player_info(session["attacker_id"])

        def_player = qu.get_player_info(session["opponent_id"])
        

        
        pf.player_steps(steps, att_player, def_player)

        
        if session["attacker_id"] == PLAYER_ID:
            player_total_mana = att_player["max_mana"]
            player_current_mana = session["attacker_mana"]
            player_total_hp = att_player["max_hp"]
            player_current_hp = session["attacker_current_hp"]

        else:
            player_total_mana = def_player["max_mana"]
            player_current_mana = session["opponent_mana"]
            player_total_hp = def_player["max_hp"]
            player_current_hp = session["opponent_current_hp"]

        is_your_turn = (session["attacker_turn"] and session["attacker_id"] == PLAYER_ID) or (not session["attacker_turn"] and session["opponent_id"] == PLAYER_ID)
        step_color = STEP_COLORS["крит урон"] if last_step["is_critical"] else STEP_COLORS["обычный урон"]
        
        if is_your_turn:
            print("\n")
            pf.step_last(
                step=last_step,
                title=step_color["text"],
                title_style=step_color["title"],
                border_style=step_color["border"]
            )


            print("\n")
            act_type = fight(
                max_mana=player_total_mana,
                cur_mana=player_current_mana,
                max_hp=player_total_hp,
                cur_hp=player_current_hp    
                )
    

            
            
            # TODO я устал
            print("")
        

        else:
            print("вы ожидайете действия врага")


        
    while True:
        text = """
        1. Просмотр персонажей;
        2. Создать персонажей;
        3. Мой профиль
        4. отправитсья в бой
        5. статистика
        6. состояние битвы
        0. Выйти.
        """
        choise = int(input(f"{text}\n Выбор: "))
        if choise == 1:
            get_user_hero()
        elif choise == 2:
            create_player()
        elif choise == 4:
            start_fight()
        elif choise == 5:
            user_statistics()
        elif choise == 6:
            fight_step()



def login():
    global USER_ID
    username = input("введите usenname: ").strip()
    password = input("введите password: ").strip()


    
    response = qu.post_login(data={"username": username, "password": password}) 
    if (response.status_code == 200):
        data = response.json()
        USER_ID = data["id"]
       
        game()

    else:
        print(response.content)
    

def register():
    global USER_ID
    username = input("Введите имя: ").strip()
    password = input("Введите пароль: ").strip()
    data = {"username": username, "password": password}

    response = qu.post_register(data)
    print(response.content)

    if (response.status_code == 201):
        data = response.json()
        USER_ID = data["id"]
        
        game()
    else:
        print("Error")

while True:
    text =  """
            1. войти по nickname
            2. Регистрация
            0. выйти
            """
    
    choise = int(input(text))

    if (choise == 1):
        login()
    
    elif (choise == 2):
        register()

    elif (choise == 0):
        exit()