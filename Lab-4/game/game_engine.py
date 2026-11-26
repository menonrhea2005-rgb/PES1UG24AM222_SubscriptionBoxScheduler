import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

class GameEngine:
    COLLISION_STEP_PX = 2  # max pixels moved between collision checks

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.bird = Bird(width // 4, height // 2)
        self.pipe_speed = 4
        self.pipe_interval = 90  # frames between pipe spawns
        self._spawn_timer = 0
        self.pipes = [Pipe(width + 100, height, speed=self.pipe_speed)]

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

    def handle_event(self, event):
        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        prev_y = self.bird.y
        self.bird.update()

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self.game_over = True
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
                    self.game_over = True
                    break
            pipe.x = start_x - pipe.speed  # same end position as pipe.move()

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over and not getattr(self, "_game_over_logged", False):
            # NOTE: no proper game-over screen yet - see Task 2 in the README.
            print("Game over! Final score:", self.score)
            self._game_over_logged = True
