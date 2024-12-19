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
    
class FTRender:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.render_buffer = pygame.Surface((screen_width * RENDER_SCALE, screen_height * RENDER_SCALE))
        self.scanline_buffer = [0] * SCANLINE_BUFFER_SIZE
        self.render_objects: List[RenderObject] = []
        self.perspective_angle = 0
        
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

class PhysicsComponent:
    def __init__(self):
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, GRAVITY)
        self.mass = 1.0
        self.on_ground = False
        
    def apply_force(self, force: pygame.math.Vector2):
        self.acceleration += force / self.mass
        
    def update(self, dt: float):
        self.velocity += self.acceleration * dt
        self.velocity.x *= FRICTION  # Apply friction
        # Terminal velocity
        self.velocity.y = min(400, max(-400, self.velocity.y))
        self.acceleration = pygame.math.Vector2(0, GRAVITY)

class GameObject:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.position = pygame.math.Vector2(x, y)
        self.physics = PhysicsComponent()
        self.collision = pygame.Rect(x, y, width, height)
        self.sprite = None
        self.render_object = None
        self.facing_right = True
        self.is_jumping = False
        
    def update(self, dt: float, platforms):
        prev_pos = pygame.math.Vector2(self.position)
        self.physics.update(dt)
        self.position += self.physics.velocity * dt
        
        # Update collision rect
        self.collision.x = self.position.x
        self.collision.y = self.position.y
        
        # Platform collision
        self.physics.on_ground = False
        for platform in platforms:
            if self.collision.colliderect(platform):
                if self.physics.velocity.y > 0:  # Falling
                    self.collision.bottom = platform.top
                    self.position.y = self.collision.y
                    self.physics.velocity.y = 0
                    self.physics.on_ground = True
                    self.is_jumping = False
                elif self.physics.velocity.y < 0:  # Jumping
                    self.collision.top = platform.bottom
                    self.position.y = self.collision.y
                    self.physics.velocity.y = 0
                
        # Update render object
        if self.render_object:
            self.render_object.position = (self.position.x, self.position.y)
            # Flip sprite based on direction
            if self.physics.velocity.x > 0:
                self.facing_right = True
            elif self.physics.velocity.x < 0:
                self.facing_right = False
            
            if not self.facing_right:
                self.render_object.texture = pygame.transform.flip(self.sprite, True, False)
            else:
                self.render_object.texture = self.sprite

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Super Mario FX Beta")
        self.clock = pygame.time.Clock()
        self.running = True
        
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
        
    def create_level(self):
        # Ground
        ground = pygame.Rect(0, 500, 800, 100)
        self.platforms.append(ground)
        
        # Platforms
        platform_positions = [
            (300, 400, 100, 20),
            (500, 300, 100, 20),
            (200, 200, 100, 20),
            (600, 450, 100, 20)
        ]
        
        for pos in platform_positions:
            self.platforms.append(pygame.Rect(*pos))
        
    def init_textures(self):
        # Create character sprites with simple shading
        mario_texture = pygame.Surface((24, 32))
        mario_texture.fill((255, 0, 0))
        # Add shading
        pygame.draw.rect(mario_texture, (200, 0, 0), (0, 16, 24, 16))
        
        luigi_texture = pygame.Surface((24, 32))
        luigi_texture.fill((0, 255, 0))
        pygame.draw.rect(luigi_texture, (0, 200, 0), (0, 16, 24, 16))
        
        self.mario.sprite = mario_texture
        self.luigi.sprite = luigi_texture
        
        self.mario.render_object = RenderObject(
            texture=mario_texture,
            position=(self.mario.position.x, self.mario.position.y),
            layer=1
        )
        
        self.luigi.render_object = RenderObject(
            texture=luigi_texture,
            position=(self.luigi.position.x, self.luigi.position.y),
            layer=1
        )

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Mario controls
        if keys[pygame.K_RIGHT]:
            self.mario.physics.apply_force(pygame.math.Vector2(RUN_SPEED, 0))
        if keys[pygame.K_LEFT]:
            self.mario.physics.apply_force(pygame.math.Vector2(-RUN_SPEED, 0))
        if keys[pygame.K_SPACE] and self.mario.physics.on_ground and not self.mario.is_jumping:
            self.mario.physics.velocity.y = JUMP_FORCE
            self.mario.is_jumping = True
            
        # Luigi controls
        if keys[pygame.K_d]:
            self.luigi.physics.apply_force(pygame.math.Vector2(RUN_SPEED, 0))
        if keys[pygame.K_a]:
            self.luigi.physics.apply_force(pygame.math.Vector2(-RUN_SPEED, 0))
        if keys[pygame.K_w] and self.luigi.physics.on_ground and not self.luigi.is_jumping:
            self.luigi.physics.velocity.y = JUMP_FORCE
            self.luigi.is_jumping = True

    def update(self):
        dt = self.clock.get_time() / 1000.0
        
        # Update game objects
        for obj in self.game_objects:
            obj.update(dt, self.platforms)
            
        # Smooth camera following
        self.target_camera.x = self.mario.position.x - 400
        self.target_camera.y = self.mario.position.y - 300
        
        self.camera += (self.target_camera - self.camera) * CAMERA_SMOOTHING
        
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
        
        # Draw everything to screen
        self.screen.blit(transformed_bg, (0, 0))
        
        # Draw platforms
        for platform in self.platforms:
            rect = platform.copy()
            rect.x -= self.camera.x
            rect.y -= self.camera.y
            pygame.draw.rect(self.screen, (139, 69, 19), rect)
        
        # Draw render objects
        for obj in self.game_objects:
            if obj.render_object:
                pos = (obj.position.x - self.camera.x, obj.position.y - self.camera.y)
                self.screen.blit(obj.render_object.texture, pos)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
