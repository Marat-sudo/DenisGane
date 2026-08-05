import requests
from rich import print
from rich.table import Table

import tools.rich.game_menus as gm
import tools.rich.print_info as pf

API_URL = "http://127.0.0.1:8000"
USER_ID = None
PLAYER_ID = None
TABLE_STEP_COLORS = {
    "крит урон": {
        "text": "Нанесён критический урон",
        "title": "red1",
        "table": "dark_red"
    },
    "обычный урон": {
        "text": "Нанесён урон",
        "title": "red3",
        "table": "red3"
    },
    "уворот": {
        "text": "Вы увернулись и не получили урон",
        "title": "bright_cyan",
        "table": "cyan"
    }
}


def game():
    global USER_ID 
    
    def get_user_hero():
        response = requests.post(f"{API_URL}/user/info", json={"id": USER_ID})
        data = response.json()

        players = data["players"]

  
        if len(players) > 0:
            pf.user_hero(players)            

        else:
            print("Нет персонажей")


    def select_player(player_id: int):
        response = requests.post(f"{API_URL}/user/info", json={"id": USER_ID})
        data = response.json()

        players = data["players"]
    
        if player_id -1 >= len(players) or player_id < 0:
            return -1 
        
        return players[player_id -1]["id"]

    def create_player():
        response = requests.get(f"{API_URL}/player/hero/list")
        data = response.json()
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

        response = requests.post(f"{API_URL}/player/create", json=data)
        if response.status_code == 201:
            print(f"Ваш персонаж {nickname} : {heroes[choise]["name"]} успено создан")


    
    def start_fight():
        get_user_hero()
        choise_id = int(input("выберите своего героя из спика: "))
        PLAYER_ID = choise_id


        response = requests.post(f"{API_URL}/locations/list")
        data = response.json()

        pf.all_locations(data["locations"])
        
        choise_loc = int(input("выберите локацию: "))

        response = requests.post(f"{API_URL}/player/update?id={PLAYER_ID}&loc_id={choise_loc}")



        response = requests.post(f"{API_URL}/fight/start?attacker_id={PLAYER_ID}")
        data = response.json()
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

        response = requests.post(f"{API_URL}/fight/history?id={PLAYER_ID}")
        res = response.json()
        
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
        
 
        response = requests.get(f"{API_URL}/fight/ActiveFight?id={PLAYER_ID}")
        if response.status_code != 200:
            print("нет активных боёв")
            return
        data = response.json()
        fight_id = data["id"]

        

        res = requests.get(f"{API_URL}/fight/session/steps?fight_id={fight_id}")
        steps = res.json()
        last_step = steps["steps"][-1]
        


        resSession = requests.get(f"{API_URL}/fight/session/info?fight_id={fight_id}")
        session = resSession.json()



        resPlayer = requests.get(f"{API_URL}/player/info?id={session["attacker_id"]}")
        att_player = resPlayer.json()

        resPlayer = requests.get(f"{API_URL}/player/info?id={session["opponent_id"]}")
        def_player = resPlayer.json()
        

        
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
        step_color = TABLE_STEP_COLORS["крит урон"] if last_step["is_critical"] else TABLE_STEP_COLORS["обычный урон"]
        
        if is_your_turn:
            print("\n")
            pf.step_last(
                step=last_step,
                att_player=att_player,
                def_player=def_player,
                title="Нанесён урон",
                title_style=step_color["title"],
                table_style=step_color["table"]
            )


            print("\n")
            gm.fight_menu(
                player_total_mana,
                player_current_mana,
                player_total_hp,
                player_current_hp
            )

            act_type = int(input("введите что-то "))

            
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



    response = requests.post(f"{API_URL}/user/login", json={"username": username, "password": password})
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
    response = requests.post(f"{API_URL}/user/register", json=data)
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