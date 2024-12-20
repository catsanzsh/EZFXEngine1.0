from ursina import Ursina, Entity, color, window, Text, held_keys, Button

app = Ursina()

# --- First Scene (Initial Screen) ---

# Window properties for the first scene
window.title = 'NINT MEGA CONECTATOR'
window.borderless = False
window.size = (800, 600)
window.color = color.light_gray

# Title Text
title_text = Text(text="NINT MEGA CONECTATOR", origin=(0, 0), scale=1.5, color=color.black, position=(0, 0.2))

# Login Button (moved to the bottom)
login_button = Button(text='LOG IN', color=color.azure, scale=(0.2, 0.1), position=(0, -0.4))

# Instructions (for quitting)
instructions = Text(text="Press 'ESC' to quit", origin=(0, -0.45), scale=0.8, color=color.black)

# --- Second Scene (Game Selection) ---

def load_second_scene():
    """Loads the second scene (game selection)."""
    # Hide elements of the first scene
    title_text.visible = False
    login_button.visible = False
    instructions.visible = False

    # Game Selection Title
    game_selection_title = Text(text="Select a Game", origin=(0, 0), scale=1.2, color=color.black, position=(0, 0.3))

    # --- Super Mario Land Button ---
    sm_land_button = Button(
        text='Super Mario Land',
        color=color.gold,
        scale=(0.3, 0.1),
        position=(-0.3, 0, 0)
    )
    sm_land_button.on_click = lambda: print("Loading Super Mario Land...")  # Replace with game load logic

    # --- Super Mario Advance SMB3 Button ---
    sm_advance_button = Button(
        text='Super Mario Advance (SMB3)',
        color=color.rgb(255, 100, 100), # Reddish color
        scale=(0.3, 0.1),
        position=(0.3, 0, 0)
    )
    sm_advance_button.on_click = lambda: print("Loading Super Mario Advance (SMB3)...")  # Replace with game load logic

    # Back Button (to go back to the first scene)
    back_button = Button(text="Back", color=color.gray, scale=(0.1, 0.05), position=(-0.7, -0.4))
    
    def load_first_scene():
      """Loads the first scene (initial screen)."""
      # Hide elements of the second scene
      game_selection_title.visible = False
      sm_land_button.visible = False
      sm_advance_button.visible = False
      back_button.visible = False
    
      # Show elements of the first scene
      title_text.visible = True
      login_button.visible = True
      instructions.visible = True

    back_button.on_click = load_first_scene

# Assign the function to the button's on_click event
login_button.on_click = load_second_scene

# Update function (for handling global events like 'ESC' to quit)
def update():
    """This function runs every frame."""
    if held_keys['escape']:
        app.quit()

app.run()   
