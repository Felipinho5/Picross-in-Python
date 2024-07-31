import json
import js

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BROWN = (94, 44, 4)
QUANTUM = (11, 11, 11)
RED = (255, 0, 0)
GRAY = (85, 73, 73)
CYAN = (72, 72, 104)
LIGHT_BLUE = (36, 176, 219)
BLUE = (0, 0, 204)
PINK = (255, 97, 219)
ORANGE = (250, 170, 65)
GREEN = (0, 153, 0)
CAPTION_TITLE = 'PICROSS - '
PROGRESS_LOCAL_STORAGE = 'progress'
PROGRESS_RESET = [
    {
        "unlocked": True,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    },
    {
        "unlocked": False,
        "completed": False,
        "fewest_errors": None
    }
]

def load_progress():
    json_data = js.window.localStorage.getItem(PROGRESS_LOCAL_STORAGE)

    if json_data is not None:
        return json.loads(json_data)

    return PROGRESS_RESET

def save_progress(pgs):
    json_data = json.dumps(pgs)
    js.window.localStorage.setItem(PROGRESS_LOCAL_STORAGE, json_data)

def reset_progress():
    save_progress(PROGRESS_RESET)
    return PROGRESS_RESET