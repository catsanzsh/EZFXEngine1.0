from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

class MainMenu(Entity):
    def __init__(self):
        super().__init__()
        self.create_main_menu()

    def create_main_menu(self):
        self.title = Text("Super Mario FX 1.0", scale=2, y=0.3, origin=(0,0))
        self.start_button = Button(text='Start', scale=(0.25, 0.1), y=0.1, on_click=self.start_game)
        self.credits_button = Button(text='Credits', scale=(0.25, 0.1), y=-0.1, on_click=self.show_credits)
        self.exit_button = Button(text='Exit', scale=(0.25, 0.1), y=-0.3, on_click=application.quit)

    def start_game(self):
        destroy_all()
        start_game()

    def show_credits(self):
        destroy_all()
        CreditsMenu()

class CreditsMenu(Entity):
    def __init__(self):
        super().__init__()
        self.create_credits()

    def create_credits(self):
        self.title = Text("Credits", scale=2, y=0.3, origin=(0,0))
        self.content = Text("Super Mario FX 1.0\nA Fan Project", scale=1, y=0.1)
        self.back_button = Button(text='Back', scale=(0.2, 0.1), y=-0.3, on_click=self.back_to_menu)

    def back_to_menu(self):
        destroy_all()
        MainMenu()

def create_bobomb(position=(0,1,0)):
    bobomb = Entity(
        model='sphere', color=color.black,
        scale=1.2, position=position,
        collider='sphere'
    )
    Entity(parent=bobomb, model='sphere', color=color.white, scale=0.2, position=(0.2, 0.1, 0.9))
    Entity(parent=bobomb, model='sphere', color=color.white, scale=0.2, position=(-0.2, 0.1, 0.9))
    return bobomb

def create_king_bobomb(position=(0,5,0)):
    king = Entity(
        model='sphere', color=color.black,
        scale=3, position=position,
        collider='sphere'
    )
    Entity(parent=king, model='cube', color=color.gold, scale=(1.2, 0.3, 1.2), position=(0, 1.7, 0))
    Entity(parent=king, model='sphere', color=color.white, scale=0.5, position=(0.5, 0.5, 1))
    Entity(parent=king, model='sphere', color=color.white, scale=0.5, position=(-0.5, 0.5, 1))
    return king

def create_hilly_terrain():
    base = Entity(
        model='plane', scale=(120, 1, 120),
        color=color.lime.tint(-.1), texture='grass',
        texture_scale=(100,100), collider='mesh'
    )
    hills = []
    for i in range(3):
        hill = Entity(
            model='plane', scale=(40, 1, 40),
            rotation=(random.uniform(10,25), random.uniform(0,45), 0),
            position=(random.uniform(-30,30), random.uniform(1,3), random.uniform(20,60)),
            color=color.lime.tint(random.uniform(-.2,0)),
            texture='grass', collider='mesh'
        )
        hills.append(hill)
    return [base] + hills

def start_game():
    # Game setup
    terrain = create_hilly_terrain()
    coins = []
    for i in range(15):
        coin = Entity(
            model='sphere', color=color.yellow,
            scale=0.5, position=(random.uniform(-30,30), 2, random.uniform(-30,90)),
            collider='sphere'
        )
        coins.append(coin)

    bobombs = []
    for _ in range(5):
        bobomb = create_bobomb(position=(random.uniform(-30,30), 2, random.uniform(0,60)))
        bobomb.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized() * 0.03
        bobombs.append(bobomb)

    king_bobomb = create_king_bobomb(position=(0, 15, 80))
    player = FirstPersonController(position=(0,2,0))
    player.gravity = 0.8
    player.jump_height = 4
    player.speed = 8

    score = 0
    score_text = Text(text=f'Score: {score}', position=(-0.85, 0.45), scale=2, parent=camera.ui)

    def update():
        nonlocal score
        for coin in coins[:]:
            if distance(player.position, coin.position) < 1.5:
                coins.remove(coin)
                destroy(coin)
                score += 100
                score_text.text = f'Score: {score}'

        if player.y < -50:
            player.position = (0, 2, 0)
            score = 0
            score_text.text = f'Score: {score}'

        for bob in bobombs:
            bob.position += bob.direction
            if random.random() < 0.005 or abs(bob.x) > 50 or abs(bob.z) > 120:
                bob.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized() * 0.03

            if distance(player.position, bob.position) < 1.3:
                player.position += (player.position - bob.position).normalized() * 1
                score = max(0, score - 50)
                score_text.text = f'Score: {score}'

        if distance(player.position, king_bobomb.position) < 5:
            score_text.text = 'You defeated King Bob-omb!'
            invoke(setattr, player, 'position', Vec3(0,2,0), delay=2)
            invoke(setattr, score_text, 'text', f'Score: {score}', delay=2)

    def input(key):
        if key == 'escape':
            destroy_all()
            MainMenu()

    Sky()

app = Ursina()
window.title = 'Super Mario FX 1.0'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
MainMenu()
app.run()
