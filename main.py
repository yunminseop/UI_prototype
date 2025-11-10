import pygame
from config_loader import load_config, init_from_config
from utils.UI_manager import UIModel

def main():
    pygame.init()
    config = load_config()
    WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE = init_from_config(config)
    ui = UIModel(WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE)
    ui.run()

if __name__ == "__main__":
    main()
