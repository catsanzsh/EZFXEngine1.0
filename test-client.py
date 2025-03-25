from ursina import *

app = Ursina()

window.title = "ULTRA MARIO 64 - File Select"
window.borderless = False
window.color = color.black
window.size = (1280, 720)

# ---------- TILED BACKGROUND ----------
bg_tiler = Entity(
    parent=camera.ui,
    model='quad',
    texture='/mnt/data/image.png',  # Should be a seamless tile!
    scale=(2.5, 1.5),
    texture_scale=(8, 4),  # Repeats texture 8x horizontally, 4x vertically
    color=color.color(240, 1, 0.6),  # Slight blue tint blend
    z=1
)

# ---------- FILE SELECT OPTIONS ----------
options = [
    ("MARIO A", 10),
    ("MARIO B", 1),
    ("MARIO C", 5),
    ("ERASE DATA", None)
]

file_texts = []
selected = 0

def update_selection():
    for i, (text, _) in enumerate(file_texts):
        text.color = color.yellow if i == selected else color.white

# Create text buttons with static star count
for i, (label, stars) in enumerate(options):
    t = Text(
        text=label,
        origin=(0, 0),
        scale=2,
        y=0.25 - i * 0.15,
        color=color.white,
        background=False
    )
    file_texts.append((t, stars))
    if stars is not None:
        Text(
            text="★ " + str(stars),
            origin=(0, 0),
            scale=1.5,
            x=0.25,
            y=0.25 - i * 0.15,
            color=color.orange
        )

update_selection()

# ---------- TRANSITION TO GAME ----------
def load_game(slot_name):
    print(f">>> Loading {slot_name}...")
    destroy(bg_tiler)
    for text, _ in file_texts:
        destroy(text)
    Text(text=f"LOADING {slot_name}...", origin=(0, 0), scale=2, color=color.azure)
    invoke(scene_loader, delay=1.5)

def scene_loader():
    import subprocess
    subprocess.Popen(["python3", "test.py"])  # Use "python" on Windows
    application.quit()

# ---------- INPUT HANDLING ----------
def input(key):
    global selected
    if key == 'w' or key == 'up arrow':
        selected = (selected - 1) % len(file_texts)
        update_selection()
    elif key == 's' or key == 'down arrow':
        selected = (selected + 1) % len(file_texts)
        update_selection()
    elif key == 'z' or key == 'enter':
        load_game(options[selected][0])

app.run()
