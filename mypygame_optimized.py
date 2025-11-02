# math_game.py
import pygame
import random
import json
import os
import sys
from pathlib import Path

SAVE_PATH = Path(__file__).parent / "savegame.json"

SCREEN_W, SCREEN_H = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (30, 200, 180)
DARK = (20, 20, 20)
GREEN = (60, 200, 60)
RED = (200, 50, 50)
YELLOW = (230, 200, 40)
GRAY = (120, 120, 120)

BASE_FALL_SPEED = 60
SPEED_PER_SCORE = 3
SPAWN_INTERVAL_BASE = 2.0
SPAWN_INTERVAL_MIN = 0.5
SPAWN_ACCEL_PER_SCORE = 0.03
COST_SKIP = 8
COST_SHIELD = 15

# Menu buttons
PLAY_BUTTON_RECT = pygame.Rect(0, 0, 0, 0)
QUIT_BUTTON_RECT = pygame.Rect(0, 0, 0, 0)
TUTORIAL_BUTTON_RECT = pygame.Rect(0, 0, 0, 0)
game_state = "menu" # Central state variable

# ---------------------
# Save/load Fnc
# ---------------------
def load_save():
    if not SAVE_PATH.exists():
        return {"high_score": 0, "coins": 0, "items": {"skip": 0, "shield": 0}}
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("high_score", 0)
        data.setdefault("coins", 0)
        data.setdefault("items", {"skip": 0, "shield": 0})
        return data
    except Exception:
        return {"high_score": 0, "coins": 0, "items": {"skip": 0, "shield": 0}}

def save_game(data):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Save failed:", e)

# ---------------------
# Draw Fnc
# ---------------------
def draw_menu(screen, font):
    """Draws the main menu and defines button positions."""
    screen.fill(GRAY)
    
    # Draw menu title
    title_font = pygame.font.SysFont("MV Boli", 120)
    title_surf = title_font.render("Math Tiles", True, WHITE)
    screen.blit(title_surf, (SCREEN_W/2 - title_surf.get_width()/2, 100))
    
    global PLAY_BUTTON_RECT, QUIT_BUTTON_RECT 
    
    # Play Button
    PLAY_BUTTON_RECT.update(SCREEN_W/2 - 100, 350, 200, 50)
    pygame.draw.rect(screen, GREEN, PLAY_BUTTON_RECT, border_radius=10) 
    play_text = font.render("Play", True, WHITE)
    screen.blit(play_text, play_text.get_rect(center=PLAY_BUTTON_RECT.center))
    
    # Tutorial Button
    TUTORIAL_BUTTON_RECT.update(SCREEN_W/2 - 100, 420, 200, 50)
    pygame.draw.rect(screen, YELLOW, TUTORIAL_BUTTON_RECT, border_radius=10)
    tut_text = font.render("Tutorial", True, DARK)
    screen.blit(tut_text, tut_text.get_rect(center=TUTORIAL_BUTTON_RECT.center))

    # Quit Button
    QUIT_BUTTON_RECT.update(SCREEN_W/2 - 100, 490, 200, 50)
    pygame.draw.rect(screen, RED, QUIT_BUTTON_RECT, border_radius=10) 
    quit_text = font.render("Quit", True, WHITE)
    screen.blit(quit_text, quit_text.get_rect(center=QUIT_BUTTON_RECT.center))
    
    pygame.display.flip()

def draw_tutorial(screen, font_small, font_mid):
    """Display tutorial / how-to-play instructions."""
    screen.fill(DARK)
    
    font_mid = pygame.font.SysFont("Comic Sans", 48)
    title = font_mid.render("How to Play Math Tiles", True, WHITE)
    screen.blit(title, (SCREEN_W/2 - title.get_width()/2, 80))

    lines = [
        "🧮 Solve the falling math problems before they reach the bottom!",
        "💡 Click the correct answer on the right panel.",
        "❤️ You start with 3 lives — lose one for each wrong or missed tile.",
        "🪙 Earn 1 coin for each correct answer.",
        "🛍️ Press S to open the shop:",
        "   - Buy 'Skip' to remove the current problem.",
        "   - Buy 'Shield' to block one mistake.",
        "",
        "🎮 Controls:",
        "   S - Open/close shop",
        "   K - Use Skip item",
        "   ESC - Quit game",
        "",
        "Click 'Back' below to return to menu."
    ]

    font_small = pygame.font.SysFont("Segoe UI Emoji", 20)
    y = 200
    for line in lines:
        text = font_small.render(line, True, WHITE)
        screen.blit(text, (80, y))
        y += 25

    # Back button
    back_rect = pygame.Rect(SCREEN_W - 200, SCREEN_H - 100, 160, 50)
    pygame.draw.rect(screen, TEAL, back_rect, border_radius=10)
    back_text = font_small.render("Back", True, BLACK)
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    pygame.display.flip()
    return back_rect

def draw_hud(surface, font_small, score, coins, lives, high_score, items):
    """Draws the Heads-Up Display and item counts."""
    score_txt = font_small.render(f"Score: {score}", True, WHITE)
    coins_txt = font_small.render(f"Coins: {coins}", True, YELLOW)
    lives_txt = font_small.render(f"Lives: {lives}", True, RED)
    high_txt = font_small.render(f"High: {high_score}", True, GRAY)
    
    surface.blit(score_txt, (20, 10))
    surface.blit(coins_txt, (20, 40))
    surface.blit(lives_txt, (180, 10))
    surface.blit(high_txt, (180, 40))

    # Draw Skip button
    skip_btn = pygame.Rect(SCREEN_W - 140, 10, 120, 34)
    pygame.draw.rect(surface, (70, 70, 70), skip_btn, border_radius=8)
    skip_label = font_small.render(f"Skip x{items.get('skip',0)}", True, WHITE)
    surface.blit(skip_label, (skip_btn.x + 8, skip_btn.y + 6))

    # Draw Shield button
    shield_btn = pygame.Rect(SCREEN_W - 280, 10, 120, 34)
    pygame.draw.rect(surface, (70, 70, 70), shield_btn, border_radius=8)
    shield_label = font_small.render(f"Shield x{items.get('shield',0)}", True, WHITE)
    surface.blit(shield_label, (shield_btn.x + 8, shield_btn.y + 6))
    
    shop_hint = font_small.render("Press S for Shop", True, GRAY)
    surface.blit(shop_hint, (SCREEN_W - 220, 52))

def draw_right_panel(surface, font_big, font_small, answer_buttons):
    panel_w = 200
    panel_rect = pygame.Rect(SCREEN_W - panel_w - 20, 100, panel_w, SCREEN_H - 200)
    pygame.draw.rect(surface, (15, 15, 15), panel_rect, border_radius=12)
    pygame.draw.rect(surface, (40, 40, 40), panel_rect, 3, border_radius=12)

    for i, (rect, val) in enumerate(answer_buttons):
        pygame.draw.rect(surface, GREEN, rect, border_radius=10)
        txt = font_big.render(str(val), True, DARK)
        surface.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2,
                          rect.y + (rect.height - txt.get_height()) // 2))

def draw_shop(surface, font_small, player_items, player_coins):
    w, h = 600, 300
    rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
    pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=12)
    pygame.draw.rect(surface, (80, 80, 80), rect, 2, border_radius=12)

    title = font_small.render("SHOP - Buy Items", True, WHITE)
    surface.blit(title, (rect.x + 18, rect.y + 12))
    
    y_start = rect.y + 60
    
    # Shop Info
    skip_txt = font_small.render(f"Skip (remove problem) - Cost: {COST_SKIP}", True, WHITE)
    surf_skip = font_small.render(f"You have: {player_items['skip']}", True, YELLOW)
    surface.blit(skip_txt, (rect.x + 20, y_start))
    surface.blit(surf_skip, (rect.x + 400, y_start))
    
    y_start += 50
    shield_txt = font_small.render(f"Shield (negate wrong) - Cost: {COST_SHIELD}", True, WHITE)
    surf_shield = font_small.render(f"You have: {player_items['shield']}", True, YELLOW)
    surface.blit(shield_txt, (rect.x + 20, y_start))
    surface.blit(surf_shield, (rect.x + 400, y_start))

    y_start += 70
    instruction = font_small.render("Click item text to buy. Press S to close shop.", True, GRAY)
    surface.blit(instruction, (rect.x + 20, y_start))
    
    return rect

# --------------------
# Create Problem
# --------------------
def generate_problem():
    op = random.choice(['+', '-', '*', '/'])
    a = random.randint(1, 12)
    b = random.randint(1, 12)
    if op == '/':
        b = random.randint(1, 12)
        a = b * random.randint(1, 6)
        answer = a // b
        display = f"{a} ÷ {b}"
    elif op == '+':
        answer = a + b
        display = f"{a} + {b}"
    elif op == '-':
        answer = a - b
        display = f"{a} - {b}"
    else:
        answer = a * b
        display = f"{a} × {b}"
    return display, answer

def make_choices(correct):
    choices = [correct]
    while len(choices) < 3:
        delta = random.randint(-10, 10)
        candidate = correct + delta
        if candidate != correct and -100 <= candidate <= 100:
            choices.append(candidate)

    return random.sample(choices, 3)

class ProblemTile:
    def __init__(self, x, y, problem_str, answer, fall_speed):
        self.x = x
        self.y = y
        self.problem = problem_str
        self.answer = answer
        self.width = 300
        self.height = 70
        self.fall_speed = fall_speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.choices = make_choices(answer)

    def update(self, dt):
        self.y += self.fall_speed * dt
        self.rect.y = int(self.y)

    def draw(self, surf, font):
        pygame.draw.rect(surf, TEAL, self.rect, border_radius=8)
        txt = font.render(self.problem, True, DARK)
        surf.blit(txt, (self.rect.x + 12, self.rect.y + (self.height - txt.get_height()) // 2))
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=8)

# ---------------------
# Game Logic Func
# ---------------------

def init_game_variables(save_data):
    return {
        "tiles": [],
        "score": 0,
        "lives": 3,
        "spawn_timer": 0.0,
        "spawn_interval": SPAWN_INTERVAL_BASE,
        "game_over": False,
        "shop_open": False,
        "high_score": save_data.get("high_score", 0),
        "coins": save_data.get("coins", 0),
        "items": save_data.get("items", {"skip": 0, "shield": 0}),
    }

def lose_life(game_vars, save_data):
    # use available shield
    if game_vars["items"].get("shield", 0) > 0:
        game_vars["items"]["shield"] -= 1
        return
    # take hit
    game_vars["lives"] -= 1
    if game_vars["lives"] <= 0:
        game_vars["game_over"] = True
        
        # Save high score, items n coins
        if game_vars["score"] > game_vars["high_score"]:
            game_vars["high_score"] = game_vars["score"]
        
        save_data["high_score"] = max(game_vars["high_score"], save_data.get("high_score", 0))
        save_data["coins"] = game_vars["coins"]
        save_data["items"] = game_vars["items"]
        save_game(save_data)

def spawn_tile(game_vars):
    """Creates a new ProblemTile and adds it to the list."""
    # spd scale
    fall_speed = BASE_FALL_SPEED + game_vars["score"] * SPEED_PER_SCORE
    x = 40
    y = -80
    pstr, ans = generate_problem()
    tile = ProblemTile(x, y, pstr, ans, fall_speed)
    tile.choices = make_choices(ans)
    game_vars["tiles"].append(tile)

def get_active_tile(game_vars):
    """Returns the current active tile."""
    return game_vars["tiles"][0] if game_vars["tiles"] else None

# ---------------------
# Main Game Loop
# ---------------------
def main():
    pygame.init()

    global game_state
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Math Tiles — Math Game")
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("Comic Sans", 48)
    font_mid = pygame.font.SysFont("Comic Sans", 35)
    font_small = pygame.font.SysFont("Comic Sans", 20)

    save_data = load_save()
    game_vars = init_game_variables(save_data)
    
    spawn_tile(game_vars)

    # Buttons setup
    global PLAY_BUTTON_RECT, QUIT_BUTTON_RECT
    PLAY_BUTTON_RECT = pygame.Rect(0, 0, 0, 0)
    QUIT_BUTTON_RECT = pygame.Rect(0, 0, 0, 0)

    # ans buttons
    button_w, button_h = 160, 80
    right_x = SCREEN_W - button_w - 40
    btn_y_positions = [140, 260, 380]
    answer_buttons = [(pygame.Rect(right_x, y, button_w, button_h), 0) for y in btn_y_positions]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        # Event
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            if game_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON_RECT.collidepoint(event.pos):
                        game_state = "playing"
                    elif TUTORIAL_BUTTON_RECT.collidepoint(event.pos):
                        game_state = "tutorial"
                    elif QUIT_BUTTON_RECT.collidepoint(event.pos):
                        running = False

            elif game_state == "tutorial":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        game_state = "menu"

            elif game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        game_state = "shop"
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_k and not game_vars["game_over"]:
                        # Use available skip
                        if game_vars["items"].get("skip", 0) > 0 and game_vars["tiles"]:
                            game_vars["items"]["skip"] -= 1
                            game_vars["tiles"].pop(0)

                # mouse click in game
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if game_vars["game_over"]:
                        # Click to restart
                        game_vars = init_game_variables(save_data)
                        spawn_tile(game_vars)
                        continue

                    # Check clicked ans button
                    for rect, val in answer_buttons:
                        if rect.collidepoint(mx, my):
                            active = get_active_tile(game_vars)
                            if not active: break
                            
                            if val == active.answer:
                                # Correct
                                game_vars["score"] += 1
                                game_vars["coins"] += 1
                                if game_vars["tiles"]:
                                    game_vars["tiles"].pop(0)
                                    game_vars["spawn_interval"] = max(SPAWN_INTERVAL_MIN,
                                                                      SPAWN_INTERVAL_BASE - game_vars["score"] * SPAWN_ACCEL_PER_SCORE)
                            else:
                                # Wrong
                                lose_life(game_vars, save_data)
                            break
                            
            elif game_state == "shop":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    game_state = "playing" # Close shop
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    
                    y_base = SCREEN_H/2 - 150 + 60
                    skip_area = pygame.Rect(SCREEN_W/2 - 300 + 20, y_base, 380, 40)
                    shield_area = pygame.Rect(SCREEN_W/2 - 300 + 20, y_base + 50, 380, 40)
                    
                    if skip_area.collidepoint(mx, my):
                        if game_vars["coins"] >= COST_SKIP:
                            game_vars["coins"] -= COST_SKIP
                            game_vars["items"]["skip"] = game_vars["items"].get("skip", 0) + 1
                    elif shield_area.collidepoint(mx, my):
                        if game_vars["coins"] >= COST_SHIELD:
                            game_vars["coins"] -= COST_SHIELD
                            game_vars["items"]["shield"] = game_vars["items"].get("shield", 0) + 1


        # not run if in menu or shop
        if game_state == "playing" and not game_vars["game_over"]:
            
            # Tile spd overtime
            for t in game_vars["tiles"]:
                t.fall_speed = BASE_FALL_SPEED + game_vars["score"] * SPEED_PER_SCORE
                t.update(dt)

            # Check for missed tile
            if game_vars["tiles"] and game_vars["tiles"][0].y > SCREEN_H:
                game_vars["tiles"].pop(0)
                lose_life(game_vars, save_data)
            
            # Tile Spawn
            game_vars["spawn_timer"] += dt
            if game_vars["spawn_timer"] >= game_vars["spawn_interval"]:
                game_vars["spawn_timer"] = 0
                spawn_tile(game_vars)

        # Upd ans buttons on active tile
        active = get_active_tile(game_vars)
        if active:
            for i, (rect, _) in enumerate(answer_buttons):
                answer_buttons[i] = (rect, active.choices[i])
        else:
            for i, (rect, _) in enumerate(answer_buttons):
                answer_buttons[i] = (rect, "-")

        # Draw Menu
        if game_state == "menu":
            draw_menu(screen, font_mid)
        elif game_state == "tutorial":
            back_button = draw_tutorial(screen, font_small, font_mid)
        
        else:
            screen.fill((12, 12, 20))
            # Draw bg n tile
            pygame.draw.rect(screen, (63, 63, 80), (20, 80, SCREEN_W - 260, SCREEN_H - 140), border_radius=10)
            for t in game_vars["tiles"]:
                t.draw(screen, font_mid)

            # Draw UI
            draw_right_panel(screen, font_big, font_small, answer_buttons)
            draw_hud(screen, font_small, game_vars["score"], game_vars["coins"], 
                     game_vars["lives"], game_vars["high_score"], game_vars["items"])

            # Draw Game Over screen
            if game_vars["game_over"]:
                go_rect = pygame.Rect(80, 120, SCREEN_W - 160, SCREEN_H - 240)
                pygame.draw.rect(screen, (20, 20, 20), go_rect, border_radius=12)
                pygame.draw.rect(screen, (150, 150, 150), go_rect, 2, border_radius=12)
                
                title = font_big.render("GAME OVER", True, RED)
                screen.blit(title, title.get_rect(centerx=go_rect.centerx, y=go_rect.y + 30))
                sc = font_mid.render(f"Score: {game_vars['score']}", True, WHITE)
                screen.blit(sc, sc.get_rect(centerx=go_rect.centerx, y=go_rect.y + 120))
                hi = font_mid.render(f"High Score: {game_vars['high_score']}", True, GRAY)
                screen.blit(hi, hi.get_rect(centerx=go_rect.centerx, y=go_rect.y + 160))
                inst = font_small.render("Click anywhere to restart", True, GRAY)
                screen.blit(inst, inst.get_rect(centerx=go_rect.centerx, y=go_rect.y + 220))
            
            # Draw Shop screen overlay
            elif game_state == "shop":
                draw_shop(screen, font_small, game_vars["items"], game_vars["coins"])
            
            pygame.display.flip()

    # Final Cleanup
    save_data["high_score"] = max(game_vars["high_score"], game_vars["score"], save_data.get("high_score", 0))
    save_data["coins"] = game_vars["coins"]
    save_data["items"] = game_vars["items"]
    save_game(save_data)
    
    pygame.quit()
    sys.exit()

main()