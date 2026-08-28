
import tools.requests_funs.querys as qu
import tools.rich.game_menus as gm
import tools.rich.print_info as pf

class GameApp:
    def __init__(self, user_id):
        self.USER_ID = user_id
        self.PLAYER_ID = None
        self.select_player_id()

        self.player_fight_id = None
        self.player_current_hp = None
        self.player_current_mana = None

        self.STEP_COLORS = {
            "крит урон": {
                "text": "Вам нанесли критический урон\n",
                "title": "red1",
                "border": "dark_red"
            },
            "обычный урон": {
                "text": "Вам нанесли базовый урон\n",
                "title": "red3",
                "border": "red3"
            },
            "skill": {
                "text": "Противник использовал скилл\n",
                "title": "red3",
                "border": "red3"
            },
            "уворот": {
                "text": "Противник увернулись и не получили урон\n",
                "title": "bright_cyan",
                "border": "cyan"
            }
        }


    def select_player_id(self):
        self.get_user_hero()
        choise_id = int(input("выберите своего героя из спика: "))

        data = qu.get_user_info(self.USER_ID)
        players = data["players"]

        while choise_id -1 >= len(players) or choise_id < 0:
            print("неверный ввод")
            choise_id = int(input("выберите своего героя из спика: "))
            
        self.PLAYER_ID = players[choise_id -1]["id"]


    def get_user_hero(self):
        data = qu.get_user_info(self.USER_ID)

        players = data["players"]

  
        if len(players) > 0:
            pf.user_hero(players)            

        else:
            print("Нет персонажей")

        

    def create_player(self):
        data = qu.get_heroes()
        heroes = data["heroes"]
        
        pf.all_heroes(heroes)
            
        choise = int(input("\nВыбор номера героя: ")) - 1
        
        hero_id = heroes[choise]["id"]
        nickname = input("Введите nickname вашего персонажа: ")
        data = {
            "nickname" : nickname,
            "hero_id" : hero_id,
            "user_id" : self.USER_ID
        }

        response = qu.post_create_player(data)
        if response.status_code == 201:
            print(f"Ваш персонаж {nickname} : {heroes[choise]["name"]} успено создан")


    
    def start_fight(self):
        data = qu.get_locations()

        pf.all_locations(data["locations"])
        
        choise_loc = int(input("введите номер локации, 0 - остаться на прежней\nвыберите локацию: "))

        if choise_loc != 0:
            qu.put_update_player_loc(self.PLAYER_ID, choise_loc)
        
        qu.post_start_fight(self.PLAYER_ID)


        response = qu.get_player_active_fight(self.PLAYER_ID)
        if response.status_code != 200:
            print("какая-то ошибка")
            return
        
        data = response.json()
        fight_id = data["id"]
        session = qu.get_session_info(fight_id)


        player = qu.get_player_info(self.PLAYER_ID)

        skills = qu.get_player_skills(self.PLAYER_ID)["skills"]
        act_type, skill = self.fight(
            max_mana=player["max_mana"],
            cur_mana=session["attacker_mana"],
            max_hp=player["max_hp"],
            cur_hp=session["attacker_current_hp"],
            skills=skills
        )

        


        match act_type:
            case 1:
                qu.post_fight_step(session["id"])
            case 2:
                qu.post_fight_step(session["id"], skill["id"])
                
                
                
    

        # if data["detail"] == "вы уже находитесь в бою":
        #     print("вы уже находитесь в бою")
        #     return

        # if data["detail"]["winner"]["id"] == self.PLAYER_ID:
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
        

    def user_statistics(self):
        
        res = qu.get_player_fight_history(self.PLAYER_ID)
        
        data = res["fights"]


        if data == []:
            print("нет статистики")
            return

        pf.user_statistics(data, self.PLAYER_ID)


    def fight_step(self):
        """отображает все ходы текущей битвы"""
        
 
        response = qu.get_player_active_fight(self.PLAYER_ID)
        if response.status_code != 200:
            print("нет активных боёв")
            return
        data = response.json()
        fight_id = data["id"]

        
        steps = qu.get_session_steps(fight_id)["steps"]
        session = qu.get_session_info(fight_id)

        att_player = qu.get_player_info(session["attacker_id"])

        def_player = qu.get_player_info(session["opponent_id"])
        

        
        pf.player_steps(steps, att_player, def_player)
        

        if session["attacker_id"] == self.PLAYER_ID:
            player = att_player
            opponent = def_player
        else:
            player = def_player
            opponent = att_player
    
    
        player_total_mana = player["max_mana"]
        player_current_mana = player["mana"]
        player_total_hp = player["max_hp"]

        player_current_hp = player["hp"]
        opponent_current_hp = opponent["hp"]


        is_your_turn = (session["attacker_turn"] and session["attacker_id"] == self.PLAYER_ID) or (not session["attacker_turn"] and session["opponent_id"] == self.PLAYER_ID)
        
        skills = qu.get_player_skills(self.PLAYER_ID)["skills"]
        
        if steps:
            last_step = steps[-1]

            if last_step["is_critical"]:
                step_color = self.STEP_COLORS["крит урон"]
            
            elif last_step["action_type"] == "dodge":
                step_color = self.STEP_COLORS["уворот"]

            elif last_step["action_type"] == "skill":
                step_color = self.STEP_COLORS["skill"]

            else:
                step_color = self.STEP_COLORS["обычный урон"]
        

        
        if is_your_turn:
            if steps:
                print(last_step)
                pf.step_last(
                    step=last_step,
                    title=step_color["text"],
                    title_style=step_color["title"],
                    border_style=step_color["border"]
                )
            


            print("")
            act_type, skill = self.fight(
                max_mana=player_total_mana,
                cur_mana=player_current_mana,
                max_hp=player_total_hp,
                cur_hp=player_current_hp,
                skills = skills  
                )
            

            

            qu.post_fight_step(fight_id, skill)
            print("")

            ses = qu.get_session_info(fight_id)

            if ses["status"] == "finish":
                pass

            pl_current_hp = player.hp
            opp_current_hp = opponent.hp

    

            steps = qu.get_session_steps(fight_id)["steps"]

            
            if steps:
                pf.player_step(player=player, 
                            opponent=opponent, 
                            pl_cur_hp=pl_current_hp, 
                            opp_cur_hp=opp_current_hp, 
                            opp_old_hp=opponent_current_hp, 
                            step=steps[-1], 
                            session=session, 
                            style="")
        else:
            pl_current_hp = player.hp
            opp_current_hp = opponent.hp


            steps = qu.get_session_steps(fight_id)["steps"]
            if steps:
                pf.player_step(player=player, 
                            opponent=opponent, 
                            pl_cur_hp=pl_current_hp, 
                            opp_cur_hp=opp_current_hp, 
                            opp_old_hp=opponent_current_hp, 
                            step=steps[-1], 
                            session=session, 
                            style="")
            print("вы ожидайете действия врага")


    def user_players(self):
        response = qu.get_player_active_fight(self.PLAYER_ID)
        pl = qu.get_player_info(self.PLAYER_ID)
        if response.status_code > 299:
            print("какая-то ошибка")
            return
        
        elif response.status_code == 203:
            pf.player_static_field_get_print(pl, pl["max_hp"])
            return
        
        data = response.json()
        fight_id = data["id"]

        ses = qu.get_session_info(fight_id)
        # TODO тут доделать

        
        pf.player_info_get_print(pl, pl["hp"], ses)

       

    def fight(self, max_mana: int, cur_mana: int, max_hp: int, cur_hp: int, skills: list):
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
            
            if choise == 1:
                break

            if choise == 2:
                print("0 - вернуться назад")
                sk = self.select_skill(skills)

            if choise == 3:
                print("0 - вернуться назад")
                
            
            if sk and sk != 0:
                return choise, sk


        return choise, None


    def select_skill(self, skills: list):
        while True:
            gm.skill_menu(
                    skills
                )

            choise = int(input("действие: "))
                
            if choise > len(skills) or choise < 0:
                print("неверный ввод")
                continue

            if choise != 0 :
                return skills[choise - 1]["id"]
                
            return None


    def start(self):       
        while True:
            text = """
            1. Просмотр персонажей;
            2. Смена игрока
            3. Создать персонажей;
            4. Мой профиль
            5. отправитсья в бой
            6. статистика
            7. состояние битвы
            0. Выйти.
            """
            choise = int(input(f"{text}\n Выбор: "))
            
            match choise:
                case 1:
                    self.get_user_hero()
                case 2:
                    self.select_player_id()
                case 3:
                    self.create_player()
                case 4:
                    self.user_players()
                case 5:
                    self.start_fight()
                case 6:
                    self.user_statistics()
                case 7:
                    self.fight_step()
