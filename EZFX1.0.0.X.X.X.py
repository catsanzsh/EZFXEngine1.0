from ursina import *
import random
import math

app = Ursina()
window.title = "Peach's Castle - B3313 Test Map"
window.borderless = False
Texture.default_filtering = None
window.color = color.black

# --- Mario (White Cube) ---
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.white,
            position=(0, 1.1, -10),  # Start in front of castle
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

# --- Castle Block ---
class Block(Entity):
    def __init__(self, position=(0, 0, 0), color=color.light_gray, scale=(1,1,1)):
        super().__init__(
            model='cube',
            color=color,
            position=position,
            scale=scale,
            collider='box'
        )

# --- Castle Map ---
def create_peachs_castle():
    # Ground courtyard
    Entity(model='cube', scale=(30, 1, 30), position=(0, -0.5, 0), color=color.green, collider='box')

    # Castle base
    for x in range(-4, 5):
        for y in range(0, 5):
            Block(position=(x, y, 5), color=color.light_gray)

    # Castle sides
    for z in range(4, 9):
        for y in range(0, 5):
            Block(position=(-4, y, z), color=color.gray)
            Block(position=(4, y, z), color=color.gray)

    # Castle towers
    for x in [-4, 4]:
        for z in [8]:
            for y in range(5, 8):
                Block(position=(x, y, z), color=color.gray)

    # Castle door
    Block(position=(0, 0, 4), color=color.brown, scale=(2,2,0.2))

    # Floating star block inside
    Block(position=(0, 2, 6), color=color.yellow, scale=(0.7, 0.7, 0.7))

# --- Camera ---
camera.position = (0, 5, -15)
camera_offset = Vec3(0, 5, -15)

def update():
    desired = player.world_position + camera_offset
    camera.world_position = lerp(camera.world_position, desired, 4 * time.dt)
    camera.look_at(player.position + Vec3(0,1,0))

# --- Game Start ---
player = Player()
create_peachs_castle()
app.run()
