ezenginev0.py 
###
[C]Flames Labs [20XX]
import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Tuple

# FTRender 1.0 System Constants
RENDER_SCALE = 2
SUBPIXEL_PRECISION = 4
MAX_SPRITES = 128
SCANLINE_BUFFER_SIZE = 256

# FX Beta-specific constants
PERSPECTIVE_DEPTH = 2.5
ROTATION_SPEED = 0.002
CAMERA_SMOOTHING = 0.15
GRAVITY = 15.0
JUMP_FORCE = -450
RUN_SPEED = 350
FRICTION = 0.85

@dataclass
class RenderObject:
    texture: pygame.Surface
    position: Tuple[float, float]
    scale: float = 1.0
    rotation: float = 0.0
    layer: int = 0
    perspective_enabled: bool = True
    ascii_mode: bool = False
    
class FTRender:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.render_buffer = pygame.Surface((screen_width * RENDER_SCALE, screen_height * RENDER_SCALE))
        self.scanline_buffer = [0] * SCANLINE_BUFFER_SIZE
        self.render_objects: List[RenderObject] = []
        self.perspective_angle = 0
        self.ascii_font = pygame.font.SysFont('Courier', 12)  # Initialize ASCII font
        self.ascii_chars = ' .:-=+*#%@'  # ASCII brightness levels
        
    def pixel_to_ascii(self, pixel):
        # Convert RGB to brightness (0-255)
        brightness = sum(pixel[:3]) / 3
        # Map brightness to ASCII character
        index = int(brightness / 256 * len(self.ascii_chars))
        return self.ascii_chars[min(index, len(self.ascii_chars)-1)]
        
    def surface_to_ascii(self, surface: pygame.Surface) -> pygame.Surface:
        width, height = surface.get_size()
        char_width, char_height = self.ascii_font.size('A')
        
        # Create new surface for ASCII art
        ascii_surface = pygame.Surface((width, height))
        ascii_surface.fill((0, 0, 0))
        
        # Convert pixels to ASCII characters
        for y in range(0, height, char_height):
            for x in range(0, width, char_width):
                # Sample pixel color
                try:
                    pixel = surface.get_at((x, y))
                    char = self.pixel_to_ascii(pixel)
                    # Render ASCII character
                    char_surface = self.ascii_font.render(char, True, (255, 255, 255))
                    ascii_surface.blit(char_surface, (x, y))
                except IndexError:
                    continue
                    
        return ascii_surface

    def add_object(self, obj: RenderObject):
        if len(self.render_objects) < MAX_SPRITES:
            self.render_objects.append(obj)
            self.render_objects.sort(key=lambda x: x.layer)
            
    def clear_buffer(self):
        self.render_buffer.fill((0, 0, 0))
        self.render_objects.clear()
        
    def apply_fx_perspective(self, surface: pygame.Surface, camera_x: float, camera_y: float):
        width, height = surface.get_size()
        result = pygame.Surface((width, height))
        
        # FX Beta-style perspective transformation
        horizon = height * 0.5
        for y in range(height):
            scale = 1.0
            if y > horizon:
                scale = 1.0 + (y - horizon) / height * PERSPECTIVE_DEPTH
            
            for x in range(width):
                # Apply perspective distortion
                source_x = (x - width/2) * scale + width/2
                source_y = y
                
                # Add subtle wave effect
                wave = math.sin(y * 0.02 + self.perspective_angle) * 5
                source_x += wave
                
                # Sample pixel with bounds checking
                if 0 <= int(source_x) < width and 0 <= int(source_y) < height:
                    color = surface.get_at((int(source_x), int(source_y)))
                    result.set_at((x, y), color)
                    
        self.perspective_angle += ROTATION_SPEED
        return result

class GameObject:
    def __init__(self, x, y, width, height):
        self.position = pygame.math.Vector2(x, y)
        self.width = width
        self.height = height
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_ground = False
        self.render_object = None

    def update(self, dt):
        # Apply gravity
        if not self.on_ground:
            self.velocity.y += GRAVITY * dt

        # Apply friction
        self.velocity.x *= FRICTION

        # Update position
        self.position += self.velocity * dt

        # Reset on_ground status
        self.on_ground = False

    def check_collision(self, platforms):
        for platform in platforms:
            if self.position.x < platform.right and self.position.x + self.width > platform.left and \
               self.position.y < platform.bottom and self.position.y + self.height > platform.top:
                if self.velocity.y > 0:  # Falling
                    self.position.y = platform.top - self.height
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:  # Jumping
                    self.position.y = platform.bottom
                    self.velocity.y = 0

    def jump(self):
        if self.on_ground:
            self.velocity.y = JUMP_FORCE

    def move_left(self):
        self.velocity.x = -RUN_SPEED

    def move_right(self):
        self.velocity.x = RUN_SPEED

    def stop(self):
        self.velocity.x = 0

    def set_render_object(self, render_object):
        self.render_object = render_object

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True
        self.ascii_mode = False  # Add ASCII mode toggle
        
        # Initialize rendering system
        self.renderer = FTRender(800, 600)
        self.camera = pygame.math.Vector2(0, 0)
        self.target_camera = pygame.math.Vector2(0, 0)
        
        # Initialize game objects
        self.mario = GameObject(100, 100, 24, 32)
        self.luigi = GameObject(160, 100, 24, 32)
        self.game_objects = [self.mario, self.luigi]
        
        # Create platforms
        self.platforms = []
        self.create_level()
        
        # Load textures and create render objects
        self.init_textures()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Add ASCII mode toggle with Tab key
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.ascii_mode = not self.ascii_mode
                    
        # [Rest of the existing input handling code]

    def render(self):
        # Clear the render buffer
        self.renderer.clear_buffer()
        
        # Create background with gradient
        background = pygame.Surface((800, 600))
        for y in range(600):
            color = (92 - y//10, 148 - y//8, 252 - y//6)
            pygame.draw.line(background, color, (0, y), (800, y))
            
        # Apply FX perspective effect
        transformed_bg = self.renderer.apply_fx_perspective(
            background,
            self.camera.x,
            self.camera.y
        )
        
        # Create a temporary surface for all game elements
        game_surface = pygame.Surface((800, 600))
        game_surface.blit(transformed_bg, (0, 0))
        
        # Draw platforms
        for platform in self.platforms:
            rect = platform.copy()
            rect.x -= self.camera.x
            rect.y -= self.camera.y
            pygame.draw.rect(game_surface, (139, 69, 19), rect)
        
        # Draw render objects
        for obj in self.game_objects:
            if obj.render_object:
                pos = (obj.position.x - self.camera.x, obj.position.y - self.camera.y)
                game_surface.blit(obj.render_object.texture, pos)
        
        # Apply ASCII conversion if enabled
        if self.ascii_mode:
            game_surface = self.renderer.surface_to_ascii(game_surface)
            
        # Final blit to screen
        self.screen.blit(game_surface, (0, 0))
        pygame.display.flip()

    def create_level(self):
        # Create some platforms for the level
        self.platforms.append(pygame.Rect(50, 500, 200, 20))
        self.platforms.append(pygame.Rect(300, 400, 200, 20))
        self.platforms.append(pygame.Rect(550, 300, 200, 20))

    def init_textures(self):
        # Load textures and create render objects for Mario and Luigi
        mario_texture = pygame.Surface((24, 32))
        mario_texture.fill((255, 0, 0))
        self.mario.set_render_object(RenderObject(mario_texture, (self.mario.position.x, self.mario.position.y)))

        luigi_texture = pygame.Surface((24, 32))
        luigi_texture.fill((0, 255, 0))
        self.luigi.set_render_object(RenderObject(luigi_texture, (self.luigi.position.x, self.luigi.position.y)))

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_input()
            self.update(dt)
            self.render()

    def update(self, dt):
        for obj in self.game_objects:
            obj.update(dt)
            obj.check_collision(self.platforms)

if __name__ == "__main__":
    game = Game()
    game.run()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True
        self.ascii_mode = False  # Add ASCII mode toggle
        
        # Initialize rendering system
        self.renderer = FTRender(800, 600)
        self.camera = pygame.math.Vector2(0, 0)
        self.target_camera = pygame.math.Vector2(0, 0)
        
        # Initialize game objects
        self.mario = GameObject(100, 100, 24, 32)
        self.luigi = GameObject(160, 100, 24, 32)
        self.game_objects = [self.mario, self.luigi]
        
        # Create platforms
        self.platforms = []
        self.create_level()
        
        # Load textures and create render objects
        self.init_textures()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Add ASCII mode toggle with Tab key
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.ascii_mode = not self.ascii_mode
                    
        # [Rest of the existing input handling code]

    def render(self):
        # Clear the render buffer
        self.renderer.clear_buffer()
        
        # Create background with gradient
        background = pygame.Surface((800, 600))
        for y in range(600):
            color = (92 - y//10, 148 - y//8, 252 - y//6)
            pygame.draw.line(background, color, (0, y), (800, y))
            
        # Apply FX perspective effect
        transformed_bg = self.renderer.apply_fx_perspective(
            background,
            self.camera.x,
            self.camera.y
        )
        
        # Create a temporary surface for all game elements
        game_surface = pygame.Surface((800, 600))
        game_surface.blit(transformed_bg, (0, 0))
        
        # Draw platforms
        for platform in self.platforms:
            rect = platform.copy()
            rect.x -= self.camera.x
            rect.y -= self.camera.y
            pygame.draw.rect(game_surface, (139, 69, 19), rect)
        
        # Draw render objects
        for obj in self.game_objects:
            if obj.render_object:
                pos = (obj.position.x - self.camera.x, obj.position.y - self.camera.y)
                game_surface.blit(obj.render_object.texture, pos)
        
        # Apply ASCII conversion if enabled
        if self.ascii_mode:
            game_surface = self.renderer.surface_to_ascii(game_surface)
            
        # Final blit to screen
        self.screen.blit(game_surface, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
