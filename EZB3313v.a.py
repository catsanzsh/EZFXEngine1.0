# test.py
# ------------------------------------------------------------------------------------
# Combined Script:
#   Main menu + Start button
#   Loads a minimal Peach's Castle scene (Stage 1) with a simple player
# ------------------------------------------------------------------------------------

from ursina import *
import math

app = Ursina()
window.title = "The Flames Co. Memory PROJECT V1.0a BETA"
window.borderless = False
Texture.default_filtering = None
window.color = color.black

# Fade Overlay for Transitions
class FadeOverlay(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='quad',
            color=color.black,
            scale=(2, 2),
            z=-9999,
            enabled=False
        )
    
    def fade_in(self, duration=1):
        """Fade from transparent to black."""
        self.enabled = True
        self.color = Color(0, 0, 0, 0)
        self.animate_color(Color(0, 0, 0, 1), duration=duration, curve=curve.linear)
    
    def fade_out(self, duration=1):
        """Fade from black to transparent."""
        def disable_after():
            self.enabled = False
        self.enabled = True
        self.color = Color(0,0,0,1)
        self.animate_color(Color(0,0,0,0), duration=duration, curve=curve.linear)
        invoke(disable_after, delay=duration)

fade_overlay = FadeOverlay()

# ------------------------------------------------------------------------------------
# Main Menu
# ------------------------------------------------------------------------------------
class MainMenu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.background = Entity(
            parent=self,
            model='quad',
            scale=(2,2),
            color=color.black,
            z=1
        )
        self.title_text = Text(
            parent=self,
            text="The Flames Co. Memory\nPROJECT V1.0a BETA",
            origin=(0,0),
            scale=2,
            y=0.25,
            color=color.white,
            z=-1
        )
        self.start_button = Button(
            parent=self,
            text="Start",
            scale=(0.2,0.1),
            y=-0.05,
            color=color.dark_gray,
            highlight_color=color.gray,
            on_click=self.start_game
        )
        self.quit_button = Button(
            parent=self,
            text="Quit",
            scale=(0.2,0.1),
            y=-0.2,
            color=color.dark_gray,
            highlight_color=color.gray,
            on_click=application.quit
        )

    def start_game(self):
        fade_overlay.fade_in(0.5)
        invoke(self.disable, delay=0.5)
        invoke(enable_castle_scene, delay=0.5)
        invoke(fade_overlay.fade_out, delay=1)

main_menu = MainMenu()

# ------------------------------------------------------------------------------------
# Stage 1 (Peach's Castle) Setup
# This will remain disabled until we press Start on the main menu.
# ------------------------------------------------------------------------------------
castle_scene = Entity(enabled=False)

# Player
class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=castle_scene,
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

        for key, value in kwargs.items():
            setattr(self, key, value)

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
                
        # Quit on ESC
        elif key == 'escape':
            application.quit()

player = Player()

# Basic cubic block for castle geometry
class Block(Entity):
    def __init__(self, position=(0, 0, 0), color=color.light_gray, scale=(1,1,1)):
        super().__init__(
            parent=castle_scene,
            model='cube',
            color=color,
            position=position,
            scale=scale,
            collider='box'
        )

# Castle generation
def create_peachs_castle():
    # Ground courtyard
    Entity(
        parent=castle_scene,
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


create_peachs_castle()

# Camera follow
camera.position = (0, 5, -15)
camera_offset = Vec3(0, 5, -15)

def castle_update():
    # Smooth camera follow
    desired = player.world_position + camera_offset
    camera.world_position = lerp(camera.world_position, desired, 4 * time.dt)
    camera.look_at(player.position + Vec3(0,1,0))

def enable_castle_scene():
    castle_scene.enabled = True
    # Move or show player, in case we want to reset position
    player.position = (0, 0.5, 4)
    player.rotation = (0, 0, 0)
    player.gravity_enabled = False

# ------------------------------------------------------------------------------------
# Master update
# We only run castle_update if the castle scene is active
# ------------------------------------------------------------------------------------
def update():
    if castle_scene.enabled:
        castle_update()

app.run()
e
