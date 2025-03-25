
import pygame
import sys
import json
import os
import random

pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SM64 VHS Menu")

font = pygame.font.SysFont("Courier New", 24, bold=True)
big_font = pygame.font.SysFont("Arial Black", 48)

save_path = "saves.json"
files = [{"name": "Mario A", "stars": 0}, {"name": "Mario B", "stars": 0},
         {"name": "Mario C", "stars": 0}, {"name": "Mario D", "stars": 0}]

def load_saves():
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            data = json.load(f)
            for i in range(4):
                files[i]["stars"] = data.get(files[i]["name"], 0)

def save_saves():
    data = {f["name"]: f["stars"] for f in files}
    with open(save_path, "w") as f:
        json.dump(data, f)

def draw_vhs_background():
    for y in range(0, HEIGHT, 10):
        color = (random.randint(50, 100), random.randint(0, 50), random.randint(100, 255))
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_main_menu():
    draw_vhs_background()
    title = big_font.render("SUPER MARIO", True, (255, 0, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    press = font.render("PRESS Z OR ENTER", True, (255, 255, 255))
    screen.blit(press, (WIDTH//2 - press.get_width()//2, 200))

    static_text = font.render("SP 00:00:00", True, (255, 255, 255))
    screen.blit(static_text, (20, HEIGHT - 40))

def draw_file_select():
    screen.fill((218, 165, 32))  # golden background
    title = big_font.render("SELECT FILE", True, (255, 0, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

    for i, file in enumerate(files):
        x = 100 + (i % 2) * 250
        y = 100 + (i // 2) * 100
        box = pygame.Rect(x, y, 200, 60)
        pygame.draw.rect(screen, (255, 255, 255), box)
        pygame.draw.rect(screen, (0, 0, 0), box, 2)

        name_text = font.render(file["name"], True, (0, 0, 0))
        star_text = font.render(f"★ {file['stars']}" if file["stars"] > 0 else "NEW", True, (0, 0, 0))
        screen.blit(name_text, (x + 10, y + 5))
        screen.blit(star_text, (x + 10, y + 30))

def draw_castle(file_idx):
    screen.fill((100, 149, 237))
    text = big_font.render(f"Welcome to the Castle, {files[file_idx]['name']}!", True, (255, 255, 255))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))

def main():
    load_saves()
    clock = pygame.time.Clock()
    in_main_menu = True
    in_file_select = False
    in_castle = False
    file_idx = None

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_saves()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if in_main_menu and (event.key == pygame.K_RETURN or event.key == pygame.K_z):
                    in_main_menu = False
                    in_file_select = True
            elif event.type == pygame.MOUSEBUTTONDOWN and in_file_select:
                mx, my = pygame.mouse.get_pos()
                for i in range(4):
                    x = 100 + (i % 2) * 250
                    y = 100 + (i // 2) * 100
                    if pygame.Rect(x, y, 200, 60).collidepoint(mx, my):
                        files[i]["stars"] += 1
                        file_idx = i
                        in_castle = True
                        in_file_select = False

        if in_main_menu:
            draw_main_menu()
        elif in_file_select:
            draw_file_select()
        elif in_castle:
            draw_castle(file_idx)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
