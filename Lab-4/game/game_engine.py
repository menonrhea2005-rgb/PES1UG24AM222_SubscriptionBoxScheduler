import math

import pygame
from .bird import Bird
from .pipe import Pipe
from .sounds import SoundManager

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DARK = (20, 20, 30)
GOLD = (255, 215, 0)
GREY = (70, 70, 85)
BUTTON_HOVER = (95, 95, 115)

# Task 3: difficulty presets (pipe speed in px/frame, gap height in px,
# frames between pipe spawns). Interval scales so pipe spacing stays fair.
DIFFICULTIES = {
    "Easy":   {"speed": 3, "gap": 190, "interval": 110, "color": (80, 200, 120)},
    "Medium": {"speed": 4, "gap": 150, "interval": 90,  "color": (240, 190, 60)},
    "Hard":   {"speed": 6, "gap": 120, "interval": 70,  "color": (230, 80, 80)},
}
DIFFICULTY_KEYS = {
    pygame.K_1: "Easy", pygame.K_e: "Easy",
    pygame.K_2: "Medium", pygame.K_m: "Medium",
    pygame.K_3: "Hard", pygame.K_h: "Hard",
}


class GameEngine:
    COLLISION_STEP_PX = 2      # max pixels moved between collision checks
    GAME_OVER_INPUT_DELAY = 30  # frames (~0.5 s) to ignore input after dying

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        self.sounds = SoundManager()  # Task 4: flap / score / die sounds
        self.quit_requested = False  # main loop exits when this is True
        self.difficulty = "Medium"   # the original game's settings
        self._buttons = {}           # label -> Rect, built when Game Over is drawn
        self.reset()

    def reset(self, difficulty=None):
        """Start a fresh round, optionally switching difficulty."""
        if difficulty is not None:
            self.difficulty = difficulty
        settings = DIFFICULTIES[self.difficulty]

        self.bird = Bird(self.width // 4, self.height // 2)
        self.pipe_speed = settings["speed"]
        self.pipe_gap = settings["gap"]
        self.pipe_interval = settings["interval"]  # frames between pipe spawns
        self._spawn_timer = 0
        self.pipes = [self._new_pipe(self.width + 100)]

        self.score = 0
        self.game_over = False
        self._game_over_frames = 0
        # Wait for the first flap before gravity/pipes start, otherwise the
        # bird falls to the ground before the player can react (the window
        # often doesn't even have keyboard focus yet when the game starts).
        self.started = False
        self._idle_frames = 0

    def _new_pipe(self, x):
        return Pipe(x, self.height, gap=self.pipe_gap, speed=self.pipe_speed)

    # ------------------------------------------------------------------ input
    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) \
                or event.type == pygame.MOUSEBUTTONDOWN:
            self.started = True  # first flap starts the round
            self.bird.flap()
            self.sounds.play_flap()

    def _handle_game_over_event(self, event):
        # Ignore input for a moment so a panicked flap doesn't skip the screen.
        if self._game_over_frames < self.GAME_OVER_INPUT_DELAY:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.quit_requested = True
            elif event.key in DIFFICULTY_KEYS:
                self.reset(DIFFICULTY_KEYS[event.key])
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                self.reset()  # replay at the same difficulty
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for label, rect in self._buttons.items():
                if rect.collidepoint(event.pos):
                    if label == "Quit":
                        self.quit_requested = True
                    else:
                        self.reset(label)
                    break

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    # ----------------------------------------------------------------- update
    def _end_game(self):
        if not self.game_over:
            self.sounds.play_die()
        self.game_over = True
        self._game_over_frames = 0

    def update(self):
        if self.game_over:
            self._game_over_frames += 1
            return

        if not self.started:
            # "Get Ready": bird hovers gently in place, pipes don't move
            self._idle_frames += 1
            self.bird.y = self.height // 2 + 8 * math.sin(self._idle_frames / 10)
            return

        prev_y = self.bird.y
        self.bird.update()

        # Ceiling / ground
        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            # keep the bird visible on screen when it dies
            self.bird.y = max(self.bird.radius, min(self.bird.y, self.height - self.bird.radius))
            self._end_game()
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(self._new_pipe(self.width))

        # Task 1: accurate collision.
        # Test the bird's full circle (not just its centre) against each pipe,
        # and split this frame's movement into small sub-steps so that at high
        # pipe speeds / fall speeds nothing can jump past an edge between frames.
        max_move = max(self.pipe_speed, abs(self.bird.y - prev_y))
        steps = max(1, int(max_move // self.COLLISION_STEP_PX) + 1)

        for pipe in self.pipes:
            start_x = pipe.x
            for i in range(1, steps + 1):
                t = i / steps
                pipe.x = start_x - pipe.speed * t
                bird_y = prev_y + (self.bird.y - prev_y) * t
                if pipe.collides_with_circle(self.bird.x, bird_y, self.bird.radius):
                    self._end_game()
                    break
            pipe.x = start_x - pipe.speed  # same end position as pipe.move()

            if not self.game_over and not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.sounds.play_score()

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    # ----------------------------------------------------------------- render
    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        if self.game_over:
            self._render_game_over(screen)
        else:
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            diff = self.small_font.render(self.difficulty, True, DIFFICULTIES[self.difficulty]["color"])
            screen.blit(diff, diff.get_rect(topright=(self.width - 10, 16)))
            if not self.started:
                self._blit_centered(screen, self.big_font, "GET READY", WHITE, self.height // 3)
                self._blit_centered(screen, self.font, "Press SPACE or click to flap", WHITE,
                                    self.height // 3 + 60)

    def _blit_centered(self, screen, font, text, color, y):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

    def _render_game_over(self, screen):
        # Dim the frozen game behind a translucent panel
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, self.width - 60, 440)
        panel.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(screen, DARK, panel, border_radius=16)
        pygame.draw.rect(screen, WHITE, panel, width=3, border_radius=16)

        cy = panel.top
        self._blit_centered(screen, self.big_font, "GAME OVER", WHITE, cy + 55)
        self._blit_centered(screen, self.font, f"Final Score: {self.score}", GOLD, cy + 115)
        self._blit_centered(screen, self.small_font, f"({self.difficulty})", WHITE, cy + 148)

        # Task 3: replay menu - pick a difficulty or quit
        self._buttons = {}
        if self._game_over_frames < self.GAME_OVER_INPUT_DELAY:
            return
        self._blit_centered(screen, self.small_font, "Play again - choose difficulty:", WHITE, cy + 190)

        mouse = pygame.mouse.get_pos()
        btn_w, btn_h, gap = 120, 48, 12
        total = 3 * btn_w + 2 * gap
        x = self.width // 2 - total // 2
        for i, (label, cfg) in enumerate(DIFFICULTIES.items()):
            rect = pygame.Rect(x + i * (btn_w + gap), cy + 220, btn_w, btn_h)
            self._draw_button(screen, rect, f"{i + 1}. {label}", cfg["color"], rect.collidepoint(mouse),
                              selected=(label == self.difficulty))
            self._buttons[label] = rect

        quit_rect = pygame.Rect(0, 0, 160, btn_h)
        quit_rect.center = (self.width // 2, cy + 310)
        self._draw_button(screen, quit_rect, "Quit (Esc)", WHITE, quit_rect.collidepoint(mouse))
        self._buttons["Quit"] = quit_rect

        self._blit_centered(screen, self.small_font, "SPACE = replay same difficulty", (180, 180, 190), cy + 385)

    def _draw_button(self, screen, rect, text, accent, hovered, selected=False):
        pygame.draw.rect(screen, BUTTON_HOVER if hovered else GREY, rect, border_radius=10)
        pygame.draw.rect(screen, accent, rect, width=4 if selected else 2, border_radius=10)
        surf = self.small_font.render(text, True, accent)
        screen.blit(surf, surf.get_rect(center=rect.center))
