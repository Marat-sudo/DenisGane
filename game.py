import requests, json
from rich import print
from rich.console import Console
from rich.table import Table
from rich import box
from rich.layout import Layout
from rich.panel import Panel

from tools.rich.fight_menu 

API_URL = "http://127.0.0.1:8000"
USER_ID = None
PLAYER_ID = None
console = Console()

def game():
    global USER_ID
    
    def get_user_hero():
        response = requests.post(f"{API_URL}/user/info", json={"id": USER_ID})
        data = response.json()

        players = data["players"]

        
        if len(players) > 0:
            table = Table(
                title="Персонажи",
                show_header=False,
                show_edge=True,
                show_lines=True,
                box=box.ROUNDED,
                padding=(0, 1)  )
  
            for index, player in enumerate(players):
                # response_hero = requests.post(f"{API_URL}/hero/info", json={"id": player["hero_id"]})
                # hero_name = response.json()
                # print(hero_name)
                text = ""

                text += f"nickname: {player["nickname"]}\n"
                text += f"id героя: {player["hero_id"]}\n"
                text += f"уровнь игрока: {player["level"]}\n"
                text += f"количество опыта игрока: {player["exp"]}"

                table.add_row(text)

            print("\n")
            print(table)

        else:
            print("Нет персонажей")


    def select_player(player_id: int):
        response = requests.post(f"{API_URL}/user/info", json={"id": USER_ID})
        data = response.json()

        players = data["players"]

        if player_id >= player_id or player_id < 0:
            return -1 
        return players[choise]["id"]

    def create_player():
        response = requests.post(f"{API_URL}/player/hero/list")
        data = response.json()
        heroes = data["heroes"]
        
        
      
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

        print("\n")
        print(table)
            
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
        table = Table(title="локации")

        table.add_column("название")
        table.add_column("описание")
        table.add_column("минимальный уровень")
        table.add_column("номер")
    
        
        for loc in data["locations"]:
            table.add_row(loc["name"], loc["didescription"], str(loc["min_level"]), str(loc["id"]))

        print(table)
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
        PLAYER_ID = select_player(choise)

        response = requests.post(f"{API_URL}/fight/userList?id={PLAYER_ID}")
        res = response.json()
        
        data = res["fights"]


        if data == []:
            print("нет статистики")
            return

        table = Table(title="[bold]статистика", show_lines=True)

        table.add_column("[green]айди победителя[/green]")
        table.add_column("[red]айди проиграшего[/red]")
        table.add_column("[cyan]дата[/cyan]")

        win_count = 0
        los_count = 0
        for fight in data:
            if fight["winner_id"] == PLAYER_ID:
                table.add_row(str(fight["winner_id"]), str(fight["loser_id"]), str(fight["fight"]), style="green")
                win_count += 1
            else:
                table.add_row(str(fight["winner_id"]), str(fight["loser_id"]), str(fight["fight"]), style="red")
                los_count += 1
        print("\n")
        print(table)

        print("[bolt]ИТОГ")
        print(f"[green]{win_count} побед")
        print(f"[red]{los_count} поражений")
        print(f"[magenta]в процентах {(win_count / (win_count + los_count)) * 100}%")


    def fight_step():
        get_user_hero()
        choise_id = int(input("выберите своего героя из спика: "))
        PLAYER_ID = select_player(choise_id)

 
        response = requests.get(f"{API_URL}/fight/ActiveFight?id={PLAYER_ID}")
        if response.status_code != 200:
            print("нет активных боёв")
            return
        data = response.json()
        fight_id = data["id"]

        print(data)

        res = requests.get(f"{API_URL}/fight/session/steps?fight_id={fight_id}")
        steps = res.json()
        print(steps)
        last_step = steps["steps"][-1]
        


        table = Table(title="[bold]Логи битвы")
        table.add_column("враг")
        table.add_column("тип атаки")
        table.add_column("всего нанёс урона")
        table.add_column("описание")

        for step in steps["steps"]:
            print(step)
            resPlayer = requests.get(f"{API_URL}/player/info?id={step["attacker_id"]}")
            player = resPlayer.json()
            
            print("=" * 50)
            print(player)
            table.add_row(player["nickname"], step["action_type"],str( step["damage_dealt"]), step["description"])
            table.add_section()
        print(table)

        res = requests.get(f"{API_URL}/fight/session/info?fight_id={fight_id}")
        session = res.json()

        is_your_turn = (session["attacker_turn"] and session["attacker_id"] == PLAYER_ID) or (not session["attacker_turn"] and session["opponent_id"] == PLAYER_ID)
         
        if is_your_turn:
            

            act_type = int(input("введите что-то"))

            resSession = requests.post(f"{API_URL}/fight/turn?session_id={fight_id}")
            session = res.json()
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
        print(USER_ID)
        game()

    else:
        print(response.content)
    
def register():
    username = input("Введите имя: ").strip()
    password = input("Введите пароль: ").strip()
    data = {"username": username, "password": password}
    response = requests.post(f"{API_URL}/user/register", json=data)
    print(response.content)

    if (response.status_code == 201):
        data = response.json()
        USER_ID = data["id"]
        print(USER_ID)
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