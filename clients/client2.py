import socket
import json
import threading
import pygame  # Library for creating graphical interface
import keyboard  # Library to detect arrow keys
import time

# Server connection configuration
HOST = 'localhost'
#HOST = 'ip here'
PORT = 12345

# Game state
positions = {}  # Dictionary to keep track of player positions locally
player_id = None  # Unique identifier for the client

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Game")

# Colors for players
PLAYER_COLOR = (0, 128, 255)  # Blue
OTHER_PLAYER_COLOR = (128, 128, 128)  # Gray

# Display the game positions
def display_positions():
    screen.fill((0, 0, 0))  # Clear screen with black background
    
    print(str(positions.items()))
    # Draw each player as a rectangle
    for pid, data in positions.items():
        print("pid: " + str(pid) + ", " + "player_id: " + str(player_id))
        # Check if this player is the local player
        position = data['position']
        if str(pid) == str(player_id):
            color = PLAYER_COLOR  # Local player color
        else:
            color = OTHER_PLAYER_COLOR  # Other players' color
        pygame.draw.rect(screen, color, (position[0], position[1], 20, 20))
    
    pygame.display.flip()  # Update the display

# Listen for updates from the server
def listen_for_updates(client_socket):
    global positions, player_id  # Ensure these are treated as global variables
    
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if data:
                update = json.loads(data)
                
                # Set player ID when first received from server
                if "player_id" in update and player_id is None:
                    player_id = update["player_id"]

                # Update player positions when received
                if "players" in update:
                    positions = update["players"]

                # Update the display
                display_positions()
    except (ConnectionResetError, json.JSONDecodeError):
        print("Disconnected from the server.")
    finally:
        client_socket.close()

# Send movement commands to the server
def send_move(client_socket, direction):
    print("player id: " + str(player_id)+ ", " + "direction: " + str(direction))
    if player_id is not None:  # Ensure player_id is set
        move_command = json.dumps({"move": direction, "player_id": player_id})
        client_socket.sendall(move_command.encode())

# Main client function with pygame loop
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Start a thread to listen for updates from the server
    threading.Thread(target=listen_for_updates, args=(client_socket,)).start()

    # Wait for the server to send the player_id
    global player_id
    while player_id is None:
        time.sleep(0.1)  # Wait for player_id to be set

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle arrow key input for movement
        try:
            if keyboard.is_pressed("up"):
                send_move(client_socket, "up")
                time.sleep(0.1)  # Small delay to avoid flooding the server
            elif keyboard.is_pressed("down"):
                send_move(client_socket, "down")
                time.sleep(0.1)
            elif keyboard.is_pressed("left"):
                send_move(client_socket, "left")
                time.sleep(0.1)
            elif keyboard.is_pressed("right"):
                send_move(client_socket, "right")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Client disconnected.")
            running = False

    # Clean up
    client_socket.close()
    pygame.quit()

if __name__ == "__main__":
    start_client()