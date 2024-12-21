from ursina import *
import math
import random
from enum import Enum

# -------------------
#    Player States
# -------------------
class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    DOUBLE_JUMPING = "double_jumping"
    TRIPLE_JUMPING = "triple_jumping"
    SIDE_FLIP = "side_flip"
    BACK_FLIP = "back_flip"
    GROUND_POUND = "ground_pound"
    WALL_SLIDING = "wall_sliding"

# -------------------
#    Utility Functions
# -------------------
def safe_audio_load(file_name):
    try:
        return Audio(file_name, autoplay=False)
    except Exception as e:
        print(f"Warning: Failed to load audio '{file_name}': {e}")
        return None

# -------------------
#    Player Controller
# -------------------
class MarioController(Entity):
    def __init__(self, position=(0,1,0)):
        super().__init__(
            position=position,
            model='cube',
            color=color.red,
            scale=(1, 2, 1),
            collider='box'
        )
        self.speed = 5
        self.run_multiplier = 1.5
        self.gravity = 1.5
        self.jump_strength = 12
        self.velocity = Vec3(0, 0, 0)
        self.is_grounded = False
        self.state = PlayerState.IDLE
        
        # Audio files
        self.sounds = {
            'jump': safe_audio_load('jump.wav'),
            'double_jump': safe_audio_load('double_jump.wav'),
            'triple_jump': safe_audio_load('triple_jump.wav'),
            'ground_pound': safe_audio_load('ground_pound.wav'),
            'coin': safe_audio_load('coin.wav')
        }

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.move()
        self.check_ground_collision()

    def handle_input(self):
        move = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        ).normalized() * self.speed * (self.run_multiplier if held_keys['shift'] else 1) * time.dt

        self.position += move

        if held_keys['space'] and self.is_grounded:
            self.jump()

    def jump(self):
        self.velocity.y = self.jump_strength
        self.is_grounded = False
        if self.sounds['jump']:
            self.sounds['jump'].play()

    def apply_gravity(self):
        self.velocity.y -= self.gravity * time.dt
        self.position += Vec3(0, self.velocity.y * time.dt, 0)

    def move(self):
        self.position += self.velocity * time.dt

    def check_ground_collision(self):
        hit_info = raycast(self.world_position, direction=Vec3(0, -1, 0), distance=1.5, ignore=[self])
        if hit_info.hit:
            self.is_grounded = True
            self.velocity.y = 0
            self.position = Vec3(self.position.x, hit_info.world_point.y + 0.5, self.position.z)

# -------------------
#    Coin Entity
# -------------------
class Coin(Entity):
    def __init__(self, position):
        super().__init__(
            model='circle',
            color=color.yellow,
            position=position,
            scale=0.5,
            collider='box'
        )
        self.rotation_speed = 100

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        if self.intersects().hit:
            destroy(self)

# -------------------
#    Camera Controller
# -------------------
class LakituCamera(Entity):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.distance = 10
        self.height = 5
        camera.fov = 70

    def update(self):
        self.position = self.target.position + Vec3(0, self.height, -self.distance)
        self.look_at(self.target.position)

# -------------------
#    Setup Game
# -------------------
def setup_game():
    window.color = color.cyan
    global player
    player = MarioController()

    for i in range(10):
        x, z = random.uniform(-5, 5), random.uniform(-5, 5)
        Coin(position=(x, 0.5, z))

    LakituCamera(target=player)
    Entity(model='plane', scale=20, texture='white_cube', collider='box')

# -------------------
#    Main
# -------------------
if __name__ == '__main__':
    app = Ursina()
    setup_game()
    app.run()
