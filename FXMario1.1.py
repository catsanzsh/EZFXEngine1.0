import pygame
import sys
import math
from enum import Enum
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class MenuState(Enum):
    MAIN = "main"
    CREDITS = "credits"
    PLAYING = "playing"

class MenuItem:
    def __init__(self, text, position, action, font_size=36):
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, font_size)
        self.is_selected = False
        self.hover_offset = 0

    def draw(self, surface):
        color = (255, 0, 0) if self.is_selected else (255, 255, 255)
        text_surface = self.font.render(self.text, True, color)
        pos = (self.position[0], self.position[1] + self.hover_offset)
        surface.blit(text_surface, pos)

    def update(self):
        # Make the selected item "hover" a little
        self.hover_offset = -5 * abs(math.sin(pygame.time.get_ticks() * 0.003)) if self.is_selected else 0

class MenuSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN
        self.selected_index = 0
        self.last_input_time = 0

        self.menu_items = [
            MenuItem("Start Super Mario FX", (screen_width // 2 - 100, screen_height // 2 - 60),
                     lambda: setattr(self, 'state', MenuState.PLAYING)),
            MenuItem("Credits", (screen_width // 2 - 60, screen_height // 2),
                     lambda: setattr(self, 'state', MenuState.CREDITS)),
            MenuItem("Exit", (screen_width // 2 - 40, screen_height // 2 + 60),
                     lambda: sys.exit())
        ]

        self.title_font = pygame.font.Font(None, 72)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_input_time < 200:
            return

        keys = pygame.key.get_pressed()

        # Reset selections
        for item in self.menu_items:
            item.is_selected = False
        self.menu_items[self.selected_index].is_selected = True

        # Menu navigation
        if keys[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            self.last_input_time = current_time
        elif keys[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            self.last_input_time = current_time
        elif keys[pygame.K_RETURN]:
            self.menu_items[self.selected_index].action()
            self.last_input_time = current_time

        # Update each menu item
        for item in self.menu_items:
            item.update()

    def draw(self, screen):
        screen.fill((0, 0, 0))
        title_text = self.title_font.render("Super Mario FX 1.0", True, (255, 0, 0))
        screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))

        for item in self.menu_items:
            item.draw(screen)

#
#   --- Bob-omb Battlefield–like environment setup ---
#

def create_bobomb(position=(0,1,0)):
    """Create a roaming Bob-omb-like entity."""
    bobomb = Entity(
        model='sphere',
        color=color.black,
        scale=1.2,
        position=position,
        collider='sphere'
    )
    # Give it eyes (just a decorative second entity)
    Entity(
        parent=bobomb,
        model='sphere',
        color=color.white,
        scale=0.2,
        position=(0.2, 0.1, 0.9)
    )
    Entity(
        parent=bobomb,
        model='sphere',
        color=color.white,
        scale=0.2,
        position=(-0.2, 0.1, 0.9)
    )
    return bobomb

def create_king_bobomb(position=(0,5,0)):
    """Create a large King Bob-omb at the top of the ‘mountain’."""
    king = Entity(
        model='sphere',
        color=color.black,
        scale=3,
        position=position,
        collider='sphere'
    )
    # A simple 'crown'
    Entity(
        parent=king,
        model='cube',
        color=color.gold,
        scale=(1.2, 0.3, 1.2),
        position=(0, 1.7, 0)
    )
    # Some eyes
    Entity(
        parent=king,
        model='sphere',
        color=color.white,
        scale=0.5,
        position=(0.5, 0.5, 1)
    )
    Entity(
        parent=king,
        model='sphere',
        color=color.white,
        scale=0.5,
        position=(-0.5, 0.5, 1)
    )
    return king

def create_hilly_terrain():
    """Create multiple ‘hills’ or angled planes for a Bob-omb Battlefield feel."""
    # Large base plane
    base = Entity(
        model='plane',
        scale=(120, 1, 120),
        color=color.lime.tint(-.1),
        texture='grass',
        texture_scale=(100,100),
        collider='mesh'
    )
    # A few angled planes that simulate hills or ramps
    hill1 = Entity(
        model='plane',
        scale=(40, 1, 40),
        rotation=(20, 0, 0),
        position=(20,1.5,20),
        color=color.lime.tint(-.15),
        texture='grass',
        texture_scale=(20,20),
        collider='mesh'
    )
    hill2 = Entity(
        model='plane',
        scale=(40, 1, 40),
        rotation=(15, 45, 0),
        position=(-15,2,35),
        color=color.lime.tint(-.05),
        texture='grass',
        texture_scale=(20,20),
        collider='mesh'
    )
    hill3 = Entity(
        model='plane',
        scale=(40, 1, 40),
        rotation=(15, -45, 0),
        position=(15,2,45),
        color=color.lime.tint(-.1),
        texture='grass',
        texture_scale=(20,20),
        collider='mesh'
    )
    # A ramp that leads to the top
    ramp = Entity(
        model='plane',
        scale=(30, 1, 60),
        rotation=(25, 0, 0),
        position=(0,6,60),
        color=color.lime.tint(-.2),
        texture='grass',
        texture_scale=(15,30),
        collider='mesh'
    )

    return [base, hill1, hill2, hill3, ramp]

def run_mario_fx():
    """
    Updated function to create a Bob-omb Battlefield–like level:
    - Hilly terrain
    - Roaming Bob-omb enemies
    - A King Bob-omb boss at the top
    """
    app = Ursina()
    window.title = 'Super Mario FX 1.0 - Bob-omb Battlefield'
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = True

    # Create terrain
    terrain = create_hilly_terrain()

    # Create some coins
    coins = []
    for i in range(15):
        coin = Entity(
            model='sphere',
            color=color.yellow,
            scale=0.5,
            position=(random.uniform(-30, 30), 2, random.uniform(-30, 90)),
            collider='sphere'
        )
        coins.append(coin)

    # Spawn several small Bob-ombs around the map
    bobombs = []
    for _ in range(5):
        x = random.uniform(-30, 30)
        z = random.uniform(0, 60)
        bobomb = create_bobomb(position=(x, 2, z))
        bobombs.append(bobomb)

    # King Bob-omb at the “top”
    king_bobomb = create_king_bobomb(position=(0, 15, 80))

    # Player setup
    player = FirstPersonController()
    player.cursor.visible = True
    player.gravity = 0.8
    player.jump_height = 4
    player.jump_duration = 0.3
    player.position = (0, 2, 0)
    player.speed = 8
    player.mouse_sensitivity = Vec2(40, 40)

    score = 0
    score_text = Text(text=f'Score: {score}', position=(-0.85, 0.45), scale=2)

    # Bob-omb movement
    def roam_bobomb(bobomb):
        """Simple random movement logic for bobombs."""
        bobomb.direction = Vec3(random.uniform(-1,1), 0, random.uniform(-1,1)).normalized() * 0.03

    for b in bobombs:
        roam_bobomb(b)

    # Attach a function to update them each frame
    def update():
        nonlocal score

        # Coin collection
        for coin in coins[:]:
            if distance(player.position, coin.position) < 1.5:
                destroy(coin)
                coins.remove(coin)
                score += 100
                score_text.text = f'Score: {score}'

        # Respawn if player falls off
        if player.y < -50:
            player.position = (0, 2, 0)
            score = 0
            score_text.text = f'Score: {score}'

        # Simple bobomb roaming
        for bob in bobombs:
            bob.position += bob.direction
            # Occasionally change direction or if it hits an edge
            if random.random() < 0.005 or bob.x < -50 or bob.x > 50 or bob.z < -10 or bob.z > 120:
                roam_bobomb(bob)

            # Simple “damage” effect if close to a bob-omb
            if distance(player.position, bob.position) < 1.3:
                # Knock the player back a bit
                player.position += (player.position - bob.position).normalized() * 1
                # Optionally reduce score
                score = max(0, score - 50)
                score_text.text = f'Score: {score}'

        # King Bob-omb “interaction”
        if distance(player.position, king_bobomb.position) < 5:
            # If close to King Bob-omb, you “win” or reset, etc.
            score_text.text = 'You defeated King Bob-omb!'
            invoke(setattr, player, 'position', Vec3(0,2,0), delay=2)
            invoke(setattr, score_text, 'text', f'Score: {score}', delay=2)

        # Quit if ESC is held
        if held_keys['escape']:
            application.quit()

    Sky()
    app.run()

#
#   --- Main Game (Menu + loop) ---
#

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Super Mario FX 1.0")
        self.clock = pygame.time.Clock()
        self.running = True
        self.menu = MenuSystem(self.screen_width, self.screen_height)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.menu.state == MenuState.PLAYING:
                # When user selects "Start Super Mario FX", run the 3D game
                pygame.display.quit()
                pygame.quit()
                run_mario_fx()
                # When Ursina app ends, re-init pygame for menu
                pygame.init()
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("Super Mario FX 1.0")
                self.menu.state = MenuState.MAIN

            if self.menu.state == MenuState.MAIN:
                self.menu.update()
                self.menu.draw(self.screen)

            elif self.menu.state == MenuState.CREDITS:
                self.screen.fill((0, 0, 0))
                credits_font = pygame.font.Font(None, 48)
                credits_text = credits_font.render("Super Mario FX 1.0", True, (255, 0, 0))
                credit_line2 = credits_font.render("A Fan Project", True, (255, 255, 255))
                self.screen.blit(credits_text, (
                    self.screen_width // 2 - credits_text.get_width() // 2,
                    self.screen_height // 2 - 40
                ))
                self.screen.blit(credit_line2, (
                    self.screen_width // 2 - credit_line2.get_width() // 2,
                    self.screen_height // 2 + 20
                ))

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] or keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                    self.menu.state = MenuState.MAIN

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
