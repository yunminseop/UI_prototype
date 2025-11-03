import yaml
import pygame

def load_config(path="config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

def init_from_config(config):
    # 화면 크기
    WIDTH = config["screen"]["width"]
    HEIGHT = config["screen"]["height"]

    # 색상
    COLORS = {
        "TOP": tuple(config["colors"]["top"]),
        "LEFT": tuple(config["colors"]["left"]),
        "MAIN": tuple(config["colors"]["main"]),
        "BOTTOM": tuple(config["colors"]["bottom"]),
        "TEXT": tuple(config["colors"]["text"]),
        "BUTTON": tuple(config["colors"]["button"]),
        "BUTTON_HOVER": tuple(config["colors"]["button_hover"]),
    }

    # 폰트
    pygame.font.init()
    font_cfg = config["fonts"]
    FONTS = {
        "main": pygame.font.SysFont(font_cfg["main"]["name"], font_cfg["main"]["size"]),
        "small": pygame.font.SysFont(font_cfg["small"]["name"], font_cfg["small"]["size"]),
        "tiny": pygame.font.SysFont(font_cfg["tiny"]["name"], font_cfg["tiny"]["size"]),
    }

    # 로그 파일 경로
    LOG_FILE = config["log"]["file"]

    return WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE
