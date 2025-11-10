# UI_manager.py
import pygame, sys, time
from utils import (
    Logger, Button, TopBar, SidePanel, BottomBar,
    HomeScreen, QuickSettingsScreen, ChargingScreen,
    AppsScreen, RadioScreen, MusicScreen, NavigationScreen, 
LightSettingsScreen,DrivingAssistScreen, LockSettingsScreen, SeatPositionScreen,
ClimateScreen, NavigationSettingsScreen, GleoAIScreen, DisplaySettingsScreen,
SecurityScreen,SoundScreen,ProfileScreen,ConvenienceScreen,ConnectivityScreen,
AppsSettingsScreen, GeneralSettingsScreen, VehicleInfoScreen
)

class UIModel:
    def __init__(self, width, height, colors, fonts, log_file):
        self.width, self.height = width, height
        self.colors, self.fonts = colors, fonts
        self.font, self.small_font, self.tiny_font = fonts["main"], fonts["small"], fonts["tiny"]

        # 상태값(상단바 표시용)
        self.vehicle_state = dict(gear="P", soc=1.0, range_km=408)

        # 공용 구성요소
        self.logger = Logger(log_file)
        self.depth_path = ["Home"]

        self.top = TopBar(width, 36, colors, self.font, self.tiny_font, self)
        self.side = SidePanel(300, 36, 64, colors, height, self)
        self.side.load_image("/mnt/data/IMG_8466.jpeg")  # 없으면 자동 대체그림
        self.bottom = BottomBar(width, 64, self, colors, self.small_font)
        self.back_btn = Button("Back", (width-76, 5, 68, 26), self.go_back, self.small_font, colors)

        # 화면 레지스트리
        self.screens = {
            "Home": HomeScreen(self),
            "Quick Settings": QuickSettingsScreen(self),
            "Charging": ChargingScreen(self),
            "Apps": AppsScreen(self),
            "Radio": RadioScreen(self),
            "Music": MusicScreen(self),
            "Navigation": NavigationScreen(self),
        }
        self.current = self.screens["Home"]

        self.screens.update({
            "Quick Settings": QuickSettingsScreen(self),
            "Light Setting": LightSettingsScreen(self),
            "Assist Setting": DrivingAssistScreen(self),
            "Lock Setting": LockSettingsScreen(self),
            "Seat Position Setting": SeatPositionScreen(self),
            "Climate Setting": ClimateScreen(self),
            "Navigation Setting": NavigationSettingsScreen(self),
            "Gleo AI": GleoAIScreen(self),
            "Display Setting": DisplaySettingsScreen(self),
            "Sec Setting": SecurityScreen(self),
            "Sound Setting": SoundScreen(self),
            "Profile Setting": ProfileScreen(self),
            "Conv Setting": ConvenienceScreen(self),
            "Connectivity Setting": ConnectivityScreen(self),
            "App Setting": AppsSettingsScreen(self),
            "General Setting": GeneralSettingsScreen(self),
            "Vehicle Info": VehicleInfoScreen(self),
        })


    # 네비게이션
    def open_screen(self, name):
    # 1️⃣ 존재하지 않으면 무시
        if name not in self.screens:
            return

        # 2️⃣ 현재 화면과 같으면 이동하지 않음
        if self.depth_path and self.depth_path[-1] == name:
            return

        # 3️⃣ 하단 바에서 'Home' 또는 최상위 메뉴로 진입 시, 상위 경로 초기화
        top_level = {"Quick Settings", "Navigation", "Apps", "Radio", "Music"}
        if name in top_level:
            self.depth_path = ["Home"]  # Home 기준으로 초기화
            self.depth_path.append(name)
        else:
            # 일반적인 경우 (계층 이동)
            self.depth_path.append(name)

        # 4️⃣ 실제 화면 전환
        self.current = self.screens[name]


    def go_back(self):
        if len(self.depth_path) > 1:
            self.depth_path.pop()
            self.current = self.screens[self.depth_path[-1]]

    # 메인 루프
    def run(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("PLEOS-like UI Prototype")
        clock = pygame.time.Clock()
        running = True

        while running:
            mouse = pygame.mouse.get_pos()
            screen.fill(self.colors["MAIN"])

            # draw
            self.top.draw(screen)
            self.side.draw(screen)
            self.bottom.draw(screen)
            self.back_btn.draw(screen, mouse)
            self.current.draw(screen, mouse)

            # events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # 눌림 상태만 반영
                    for b in self.bottom.buttons + [self.back_btn]:
                        if b.check_click(e.pos):
                            b.is_pressed = True

                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    handled = False  # ✅ 클릭이 처리되었는지 추적

                    for b in self.bottom.buttons + [self.back_btn]:
                        if b.is_pressed:
                            b.is_pressed = False
                            if b.check_click(e.pos):
                                handled = True  # ✅ 클릭 처리됨
                                if b == self.back_btn:
                                    self.go_back()
                                    self.logger.log(self.depth_path, "Back", e.pos, len(self.depth_path))
                                else:
                                    if callable(b.action):
                                        b.action()
                                        self.logger.log(self.depth_path, b.text, e.pos, len(self.depth_path))
                            break  # 버튼 클릭 루프 탈출

                    # ✅ Back/하단바 버튼 외에는 현재 화면의 on_click()으로 전달
                    if not handled and hasattr(self.current, "on_click"):
                        self.current.on_click(e.pos)


                # 개별 화면 이벤트(스크롤 등) 필요 시
                if hasattr(self.current, "handle_event"):
                    self.current.handle_event(e)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
