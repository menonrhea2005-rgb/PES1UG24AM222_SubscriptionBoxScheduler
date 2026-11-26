import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DARK = (20, 20, 30)
GOLD = (255, 215, 0)


class GameEngine:
    COLLISION_STEP_PX = 2      # max pixels moved between collision checks
    GAME_OVER_INPUT_DELAY = 30  # frames (~0.5 s) to ignore input after dying

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)

        self.quit_requested = False  # main loop exits when this is True
        self.reset()

    def reset(self):
        """Start a fresh round."""
        self.bird = Bird(self.width // 4, self.height // 2)
        self.pipe_speed = 4
        self.pipe_interval = 90  # frames between pipe spawns
        self._spawn_timer = 0
        self.pipes = [Pipe(self.width + 100, self.height, speed=self.pipe_speed)]

        self.score = 0
        self.game_over = False
        self._game_over_frames = 0

    # ------------------------------------------------------------------ input
    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()

    def _handle_game_over_event(self, event):
        # Ignore input for a moment so a panicked flap doesn't skip the screen.
        if self._game_over_frames < self.GAME_OVER_INPUT_DELAY:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.quit_requested = True
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_r):
                self.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.reset()

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    # ----------------------------------------------------------------- update
    def _end_game(self):
        self.game_over = True
        self._game_over_frames = 0

    def update(self):
        if self.game_over:
            self._game_over_frames += 1
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
            self.pipes.append(Pipe(self.width, self.height, speed=self.pipe_speed))

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

    def _blit_centered(self, screen, font, text, color, y):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

    def _render_game_over(self, screen):
        # Dim the frozen game behind a translucent panel
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, self.width - 80, 260)
        panel.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(screen, DARK, panel, border_radius=16)
        pygame.draw.rect(screen, WHITE, panel, width=3, border_radius=16)

        cy = panel.top
        self._blit_centered(screen, self.big_font, "GAME OVER", WHITE, cy + 55)
        self._blit_centered(screen, self.font, f"Final Score: {self.score}", GOLD, cy + 120)

        if self._game_over_frames >= self.GAME_OVER_INPUT_DELAY:
            self._blit_centered(screen, self.small_font, "SPACE / Click  -  Play again", WHITE, cy + 180)
            self._blit_centered(screen, self.small_font, "ESC  -  Quit", WHITE, cy + 215)
