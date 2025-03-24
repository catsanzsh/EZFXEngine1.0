from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import basic_lighting_shader
import random
import time
import math

app = Ursina()

# --------------------------------------------------------------------------------
# B3313-Like Settings
# --------------------------------------------------------------------------------
window.fullscreen = True
window.title = "EZENGINE2.0A - B3313-Style Experience"
window.color = color.black
window.fps_counter.enabled = False  # Hide FPS counter
window.exit_button.visible = False  # Hide exit button

# Player tracking data
player_data = {
    "moves": 0,
    "jumps": 0,
    "stars_collected": {"yellow": 0, "red": 0, "green": 0},
    "time_spent": 0,
    "glitches_encountered": 0
}

# --------------------------------------------------------------------------------
# B3313-Inspired Player
# --------------------------------------------------------------------------------
class B3313Player(Entity):
    def __init__(self):
        super().__init__()
        self.speed = 11
        self.jump_height = 2.7
        self.jump_duration = 0.35
        self.gravity = 1.3
        self.velocity_y = 0
        self.jumping = False
        self.grounded = False
        self.triple_jump_counter = 0
        self.triple_jump_cooldown = 0.7

        self.model = 'cube'
        self.scale = (0.7, 1.7, 0.7)
        self.color = color.rgb(255, 215, 0)
        self.collider = BoxCollider(self, center=(0, 0.85, 0), size=(0.7, 1.7, 0.7))

        camera.parent = self
        camera.position = (0, 1.3, -1)
        camera.fov = 75

    def update(self):
        player_data["time_spent"] += time.dt
        direction = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()

        if direction.length() > 0:
            player_data["moves"] += 1
            self.position += direction * self.speed * time.dt
            self.rotation_y = lerp(self.rotation_y, -direction.x * 35 + random.uniform(-5, 5), 0.15)

        self.velocity_y -= self.gravity * time.dt

        if held_keys['space'] and self.grounded and not self.jumping and self.triple_jump_cooldown <= 0:
            self.jumping = True
            player_data["jumps"] += 1
            self.triple_jump_counter += 1
            jump_modifier = (1 + 0.25 * min(self.triple_jump_counter - 1, 2))
            self.velocity_y = self.jump_height * jump_modifier + random.uniform(-0.3, 0.3)

            if self.triple_jump_counter >= 3:
                self.triple_jump_counter = 0
                self.triple_jump_cooldown = 0.7

            invoke(self.reset_jump, delay=self.jump_duration)

        self.y += self.velocity_y * time.dt

        hit_info = raycast(self.position + Vec3(0, 0.1, 0), Vec3(0, -1, 0), distance=0.55)
        if hit_info.hit:
            self.grounded = True
            self.y = hit_info.world_point.y
            self.velocity_y = max(self.velocity_y, 0)
        else:
            self.grounded = False
            if not self.jumping and self.velocity_y < -5 and random.random() < 0.01:
                self.y -= 0.5
                player_data["glitches_encountered"] += 1

        if self.triple_jump_cooldown > 0:
            self.triple_jump_cooldown -= time.dt

    def reset_jump(self):
        self.jumping = False

# --------------------------------------------------------------------------------
# B3313-Style Star
# --------------------------------------------------------------------------------
class Star(Entity):
    def __init__(self, position, star_type):
        super().__init__()
        self.position = position
        self.star_type = star_type
        self.y_offset = random.random()
        self.rotation_speed = random.uniform(45, 75)
        self.scale_factor = 1
        self.scale_direction = 0.01

        self.model = 'icosahedron'
        self.scale = 0.5
        self.color = {
            'yellow': color.rgb(255, 255, 100),
            'red': color.rgb(255, 50, 50),
            'green': color.rgb(50, 255, 50)
        }[star_type]
        self.collider = SphereCollider(self, radius=0.5)

    def update(self):
        self.rotation_y += self.rotation_speed * time.dt
        self.y = self.position.y + math.sin(time.time() * 4 + self.y_offset) * 0.25

        self.scale_factor += self.scale_direction
        if self.scale_factor > 1.1 or self.scale_factor < 0.9:
            self.scale_direction *= -1
        self.scale = 0.5 * self.scale_factor

        if distance(self.position, player.position) < 1.5:
            player_data["stars_collected"][self.star_type] += 1
            destroy(self)

# --------------------------------------------------------------------------------
# B3313-Style Block
# --------------------------------------------------------------------------------
class Block(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            position=position,
            collider='box',
            color=color.hsv(
                (player_data["moves"] + player_data["jumps"]) % 360,
                0.9,
                0.7 + random.uniform(-0.1, 0.1)
            )
        )
        self.scale = (1.05, 1.05, 1.05)
        if random.random() < 0.05:
            self.position += Vec3(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
            self.scale += random.uniform(-0.05, 0.05)

# --------------------------------------------------------------------------------
# Level Generation
# --------------------------------------------------------------------------------
def create_level():
    random.seed(time.time() + player_data["moves"] + player_data["jumps"] + player_data["glitches_encountered"])

    for z in range(-18, 19):
        for x in range(-18, 19):
            Block(position=(x, 0, z))

    platforms = int(player_data["time_spent"] * 2.5) % 12 + 4
    for _ in range(platforms):
        x, z = random.randint(-15, 15), random.randint(-15, 15)
        height = random.randint(1, 7 + int(player_data["jumps"] / 20))
        for y in range(1, height + 1):
            Block(position=(
                x + random.uniform(-0.2, 0.2),
                y + random.uniform(-0.1, 0.1),
                z + random.uniform(-0.2, 0.2)
            ))

    star_definitions = [(50, 'yellow'), (14, 'red'), (14, 'green')]  # Reduced star counts for performance
    for count, star_type in star_definitions:
        for _ in range(count):
            x, z = random.randint(-15, 15), random.randint(-15, 15)
            y = random.randint(1, 15 + int(player_data["stars_collected"]["yellow"] / 120))
            Star(position=(
                x + random.uniform(-0.3, 0.3),
                y + random.uniform(-0.3, 0.3),
                z + random.uniform(-0.3, 0.3)
            ), star_type=star_type)

# --------------------------------------------------------------------------------
# B3313-Style Sky
# --------------------------------------------------------------------------------
class Sky(Entity):
    def __init__(self):
        super().__init__(
            model='sphere',
            scale=280,
            double_sided=True,
            segments=6,
            texture='sky_default'
        )
        self.color = color.hsv((player_data["time_spent"] * 2) % 360, 0.8, 0.8 + random.uniform(-0.2, 0.2))

    def update(self):
        self.color = color.hsv((player_data["time_spent"] * 2) % 360 + random.uniform(-10, 10), 0.8, 0.8 + random.uniform(-0.2, 0.2))

# --------------------------------------------------------------------------------
# Star Counter HUD
# --------------------------------------------------------------------------------
class StarCounter(Text):
    def __init__(self):
        super().__init__(
            text="Y:0 | R:0 | G:0",
            position=(-0.85, 0.45),
            scale=1.6,
            color=color.rgb(100, 255, 200)
        )

    def update(self):
        s = player_data["stars_collected"]
        self.text = f"Y:{s['yellow']} | R:{s['red']} | G:{s['green']}"
        if sum(s.values()) >= 50:
            self.text += "\nB0NUS!"

# --------------------------------------------------------------------------------
# Initialize and Run
# --------------------------------------------------------------------------------
player = B3313Player()
Sky()
StarCounter()
create_level()

Text(
    text="WASD MOVE | SPACE JUMP | COLLECT STARS",
    position=(-0.5, -0.4),
    scale=1.3,
    color=color.rgb(100, 255, 200)
)

app.run()
