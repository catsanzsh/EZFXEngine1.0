import pygame
import json  # Retained in case you plan to use it elsewhere
## [C] Team Flames 20XX

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40

# Animation states
IDLE = 'idle'
WALKING = 'walking'
JUMPING = 'jumping'

# Colors for placeholder sprites
COLOR_MAP = {
    'mario': {
        IDLE: (255, 0, 0),       # Red
        WALKING: (200, 0, 0),
        JUMPING: (150, 0, 0)
    },
    'luigi': {
        IDLE: (0, 255, 0),       # Green
        WALKING: (0, 200, 0),
        JUMPING: (0, 150, 0)
    },
    'goomba': {
        WALKING: (139, 69, 19)   # Brown
    },
    'koopa': {
        WALKING: (0, 0, 255)     # Blue
    }
}

class SpriteSheet:
    def __init__(self):
        """
        Instead of loading from a file, generate placeholder sprites.
        """
        self.sprite_locations = {
            'mario': {
                IDLE: [self.create_sprite('mario', IDLE)],
                WALKING: [self.create_sprite('mario', WALKING, i) for i in range(3)],
                JUMPING: [self.create_sprite('mario', JUMPING)]
            },
            'luigi': {
                IDLE: [self.create_sprite('luigi', IDLE)],
                WALKING: [self.create_sprite('luigi', WALKING, i) for i in range(3)],
                JUMPING: [self.create_sprite('luigi', JUMPING)]
            },
            'goomba': {
                WALKING: [self.create_sprite('goomba', WALKING, i) for i in range(2)]
            },
            'koopa': {
                WALKING: [self.create_sprite('koopa', WALKING, i) for i in range(2)]
            }
        }

    def create_sprite(self, character, state, variation=0):
        """
        Create a placeholder sprite as a colored rectangle.
        Different variations have slight color changes to simulate animation frames.
        """
        width, height = 32, 32  # Base size before scaling
        color = COLOR_MAP.get(character, {}).get(state, (255, 255, 255))
        
        # Slight variation for different frames
        if variation > 0:
            color = tuple(max(min(c - variation * 20, 255), 0) for c in color)
        
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.fill(color)
        
        # Optionally, draw a simple shape or text to differentiate characters
        pygame.draw.rect(sprite, (0, 0, 0), sprite.get_rect(), 2)  # Black border
        
        font = pygame.font.SysFont(None, 20)
        text = font.render(character[0].upper(), True, (0, 0, 0))
        text_rect = text.get_rect(center=(width//2, height//2))
        sprite.blit(text, text_rect)
        
        return sprite

    def get_animation_frames(self, character, state):
        """Get all frames for a character's animation state."""
        return self.sprite_locations.get(character, {}).get(state, [])

class AnimatedSprite:
    def __init__(self, sprite_sheet, character, x, y, scale=2):
        self.x = x
        self.y = y
        self.scale = scale
        self.velocity_x = 0
        self.velocity_y = 0
        self.facing_right = True
        self.character = character
        self.current_state = IDLE
        
        # Load animations
        self.animations = {
            IDLE: sprite_sheet.get_animation_frames(character, IDLE),
            WALKING: sprite_sheet.get_animation_frames(character, WALKING),
            JUMPING: sprite_sheet.get_animation_frames(character, JUMPING)
        }
        
        # Remove empty animation states
        self.animations = {state: frames for state, frames in self.animations.items() if frames}
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # milliseconds per frame
        
        # Set initial sprite dimensions based on the first frame
        initial_frames = self.animations.get(IDLE) or self.animations.get(WALKING) or self.animations.get(JUMPING)
        if initial_frames:
            first_frame = initial_frames[0]
            self.width = first_frame.get_width() * scale
            self.height = first_frame.get_height() * scale
        else:
            # Fallback if no animations are found
            self.width = self.height = 32 * scale

    def update(self, dt):
        """Update sprite animation and position."""
        # Update animation frame
        self.animation_timer += dt
        frames = self.animations.get(self.current_state, [])
        if frames:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(frames)
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self, surface):
        """Draw the sprite with current animation frame."""
        frames = self.animations.get(self.current_state, [])
        if not frames:
            return

        current_sprite = frames[self.current_frame]
        
        # Scale sprite
        scaled_sprite = pygame.transform.scale(
            current_sprite, (self.width, self.height)
        )
        
        # Flip sprite if facing left
        if not self.facing_right:
            scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
        
        surface.blit(scaled_sprite, (self.x, self.y))

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()  # Initialize font module
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario World with Sprites")
        self.clock = pygame.time.Clock()
        
        # Load sprite sheet (placeholder)
        self.sprite_sheet = SpriteSheet()
        
        # Create characters
        self.mario = AnimatedSprite(self.sprite_sheet, 'mario', 100, SCREEN_HEIGHT - 64)
        self.luigi = AnimatedSprite(self.sprite_sheet, 'luigi', 200, SCREEN_HEIGHT - 64)
        
        # Create enemies
        self.enemies = [
            AnimatedSprite(self.sprite_sheet, 'goomba', 400, SCREEN_HEIGHT - 48),
            AnimatedSprite(self.sprite_sheet, 'koopa', 600, SCREEN_HEIGHT - 48)
        ]
        
        # Physics
        self.gravity = 0.8
        self.jump_force = -15
        self.move_speed = 5

    def handle_character_input(self, character, controls, keys):
        """
        Generic input handler for a character. `controls` is a dict:
            {
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'jump': pygame.K_SPACE
            }
        `keys` is the set of pressed keys from pygame.
        """
        left_key = controls['left']
        right_key = controls['right']
        jump_key = controls['jump']
        
        # Horizontal movement
        if keys[left_key]:
            character.velocity_x = -self.move_speed
            character.facing_right = False
            if character.current_state != JUMPING:
                character.current_state = WALKING
        elif keys[right_key]:
            character.velocity_x = self.move_speed
            character.facing_right = True
            if character.current_state != JUMPING:
                character.current_state = WALKING
        else:
            character.velocity_x = 0
            if character.current_state != JUMPING:
                character.current_state = IDLE

        # Jumping
        if keys[jump_key] and character.velocity_y == 0:
            character.velocity_y = self.jump_force
            character.current_state = JUMPING

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Mario controls
        mario_controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'jump': pygame.K_SPACE
        }
        self.handle_character_input(self.mario, mario_controls, keys)

        # Luigi controls
        luigi_controls = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'jump': pygame.K_w
        }
        self.handle_character_input(self.luigi, luigi_controls, keys)

    def update(self):
        dt = self.clock.tick(60)  # Ensure the game runs at 60 FPS and get the time since last tick in ms
        
        # Update players and enemies together
        all_sprites = [self.mario, self.luigi] + self.enemies
        
        for sprite in all_sprites:
            # Apply gravity
            sprite.velocity_y += self.gravity
            # Update position and animation
            sprite.update(dt)
            
            # Ground collision
            ground_level = SCREEN_HEIGHT - sprite.height
            if sprite.y >= ground_level:
                sprite.y = ground_level
                sprite.velocity_y = 0
                # Reset state if landing from jump
                if sprite.current_state == JUMPING:
                    sprite.current_state = IDLE

        # Simple enemy logic: always walking left
        for enemy in self.enemies:
            enemy.current_state = WALKING
            enemy.velocity_x = -2
            # Optional: Add boundary checks to make enemies turn around
            if enemy.x < -enemy.width:
                enemy.x = SCREEN_WIDTH

    def draw(self):
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        # Draw ground
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - 32, SCREEN_WIDTH, 32)
        pygame.draw.rect(self.screen, (34, 139, 34), ground_rect)  # Green ground
        
        # Draw characters and enemies
        for sprite in [self.mario, self.luigi] + self.enemies:
            sprite.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.handle_input()
            self.update()
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
