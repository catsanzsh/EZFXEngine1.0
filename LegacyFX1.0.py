from ursina import Ursina, Entity, camera, Vec3, Text, time, window, color, application, held_keys
from ursina.scene import Scene  # Import Scene class

class GameEntity:
    def __init__(self, name):
        self.name = name
        self.ursina_entity = None
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def update(self):
        for component in self.components:
            component.update()

class InputSystem:
    def __init__(self):
        pass

    def update(self):
        pass

class MovementSystem:
    def __init__(self):
        pass

    def update(self):
        pass

class InputComponent:
    def __init__(self):
        pass

    def update(self):
        # Input handling logic here
        pass

class MovementComponent:
    def __init__(self, speed):
        self.speed = speed

    def update(self):
        # Movement logic here
        pass

class GameEngine:
    def __init__(self):
        self.game_engine = None
        self.camera_pivot = Entity()  # Camera pivot for follow behavior
        self.current_game_id = None
        self.app = Ursina(borderless=False)
        self.app.window.title = "Super Mario FX Beta"
        self.app.fullscreen = False
        self.app.size = (800, 600)
    
    def register_systems(self):
        """Register systems to the game engine."""
        self.game_engine.add_system(InputSystem())
        self.game_engine.add_system(MovementSystem())  # Example

    def _create_sm64_scene(self):
        """Creates and returns the Super Mario 64 scene."""
        scene = Scene("sm64")

        # Ground
        ground_entity = GameEntity("Ground")
        ground_entity.ursina_entity = Entity(model='plane', scale=32, color=color.gray)
        scene.add_entity(ground_entity)

        # Player
        player_entity = GameEntity("Player")
        player_entity.add_component(InputComponent())
        player_entity.add_component(MovementComponent(speed=10))
        player_entity.ursina_entity = Entity(model='cube', color=color.orange, scale=1, position=(0, 0.5, 0))
        scene.add_entity(player_entity)

        # Camera setup (parented to player for follow)
        self.camera_pivot.position = player_entity.ursina_entity.position + Vec3(0, 2, 0)
        camera.parent = self.camera_pivot
        camera.position = (0, 10, -15)
        camera.look_at(player_entity.ursina_entity)
        camera.fov = 90

        return scene

    def _create_nsmb_scene(self):
        """Creates and returns the New Super Mario Bros. scene."""
        scene = Scene("nsmb")

        # Ground
        ground_entity = GameEntity("Ground")
        ground_entity.ursina_entity = Entity(model='plane', scale=32, color=color.green)
        scene.add_entity(ground_entity)

        # Player
        player_entity = GameEntity("Player")
        player_entity.add_component(InputComponent())
        player_entity.add_component(MovementComponent(speed=8))
        player_entity.ursina_entity = Entity(model='sphere', color=color.red, scale=1, position=(0, 0.5, 0))
        scene.add_entity(player_entity)

        camera.orthographic = True
        camera.fov = 8
        instructions_text = Text("2D Game Controls:\nWASD to move, ESC to quit", origin=(0, -0.4), scale=0.8, color=color.white)
        camera.position = (0, 10, -15)
        camera.look_at(Vec3(0, 0, 0))
        camera.fov = 90

        return scene

    def start_game(self, game_id):
        """Initializes and runs the selected game within the engine."""
        window.title = f"Super Mario FX Beta - Playing: {game_id}"
        self.current_game_id = game_id
        self.game_engine.scenes.clear()  # Clear previous scenes
        self.camera_pivot.position = (0, 0, 0)  # Reset the camera pivot position

        # Create the respective scenes
        if game_id == "sm64":
            sm64_scene = self._create_sm64_scene()
            self.game_engine.add_scene(sm64_scene)
            self.game_engine.set_scene("sm64")
        elif game_id == "nsmb":
            nsmb_scene = self._create_nsmb_scene()
            self.game_engine.add_scene(nsmb_scene)
            self.game_engine.set_scene("nsmb")

        self.app.run(self.update)

    def update(self):
        """Ursina update loop, driving the game engine."""
        if self.current_game_id is not None:
            self.game_engine.update(time.dt)

            # Ensure player entity exists
            player_entity = None
            if self.game_engine.current_scene:
                for entity in self.game_engine.current_scene.entities:
                    if isinstance(entity, GameEntity) and entity.name == "Player":
                        player_entity = entity
                        break

            # Camera follow logic
            if player_entity and player_entity.ursina_entity:
                self.camera_pivot.position = player_entity.ursina_entity.position + Vec3(0, 2, 0)
                camera.position = self.camera_pivot.position + Vec3(0, 10, -15)
                camera.look_at(player_entity.ursina_entity)

        # Handle quit logic
        if held_keys['escape']:
            self.app.quit()
            self.current_game_id = None

# Main Game Loop Execution
if __name__ == "__main__":
    game_engine = GameEngine()
    game_engine.start_game("sm64")  # Start the game with SM64