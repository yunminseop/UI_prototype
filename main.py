import pygame
from config_loader import load_config, init_from_config
from UI_manager import UIModel
import os

def main():
    pygame.init()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(base_dir, "config", "config.yaml")

    config = load_config(cfg_path)
    WIDTH, HEIGHT, COLORS, FONTS, _ = init_from_config(config)
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    from datetime import datetime
    now = datetime.now()
    
    log_dir = os.path.join(base_dir, "data")
    os.makedirs(log_dir, exist_ok=True)
    
    log_name = f"{now.year}_{now.month:02d}_{now.day:02d}_{now.hour:02d}_{now.minute:02d}.csv"
    log_file = os.path.join(log_dir, log_name)

    # display 초기화 후 UIModel 생성
    ui = UIModel(WIDTH, HEIGHT, COLORS, FONTS, log_file)
    ui.run()


if __name__ == "__main__":
    main()
