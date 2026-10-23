import pygame
import sys
import random
import math

# --- INITIALIZATION ---
pygame.init()

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 24
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Snake")

# --- NATURAL COLOR PALETTE ---
BG_DIRT = (65, 55, 45)           # Earthy brown
GRASS_GREEN = (50, 90, 40)       # Dark natural green
SNAKE_BODY = (75, 120, 60)       # Olive green
SNAKE_BODY_LIGHT = (95, 140, 75) # Lighter scale color
SNAKE_BELLY = (180, 190, 150)    # Pale underbelly
SNAKE_EYE = (220, 180, 50)       # Yellow eye
SNAKE_PUPIL = (10, 10, 10)       # Slit pupil
TONGUE_COLOR = (200, 50, 50)     # Red tongue
APPLE_RED = (180, 30, 30)
APPLE_HIGHLIGHT = (255, 100, 100)
APPLE_STEM = (80, 50, 30)
LEAF_GREEN = (60, 120, 40)
TEXT_COLOR = (240, 230, 210)

clock = pygame.time.Clock()

# Pre-generate background texture so it doesn't flicker
bg_texture = pygame.Surface((WIDTH, HEIGHT))
bg_texture.fill(BG_DIRT)
for _ in range(8000):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    color = random.choice([(55, 45, 35), (75, 65, 55), (40, 50, 30)])
    pygame.draw.circle(bg_texture, color, (x, y), random.randint(1, 3))

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), 
                          (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2), 
                          (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.grow = False
        self.tongue_timer = 0

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # Wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            return False
            
        # Self collision
        if new_head in self.positions[:-1]:
            return False

        self.positions.insert(0, new_head)
        
        if self.grow:
            self.grow = False
        else:
            self.positions.pop()
            
        self.tongue_timer += 1
        return True

    def draw(self, surface):
        # 1. Draw Shadows underneath the snake
        for i, (x, y) in enumerate(self.positions):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + 4, CELL_SIZE, CELL_SIZE)
            pygame.draw.ellipse(surface, (30, 25, 20), rect)

        # 2. Draw the Body (Tail to Head so head overlaps)
        for i in range(len(self.positions) - 1, 0, -1):
            x, y = self.positions[i][0] * CELL_SIZE, self.positions[i][1] * CELL_SIZE
            
            # Taper the tail
            tail_ratio = i / len(self.positions)
            radius = (CELL_SIZE // 2) * (0.5 + 0.5 * (1 - tail_ratio))
            center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
            
            # Draw body segments
            pygame.draw.circle(surface, SNAKE_BODY, center, int(radius))
            
            # Draw scales (lighter pattern)
            if i % 2 == 0:
                pygame.draw.circle(surface, SNAKE_BODY_LIGHT, center, int(radius * 0.7))
                
            # Draw belly line
            pygame.draw.line(surface, SNAKE_BELLY, 
                             (center[0] - radius//2, center[1] + radius//2), 
                             (center[0] + radius//2, center[1] + radius//2), 2)

        # 3. Draw the Head
        head_x, head_y = self.positions[0][0] * CELL_SIZE, self.positions[0][1] * CELL_SIZE
        head_center = (head_x + CELL_SIZE // 2, head_y + CELL_SIZE // 2)
        
        # Head shadow
        pygame.draw.ellipse(surface, (30, 25, 20), (head_x - 2, head_y + 2, CELL_SIZE + 4, CELL_SIZE))

        # Head shape (Oval based on direction)
        head_rect = pygame.Rect(head_x - 2, head_y - 2, CELL_SIZE + 4, CELL_SIZE + 4)
        pygame.draw.ellipse(surface, SNAKE_BODY_LIGHT, head_rect)
        
        # Draw Eyes and Tongue
        dx, dy = self.direction
        eye_offset = 6
        eye_radius = 4
        
        # Eye positions
        if dx == 1: # Right
            eye1, eye2 = (head_center[0] + 4, head_center[1] - 6), (head_center[0] + 4, head_center[1] + 6)
        elif dx == -1: # Left
            eye1, eye2 = (head_center[0] - 4, head_center[1] - 6), (head_center[0] - 4, head_center[1] + 6)
        elif dy == -1: # Up
            eye1, eye2 = (head_center[0] - 6, head_center[1] - 4), (head_center[0] + 6, head_center[1] - 4)
        elif dy == 1: # Down
            eye1, eye2 = (head_center[0] - 6, head_center[1] + 4), (head_center[0] + 6, head_center[1] + 4)

        # Draw Eyes (Yellow with vertical slit pupils)
        for eye in (eye1, eye2):
            pygame.draw.circle(surface, SNAKE_EYE, eye, eye_radius)
            if dx != 0: # Vertical pupil for horizontal movement
                pygame.draw.line(surface, SNAKE_PUPIL, (eye[0], eye[1]-2), (eye[0], eye[1]+2), 2)
            else: # Horizontal pupil for vertical movement
                pygame.draw.line(surface, SNAKE_PUPIL, (eye[0]-2, eye[1]), (eye[0]+2, eye[1]), 2)

        # Flickering Tongue
        if (self.tongue_timer // 15) % 2 == 0: # Flicks every ~1 second
            start = head_center
            if dx == 1: end = (head_center[0] + 15, head_center[1])
            elif dx == -1: end = (head_center[0] - 15, head_center[1])
            elif dy == -1: end = (head_center[0], head_center[1] - 15)
            elif dy == 1: end = (head_center[0], head_center[1] + 15)
            
            # Draw forked tongue
            pygame.draw.line(surface, TONGUE_COLOR, start, end, 2)
            if dx == 1: 
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]+4, end[1]-4), 2)
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]+4, end[1]+4), 2)
            elif dx == -1: 
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]-4, end[1]-4), 2)
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]-4, end[1]+4), 2)
            elif dy == -1:
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]-4, end[1]-4), 2)
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]+4, end[1]-4), 2)
            elif dy == 1:
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]-4, end[1]+4), 2)
                pygame.draw.line(surface, TONGUE_COLOR, end, (end[0]+4, end[1]+4), 2)

class Food:
    def __init__(self):
        self.randomize()
        
    def randomize(self):
        self.position = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
        
    def draw(self, surface):
        x = self.position[0] * CELL_SIZE + CELL_SIZE // 2
        y = self.position[1] * CELL_SIZE + CELL_SIZE // 2
        
        # Draw Shadow
        pygame.draw.ellipse(surface, (30, 25, 20), (x - CELL_SIZE//2, y + 2, CELL_SIZE, CELL_SIZE - 4))
        
        # Draw Apple Base
        pygame.draw.circle(surface, APPLE_RED, (x, y), CELL_SIZE // 2 - 2)
        
        # Draw Highlight (Shine)
        pygame.draw.circle(surface, APPLE_HIGHLIGHT, (x - 4, y - 4), 3)
        
        # Draw Stem
        pygame.draw.line(surface, APPLE_STEM, (x, y - CELL_SIZE//2 + 2), (x + 2, y - CELL_SIZE//2 - 3), 2)
        
        # Draw Leaf
        leaf_rect = pygame.Rect(x + 1, y - CELL_SIZE//2 - 4, 8, 5)
        pygame.draw.ellipse(surface, LEAF_GREEN, leaf_rect)

def main():
    snake = Snake()
    food = Food()
    
    state = "START" # START, PLAYING, GAME_OVER
    speed = 9 # Slower, more natural pace
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if state == "START":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        snake.reset()
                        food.randomize()
                        
                elif state == "PLAYING":
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and snake.direction != (0, 1):
                        snake.next_direction = (0, -1)
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and snake.direction != (0, -1):
                        snake.next_direction = (0, 1)
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and snake.direction != (1, 0):
                        snake.next_direction = (-1, 0)
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and snake.direction != (-1, 0):
                        snake.next_direction = (1, 0)
                        
                elif state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        state = "PLAYING"
                        snake.reset()
                        food.randomize()

        if state == "PLAYING":
            if not snake.move():
                state = "GAME_OVER"
            
            # Food Collision
            if snake.positions[0] == food.position:
                snake.grow = True
                snake.score += 1
                
                # Ensure food doesn't spawn on snake
                while food.position in snake.positions:
                    food.randomize()
                    
                # Slightly increase speed
                if speed < 16:
                    speed += 0.2
        
        # --- RENDERING ---
        # Draw Background Texture
        screen.blit(bg_texture, (0, 0))
        
        # Draw Game Elements
        food.draw(screen)
        snake.draw(screen)

        # Draw UI Text
        font = pygame.font.SysFont("Georgia", 28, bold=True) # Serif font for a natural feel
        score_text = font.render(f"Apples: {snake.score}", True, TEXT_COLOR)
        
        # Text Shadow
        shadow_text = font.render(f"Apples: {snake.score}", True, (0, 0, 0))
        screen.blit(shadow_text, (22, 22))
        screen.blit(score_text, (20, 20))

        if state == "START":
            title_font = pygame.font.SysFont("Georgia", 60, bold=True)
            title = title_font.render("The Snake", True, SNAKE_BODY)
            title_shadow = title_font.render("The Snake", True, (0,0,0))
            screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, HEIGHT//2 - 100 + 3))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
            
            sub = font.render("Press SPACE to Play", True, TEXT_COLOR)
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

        elif state == "GAME_OVER":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            go_font = pygame.font.SysFont("Georgia", 70, bold=True)
            go_text = go_font.render("GAME OVER", True, APPLE_RED)
            restart = font.render("Press SPACE to try again", True, TEXT_COLOR)
            
            screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 80))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 30))

        pygame.display.flip()
        clock.tick(int(speed))

if __name__ == "__main__":
    main()