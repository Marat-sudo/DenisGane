import requests, json

API_UTL = "http://127.0.0.1:8000"
USER_ID = None



def game():
    global USER_ID
    
    def get_user_hero():
        response = requests.post(f"{API_UTL}/user/info", json={"id": USER_ID})
        data = response.json()

        print(USER_ID)
        print(data)

        if len(data["players"]) > 0:
            print(f"data {data}")

        else:
            print("Нет персонажей")




    def create_player():
        pass

    while True:
        text = """
        1. Просмотр персонажей;
        2. Создать персонажей;
        3. Мой профиль
        0. Выйти.
        """
        choise = int(input(f"{text}\n Выбор: "))
        if choise == 1:
            get_user_hero()
        elif choise == 2:
            exit()



    

def login():
    global USER_ID
    username = input("введите usenname: ").strip()
    response = requests.post(f"{API_UTL}/user/login", json={"username": username})
    if (response.status_code == 200):
        data = response.json()
        USER_ID = data["id"]
        print(USER_ID)
        game()
    
    
def register():
    username = input("Введите имя: ").strip()
    data = {"username": username}
    response = requests.post(f"{API_UTL}/user/register", json=data)
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