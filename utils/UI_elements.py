import pygame
import csv
from datetime import datetime

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

class Button:
    def __init__(self, text, rect, action, font, colors):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.action = action
        self.font = font
        self.colors = colors

    def draw(self, surface, mouse_pos):
        color = self.colors["BUTTON_HOVER"] if self.rect.collidepoint(mouse_pos) else self.colors["BUTTON"]
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, self.colors["TEXT"])
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

class TopBar:
    def __init__(self, width, height, colors, font, tiny_font, ui_manager):
        self.width = width
        self.height = height
        self.colors = colors
        self.font = font
        self.tiny_font = tiny_font
        self.ui_manager = ui_manager

    def draw(self, screen):
        pygame.draw.rect(screen, self.colors["TOP"], (0, 0, self.width, self.height))
        screen.blit(self.font.render("Prototype", True, self.colors["TEXT"]), (3, 3))
        path_text = " / ".join(self.ui_manager.depth_path)
        screen.blit(self.tiny_font.render(path_text, True, self.colors["TEXT"]), (250, 5))

class SideMenu:
    def __init__(self, width, top_height, bottom_height, colors, height):
        self.width = width
        self.top_height = top_height
        self.bottom_height = bottom_height
        self.colors = colors
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, self.colors["LEFT"],
                         (0, self.top_height, self.width, self.height - self.top_height - self.bottom_height))

class BottomBar:
    def __init__(self, width, height, ui_manager, colors, small_font):
        self.width = width
        self.height = height
        self.ui_manager = ui_manager
        self.colors = colors
        self.small_font = small_font
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        y = self.ui_manager.height - self.height + 5
        x = 10
        gap = 110
        labels = [
            "Seat Temp (-)", "Seat Temp (+)",
            "Heat ray", "Air Cond",
            "Call", "Menu", "Navi",
            "Remove WS Frost", "Remove Rear WS Frost",
            "heat ray (-)", "heat ray (+)"
        ]
        for label in labels:
            rect = pygame.Rect(x, y, 110, self.height - 10)
            self.buttons.append({"label": label, "rect": rect})
            x += gap

    def draw(self, screen):
        y_pos = self.ui_manager.height - self.height
        pygame.draw.rect(screen, self.colors["BOTTOM"], (0, y_pos, self.width, self.height))
        for btn in self.buttons:
            pygame.draw.rect(screen, self.colors["BUTTON"], btn["rect"], border_radius=8)
            text = self.small_font.render(btn["label"], True, self.colors["TEXT"])
            screen.blit(text, text.get_rect(center=btn["rect"].center))
