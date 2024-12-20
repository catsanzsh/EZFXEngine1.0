import pygame
import sys
import math
from enum import Enum
from ursina import Ursina, Entity, camera, held_keys, window, color, application, time, curve, Text, destroy, Vec3

# ------------------------ CORE ENGINE COMPONENTS ------------------------

class FTRender:
    """Placeholder for an advanced renderer."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def render(self, surface):
        """Basic render method."""
        pass

class MenuState(Enum):
    """Menu state controller."""
    MAIN = "main"
    CREDITS = "credits"
    PLAYING = "playing"
    GAME_SELECT = "game_select"

class MenuItem:
    """Menu item with hover effects."""
    def __init__(self, text, position, action, font_size=36):
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, font_size)
        self.is_selected = False
        self.hover_offset = 0

    def draw(self, surface):
        """Draw menu item with selection effects."""
        color = (255, 255, 0) if self.is_selected else (255, 255, 255)
        text_surface = self.font.render(self.text, True, color)
        pos = (self.position[0], self.position[1] + self.hover_offset)
        surface.blit(text_surface, pos)

    def update(self):
        """Animate hover effect."""
        if self.is_selected:
            self.hover_offset = -5 * abs(math.sin(pygame.time.get_ticks() * 0.003))
        else:
            self.hover_offset = 0

class MenuSystem:
    """Main menu system controller."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN
        self.selected_index = 0
        self.last_input_time = 0
        self.last_input_time_game_select = 0

        # Initialize menu items
        self.menu_items = [
            MenuItem("Start Game", (screen_width // 2 - 80, screen_height // 2 - 60),
                     lambda: setattr(self, 'state', MenuState.GAME_SELECT)),
            MenuItem("Credits", (screen_width // 2 - 60, screen_height // 2),
                     lambda: setattr(self, 'state', MenuState.CREDITS)),
            MenuItem("Exit", (screen_width // 2 - 40, screen_height // 2 + 60),
                     lambda: sys.exit())
        ]

        # Game selection menu items
        self.game_select_items = [
            MenuItem("Super Mario 64", (screen_width // 2 - 100, screen_height // 2 - 60),
                     lambda: self.run_game("sm64")),
            MenuItem("The New Super Mario Bros.", (screen_width // 2 - 140, screen_height // 2),
                     lambda: self.run_game("nsmb")),
            MenuItem("Back", (screen_width // 2 - 40, screen_height // 2 + 60),
                     lambda: setattr(self, 'state', MenuState.MAIN))
        ]

        self.title_font = pygame.font.Font(None, 72)

    def run_game(self, game_id):
        """Launch selected game."""
        self.state = MenuState.PLAYING
        
    def update(self):
        """Handle menu navigation and selection."""
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        if self.state == MenuState.MAIN:
            if current_time - self.last_input_time < 200:
                return
            
            self._update_menu_items(self.menu_items, keys)
            self.last_input_time = current_time

        elif self.state == MenuState.GAME_SELECT:
            if current_time - self.last_input_time_game_select < 200:
                return
            
            self._update_menu_items(self.game_select_items, keys)
            
            if keys[pygame.K_ESCAPE] or keys[pygame.K_BACKSPACE]:
                self.state = MenuState.MAIN
                self.selected_index = 0
            
            self.last_input_time_game_select = current_time

    def _update_menu_items(self, items, keys):
        """Helper method for updating menu items."""
        for item in items:
            item.is_selected = False
        items[self.selected_index].is_selected = True

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(items)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(items)
        elif keys[pygame.K_RETURN]:
            items[self.selected_index].action()

        for item in items:
            item.update()

    def draw(self, screen):
        """Render current menu state."""
        screen.fill((0, 0, 40))
        
        if self.state == MenuState.MAIN:
            title_text = self.title_font.render("Super Mario FX Beta", True, (255, 255, 255))
            screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))
            for item in self.menu_items:
                item.draw(screen)
        
        elif self.state == MenuState.GAME_SELECT:
            title_text = self.title_font.render("Select a Game", True, (255, 255, 255))
            screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))
            for item in self.game_select_items:
                item.draw(screen)

def run_ursina_game(game_to_run):
    """Initialize and run 3D game environment."""
    app = Ursina(borderless=False)
    window.title = f"Super Mario FX Beta - Playing: {game_to_run}"
    window.fullscreen = False
    window.size = (800, 600)
    
    # Set up game environment
    if game_to_run == "Super Mario 64":
        ground = Entity(model='plane', scale=32, color=color.gray)
        player = Entity(model='cube', color=color.orange, scale=1, position=(0, 0.5, 0))
        box1 = Entity(model='cube', color=color.red, scale=1, position=(2, 0.5, 2))
        box2 = Entity(model='cube', color=color.blue, scale=1, position=(-2, 0.5, -2))
        box3 = Entity(model='cube', color=color.green, scale=1, position=(2, 0.5, -2))
        box4 = Entity(model='cube', color=color.yellow, scale=1, position=(-2, 0.5, 2))
    else:
        ground = Entity(model='plane', scale=32, color=color.green)
        player = Entity(model='sphere', color=color.red, scale=1, position=(0, 0.5, 0))
        camera.orthographic = True
        camera.fov = 8
        obstacle = Entity(model='quad', color=color.brown, scale=(2, 5, 1), position=(5, 2.5, 0))
        instructions_text = Text("2D Game Controls:\nWASD to move, ESC to quit", origin=(0, -0.4), scale=0.8, color=color.white)

    camera.position = (0, 10, -15)
    camera.look_at(Vec3(0, 0, 0))
    camera.fov = 90

    def update():
        """Game update loop."""
        speed = 5 * time.dt
        if held_keys['w']: player.z += speed
        if held_keys['s']: player.z -= speed
        if held_keys['a']: player.x -= speed
        if held_keys['d']: player.x += speed
        
        camera.position = player.position + Vec3(0, 10, -15)
        camera.look_at(player.position)
        
        if held_keys['escape']:
            application.quit()

    app.run()

class Game:
    """Main game controller."""
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True

        self.menu = MenuSystem(self.screen_width, self.screen_height)
        self.renderer = FTRender(self.screen_width, self.screen_height)

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.menu.state == MenuState.PLAYING:
                pygame.display.quit()
                pygame.quit()
                
                # Run appropriate game version
                if self.menu.selected_index == 0:
                    run_ursina_game("Super Mario 64")
                elif self.menu.selected_index == 1:
                    run_ursina_game("New Super Mario Bros.")
                
                # Reinitialize pygame after game ends
                pygame.init()
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("Super Mario FX Beta")
                self.menu.state = MenuState.MAIN
                self.menu.selected_index = 0

            elif self.menu.state == MenuState.MAIN:
                self.menu.update()
                self.menu.draw(self.screen)
                self.renderer.render(self.screen)

            elif self.menu.state == MenuState.CREDITS:
                self.screen.fill((0, 0, 0))
                credits_font = pygame.font.Font(None, 48)
                credits_text = credits_font.render("Credits: Made by Gemini", True, (255, 255, 255))
                self.screen.blit(credits_text, (
                    self.screen_width // 2 - credits_text.get_width() // 2,
                    self.screen_height // 2 - 20
                ))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
