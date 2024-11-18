import socket
import threading
import random
import pickle

# Constants
WORD_LIST = [
    "apple", "banana", "cherry", "grape", "orange"
]
LIVES = 5

# Server class
class GameServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("192.168.0.107", 5555))  # Bind to ipv4 and a port
        self.server.listen(2)  # Listen for 2 players
        self.players = []
        self.lives = [LIVES, LIVES]
        self.current_word = ""
        self.scrambled_word = ""
        self.current_player = 0  # Track whose turn it is

    def scramble_word(self, word):
        word_list = list(word)
        random.shuffle(word_list)
        return ''.join(word_list)

    def handle_client(self, conn, player_index):
        conn.send(pickle.dumps((self.scrambled_word, self.lives, player_index + 1)))

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                user_input = data.decode('utf-8')

                if user_input.lower() == self.current_word.lower():
                    self.lives[1 - player_index] -= 1  # Decrease other player's lives
                    if self.lives[1 - player_index] <= 0:
                        winner = player_index + 1
                        self.broadcast(f'{winner}')
                        break
                    else:
                        self.new_word()
                else:
                    self.current_player = 1 - player_index  # Switch turn

                self.broadcast((self.scrambled_word, self.lives, player_index + 1))
            except:
                break

        conn.close()

    def broadcast(self, message):
        for player in self.players:
            player.send(pickle.dumps(message))

    def new_word(self):
        self.current_word = random.choice(WORD_LIST)
        self.scrambled_word = self.scramble_word(self.current_word)

    def start(self):
        print("Server started...")
        while len(self.players) < 2:
            conn, addr = self.server.accept()
            print(f"Player {len(self.players) + 1} connected")
            self.players.append(conn)
            if len(self.players) == 2:
                self.new_word()
                for index, player in enumerate(self.players):
                    threading.Thread(target=self.handle_client, args=(player, index)).start()

if __name__ == "__main__":
    server = GameServer()
    server.start()