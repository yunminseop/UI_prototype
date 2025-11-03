import pygame
import sys
import csv
from datetime import datetime
import yaml
from config_loader import load_config, init_from_config

pygame.init()

config = load_config()
WIDTH, HEIGHT, COLORS, FONTS, LOG_FILE = init_from_config(config)

COLOR_TOP = COLORS["TOP"]
COLOR_TEXT = COLORS["TEXT"]
COLOR_LEFT = COLORS["LEFT"]
COLOR_MAIN = COLORS["MAIN"]
COLOR_BOTTOM = COLORS["BOTTOM"]
COLOR_BUTTON = COLORS["BUTTON"]
COLOR_BUTTON_HOVER = COLORS["BUTTON_HOVER"]
font = FONTS["main"]
small_font = FONTS["small"]
tiny_font = FONTS["tiny"]

# -----------------------------------------------------
# Logger
# -----------------------------------------------------
class Logger:
    def __init__(self, file_path):
        self.file = file_path
        with open(self.file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Path", "Target", "Pos", "Depth"])

    def log(self, path, target, pos, depth):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([now, " / ".join(path), target, pos, f"{depth}"])

# -----------------------------------------------------
# Button
# -----------------------------------------------------
class Button:
    def __init__(self, text, rect, action):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.action = action

    def draw(self, surface, mouse_pos):
        color = COLOR_BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        surface.blit(font.render(self.text, True, COLOR_TEXT), font.render(self.text, True, COLOR_TEXT).get_rect(center=self.rect.center))

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# -----------------------------------------------------
# 상단바
# -----------------------------------------------------
class TopBar:
    def __init__(self, width, height, ui_manager):
        self.width = width
        self.height = height
        self.ui_manager = ui_manager

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_TOP, (0, 0, self.width, self.height))
        screen.blit(font.render("Prototype", True, COLOR_TEXT), (3, 3))
        # screen.blit(small_font.render(" / ".join(self.ui_manager.depth_path), True, COLOR_TEXT), (1000, 3))

        path_text = " / ".join(self.ui_manager.depth_path)
        screen.blit(tiny_font.render(path_text, True, COLOR_TEXT), (250, 5))

# -----------------------------------------------------
# SideMenu
# -----------------------------------------------------
class SideMenu:
    def __init__(self, width, top_height, bottom_height):
        self.width = width
        self.top_height = top_height
        self.bottom_height = bottom_height

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_LEFT, (0, self.top_height, self.width, HEIGHT - self.top_height - self.bottom_height))

# -----------------------------------------------------
# BottomBar
# -----------------------------------------------------
class BottomBar:
    def __init__(self, width, height, ui_manager):
        self.width = width
        self.height = height
        self.ui_manager = ui_manager

        # 버튼들 초기화
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        """하단 바의 버튼 배치 정의"""
        y = self.ui_manager.height - self.height + 5
        x = 10
        gap = 110  # 버튼 간격

        # (버튼 이름, x좌표) 순으로 배치
        button_labels = [
            "Seat Temp (-)", "Seat Temp (+)",
            "Heat ray", "Air Cond",
            "Call", "Menu", "Navi",
            "Remove WS Frost", "Remove Rear WS Frost",
            "heat ray (-)", "heat ray (+)"
        ]

        for label in button_labels:
            rect = pygame.Rect(x, y, 110, self.height - 10)
            self.buttons.append({"label": label, "rect": rect})
            x += gap

    def draw(self, screen):
        # 하단 바 배경
        y_pos = self.ui_manager.height - self.height
        pygame.draw.rect(screen, COLOR_BOTTOM, (0, y_pos, self.width, self.height))

        # 버튼 그리기
        for btn in self.buttons:
            pygame.draw.rect(screen, COLOR_BUTTON, btn["rect"], border_radius=8)
            text = small_font.render(btn["label"], True, COLOR_TEXT)
            text_rect = text.get_rect(center=btn["rect"].center)
            screen.blit(text, text_rect)

    def handle_event(self, event):
        """마우스 클릭 처리 (필요 시)"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                if btn["rect"].collidepoint(pos):
                    print(f"'{btn['label']}' 버튼 클릭됨")

# -----------------------------------------------------
# ScreenBase
# -----------------------------------------------------
class ScreenBase:
    def __init__(self, name, ui_manager):
        self.name = name
        self.ui_manager = ui_manager
        self.buttons = []

    def draw(self, screen, mouse_pos):
        pass

    def handle_click(self, pos):
        for b in self.buttons:
            if b.check_click(pos):
                b.action()
                self.ui_manager.logger.log(self.ui_manager.depth_path, b.text, pos, len(self.ui_manager.depth_path))
                return True
        return False

# -----------------------------------------------------
# HomeScreen
# -----------------------------------------------------
class HomeScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Home", ui_manager)
        items = ["Navigation", "Media", "Setting"]
        for i, item in enumerate(items):
            rect = (20, 120 + i * 70, 200, 50)
            self.buttons.append(Button(item, rect, lambda i=item: ui_manager.open_screen(i)))

    def draw(self, screen, mouse_pos):
        for b in self.buttons:
            b.draw(screen, mouse_pos)
        txt = font.render("Home Screen", True, COLOR_TEXT)
        screen.blit(txt, (300, 150))

# -----------------------------------------------------
# MediaScreen
# -----------------------------------------------------
class MediaScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Media", ui_manager)
        self.buttons.append(Button("Radio", (300, 200, 150, 50), lambda: print("Radio clicked")))
        self.buttons.append(Button("Bluetooth", (300, 300, 150, 50), lambda: print("Bluetooth clicked")))

    def draw(self, screen, mouse_pos):
        txt = font.render("Media Screen", True, COLOR_TEXT)
        screen.blit(txt, (400, 150))
        for b in self.buttons:
            b.draw(screen, mouse_pos)

# -----------------------------------------------------
# SettingScreen
# -----------------------------------------------------
class SettingScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Setting", ui_manager)
        self.buttons.append(Button("Lighting", (300, 200, 150, 50), lambda: print("Lighting clicked")))
        self.buttons.append(Button("Mode", (300, 300, 150, 50), lambda: print("Mode clicked")))

    def draw(self, screen, mouse_pos):
        txt = font.render("Setting Screen", True, COLOR_TEXT)
        screen.blit(txt, (400, 150))
        for b in self.buttons:
            b.draw(screen, mouse_pos)

# -----------------------------------------------------
# NavigationScreen
# -----------------------------------------------------
class NavigationScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Navigation", ui_manager)
        self.buttons.append(Button("Destination", (20, 120, 200, 50), lambda: ui_manager.open_screen("Destination")))

    def draw(self, screen, mouse_pos):
        pygame.draw.rect(screen, (70, 100, 140), (300, 100, 800, 500), border_radius=10)
        txt = font.render("Navigation Map (Demo)", True, COLOR_TEXT)
        screen.blit(txt, (350, 120))
        for b in self.buttons:
            b.draw(screen, mouse_pos)

# -----------------------------------------------------
# DestinationScreen (QWERTY + Enter + Voice)
# -----------------------------------------------------
class DestinationScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Destination", ui_manager)
        self.input_text = ""
        self.voice_active = False

        rows = [
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
        ]

        start_x = 300
        start_y = 300
        key_w, key_h = 60, 60
        key_gap = 10

        for row_idx, row_keys in enumerate(rows):
            for col_idx, key in enumerate(row_keys):
                x = start_x + col_idx * (key_w + key_gap)
                y = start_y + row_idx * (key_h + key_gap)
                self.buttons.append(Button(key, (x, y, key_w, key_h), lambda k=key: self.add_char(k)))

        # Space / Back / Voice / Enter
        self.buttons.append(Button("Space", (start_x, start_y + 3*(key_h+key_gap), 300, key_h), lambda: self.add_char(" ")))
        self.buttons.append(Button("Back", (start_x + 320, start_y + 3*(key_h+key_gap), 100, key_h), self.backspace))
        self.buttons.append(Button("Voice", (start_x + 440, start_y + 3*(key_h+key_gap), 150, key_h), self.toggle_voice))
        self.buttons.append(Button("Enter", (start_x + 600, start_y + 3*(key_h+key_gap), 100, key_h), self.enter_pressed))

    def add_char(self, char):
        self.input_text += char

    def backspace(self):
        self.input_text = self.input_text[:-1]

    def toggle_voice(self):
        self.voice_active = not self.voice_active

    def enter_pressed(self):
        print("Input Entered:", self.input_text)
        self.ui_manager.logger.log(self.ui_manager.depth_path, "Enter", (0,0), len(self.ui_manager.depth_path))
        self.input_text = ""

    def draw(self, screen, mouse_pos):
        # 입력창
        pygame.draw.rect(screen, (60, 60, 90), (300, 200, 600, 60), border_radius=8)
        input_surface = font.render(self.input_text, True, COLOR_TEXT)
        screen.blit(input_surface, (310, 210))

        # 음성 상태 표시
        voice_status = "ON" if self.voice_active else "OFF"
        screen.blit(small_font.render(f"Voice: {voice_status}", True, COLOR_TEXT), (920, 220))

        # 버튼 그리기 (키보드 + Space/Back/Voice/Enter)
        for b in self.buttons:
            b.draw(screen, mouse_pos)

        voice_status = "ON" if self.voice_active else "OFF"
        screen.blit(small_font.render(f"Voice: {voice_status}", True, COLOR_TEXT), (920, 220))
        for b in self.buttons:
            b.draw(screen, mouse_pos)

# -----------------------------------------------------
# UIModel: 모든 화면 + UI 요소 통합
# -----------------------------------------------------
class UIModel:
    def __init__(self):
        self.logger = Logger(LOG_FILE)
        self.depth_path = ["Home"]
        self.width = WIDTH
        self.height = HEIGHT
        self.margin = 10
        # 화면 객체 생성
        self.screens = {
            "Home": HomeScreen(self),
            "Navigation": NavigationScreen(self),
            "Destination": DestinationScreen(self),
            "Media": MediaScreen(self),
            "Setting": SettingScreen(self),
        }
        self.current_screen = self.screens["Home"]
        # UI 요소
        self.top_bar = TopBar(WIDTH, 30, self)
        self.side_menu = SideMenu(250, 30, 60)
        self.bottom_bar = BottomBar(WIDTH, 30, self)
        
        btn_w, btn_h = 60, 25
        self.back_button = Button("Back", (WIDTH - btn_w - self.margin, self.margin, btn_w, btn_h), self.go_back)


    def open_screen(self, name):
        if name in self.screens:
            self.depth_path.append(name)
            self.current_screen = self.screens[name]

    def go_back(self):
        if len(self.depth_path) > 1:
            self.depth_path.pop()
            self.current_screen = self.screens[self.depth_path[-1]]

    def run(self):
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("UI Prototype")
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()
            screen.fill(COLORS["MAIN"])

            # UI 요소 그리기
            self.top_bar.draw(screen)
            self.side_menu.draw(screen)
            self.bottom_bar.draw(screen)
            self.back_button.draw(screen, mouse_pos)
            self.current_screen.draw(screen, mouse_pos)

            # 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.check_click(event.pos):
                        self.go_back()
                        self.logger.log(self.depth_path, "Back", event.pos, len(self.depth_path))
                    else:
                        self.current_screen.handle_click(event.pos)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

# -----------------------------------------------------
# main
# -----------------------------------------------------
def main():
    ui_model = UIModel()
    ui_model.run()

if __name__ == "__main__":
    main()