import requests
from fastapi import APIRouter, Depends, HTTPException

API_URL = "http://127.0.0.1:8000"


def http_logic(response):
    if response.status_code > 299:
        print(f"не предвиденная ошибка, code: {response.status_code}\n{response.content}", )
        raise HTTPException(status_code=response.status_code, detail=response.content)


def get_user_info(user_id: int):
    response = requests.get(f"{API_URL}/user/info?id={user_id}")
    http_logic(response)
    
    return response.json()


def get_heroes():
    response = requests.get(f"{API_URL}/player/hero/list")
    http_logic(response)

    return response.json()

def get_player_skills(plaeyr_id):
    response = requests.get(f"{API_URL}/player/skills?id={plaeyr_id}")
    http_logic(response)

    return response.json()


def post_create_player(data: dict):
    response = requests.post(f"{API_URL}/player/create", json=data)
    http_logic(response)

    return response

def get_locations():
    response = requests.get(f"{API_URL}/locations/list")
    http_logic(response)
    return response.json()

def put_update_player_loc(player_id: int, loc_id: int):
    response = requests.put(f"{API_URL}/player/updatePlayerLocation?id={player_id}&loc_id={loc_id}")
    http_logic(response)
    
    return response

def post_start_fight(player_id):
    response = requests.post(f"{API_URL}/fight/start?attacker_id={player_id}")
    http_logic(response)

    return response

def get_player_fight_history(player_id):
    response = requests.get(f"{API_URL}/fight/history?id={player_id}")
    http_logic(response)

    return response.json()


def get_player_active_fight(player_id):
    """Почему тут логика такая странная"""
    response = requests.get(f"{API_URL}/fight/ActiveFight?id={player_id}")
    
    return response


def get_session_steps(fight_id):
    response= requests.get(f"{API_URL}/fight/session/steps?fight_id={fight_id}")
    http_logic(response)

    return response.json()


def get_session_info(fight_id):
    response = requests.get(f"{API_URL}/fight/session/info?fight_id={fight_id}")
    http_logic(response)

    return response.json()


def get_player_info(player_id):
    response = requests.get(f"{API_URL}/player/info?id={player_id}")
    http_logic(response)

    return response.json()


def post_login(data: dict):
    response = requests.post(f"{API_URL}/user/login", json=data)

    return response

    
def post_register(data: dict):
    response = requests.post(f"{API_URL}/user/register", json=data)

    return response


def post_fight_step(session_id: int, skill_id:int = None):
    response = requests.post(f"{API_URL}/fight/step?session_id={session_id}&skill_id={skill_id}")
    http_logic(response)

    return response.json()