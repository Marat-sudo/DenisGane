import requests, json

API_URL = "http://127.0.0.1:8000"
USER_ID = None
PLAYER_ID = None


def game():
    global USER_ID
    
    def get_user_hero():
        response = requests.post(f"{API_URL}/user/info", json={"id": USER_ID})
        data = response.json()

        players = data["players"]

        
        if len(players) > 0:
            max_size = 0
            text = ""
            
            for index, player in enumerate(players):
                size = (
                f"nickname: {player["nickname"]}",
                f"номер героя: {index + 1}",
                f"id героя: {player["hero_id"]}",
                f"уровнь игрока: {player["level"]}",
                f"количество опыта игрока: {player["exp"]}",
                )
                s = len(max(size, key=len))
                if s > max_size:
                    max_size = s 

            text_border =  "|" + ("=" * (max_size + 4)) + "|\n" 
            

            
            for index, player in enumerate(players):
                # response_hero = requests.post(f"{API_URL}/hero/info", json={"id": player["hero_id"]})
                # hero_name = response.json()
                # print(hero_name)

                text_nickname = f"nickname: {player["nickname"]}"
                text_number = f"номер героя: {index + 1}"
                text_hero_id = f"id героя: {player["hero_id"]}"
                text_level = f"уровнь игрока: {player["level"]}"
                text_exp = f"количество опыта игрока: {player["exp"]}"

                text += text_border
                
                text += f"|%-{max_size + 4}s|" % text_nickname
                text += "\n"
                text += f"|%-{max_size + 4}s|" % text_number
                text += "\n"

                text += f"|%-{max_size + 4}s|" % text_hero_id
                text += "\n"

                text += f"|%-{max_size + 4}s|" % text_level
                text += "\n"

                text += f"|%-{max_size + 4}s|" % text_exp
                text += "\n"
                text += text_border

            print(text)

        else:
            print("Нет персонажей")




    def create_player():
        response = requests.post(f"{API_URL}/player/hero/list")
        data = response.json()
        heroes = data["heroes"]
        text = ""
        max_name = 0

        for hero in heroes:
            text_name = f"название героя {hero["name"]}"
            if len(text_name) > max_name:
                max_name = len(text_name)


        text_border ="|" + ("=" * (max_name + 4))+ "|\n"
        text += text_border 
        for index, hero in enumerate(heroes):
            text_name = f"название героя {hero["name"]}"
            text_number = f"номер героя {index + 1}"

            text += f"|%-{max_name + 4}s|" % text_name
            text += "\n"
            text += f"|%-{max_name + 4}s|" % text_number
            text += "\n"
            text += text_border
            
        choise = int(input(text + "\nВыбор номера героя: ")) - 1
        
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


        data = requests.post(f"{API_URL}/locations/list")
        
        print(data.json())

        choise_loc = int(input("выберите локацию: "))

        

        response = requests.post(f"{API_URL}/player/update?id={PLAYER_ID}&loc_id={choise_loc}")


        # print(PLAYER_ID)
        # response = requests.post(f"{API_URL}/fight/start?attacker_id={PLAYER_ID}")
        # data = response.json()
        # print(data)



    while True:
        text = """
        1. Просмотр персонажей;
        2. Создать персонажей;
        3. Мой профиль
        4. отправитсья в бой
        0. Выйти.
        """
        choise = int(input(f"{text}\n Выбор: "))
        if choise == 1:
            get_user_hero()
        elif choise == 2:
            create_player()
        elif choise == 4:
            start_fight()



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