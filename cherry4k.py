from ursina import *
import random
import math

app = Ursina()
window.title = "B3313-Inspired Surreal Game"
window.borderless = False
Texture.default_filtering = None
window.color = color.black

# --- Player ---
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.white,
            position=(0, 3, 0),  # Spawn higher for safety
            scale=(0.5, 1, 0.5),
            collider='box'
        )
        self.speed = 6
        self.jump_power = 8
        self.velocity_y = 0
        self.grounded = False
        self.move_dir = Vec3(0,0,0)

    def update(self):
        move_input = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        )

        if move_input.length() > 0:
            move_input = move_input.normalized()
            self.move_dir = lerp(self.move_dir, move_input, 6 * time.dt)
        else:
            self.move_dir = lerp(self.move_dir, Vec3(0,0,0), 4 * time.dt)

        move_amount = self.move_dir * self.speed
        self.position += move_amount * time.dt

        if self.move_dir.length() > 0.1:
            target_angle = math.degrees(math.atan2(-self.move_dir.x, -self.move_dir.z))
            self.rotation_y = lerp(self.rotation_y, target_angle, 10 * time.dt)

        self.velocity_y -= 20 * time.dt
        self.y += self.velocity_y * time.dt

        hit_info = raycast(self.world_position + Vec3(0,0.1,0), Vec3(0,-1,0), distance=0.6, ignore=[self])
        self.grounded = hit_info.hit
        if self.grounded:
            self.velocity_y = 0
            self.y = hit_info.world_point.y + 0.5

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity_y = self.jump_power
        elif key == 'escape':
            application.quit()

# --- Glitch Block ---
class Block(Entity):
    def __init__(self, position=(0, 0, 0), color=color.random_color()):
        super().__init__(
            model='cube',
            texture=None,
            color=color,
            position=position,
            scale=(1, 1, 1),
            collider='box'
        )
        offset = random.uniform(-0.05, 0.05)
        self.scale = Vec3(1 + offset, 1 + offset, 1 + offset)

    def update(self):
        offset = random.uniform(-0.02, 0.02)
        self.scale += Vec3(offset, offset, offset)
        self.scale = Vec3(
            max(0.1, min(2, self.scale.x)),
            max(0.1, min(2, self.scale.y)),
            max(0.1, min(2, self.scale.z))
        )

# --- Level Gen ---
def create_level():
    # Base ground
    Entity(
        model='cube',
        color=color.green,
        scale=(40, 1, 40),
        position=(0, -0.5, 0),
        collider='box'
    )
    # Guaranteed spawn block
    Block(position=(0, 0.5, 0), color=color.azure)
    # Surrounding glitch blocks
    for x in range(-5, 6):
        for z in range(-5, 6):
            if random.random() < 0.3:
                Block(position=(x, 0.5, z))

# --- Camera ---
camera.position = (0, 5, -12)
camera_offset = Vec3(0, 5, -12)

def update():
    desired = player.world_position + camera_offset
    camera.world_position = lerp(camera.world_position, desired, 4 * time.dt)
    camera.look_at(player.position + Vec3(0,1,0))

# --- Start Game ---
player = Player()
create_level()
app.run()
