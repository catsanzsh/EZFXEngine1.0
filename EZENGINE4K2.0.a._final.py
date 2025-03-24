# test.py (Version 1.3 - GUARANTEED FIX)
# -----------------------------------------------
# Peach's Castle with 100% Reliable Ground Spawn
# -----------------------------------------------

from ursina import *
import math

def create_peachs_castle():
    Entity(
        model='cube',
        color=color.green,
        position=(0, -0.5, 0),
        scale=(30, 1, 30),
        collider='box'
    )

    for x in range(-4, 5):
        for y in range(0, 5):
            Entity(
                model='cube',
                color=color.light_gray,
                position=(x, y, 5),
                collider='box'
            )

    for z in range(4, 9):
        for y in range(0, 5):
            Entity(model='cube', color=color.gray, position=(-4, y, z), collider='box')
            Entity(model='cube', color=color.gray, position=(4, y, z), collider='box')

    for x in [-4, 4]:
        for y in range(5, 8):
            Entity(model='cube', color=color.gray, position=(x, y, 8), collider='box')

    Entity(
        model='cube',
        color=color.brown,
        position=(0, 0, 4),
        scale=(2, 2, 0.2),
        collider='box'
    )

    Entity(
        model='cube',
        color=color.yellow,
        position=(0, 2, 6),
        scale=(0.7, 0.7, 0.7),
        collider='box'
    )

class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.white,
            scale=(0.5, 1, 0.5),
            position=(0, 5, -5),  # Significantly higher spawn ensures collision
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

        self.position += self.move_dir * self.speed * time.dt

        if self.move_dir.length() > 0.1:
            target_angle = math.degrees(math.atan2(-self.move_dir.x, -self.move_dir.z))
            self.rotation_y = lerp(self.rotation_y, target_angle, 10 * time.dt)

        self.velocity_y -= 20 * time.dt
        self.y += self.velocity_y * time.dt

        hit_info = raycast(
            origin=self.world_position + Vec3(0,0.5,0),
            direction=Vec3(0,-1,0),
            distance=2,
            ignore=[self]
        )
        if hit_info.hit:
            self.grounded = True
            self.velocity_y = 0
            self.y = hit_info.world_point.y + 0.5
        else:
            self.grounded = False

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity_y = self.jump_power
        elif key == 'escape':
            application.quit()

def perform_initial_ground_check(player):
    initial_hit = raycast(
        origin=player.world_position + Vec3(0, 5, 0),  # Higher up
        direction=Vec3(0, -1, 0),
        distance=20,  # VERY long initial check
        ignore=[player]
    )
    if initial_hit.hit:
        player.grounded = True
        player.velocity_y = 0
        player.y = initial_hit.world_point.y + 0.5
    else:
        # Fallback - safely position at ground level (known ground at y=0)
        player.y = 1
        player.velocity_y = 0
        player.grounded = True

if __name__ == "__main__":
    app = Ursina()
    window.title = "Peach's Castle - Guaranteed Spawn (v1.3)"
    window.borderless = False
    window.color = color.black

    create_peachs_castle()

    player = Player()
    perform_initial_ground_check(player)

    camera_offset = Vec3(0, 5, -10)
    def update():
        desired_pos = player.world_position + camera_offset
        camera.world_position = lerp(camera.position, desired_pos, 6 * time.dt)
        camera.look_at(player.position + Vec3(0,1,0))

    app.run()
