import threading
import time
import sys
import readline

def background_task():
    while True:
        # Save the input line's current state
        saved_input = readline.get_line_buffer()
        saved_pos = readline.get_begidx()

        # Clear the current line and print the background update
        sys.stdout.write("\r\033[K")  # Clear the line
        print("[Background Update] New message received!")

        # Restore the input line
        sys.stdout.write(f"\r{saved_input}")
        sys.stdout.flush()

        # Sleep before the next update
        time.sleep(2)

# Start the background task
bg_thread = threading.Thread(target=background_task)
bg_thread.daemon = True
bg_thread.start()

# Main input loop
while True:
    try:
        # Prompt the user for input
        user_input = input("Enter a command: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Exiting...")
            break
    except KeyboardInterrupt:
        break

