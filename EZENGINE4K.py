# debug_mario64.py
# -------------------------------------------------
# A minimal Ursina scene resembling a debug Mario 64
# with "ULTRA MARIO" logo and stage select screen
# -------------------------------------------------

from ursina import *
import random
import math

app = Ursina()

# Window settings
window.title = "ULTRA MARIO 64 - DEBUG MODE"
window.borderless = False
Texture.default_filtering = None
window.color = color.black

# -------------------------------------------------
# Create debug logo text entities
# -------------------------------------------------
def create_debug_logo():
    # Background for the logo
    Entity(
        model='quad',
        scale=(1.8, 0.7, 1),
        position=(0, 0.3, 0),
        color=color.blue.tint(-.4),
        parent=camera.ui
    )
    
    # ULTRA text
    Text(
        text="ULTRA",
        scale=3,
        position=(-0.22, 0.35, -0.1),
        color=color.red,
        parent=camera.ui
    )
    
    # MARIO text
    Text(
        text="MARIO",
        scale=3,
        position=(-0.22, 0.15, -0.1),
        color=color.green,
        parent=camera.ui
    )
    
    # SELECT STAGE text
    Text(
        text="SELECT STAGE",
        scale=1.5,
        position=(-0.15, 0, -0.1),
        color=color.yellow,
        parent=camera.ui
    )
    
    # Menu options
    Text(
        text="1: EXIT  H0R1 MINI",
        scale=1,
        position=(-0.15, -0.15, -0.1),
        color=color.white,
        parent=camera.ui
    )
    
    # Press Start text
    Text(
        text="PRESS START B3313",
        scale=1,
        position=(-0.15, -0.25, -0.1),
        color=color.orange,
        parent=camera.ui
    )
    
    # Super Mario text in Japanese style (simulated)
    for i in range(-3, 4):
        Text(
            text="スーパー マリオ",
            scale=0.7,
            position=(0.25*i, 0.45, -0.1),
            color=color.blue,
            parent=camera.ui
        )
        Text(
            text="スーパー マリオ",
            scale=0.7,
            position=(0.25*i, -0.35, -0.1),
            color=color.blue,
            parent=camera.ui
        )

# -------------------------------------------------
# Player (white cube) with simple movement & jumping
# -------------------------------------------------
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.white,
            position=(0, 0.5, 4),  # Start at the castle entrance
            scale=(0.5, 1, 0.5),
            collider='box'
        )
        self.speed = 6
        self.jump_power = 8
        self.velocity_y = 0
        self.grounded = True  # Start as grounded
        self.move_dir = Vec3(0,0,0)
        self.gravity_enabled = False  # Disable gravity by default

    def update(self):
        # Gather movement input
        move_input = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        )

        # Smooth directional movement
        if move_input.length() > 0:
            move_input = move_input.normalized()
            self.move_dir = lerp(self.move_dir, move_input, 6 * time.dt)
        else:
            self.move_dir = lerp(self.move_dir, Vec3(0,0,0), 4 * time.dt)

        # Apply movement
        move_amount = self.move_dir * self.speed
        self.position += move_amount * time.dt

        # Face the direction of movement
        if self.move_dir.length() > 0.1:
            target_angle = math.degrees(math.atan2(-self.move_dir.x, -self.move_dir.z))
            self.rotation_y = lerp(self.rotation_y, target_angle, 10 * time.dt)

        # Only apply gravity if enabled
        if self.gravity_enabled:
            self.velocity_y -= 20 * time.dt
            self.y += self.velocity_y * time.dt

            # Raycast for ground collision
            hit_info = raycast(
                self.world_position + Vec3(0, 0.1, 0),
                Vec3(0, -1, 0),
                distance=0.6,
                ignore=[self]
            )
            self.grounded = hit_info.hit
            if self.grounded:
                self.velocity_y = 0
                # Adjust y so we rest neatly on top of blocks
                self.y = hit_info.world_point.y + 0.5

    def input(self, key):
        # Jump if on ground and gravity is enabled
        if key == 'space' and self.grounded and self.gravity_enabled:
            self.velocity_y = self.jump_power
        
        # Toggle gravity with G key
        elif key == 'g':
            self.gravity_enabled = not self.gravity_enabled
            if not self.gravity_enabled:
                self.velocity_y = 0  # Reset vertical velocity when disabling gravity
        
        # Toggle debug logo with L key
        elif key == 'l':
            toggle_debug_logo()
                
        # Quit on ESC
        elif key == 'escape':
            application.quit()


# -------------------------------------------------
# Basic cubic block for castle geometry
# -------------------------------------------------
class Block(Entity):
    def __init__(self, position=(0, 0, 0), color=color.light_gray, scale=(1,1,1)):
        super().__init__(
            model='cube',
            color=color,
            position=position,
            scale=scale,
            collider='box'
        )


# -------------------------------------------------
# Castle generation
# -------------------------------------------------
def create_peachs_castle():
    # Ground courtyard
    Entity(
        model='cube',
        scale=(30, 1, 30),
        position=(0, -0.5, 0),
        color=color.green,
        collider='box'
    )

    # Castle base (front wall)
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

    # Castle door (thin block)
    Block(position=(0, 0, 4), color=color.brown, scale=(2,2,0.2))

    # Floating star block inside
    Block(position=(0, 2, 6), color=color.yellow, scale=(0.7, 0.7, 0.7))


# Global flag for debug logo visibility
debug_logo_visible = True
logo_entities = []

# Function to toggle debug logo
def toggle_debug_logo():
    global debug_logo_visible, logo_entities
    
    if debug_logo_visible:
        # Hide all logo entities
        for entity in logo_entities:
            destroy(entity)
        logo_entities = []
    else:
        # Recreate logo
        create_debug_logo()
    
    debug_logo_visible = not debug_logo_visible

# -------------------------------------------------
# Setup camera and top-level update for camera follow
# -------------------------------------------------
camera.position = (0, 5, -15)
camera_offset = Vec3(0, 5, -15)

def update():
    # Smooth camera follow
    desired = player.world_position + camera_offset
    camera.world_position = lerp(camera.world_position, desired, 4 * time.dt)
    camera.look_at(player.position + Vec3(0,1,0))


# -------------------------------------------------
# Initialize game
# -------------------------------------------------
player = Player()
create_peachs_castle()
create_debug_logo()

app.run()
