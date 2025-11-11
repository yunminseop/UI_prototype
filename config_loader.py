import yaml
import pygame
import os

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

    pygame.font.init()

    # 폰트 파일 경로 설정
    font_path = os.path.join("assets", "NanumGothic.ttf")

    # 폰트 존재 여부 확인
    if os.path.exists(font_path):
        main_font = pygame.font.Font(font_path, config["fonts"]["main"]["size"])
        small_font = pygame.font.Font(font_path, config["fonts"]["small"]["size"])
        tiny_font = pygame.font.Font(font_path, config["fonts"]["tiny"]["size"])
    else:
        
        fallback_font_name = pygame.font.match_font(['NotoSansCJKkr', 'NanumGothic', 'malgun'])
        main_font = pygame.font.Font(fallback_font_name, config["fonts"]["main"]["size"])
        small_font = pygame.font.Font(fallback_font_name, config["fonts"]["small"]["size"])
        tiny_font = pygame.font.Font(fallback_font_name, config["fonts"]["tiny"]["size"])

    FONTS = {
        "main": main_font,
        "small": small_font,
        "tiny": tiny_font,
    }

    # 로그 파일 경로
    LOG_FILE = config["log"]["file"]

    return WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE
