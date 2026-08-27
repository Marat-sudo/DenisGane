from rich import print


import tools.requests_funs.querys as qu
from gameApp import GameApp


USER_ID = None



def login():
    global USER_ID
    username = input("введите usenname: ").strip()
    password = input("введите password: ").strip()


    
    response = qu.post_login(data={"username": username, "password": password}) 
    if (response.status_code == 200):
        data = response.json()
        USER_ID = data["id"]
        game = GameApp(USER_ID)
        game.start()

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
        
        game = GameApp(USER_ID)
        game.start()
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
        break