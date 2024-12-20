from ursina import *

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'cube'  # Placeholder, replace with actual player model
        self.color = color.red
        self.scale_y = 2
        self.x = -5
        self.y = -2

    def update(self):
        self.y += held_keys['w'] * 6 * time.dt
        self.y -= held_keys['s'] * 6 * time.dt
        self.x += held_keys['d'] * 6 * time.dt
        self.x -= held_keys['a'] * 6 * time.dt

class MenuSystem(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.menu_items = []
        self.main_menu = Entity(parent=self, enabled=True)
        self.b3313_info = Entity(parent=self, enabled=False)

        self.create_main_menu()
        self.create_b3313_info()

    def create_main_menu(self):
        Button(text='Start Game', parent=self.main_menu, y=0.1, scale=(0.3, 0.1), on_click=self.start_game)
        Button(text='B3313 Info', parent=self.main_menu, y=-0.1, scale=(0.3, 0.1), on_click=self.show_b3313_info)
        Button(text='Quit', parent=self.main_menu, y=-0.3, scale=(0.3, 0.1), on_click=application.quit)

    def create_b3313_info(self):
        Text('B3313 Information', parent=self.b3313_info, y=0.4)
        Text('This is a placeholder for B3313 info.', parent=self.b3313_info)
        Button(text='Back', parent=self.b3313_info, y=-0.4, scale=(0.1, 0.05), on_click=self.show_main_menu)

    def start_game(self):
        self.disable()
        # Add game start logic here

    def show_b3313_info(self):
        self.main_menu.disable()
        self.b3313_info.enable()

    def show_main_menu(self):
        self.b3313_info.disable()
        self.main_menu.enable()

app = Ursina()

player = Player()
menu = MenuSystem()

def update():
    if held_keys['escape']:
        menu.enable()

def input(key):
    if key == 'escape':
        menu.show_main_menu()

Sky()

app.run()
