import pygame
import sys
from collections import deque
import copy

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOTTLE_WIDTH = 60
BOTTLE_HEIGHT = 200
LEVEL_HEIGHT = 40
MARGIN = 12

# Base colors

COLORS = {
    'r': (255, 0, 0),
    'g': (0, 255, 0),
    'b': (0, 0, 255),
    'y': (255, 255, 0),
    'p': (255, 0, 255),
    'o': (255, 165, 0),
    'w': (255, 255, 255),
    'k': (0, 0, 0)
}
# Extra colors for uppercase letters (alt shades)

EXTRA_COLORS = {
    'B': (150, 75, 0),    # Brown
    'G': (0, 128, 0),     # Dark Green
    'Y': (200, 200, 0),   # Mustard Yellow
    'P': (128, 0, 128),   # Purple
    'O': (255, 140, 0),   # Dark Orange
    'W': (220, 220, 220), # Light Gray
    'K': (50, 50, 50)     # Dark Gray
}

def get_color(letter):
    # Return the extra color if available, otherwise, return the base color
    if letter in EXTRA_COLORS:
        return EXTRA_COLORS[letter]
    else:
        return COLORS.get(letter.lower(), (128, 128, 128))

# ------------------------------
# Settings screen for user input
# ------------------------------
def get_settings():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enter Puzzle Settings")
    font = pygame.font.Font(None, 36)
    input_box1 = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60, 200, 50)
    input_box2 = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 10, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color1 = color_inactive
    color2 = color_inactive
    active1 = False
    active2 = False
    text1 = ''
    text2 = ''
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(event.pos):
                    active1 = True
                    active2 = False
                elif input_box2.collidepoint(event.pos):
                    active2 = True
                    active1 = False
                else:
                    active1 = False
                    active2 = False
                color1 = color_active if active1 else color_inactive
                color2 = color_active if active2 else color_inactive
            if event.type == pygame.KEYDOWN:
                if active1:
                    if event.key == pygame.K_RETURN:
                        active1 = False
                    elif event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        text1 += event.unicode
                elif active2:
                    if event.key == pygame.K_RETURN:
                        active2 = False
                    elif event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        text2 += event.unicode
                if event.key == pygame.K_TAB:
                    active1, active2 = active2, active1
                    color1 = color_active if active1 else color_inactive
                    color2 = color_active if active2 else color_inactive
                # If Enter is pressed and both fields are filled, finish input
                if event.key == pygame.K_RETURN and not active1 and not active2 and text1 and text2:
                    done = True

        screen.fill((30, 30, 30))
        txt_surface1 = font.render("Number of Bottles:              " + text1, True, (255, 255, 255))
        txt_surface2 = font.render("Max Levels:                    " + text2, True, (255, 255, 255))
        screen.blit(txt_surface1, (input_box1.x - 240, input_box1.y - -15))
        screen.blit(txt_surface2, (input_box2.x - 200, input_box2.y - -15))
        pygame.draw.rect(screen, color1, input_box1, 3)
        pygame.draw.rect(screen, color2, input_box2, 3)
        pygame.display.flip()
    try:
        num_bottles = int(text1)
        max_levels = int(text2)
    except:
        num_bottles = 5
        max_levels = 4
    return num_bottles, max_levels

# ------------------------------
# Pygame Bottle Builder Interface
# ------------------------------
class BottleBuilder:
    def __init__(self, num_bottles, max_levels):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Water Sort Puzzle Builder")
        
        self.num_bottles = num_bottles
        self.max_levels = max_levels
        self.bottles = [[] for _ in range(num_bottles)]
        self.selected_bottle = 0
        self.running = True
        self.confirmed = False
        
        self.font = pygame.font.Font(None, 36)
        
        # Bottle positions
        self.bottle_positions = []
        start_x = (SCREEN_WIDTH - (num_bottles * (BOTTLE_WIDTH + MARGIN))) // 2
        for i in range(num_bottles):
            x = start_x + i * (BOTTLE_WIDTH + MARGIN)
            y = SCREEN_HEIGHT // 1.3 - BOTTLE_HEIGHT // 2
            self.bottle_positions.append((x, y))
        
    def draw(self):
        self.screen.fill((30, 30, 30))
        
        # instructions
        instructions = [
            "Type colors (r, g, b, y, p, o, w, k). Use capital letters for alternative shades.",
            "Example: Capital B for brown, Capital G for dark green, etc. more colors in the codes' comments",
            "Backspace: Delete last color | Enter: Confirm",
            f"Bottle {self.selected_bottle+1} selected"
        ]
        for idx, line in enumerate(instructions):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (20, 20 + idx * 30))
        
        # Bottles
        for i, (x, y) in enumerate(self.bottle_positions):
            # Bottle outline
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, BOTTLE_WIDTH, BOTTLE_HEIGHT), 2)
            
            # Bottle selected highlight
            if i == self.selected_bottle:
                pygame.draw.rect(self.screen, (255, 255, 0), (x-5, y-5, BOTTLE_WIDTH+10, BOTTLE_HEIGHT+10), 2)
            
            # Liquid levels using get_color
            for l, color in enumerate(reversed(self.bottles[i])):
                pygame.draw.circle(self.screen, get_color(color), 
                    (x + BOTTLE_WIDTH//2, y + BOTTLE_HEIGHT - (l * LEVEL_HEIGHT) - LEVEL_HEIGHT//2),
                    BOTTLE_WIDTH//2 - 5)
        
        pygame.display.flip()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.confirmed = True
                    self.running = False
                elif event.key == pygame.K_BACKSPACE:
                    if len(self.bottles[self.selected_bottle]) > 0:
                        self.bottles[self.selected_bottle].pop()
                elif event.unicode:
                    # If the key pressed is in the extra colors (e.g., capital letters), add it directly.
                    if event.unicode in EXTRA_COLORS:
                        if len(self.bottles[self.selected_bottle]) < self.max_levels:
                            self.bottles[self.selected_bottle].append(event.unicode)
                    # Otherwise, check for regular colors (using lowercase).
                    elif event.unicode.lower() in COLORS:
                        if len(self.bottles[self.selected_bottle]) < self.max_levels:
                            self.bottles[self.selected_bottle].append(event.unicode.lower())
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for i, (bx, by) in enumerate(self.bottle_positions):
                    if bx <= x <= bx + BOTTLE_WIDTH and by <= y <= by + BOTTLE_HEIGHT:
                        self.selected_bottle = i
    
    # special code 👻👻
    def build_special_code(self):
        codes = []
        for bottle in self.bottles:
            if not bottle:
                codes.append('_')
            else:
                codes.append(''.join(bottle))
        return ','.join(codes)

# ------------------------------
# Puzzle Solving Functions
# ------------------------------
def is_goal_state(state):
    for bottle in state:
        if len(bottle) > 0 and len(set(bottle)) != 1:
            return False
    return True

def can_pour(source, destination, max_levels):
    if not source:
        return False
    if not destination:
        return True
    return source[-1] == destination[-1] and len(destination) < max_levels

def get_possible_moves(state, max_levels):
    moves = []
    for i in range(len(state)):
        for j in range(len(state)):
            if i != j and can_pour(state[i], state[j], max_levels):
                moves.append((i, j))
    return moves

def pour(source, destination):
    destination.append(source.pop())

def print_bottles(state):
    print("\nCurrent State:")
    for i, bottle in enumerate(state):
        print(f"Bottle {i+1}: {bottle}")
    print()

def solve_puzzle(initial_state, max_levels):
    queue = deque()
    queue.append((initial_state, []))
    visited = set()

    while queue:
        current_state, path = queue.popleft()
        if is_goal_state(current_state):
            return path
        state_key = tuple(tuple(bottle) for bottle in current_state)
        if state_key in visited:
            continue
        visited.add(state_key)
        for i, j in get_possible_moves(current_state, max_levels):
            if not current_state[i]:
                continue
            new_state = [bottle.copy() for bottle in current_state]
            pour(new_state[i], new_state[j])
            source_color = current_state[i][-1] if current_state[i] else "empty"
            dest_color = current_state[j][-1] if current_state[j] else "empty"
            queue.append((new_state, path + [(i, j, source_color, dest_color)]))
    return None

def decode_special_code(code, num_bottles):
    state = []
    bottles = code.split(',')
    for i in range(num_bottles):
        if i < len(bottles) and bottles[i].strip() != '_':
            state.append(list(bottles[i].strip()))
        else:
            state.append([])
    return state

# ------------------------------
# Main Function
# ------------------------------
def main():
    # Puzzle sttings
    num_bottles, max_levels = get_settings()

    # Run builder interface
    builder = BottleBuilder(num_bottles, max_levels)
    while builder.running:
        builder.handle_input()
        builder.draw()
    
    if builder.confirmed:
        # Generate special code
        special_code = builder.build_special_code()
        # Fix the special code by reversing each bottle's string to get the correct order (this was because of a mess up i did earlier by reversing all colors on the builder 😭)
        fixed_parts = []
        for part in special_code.split(','):
            if part.strip() != '_':
                fixed_parts.append(part.strip()[::-1])
            else:
                fixed_parts.append('_')
        fixed_special_code = ','.join(fixed_parts)
        full_code = f"{fixed_special_code},{max_levels},{num_bottles}"
        print(f"Generated Special Code: {full_code}")
        
        # Waiting message
        builder.screen.fill((30, 30, 30))
        wait_text = builder.font.render("Wait a second while the solution is being generated :)", True, (255,255,255))
        builder.screen.blit(wait_text, (SCREEN_WIDTH//2 - wait_text.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        
        # Decode special code to initial state
        initial_state = decode_special_code(fixed_special_code, num_bottles)
        print_bottles(initial_state)
        
        # Solve the puzzle
        solution = solve_puzzle(initial_state, max_levels)
        
        # Enumerate and print solution
        if solution:
            print("\nSolution Steps:")
            for step_num, step in enumerate(solution, start=1):
                source_bottle = step[0] + 1
                dest_bottle = step[1] + 1
                source_color = step[2][0] if step[2] != "empty" else "e"
                dest_color = step[3][0] if step[3] != "empty" else "e"
                print(f"{step_num}. {source_bottle}{source_color} -> {dest_bottle}{dest_color}")
        else:
            print("No solution found!")

if __name__ == "__main__":
    main()
    
# --------------------------------------------------------------------------------------------------------
# Enjoy while its not patched oon these trash offerwall puzzle games, feel free to optimize it in any way
#---------------------------------------------------------------------------------------------------------
