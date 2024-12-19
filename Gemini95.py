import pygame
import sys
import math
from enum import Enum
from ursina import Ursina, Entity, camera, held_keys, window, color, application, time

# ------------------------ CORE ENGINE COMPONENTS ------------------------

class FTRender:
    """Basic renderer for 2D elements."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def render(self):
        self.surface.fill((0, 0, 0, 0))

    def draw_text(self, text, position, color=(255, 255, 255), font_size=36, font_name=None):
        font = pygame.font.Font(font_name, font_size) if font_name else pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        self.surface.blit(text_surface, position)

    def draw_rect(self, rect, color):
        pygame.draw.rect(self.surface, color, rect)

    def draw_to_screen(self, screen):
        screen.blit(self.surface, (0, 0))


class MenuState(Enum):
    MAIN = "main"
    PLAYING = "playing"
    CREDITS = "credits"

class MenuItem:
    def __init__(self, text, position, action):
        self.text = text
        self.position = position
        self.action = action
        self.is_selected = False
        self.hover_offset = 0

    def update(self):
        self.hover_offset = -5 * abs(math.sin(pygame.time.get_ticks() * 0.003)) if self.is_selected else 0

class MenuSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN
        self.selected_index = 0
        self.menu_items = [
            MenuItem("Start Game", (screen_width // 2 - 80, screen_height // 2 - 60), lambda: setattr(self, 'state', MenuState.PLAYING)),
            MenuItem("Credits", (screen_width // 2 - 60, screen_height // 2), lambda: setattr(self, 'state', MenuState.CREDITS)),
            MenuItem("Exit", (screen_width // 2 - 40, screen_height // 2 + 60), sys.exit)
        ]

    def update(self):
        keys = pygame.key.get_pressed()
        for item in self.menu_items:
            item.is_selected = False
        self.menu_items[self.selected_index].is_selected = True

        if keys[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif keys[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif keys[pygame.K_RETURN]:
            self.menu_items[self.selected_index].action()

    def draw(self, renderer):
        # Space World 95 inspired colors (approximate)
        bg_color = (0, 0, 64)  # Dark blue background
        title_color = (255, 215, 0)  # Gold/Yellow title
        menu_color = (192,192,192) #light gray menu
        selected_color = (255, 255, 0) #yellow selection

        renderer.draw_rect((0,0, renderer.width, renderer.height), bg_color)
        renderer.draw_text("Super Mario FX Beta", (self.screen_width // 2 - 200, 100), font_size=72, color=title_color)

        for item in self.menu_items:
            item.update()
            color = selected_color if item.is_selected else menu_color
            renderer.draw_text(item.text, (item.position[0], item.position[1] + item.hover_offset), color=color)


# ------------------------ GAMEPLAY AND URSINA ------------------------

def run_ursina_game():
    app = Ursina()

    player = Entity(model='cube', color=color.orange, scale_y=2, position=(0,1,0))

    def update():
        if held_keys['a']: 
            player.x -= 5 * time.dt
        if held_keys['d']: 
            player.x += 5 * time.dt

    app.run()

# ------------------------ MAIN GAME CLASS ------------------------

class Game:
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
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.menu.state == MenuState.PLAYING:
                pygame.display.quit()
                run_ursina_game()
                pygame.init()
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("Super Mario FX Beta")
                self.menu.state = MenuState.MAIN

            if self.menu.state == MenuState.CREDITS:
                bg_color = (0, 0, 64)
                self.renderer.render()
                self.renderer.draw_rect((0,0, self.screen_width, self.screen_height), bg_color)
                self.renderer.draw_text("Credits: Made by Gemini", (self.screen_width // 2 - 150, self.screen_height // 2), font_size=36)
                self.renderer.draw_text("Press ESC to return", (self.screen_width // 2 - 100, self.screen_height // 2 + 50), font_size = 24)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.menu.state = MenuState.MAIN
                self.renderer.draw_to_screen(self.screen)

            if self.menu.state == MenuState.MAIN:
                self.renderer.render()
                self.menu.update()
                self.menu.draw(self.renderer)
                self.renderer.draw_to_screen(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
