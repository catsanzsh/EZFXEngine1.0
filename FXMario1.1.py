import pygame
import sys
import math
from enum import Enum
from ursina import Ursina, Entity, camera, held_keys, window, color, application, time, curve


# ------------------------ CORE ENGINE COMPONENTS ------------------------

class FTRender:
    """Placeholder for an advanced renderer... but for now, it's just here to make things look cool."""
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def render(self, surface):
        """Render method without doing anything at the moment, because sometimes less is more."""
        pass  # Rendering... but not yet


class MenuState(Enum):
    """This enum controls the various states of our mystical menu. It's simple, yet powerful."""
    MAIN = "main"  # Main menu, where everything begins
    CREDITS = "credits"  # Where we thank the people who made this thing happen
    PLAYING = "playing"  # The game is on, folks!


class MenuItem:
    """Represents a menu item, ready to be clicked or hovered over. Oh, the drama of selection."""
    def __init__(self, text, position, action, font_size=36):
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, font_size)
        self.is_selected = False
        self.hover_offset = 0  # Hover animation to make it extra jazzy

    def draw(self, surface):
        """Draw the menu item with a glowing effect if it's selected. Like magic, but with pixels."""
        color = (255, 255, 0) if self.is_selected else (255, 255, 255)  # Yellow for selected, white for normal
        text_surface = self.font.render(self.text, True, color)
        pos = (self.position[0], self.position[1] + self.hover_offset)  # Hover effect adds a little flair
        surface.blit(text_surface, pos)

    def update(self):
        """Animate the menu item. It's like a dance—hovering in a rhythmic motion."""
        self.hover_offset = -5 * abs(math.sin(pygame.time.get_ticks() * 0.003)) if self.is_selected else 0


class MenuSystem:
    """The all-powerful system that controls the game's menus. Where the magic of navigation happens."""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = MenuState.MAIN  # Starting in the main menu, naturally
        self.selected_index = 0
        self.last_input_time = 0  # Don't let the player spam too much, time is precious!

        # Menu items—each one is a chance for the player to pick their fate
        self.menu_items = [
            MenuItem("Start Game", (screen_width // 2 - 80, screen_height // 2 - 60),
                     lambda: setattr(self, 'state', MenuState.PLAYING)),
            MenuItem("Credits", (screen_width // 2 - 60, screen_height // 2),
                     lambda: setattr(self, 'state', MenuState.CREDITS)),
            MenuItem("Exit", (screen_width // 2 - 40, screen_height // 2 + 60),
                     lambda: sys.exit())  # When you're done, you're DONE
        ]

        # Title font—because a game like this deserves a title that stands tall
        self.title_font = pygame.font.Font(None, 72)

    def update(self):
        """Update the menu state based on user input. Let the keys guide you."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_input_time < 200:  # Limit input speed to avoid menu spamming
            return

        keys = pygame.key.get_pressed()  # What keys is the player holding? We need to know.
        for item in self.menu_items:
            item.is_selected = False  # Deselect all items
        self.menu_items[self.selected_index].is_selected = True  # The selected item gets special treatment
        
        # Handle navigation—it's like a dance, up and down, selecting with grace
        if keys[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            self.last_input_time = current_time  # Keep track of when we last input something
        elif keys[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            self.last_input_time = current_time
        elif keys[pygame.K_RETURN]:
            self.menu_items[self.selected_index].action()
            self.last_input_time = current_time

        for item in self.menu_items:
            item.update()  # Update the hover animations

    def draw(self, screen):
        """Render the menu to the screen, in all its pixelated glory."""
        screen.fill((0, 0, 40))  # Dark blue background, because we're cool like that
        title_text = self.title_font.render("Super Mario FX Beta", True, (255, 255, 255))
        screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))

        for item in self.menu_items:
            item.draw(screen)  # Draw each menu item


# ------------------------ GAMEPLAY AND URSINA ------------------------

def run_ursina_game():
    """Run the 3D Ursina gameplay. A whole new world of polygons awaits."""
    print("Starting game engine Ninnt 1.0... Wait, what's Ninnt? Is it real? Find out in the game.")
    app = Ursina(borderless=False)
    window.title = "Super Mario FX Beta - 3D Gameplay"
    window.fullscreen = False
    window.size = (800, 600)

    ground = Entity(model='plane', scale=32, color=color.gray)  # The ground. Always a good place to start.
    player = Entity(model='cube', color=color.orange, scale=1, position=(0, 0.5, 0))  # You, the hero.

    # Some boxes to spice up the environment. Because who doesn’t love boxes?
    box1 = Entity(model='cube', color=color.red, scale=1, position=(2, 0.5, 2))
    box2 = Entity(model='cube', color=color.blue, scale=1, position=(-2, 0.5, -2))
    box3 = Entity(model='cube', color=color.green, scale=1, position=(2, 0.5, -2))
    box4 = Entity(model='cube', color=color.yellow, scale=1, position=(-2, 0.5, 2))

    camera.position = (0, 10, -15)  # Camera follows you, because that's what good cameras do
    camera.look_at(player.position)  # Always watching you
    camera.fov = 90  # Give the player a wide field of view, because they're going places

    def update():
        speed = 5 * time.dt  # Player speed, scaling with time
        if held_keys['w']:
            player.z += speed
        if held_keys['s']:
            player.z -= speed
        if held_keys['a']:
            player.x -= speed
        if held_keys['d']:
            player.x += speed

        # Camera follows the player. Just like the world follows their every move.
        camera.position = player.position + (0, 10, -15)
        camera.look_at(player.position)

        if held_keys['escape']:  # Escape the madness. We all need an escape button.
            application.quit()

    app.run()


# ------------------------ MAIN GAME CLASS ------------------------

class Game:
    """Main game class. The center of all things—menus, gameplay, and artful destruction."""
    def __init__(self):
        pygame.init()  # Initialize Pygame, because it's the law
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True  # Run it until the end of time (or until you quit)

        # Components—menu, renderer, the usual suspects
        self.menu = MenuSystem(self.screen_width, self.screen_height)
        self.renderer = FTRender(self.screen_width, self.screen_height)

    def run(self):
        """The main loop. The heart of the game, pulsing with every frame."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.menu.state == MenuState.PLAYING:
                pygame.display.quit()  # Pygame window, time to go
                pygame.quit()
                run_ursina_game()  # Start the Ursina game. It's go time!
                pygame.init()  # Reinitialize Pygame like a phoenix rising from the ashes
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("Super Mario FX Beta")
                self.menu.state = MenuState.MAIN  # Back to the main menu, folks!

            if self.menu.state == MenuState.MAIN:
                self.menu.update()
                self.menu.draw(self.screen)
                self.renderer.render(self.screen)

            elif self.menu.state == MenuState.CREDITS:
                # Credits screen. A moment of glory for the creators.
                self.screen.fill((0, 0, 0))  # Black background for a dramatic effect
                credits_font = pygame.font.Font(None, 48)
                credits_text = credits_font.render("Credits: Made by Gemini", True, (255, 255, 255))
                self.screen.blit(credits_text, (self.screen_width // 2 - credits_text.get_width() // 2,
                                                 self.screen_height // 2 - 20))

                # A way to escape the credits. Because sometimes, you just want to get back to the game.
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] or keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                    self.menu.state = MenuState.MAIN

            pygame.display.flip()  # Flip that display buffer like a pancake
            self.clock.tick(60)  # 60 FPS. Smooth like butter.

        pygame.quit()  # Pygame says goodbye


# ------------------------ ENTRY POINT ------------------------

if __name__ == "__main__":
    game = Game()
    game.run()
    ##
    ## [c] [ Team Flames 199X-20XX]
