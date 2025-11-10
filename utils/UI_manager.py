import pygame
import sys
from utils.UI_elements import Logger, TopBar, SideMenu, BottomBar, Button
from utils.screens import HomeScreen, RadioScreen, MusicScreen, SettingScreen, NavigationScreen, DestinationScreen, RadioSelectChannelScreen

class UIModel:
    def __init__(self, width, height, colors, fonts, log_file):
        self.width = width
        self.height = height
        self.colors = colors
        self.font = fonts["main"]
        self.small_font = fonts["small"]
        self.tiny_font = fonts["tiny"]

        self.logger = Logger(log_file)
        self.depth_path = ["Home"]

        self.screens = {
            "Home": HomeScreen(self, self.font, self.colors),
            "Navigation": NavigationScreen(self),
            "Destination": DestinationScreen(self),
            "Radio": RadioScreen(self),
            "Music": MusicScreen(self),
            "Setting": SettingScreen(self),
            "Select Channel": RadioSelectChannelScreen(self),
        }
        self.current_screen = self.screens["Home"]

        self.top_bar = TopBar(width, 30, colors, self.font, self.tiny_font, self)
        self.side_menu = SideMenu(250, 30, 60, colors, height)
        self.bottom_bar = BottomBar(width, 30, self, colors, self.small_font)
        self.back_button = Button("Back", (width - 70, 5, 60, 25), self.go_back, self.font, colors)

    def open_screen(self, name):
        if name in self.screens:
            self.depth_path.append(name)
            self.current_screen = self.screens[name]

    def go_back(self):
        if len(self.depth_path) > 1:
            self.depth_path.pop()
            self.current_screen = self.screens[self.depth_path[-1]]

    def run(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("UI Prototype")
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()
            screen.fill(self.colors["MAIN"])

            self.top_bar.draw(screen)
            self.side_menu.draw(screen)
            self.bottom_bar.draw(screen)
            self.back_button.draw(screen, mouse_pos)
            self.current_screen.draw(screen, mouse_pos)

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
