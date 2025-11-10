import pygame
from config_loader import load_config, init_from_config
from UI_manager import UIModel
import os

def main():
    pygame.init()
    LOG_FILE = "logs/log.csv"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(base_dir, "config", "config.yaml")

    cfg = load_config(config_dir)
    WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE = init_from_config(cfg)
    ui = UIModel(WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE)
    ui.run()

if __name__ == "__main__":
    main()