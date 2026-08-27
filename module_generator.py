import time
from quest_generator import generate_quest
from tools.log_tools import *

def main():
    # Reset log
    log_clear()

    # Start timer
    start_time = time.time()

    player_count = 4
    party_level = 1
    
    quest = generate_quest(player_count, party_level)

    if quest is None:
        log_error("Quest generation failed... Exiting.")
        return

    # End timer
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    log_success(f"Module generation complete in {minutes}m {seconds}s")

if __name__ == "__main__":
    main()

