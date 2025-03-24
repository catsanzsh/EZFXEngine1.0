from ursina import *
import math

def create_peachs_castle():
    """Construct a simple Peach's Castle scene: ground + walls + door + star block."""
    # Ground courtyard (cube of scale 30x1x30, top at y=0.5)
    ground = Entity(
        model='cube',
        color=color.green,
        position=(0, -0.5, 0),
        scale=(30, 1, 30),
        collider='box'
    )
    
    # Castle base (front wall)
    for x in range(-4, 5):
        for y in range(0, 5):
            Entity(
                model='cube',
                color=color.light_gray,
                position=(x, y, 5),
                scale=(1, 1, 1),
                collider='box'
            )

    # Castle sides
    for z in range(4, 9):
        for y in range(0, 5):
            Entity(model='cube', color=color.gray, position=(-4, y, z), collider='box')
            Entity(model='cube', color=color.gray, position=(4, y, z), collider='box')

    # Castle towers
    for x in [-4, 4]:
        for z in [8]:
            for y in range(5, 8):
                Entity(model='cube', color=color.gray, position=(x, y, z), collider='box')

    # Castle door
    Entity(
        model='cube',
        color=color.brown,
        position=(0, 0, 4),
        scale=(2, 2, 0.2),
        collider='box'
    )

    # Floating star block inside
    Entity(
        model='cube',
        color=color.yellow,
        position=(0, 2, 6),
        scale=(0.7, 0.7, 0.7),
        collider='box'
    )

    return ground

class Player(Entity):
    """A simple player with basic WASD movement, jump, and ground detection."""
    def __init__(self, spawn_position=(0, 1, -10), ground_entity=None):
        super().__init__(
            model='cube',
            color=color.white,
            scale=(0.5, 1, 0.5),
            position=spawn_position,
            collider='box'
        )
        self.speed = 6
        self.jump_power = 8
        self.velocity_y = 0
        self.grounded = False
        self.move_dir = Vec3(0, 0, 0)
        self.ground_entity = ground_entity
        
        # Use invoke to delay the initial ground check.  This is crucial.
        invoke(self.ensure_proper_spawn, delay=0.05)

    def ensure_proper_spawn(self):
        """Make sure player spawns correctly on the ground"""
        if self.ground_entity:
            # Get the ground's y position.  Use world_position.
            ground_y = self.ground_entity.world_position.y + (self.ground_entity.scale_y / 2)
            # Position the player *above* the ground.
            self.y = ground_y + (self.scale_y / 2) + 0.01
            self.grounded = True
            self.velocity_y = 0
            return
        
        self.perform_ground_check(max_distance=20) # Increased max distance

    def perform_ground_check(self, max_distance=2.0):
        """Ground check using raycast."""
        # Raycast downwards from the player's position
        hit_info = raycast(
            origin=self.world_position + Vec3(0, 0.1, 0),  # Start slightly above the player
            direction=Vec3(0, -1, 0),
            distance=max_distance,
            ignore=[self]  # Important: Ignore the player's own collider
        )

        if hit_info.hit:
            self.grounded = True
            self.velocity_y = 0
            # Position the player directly on top of the ground
            self.y = hit_info.world_point.y + (self.scale_y / 2)
        else:
             self.grounded = False

    def update(self):
        # Input for movement
        move_input = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        )

        # Normalize diagonal movement
        if move_input.length() > 0:
            move_input = move_input.normalized()
        
        self.move_dir = lerp(self.move_dir, move_input, 6 * time.dt)

        # Move the player
        self.position += self.move_dir * self.speed * time.dt
        
        if self.move_dir.length() > 0.1:
            target_angle = math.degrees(math.atan2(-self.move_dir.x, -self.move_dir.z))
            self.rotation_y = lerp(self.rotation_y, target_angle, 10 * time.dt)

        # Apply gravity
        if not self.grounded:
            self.velocity_y -= 20 * time.dt  # Gravity
            self.y += self.velocity_y * time.dt

        # Ground check:  Check for ground *below* the player.
        hit_info = raycast(
            origin=self.world_position + Vec3(0, 0.1, 0), # start a little above
            direction=Vec3(0, -1, 0),
            distance=1.2, # slightly more than half of player height
            ignore=[self]
        )
        
        if hit_info.hit:
            self.grounded = True
            self.velocity_y = 0
            self.y = hit_info.world_point.y + (self.scale_y / 2)
        else:
            self.grounded = False

    def input(self, key):
        if key == 'space' and self.grounded:
            self.velocity_y = self.jump_power
            self.grounded = False # set grounded to false when jumping
        elif key == 'escape':
            application.quit()

if __name__ == "__main__":
    app = Ursina()
    window.title = "Peach's Castle - Improved Spawn (v1.1)"
    window.borderless = False
    window.color = color.black

    ground = create_peachs_castle()
    player = Player(ground_entity=ground)

    camera_offset = Vec3(0, 5, -15)  # Camera offset

    def update():
        # Smoothly move the camera
        desired_pos = player.world_position + camera_offset
        camera.world_position = lerp(camera.world_position, desired_pos, 4 * time.dt)
        camera.look_at(player.position + Vec3(0, 0.5, 0))  # Make camera look at player

    app.run()
