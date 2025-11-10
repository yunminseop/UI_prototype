import pygame
from utils.UI_elements import Button
from config_loader import load_config, init_from_config

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

class HomeScreen(ScreenBase):
    def __init__(self, ui_manager, font, colors):
        super().__init__("Home", ui_manager)
        items = ["Navigation", "Radio", "Music", "Setting"]
        for i, item in enumerate(items):
            rect = (20, 120 + i * 70, 200, 50)
            self.buttons.append(Button(item, rect, lambda i=item: ui_manager.open_screen(i), font, colors))

    def draw(self, screen, mouse_pos):
        for b in self.buttons:
            b.draw(screen, mouse_pos)
        txt = self.ui_manager.font.render("Home Screen", True, self.ui_manager.colors["TEXT"])
        screen.blit(txt, (300, 150))

# -----------------------------------------------------
# RadioScreen
# -----------------------------------------------------
class RadioScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Radio", ui_manager)
        self.buttons.append(Button("Radio", (300, 200, 150, 50), lambda: print("Radio clicked"), ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("Select Channel", (300, 300, 150, 50), lambda: ui_manager.open_screen("Select Channel"), ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("<(Prev)", (500, 400, 50, 50), lambda: print("Previous Channel"), ui_manager.font, ui_manager.colors))
        self.buttons.append(Button(">(Next)", (600, 400, 50, 50), lambda: print("Next Channel"), ui_manager.font, ui_manager.colors))

    def draw(self, screen, mouse_pos):
        txt = font.render("Radio Screen", True, COLOR_TEXT)
        screen.blit(txt, (400, 150))
        for b in self.buttons:
            b.draw(screen, mouse_pos)

# -----------------------------------------------------
# RadioSelectChannelScreen
# -----------------------------------------------------
class RadioSelectChannelScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Select Channel", ui_manager)

        # 채널 목록
        self.channel_list = [
            "FM 89.1 MHz - KBS CoolFM",
            "FM 91.9 MHz - MBC FM4U",
            "FM 93.1 MHz - KBS 제1라디오",
            "FM 93.9 MHz - CBS 음악FM",
            "FM 94.5 MHz - YTN 뉴스FM",
            "FM 95.1 MHz - TBS 교통FM",
            "FM 95.9 MHz - MBC 표준FM",
            "FM 101.9 MHz - BBS 불교FM",
            "FM 103.5 MHz - SBS 러브FM",
            "FM 104.5 MHz - EBS FM",
            "FM 104.9 MHz - KBS 제3라디오",
            "FM 105.3 MHz - 가톨릭평화방송",
            "FM 107.7 MHz - SBS 파워FM",
        ]

        # 버튼 생성
        self.buttons = []
        self.button_height = 50
        self.spacing = 10

        self.list_left = 300
        self.list_top = 200
        self.list_width = 300
        self.list_view_h = HEIGHT - 250  # 보이는 영역 높이

        y = self.list_top
        for ch in self.channel_list:
            self.buttons.append(
                Button(ch, (self.list_left, y, self.list_width, self.button_height),
                       lambda c=ch: print(f"선택: {c}"), ui_manager.font, ui_manager.colors)
            )
            y += self.button_height + self.spacing

        # 스크롤 관련
        self.scroll_offset = 0
        self.content_height = len(self.buttons) * (self.button_height + self.spacing)
        self.content_height -= self.spacing  # 마지막 간격 보정

        # 스크롤바 영역(트랙)
        self.scrollbar_rect = pygame.Rect(self.list_left + self.list_width + 20,
                                          self.list_top,
                                          12,
                                          self.list_view_h)

        # 핸들 높이: 콘텐츠 길이에 비례 (최소 30)
        if self.content_height <= self.list_view_h:
            self.handle_height = self.scrollbar_rect.height  # 스크롤 필요 없음
        else:
            self.handle_height = max(30, int(self.scrollbar_rect.height * (self.list_view_h / self.content_height)))

        # 핸들 초기 위치
        self.handle_rect = pygame.Rect(self.scrollbar_rect.x,
                                       self.scrollbar_rect.y,
                                       self.scrollbar_rect.width,
                                       self.handle_height)

        # 드래그 상태
        self.is_dragging = False
        self.drag_offset_y = 0

    def draw(self, screen, mouse_pos):
        title = font.render("Select Channel Screen", True, COLOR_TEXT)
        screen.blit(title, (self.list_left, self.list_top - 40))

        # 리스트 영역의 클리핑(선택 사항) – 성능/미관용
        clip_rect = pygame.Rect(self.list_left, self.list_top, self.list_width, self.list_view_h)
        prev_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        # 버튼 그리기 (offset 적용)
        for btn in self.buttons:
            draw_rect = btn.rect.move(0, self.scroll_offset)
            if (self.list_top - self.button_height) < draw_rect.bottom and draw_rect.top < (self.list_top + self.list_view_h):
                # 임시로 위치 바꿔 그리기
                old = btn.rect
                btn.rect = draw_rect
                btn.draw(screen, mouse_pos)
                btn.rect = old

        screen.set_clip(prev_clip)

        # 스크롤바 (트랙 & 핸들)
        pygame.draw.rect(screen, (200, 200, 200), self.scrollbar_rect, border_radius=4)
        pygame.draw.rect(screen, (100, 100, 100), self.handle_rect, border_radius=4)

    def handle_click(self, pos):
        # offset을 고려한 충돌 체크
        if self.content_height <= self.list_view_h:
            # 스크롤 필요 없으면 평소대로
            for btn in self.buttons:
                if btn.check_click(pos):
                    if callable(btn.action):
                        btn.action()
            return

        # 스크롤 적용 클릭
        for btn in self.buttons:
            rect = btn.rect.move(0, self.scroll_offset)
            if rect.collidepoint(pos):
                if callable(btn.action):
                    btn.action()

    def handle_event(self, event):
        # 스크롤 필요 없는 경우 핸들 드래그 무시
        scrollable = self.content_height > self.list_view_h

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if scrollable and self.handle_rect.collidepoint(event.pos):
                self.is_dragging = True
                self.drag_offset_y = event.pos[1] - self.handle_rect.y

            # 트랙 클릭 시, 핸들을 해당 위치로 점프(페이지 점프)
            elif scrollable and self.scrollbar_rect.collidepoint(event.pos):
                # 중앙 정렬로 점프
                new_y = event.pos[1] - self.handle_height // 2
                new_y = max(self.scrollbar_rect.top,
                            min(new_y, self.scrollbar_rect.bottom - self.handle_height))
                self.handle_rect.y = new_y
                self._sync_offset_from_handle()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            new_y = event.pos[1] - self.drag_offset_y
            new_y = max(self.scrollbar_rect.top,
                        min(new_y, self.scrollbar_rect.bottom - self.handle_height))
            self.handle_rect.y = new_y
            self._sync_offset_from_handle()

    # 핸들 위치 ↔ 컨텐츠 오프셋 동기화
    def _sync_offset_from_handle(self):
        # 핸들의 상대 위치(0~1)
        track_range = self.scrollbar_rect.height - self.handle_height
        if track_range <= 0:
            ratio = 0.0
        else:
            ratio = (self.handle_rect.y - self.scrollbar_rect.top) / track_range

        scroll_range = self.content_height - self.list_view_h
        self.scroll_offset = -int(ratio * scroll_range)

    def _sync_handle_from_offset(self):
        scroll_range = max(1, self.content_height - self.list_view_h)
        ratio = -self.scroll_offset / scroll_range
        track_range = self.scrollbar_rect.height - self.handle_height
        self.handle_rect.y = int(self.scrollbar_rect.top + ratio * track_range)



# -----------------------------------------------------
# MusicScreen
# -----------------------------------------------------
class MusicScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Music", ui_manager)
        self.buttons.append(Button("Music", (300, 200, 150, 50), lambda: print("Music clicked"), ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("Bluetooth", (300, 300, 150, 50), lambda: print("Bluetooth clicked"), ui_manager.font, ui_manager.colors))

    def draw(self, screen, mouse_pos):
        txt = font.render("Music Screen", True, COLOR_TEXT)
        screen.blit(txt, (400, 150))
        for b in self.buttons:
            b.draw(screen, mouse_pos)

# -----------------------------------------------------
# SettingScreen
# -----------------------------------------------------
class SettingScreen(ScreenBase):
    def __init__(self, ui_manager):
        super().__init__("Setting", ui_manager)
        self.buttons.append(Button("Lighting", (300, 200, 150, 50), lambda: print("Lighting clicked"), ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("Mode", (300, 300, 150, 50), lambda: print("Mode clicked"), ui_manager.font, ui_manager.colors))

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
        self.buttons.append(Button("Destination", (20, 120, 200, 50), lambda: ui_manager.open_screen("Destination"), ui_manager.font, ui_manager.colors))

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
                self.buttons.append(Button(key, (x, y, key_w, key_h), lambda k=key: self.add_char(k), ui_manager.font, ui_manager.colors))

        # Space / Back / Voice / Enter
        self.buttons.append(Button("Space", (start_x, start_y + 3*(key_h+key_gap), 300, key_h), lambda: self.add_char(" "), ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("Back", (start_x + 320, start_y + 3*(key_h+key_gap), 100, key_h), self.backspace, ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("Voice", (start_x + 440, start_y + 3*(key_h+key_gap), 150, key_h), self.toggle_voice, ui_manager.font, ui_manager.colors))
        self.buttons.append(Button("Enter", (start_x + 600, start_y + 3*(key_h+key_gap), 100, key_h), self.enter_pressed, ui_manager.font, ui_manager.colors))

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