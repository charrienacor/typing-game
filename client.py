import socket
import pickle
import pygame
import threading

# Constants
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Client class
class WordUnscrambleClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("192.168.0.107", 5555))  # Connect to server
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Word Unscramble Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)  # Smaller font size
        self.user_input = ""
        self.lives = [5, 5]
        self.scrambled_word = ""
        self.game_over = False
        self.winner = None
        self.player_number = None

        # Start a thread to listen for server messages
        threading.Thread(target=self.receive_data, daemon=True).start()

    def receive_data(self):
        while True:
            try:
                data = self.client.recv(1024)
                if data:
                    message = pickle.loads(data)
                    if isinstance(message, tuple):
                        self.scrambled_word, self.lives, self.player_number = message
                    else:
                        self.winner = message
                        self.game_over = True
            except:
                break

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_RETURN:
                        self.client.send(self.user_input.encode('utf-8'))
                        self.user_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_input = self.user_input[:-1]
                    else:
                        self.user_input += event.unicode

            # Drawing
            self.screen.fill(WHITE)

            if not self.game_over:
                # Render text surfaces
                scrambled_surface = self.font.render(self.scrambled_word, True, BLACK)
                input_surface = self.font.render(self.user_input, True, BLUE)
                lives_surface = self.font.render(f"Player 1 Lives: {self.lives[0]}  |  Player 2 Lives: {self.lives[1]}", True, BLACK)

                # Draw lives higher on the screen
                lives_rect = lives_surface.get_rect(center=(WIDTH // 2, HEIGHT // 5))
                self.screen.blit(lives_surface, lives_rect)

                # Draw the scrambled word
                scrambled_rect = scrambled_surface.get_rect(center=(WIDTH // 2, HEIGHT * 2 / 5))
                self.screen.blit(scrambled_surface, scrambled_rect)

                # Draw the input box with an outline
                input_box_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT * 3 / 5 - 25, 400, 50)
                pygame.draw.rect(self.screen, BLACK, input_box_rect, 2)  # Draw the black outline
                pygame.draw.rect(self.screen, WHITE, input_box_rect.inflate(-4, -4))  # Fill the box with white, leaving a small border

                # Center the input text in the box
                text_x = input_box_rect.x + (input_box_rect.width - input_surface.get_width()) // 2
                text_y = input_box_rect.y + (input_box_rect.height - input_surface.get_height()) // 2
                self.screen.blit(input_surface, (text_x, text_y))  # Draw user input

            else:
                # Clear the screen and show winner message
                winner_surface = self.font.render(f"Player {self.winner} wins!", True, BLUE)
                winner_rect = winner_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.fill(WHITE)  # Clear the screen
                self.screen.blit(winner_surface, winner_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    pygame.init()
    client = WordUnscrambleClient()
    client.run()