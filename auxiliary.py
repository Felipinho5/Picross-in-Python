import json

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
PROGRESS_FILE = 'progress.json'
PROGRESS_RESET_FILE = 'progress_reset.json'

def load_progress():
    with open(PROGRESS_FILE, 'r') as file:
        return json.load(file)

def save_progress(pgs):
    with open(PROGRESS_FILE, 'w') as file:
        json.dump(pgs, file, indent = 4)

def reset_progress():
    with open(PROGRESS_RESET_FILE, 'r') as source:
        reset_pgs = json.load(source)

    with open(PROGRESS_FILE, 'w') as target:
        json.dump(reset_pgs, target, indent = 4)

    return reset_pgs