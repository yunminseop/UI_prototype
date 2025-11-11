import pygame
from UI_elements import *

class ScreenBase:
    def __init__(self, name, ui):
        self.name, self.ui = name, ui
        self.buttons = []

    def draw(self, screen, mouse_pos):  # override
        pass

    def on_click(self, pos):  # 기본 버튼 클릭 핸들
        for btn in self.buttons:
            if btn.check_click(pos):
                if callable(btn.action):
                    btn.action()
                self.ui.logger.log(self.ui.depth_path, btn.text, pos, len(self.ui.depth_path))
                return True
        return False

    def handle_event(self, event):  # 필요한 화면만 override
        return

# HOME: 좌-차량 패널, 중/우-탭 플레이스홀더
class HomeScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Home", ui)

    def draw(self, screen, mouse_pos):
        # 가운데/오른쪽 카드
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70, self.ui.width - left_w - 40, self.ui.height - self.ui.bottom.h - 90)
        # 중앙(브라우저 느낌)
        mid = area.copy(); mid.width = int(area.width*0.52)
        right = area.copy(); right.x = mid.right + 12; right.width = area.width - mid.width - 12

        pygame.draw.rect(screen, (235, 238, 243), mid, border_radius=12)
        pygame.draw.rect(screen, (245, 246, 248), right, border_radius=12)

        t1 = self.ui.font.render("Navigation (Demo)", True, self.ui.colors["TEXT"])
        screen.blit(t1, (mid.x+20, mid.y+16))
        t2 = self.ui.font.render("전화/위젯 (Demo)", True, self.ui.colors["TEXT"])
        screen.blit(t2, (right.x+20, right.y+16))

# 1. 차량 설정
class QuickSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Quick Settings", ui)
        self.scroll_offset = 0
        self.menu_rects = []
        self.grid = []
        self.dragging_scrollbar = False
        self.scroll_start_y = 0
        self.scroll_start_offset = 0
        self.hovered_menu = None
        self._build_tiles()

        # --- 기존 상태 변수들 그대로 유지 ---
        self.status = {...}
        self.state_labels = {...}
        self.light_modes = ["Off", "Auto", "미등", "전조등"]
        self.wiper_modes = ["Off", "Auto", "I", "II", "III"]
        self.selected_light = "Auto"
        self.selected_wiper = "Off"

        # 각 기능의 상태 (True=활성화)
        self.status = {
            "도어 잠금": False,
            "창문": False,
            "창문 잠금": False,
            "어린이 보호 잠금": False,
            "글로브박스": False,
            "프렁크": False,
            "트렁크": False,
            "선루프": False,
            "사이드미러": False,
            "충전구": False,
        }

        # 각 기능별 상태 명칭
        self.state_labels = {
            "도어 잠금": ("설정됨", "해제됨"),
            "창문": ("열림", "닫힘"),
            "창문 잠금": ("설정됨", "해제됨"),
            "어린이 보호 잠금": ("설정됨", "해제됨"),
            "글로브박스": ("열림", "닫힘"),
            "프렁크": ("열림", "닫힘"),
            "트렁크": ("열림", "닫힘"),
            "선루프": ("열림", "닫힘"),
            "사이드미러": ("펴짐", "접힘"),
            "충전구": ("열림", "닫힘"),
        }

        # 하단 선택형 버튼
        self.light_modes = ["Off", "Auto", "미등", "전조등"]
        self.wiper_modes = ["Off", "Auto", "I", "II", "III"]
        self.selected_light = "Auto"
        self.selected_wiper = "Off"

    def _build_tiles(self):
        # 좌측 카테고리
        self.left_menu = [
            ("빠른 설정", "Quick Settings"),
            ("라이트", "Light Setting"),
            ("주행 보조", "Assist Setting"),
            ("잠금", "Lock Setting"),
            ("시트 포지션", "Seat Position Setting"),
            ("공조", "Climate Setting"),
            ("충전", "Charging"),
            ("내비게이션", "Navigation Setting"),
            ("Gleo AI", "Gleo AI"),
            ("화면", "Display Setting"),
            ("보안", "Sec Setting"),
            ("사운드", "Sound Setting"),
            ("프로필", "Profile Setting"),
            ("편의 기능", "Conv Setting"),
            ("연결", "Connectivity Setting"),
            ("앱", "App Setting"),
            ("일반 설정", "General Setting"),
            ("차량 정보", "Vehicle Info"),
        ]

        # 좌측 메뉴 rect 구성
        self.menu_rects = []
        left_x = self.ui.side.width + 20
        y = 70
        for name, goto in self.left_menu:
            rect = pygame.Rect(left_x, y, 190, 40)
            self.menu_rects.append((rect, name, goto))
            y += 44

        # 우측 타일
        self.grid = []
        gx, gy = left_x + 210, 70
        w, h, gap = 170, 70, 12
        labels = [
            "도어 잠금", "창문", "창문 잠금", "어린이 보호 잠금",
            "글로브박스", "프렁크", "트렁크", "선루프",
            "사이드미러", "충전구"
        ]
        i = 0
        for r in range(3):
            for c in range(4):
                if i >= len(labels):
                    break
                rect = pygame.Rect(gx + c * (w + gap), gy + r * (h + gap), w, h)
                self.grid.append((rect, labels[i]))
                i += 1

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset += event.y * 20
            max_scroll = max(0, (len(self.left_menu) * 44) - (self.ui.height - 200))
            self.scroll_offset = max(-max_scroll, min(0, self.scroll_offset))

        # --- 스크롤바 클릭 & 드래그 ---
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, "scrollbar_rect") and self.scrollbar_rect.collidepoint(event.pos):
                self.dragging_scrollbar = True
                self.scroll_start_y = event.pos[1]
                self.scroll_start_offset = self.scroll_offset

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_scrollbar = False

        elif event.type == pygame.MOUSEMOTION:
            # Hover 감지
            self.hovered_menu = None
            for rect, name, goto in self.menu_rects:
                moved = rect.move(0, self.scroll_offset)
                if moved.collidepoint(event.pos):
                    self.hovered_menu = name
                    break

            # 스크롤바 드래그 중
            if self.dragging_scrollbar:
                total_h = len(self.menu_rects) * 44
                visible_h = self.ui.height - self.ui.bottom.h - 160
                if total_h > visible_h:
                    max_scroll = total_h - visible_h
                    scroll_ratio = (event.pos[1] - self.scroll_start_y) / visible_h
                    new_offset = self.scroll_start_offset - scroll_ratio * max_scroll
                    self.scroll_offset = max(-max_scroll, min(0, new_offset))

    def draw(self, screen, mouse_pos):
            left_w = self.ui.side.width
            panel = pygame.Rect(left_w + 20, 70,
                                self.ui.width - left_w - 40,
                                self.ui.height - self.ui.bottom.h - 90)
            pygame.draw.rect(screen, (250, 250, 250), panel, border_radius=14)

            # === (1) 좌측 메뉴 ===
            for rect, name, goto in self.menu_rects:
                moved_rect = rect.move(0, self.scroll_offset)
                if moved_rect.bottom < panel.top or moved_rect.top > panel.bottom:
                    continue
                # hover 색상 적용
                if name == self.hovered_menu:
                    color = (210, 210, 210)
                else:
                    color = (235, 235, 235)
                pygame.draw.rect(screen, color, moved_rect, border_radius=10)
                t = self.ui.small_font.render(name, True, (30, 30, 30))
                screen.blit(t, t.get_rect(center=moved_rect.center))

            # === (2) 스크롤바 ===
            total_h = len(self.menu_rects) * 44
            visible_h = panel.height
            if total_h > visible_h:
                scrollbar_h = visible_h * (visible_h / total_h)
                max_scroll = total_h - visible_h
                scroll_ratio = -self.scroll_offset / max_scroll if max_scroll > 0 else 0
                scrollbar_y = panel.y + scroll_ratio * (visible_h - scrollbar_h)
                self.scrollbar_rect = pygame.Rect(panel.x + 192, scrollbar_y, 6, scrollbar_h)
                pygame.draw.rect(screen, (160, 160, 160), self.scrollbar_rect, border_radius=3)
            
            # 우측 타일
            for rect, label in self.grid:
                active = self.status[label]
                color = (150, 255, 150) if active else (230, 230, 230)
                pygame.draw.rect(screen, color, rect, border_radius=12)
                s = self.ui.small_font.render(label, True, (40, 40, 40))
                screen.blit(s, (rect.x + 16, rect.y + 10))
                # 상태 텍스트
                state = self.state_labels[label][0 if active else 1]
                stxt = self.ui.tiny_font.render(state, True, (60, 60, 60))
                screen.blit(stxt, (rect.x + 16, rect.y + 40))

            # 하단: 라이트 모드 버튼
            y0 = panel.bottom - 120
            x0 = left_w + 250
            self.light_rects = []
            for i, name in enumerate(self.light_modes):
                r = pygame.Rect(x0 + i * 90, y0, 80, 36)
                color = (150, 255, 150) if name == self.selected_light else (230, 230, 230)
                pygame.draw.rect(screen, color, r, border_radius=10)
                t = self.ui.tiny_font.render(name, True, (30, 30, 30))
                screen.blit(t, t.get_rect(center=r.center))
                self.light_rects.append((name, r))

            # 하단: 와이퍼 모드 버튼
            y0 += 60
            self.wiper_rects = []
            for i, name in enumerate(self.wiper_modes):
                r = pygame.Rect(x0 + i * 90, y0, 80, 36)
                color = (150, 255, 150) if name == self.selected_wiper else (230, 230, 230)
                pygame.draw.rect(screen, color, r, border_radius=10)
                t = self.ui.tiny_font.render(name, True, (30, 30, 30))
                screen.blit(t, t.get_rect(center=r.center))
                self.wiper_rects.append((name, r))

    def on_click(self, pos):
        # 좌측 메뉴 클릭
        for rect, name, goto in self.menu_rects:
            moved_rect = rect.move(0, self.scroll_offset)
            if moved_rect.collidepoint(pos):
                if goto:
                    # 화면 전환 먼저 → depth_path가 최신 상태로 반영됨
                    self.ui.open_screen(goto)
                # 화면 이동 완료 후 로그 기록
                self.ui.logger.log(self.ui.depth_path, name, pos, len(self.ui.depth_path))
                return True

        # 타일 클릭 (활성화/비활성 전환)
        for rect, label in self.grid:
            if rect.collidepoint(pos):
                self.status[label] = not self.status[label]
                state = self.state_labels[label][0 if self.status[label] else 1]
                self.ui.logger.log(self.ui.depth_path, f"{label}: {state}", pos, len(self.ui.depth_path))
                return True

        # 라이트 버튼 클릭
        for name, r in self.light_rects:
            if r.collidepoint(pos):
                self.selected_light = name
                self.ui.logger.log(self.ui.depth_path, f"라이트: {name}", pos, len(self.ui.depth_path))
                return True

        # 와이퍼 버튼 클릭
        for name, r in self.wiper_rects:
            if r.collidepoint(pos):
                self.selected_wiper = name
                self.ui.logger.log(self.ui.depth_path, f"와이퍼: {name}", pos, len(self.ui.depth_path))
                return True

        return False


# 2. 라이트
class LightSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Light Setting", ui)
        self.ui = ui

        # 상태 변수
        self.light_modes = ["Off", "Auto", "미등", "전조등"]
        self.selected_mode = "Auto"

        # 토글 상태
        self.steering_button_light = False
        self.auto_turn_signal = False
        self.auto_hazard = False

        # 슬라이더 값 (0~1.0)
        self.sliders = {"실내등 밝기": 0.5, "무드조명": 0.5}
        self.slider_rects = {}
        self.knob_rects = {}
        self.dragging_slider = None

        self.mode_buttons = []
        self.toggles = {}

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(
            left_w + 20, 70,
            self.ui.width - left_w - 40,
            self.ui.height - self.ui.bottom.h - 90
        )
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # === 대제목 ===
        title = self.ui.font.render("라이트", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        # === 상단 버튼 그룹 ===
        base_x, base_y = area.x + 20, area.y + 60
        w, h, gap = 100, 46, 10
        self.mode_buttons.clear()

        for i, mode in enumerate(self.light_modes):
            rect = pygame.Rect(base_x + i * (w + gap), base_y, w, h)
            color = (150, 255, 150) if self.selected_mode == mode else (230, 230, 230)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            txt = self.ui.small_font.render(mode, True, (25, 25, 25))
            screen.blit(txt, txt.get_rect(center=rect.center))
            self.mode_buttons.append((mode, rect))

        # === 운전대 버튼 표시등 토글 ===
        y = base_y + 80
        label = self.ui.small_font.render("운전대 버튼 표시등", True, (30, 30, 30))
        screen.blit(label, (area.x + 20, y))
        toggle_rect = pygame.Rect(area.x + 260, y - 5, 50, 26)
        self.toggles["steering"] = toggle_rect
        color_bg = (150, 255, 150) if self.steering_button_light else (180, 180, 180)
        knob_x = toggle_rect.x + (28 if self.steering_button_light else 2)
        pygame.draw.rect(screen, color_bg, toggle_rect, border_radius=13)
        pygame.draw.circle(screen, (255, 255, 255),
                           (knob_x + 10, toggle_rect.centery), 10)

        # === 슬라이더들 ===
        y += 70
        self.slider_rects.clear()
        self.knob_rects.clear()

        for name, val in self.sliders.items():
            label = self.ui.small_font.render(name, True, (30, 30, 30))
            screen.blit(label, (area.x + 20, y))
            bar_rect = pygame.Rect(area.x + 160, y + 10, 300, 8)
            self.slider_rects[name] = bar_rect

            # 채움 영역 + 손잡이
            fill_w = int(bar_rect.width * val)
            pygame.draw.rect(screen, (150, 255, 150),
                             (bar_rect.x, bar_rect.y, fill_w, bar_rect.height),
                             border_radius=4)
            pygame.draw.rect(screen, (210, 210, 210),
                             (bar_rect.x + fill_w, bar_rect.y,
                              bar_rect.width - fill_w, bar_rect.height),
                             border_radius=4)
            knob_x = bar_rect.x + fill_w
            knob_y = bar_rect.y + bar_rect.height // 2
            knob_r = 10
            knob_rect = pygame.Rect(knob_x - knob_r, knob_y - knob_r, knob_r * 2, knob_r * 2)
            self.knob_rects[name] = knob_rect
            pygame.draw.circle(screen, (80, 80, 80), knob_rect.center, knob_r)

            percent_text = self.ui.tiny_font.render(f"{int(val * 100)}%", True, (40, 40, 40))
            screen.blit(percent_text, (bar_rect.right + 25, bar_rect.y - 6))
            y += 60

        # === 방향지시등 ===
        y += 10
        subtitle = self.ui.small_font.render("방향지시등", True, (30, 30, 30))
        screen.blit(subtitle, (area.x + 16, y))

        # 자동 방향지시등
        y += 50
        self._draw_toggle(screen, area.x + 20, y, "자동 방향지시등",
                          "turn", self.auto_turn_signal)
        # 자동 비상등
        y += 50
        self._draw_toggle(screen, area.x + 20, y, "자동 비상등",
                          "hazard", self.auto_hazard)

    def _draw_toggle(self, screen, x, y, label_text, key, state):
        """토글 공용 드로잉"""
        label = self.ui.small_font.render(label_text, True, (30, 30, 30))
        screen.blit(label, (x, y))
        toggle_rect = pygame.Rect(x + 240, y - 5, 50, 26)
        self.toggles[key] = toggle_rect
        color_bg = (150, 255, 150) if state else (180, 180, 180)
        knob_x = toggle_rect.x + (28 if state else 2)
        pygame.draw.rect(screen, color_bg, toggle_rect, border_radius=13)
        pygame.draw.circle(screen, (255, 255, 255),
                           (knob_x + 10, toggle_rect.centery), 10)

    # -----------------------------
    # 이벤트
    # -----------------------------
    def on_click(self, pos):
        # 모드 버튼
        for mode, rect in self.mode_buttons:
            if rect.collidepoint(pos):
                self.selected_mode = mode
                self.ui.logger.log(self.ui.depth_path, f"라이트 모드: {mode}",
                                   pos, len(self.ui.depth_path))
                return True

        # 토글 클릭
        for key, rect in self.toggles.items():
            if rect.collidepoint(pos):
                if key == "steering":
                    self.steering_button_light = not self.steering_button_light
                    st = "On" if self.steering_button_light else "Off"
                    self.ui.logger.log(self.ui.depth_path, f"운전대 버튼 표시등: {st}",
                                       pos, len(self.ui.depth_path))
                elif key == "turn":
                    self.auto_turn_signal = not self.auto_turn_signal
                    st = "On" if self.auto_turn_signal else "Off"
                    self.ui.logger.log(self.ui.depth_path, f"자동 방향지시등: {st}",
                                       pos, len(self.ui.depth_path))
                elif key == "hazard":
                    self.auto_hazard = not self.auto_hazard
                    st = "On" if self.auto_hazard else "Off"
                    self.ui.logger.log(self.ui.depth_path, f"자동 비상등: {st}",
                                       pos, len(self.ui.depth_path))
                return True

        # 슬라이더 클릭 시 드래그 시작
        for name, knob_rect in self.knob_rects.items():
            if knob_rect.collidepoint(pos):
                self.dragging_slider = name
                return True
        for name, bar_rect in self.slider_rects.items():
            if bar_rect.collidepoint(pos):
                self.dragging_slider = name
                self._update_slider_value(name, pos[0])
                return True
        return False

    def handle_event(self, event):
        """Display 슬라이더와 동일한 방식: 누르면 드래그 시작, 움직이면 갱신, 떼면 종료+로그"""
        # 안전장치: 아직 레이아웃(슬라이더/노브) 정보가 없다면 무시
        if not self.slider_rects or not self.knob_rects:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 노브를 크게 잡히도록 클릭 영역 약간 키움
            for name, knob_rect in self.knob_rects.items():
                if knob_rect.inflate(10, 10).collidepoint(event.pos):
                    self.dragging_slider = name
                    return

            # 바를 눌러도 즉시 해당 위치로 이동 + 드래그 시작
            for name, bar_rect in self.slider_rects.items():
                if bar_rect.collidepoint(event.pos):
                    self.dragging_slider = name
                    self._update_slider_value(name, event.pos[0])
                    return

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            self._update_slider_value(self.dragging_slider, event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_slider:
                name = self.dragging_slider
                self.dragging_slider = None
                # 드래그 종료 시 한 번만 로그
                self.ui.logger.log(
                    self.ui.depth_path,
                    f"{name}: {self.sliders[name]:.2f}",
                    event.pos, len(self.ui.depth_path)
                )

    def _update_slider_value(self, name, mouse_x):
        """바 좌우 경계 안에서 값(0~1) 갱신"""
        bar = self.slider_rects[name]
        x = max(bar.left, min(mouse_x, bar.right))
        self.sliders[name] = (x - bar.left) / bar.width





# 3. 주행 보조
class DrivingAssistScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Assist Setting", ui)
        self.ui = ui

        # 선택 상태
        self.selected_mode = None
        self.selected_sens = None

        # 버튼 그룹
        self.mode_buttons = []
        self.sens_buttons = []

        self._build_buttons()

    def _build_buttons(self):
        left_w = self.ui.side.width

        # --- 주행 모드 버튼 ---
        modes = ["표준", "에코", "스포츠"]
        base_x, base_y = left_w + 40, 130
        w, h, gap = 120, 50, 10

        for i, name in enumerate(modes):
            rect = (base_x + i * (w + gap), base_y, w, h)
            b = Button(
                text=name,
                rect=rect,
                action=lambda n=name: self._on_mode_click(n),
                font=self.ui.small_font,
                colors=self.ui.colors
            )
            self.mode_buttons.append(b)

        # --- 충돌 경고 민감도 버튼 ---
        sens = ["낮음", "보통", "높음"]
        base_x, base_y = left_w + 40, 300
        w, h, gap = 100, 40, 10

        for i, name in enumerate(sens):
            rect = (base_x + i * (w + gap), base_y, w, h)
            b = Button(
                text=name,
                rect=rect,
                action=lambda n=name: self._on_sens_click(n),
                font=self.ui.small_font,
                colors=self.ui.colors
            )
            self.sens_buttons.append(b)

    # ======================================================
    # 클릭 시 동작
    # ======================================================
    def _on_mode_click(self, mode):
        self.selected_mode = mode
        print(f"Clicked: 주행모드 {mode}")

    def _on_sens_click(self, sens):
        self.selected_sens = sens
        print(f"Clicked: 충돌민감도 {sens}")

    # ======================================================
    # 그리기
    # ======================================================
    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 제목
        title = self.ui.font.render("주행 보조", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 8))

        # --- 주행모드 라벨 ---
        lbl = self.ui.small_font.render("주행 모드", True, (30, 30, 30))
        screen.blit(lbl, (area.x + 20, area.y + 30))

        # --- 주행모드 버튼 ---
        for b in self.mode_buttons:
            color = (150, 255, 150) if b.text == self.selected_mode else (235, 235, 235)
            pygame.draw.rect(screen, color, b.rect, border_radius=10)
            label = self.ui.small_font.render(b.text, True, (30, 30, 30))
            screen.blit(label, label.get_rect(center=b.rect.center))

        # --- 충돌 감도 라벨 ---
        txt = self.ui.small_font.render("충돌 경고 민감도", True, (30, 30, 30))
        screen.blit(txt, (area.x + 20, area.y + 200))

        # --- 충돌민감도 버튼 ---
        for b in self.sens_buttons:
            color = (150, 255, 150) if b.text == self.selected_sens else (235, 235, 235)
            pygame.draw.rect(screen, color, b.rect, border_radius=8)
            label = self.ui.small_font.render(b.text, True, (30, 30, 30))
            screen.blit(label, label.get_rect(center=b.rect.center))

    # ======================================================
    # 클릭 처리
    # ======================================================
    def on_click(self, pos):
        for b in self.mode_buttons + self.sens_buttons:
            if b.check_click(pos):
                b.trigger(self.ui, pos)
                return True
        return False



# 4. 잠금
class LockSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Lock Setting", ui)
        self.ui = ui
        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        # 섹션1: 자동 잠금 해제
        self.unlock_modes = ["운전자 접근", "손잡이 터치"]
        self.selected_unlock = "운전자 접근"
        self.unlock_toggles = {
            "스마트 트렁크": False,
            "웰컴 사이드미러": False,
            "웰컴 라이트": False,
        }

        # 섹션2: 자동 잠금
        self.lock_modes = ["운전자 이탈", "손잡이 터치"]
        self.selected_lock = "운전자 이탈"
        self.lock_toggles = {
            "이탈 시 라이트 끔": False,
        }

        # 라디오 버튼 객체
        self.unlock_radio_btns = []
        self.lock_radio_btns   = []

        # 클릭 감지용 토글 히트박스
        self.toggle_hitboxes = {}

        self._build_buttons()

    def _build_buttons(self):
        # 버튼의 기본 크기만 정해두고, 실제 위치는 draw에서 일괄 배치
        bw, bh = 140, 50
        for name in self.unlock_modes:
            self.unlock_radio_btns.append(
                Button(name, (0, 0, bw, bh),
                       action=lambda n=name: self._select_unlock(n),
                       font=self.small_font, colors=self.colors)
            )
        for name in self.lock_modes:
            self.lock_radio_btns.append(
                Button(name, (0, 0, bw, bh),
                       action=lambda n=name: self._select_lock(n),
                       font=self.small_font, colors=self.colors)
            )

    # 상태 변경 + 로깅
    def _select_unlock(self, name):
        self.selected_unlock = name
        self.ui.logger.log(self.ui.depth_path, f"UnlockMode: {name}", pygame.mouse.get_pos(), len(self.ui.depth_path))

    def _select_lock(self, name):
        self.selected_lock = name
        self.ui.logger.log(self.ui.depth_path, f"LockMode: {name}", pygame.mouse.get_pos(), len(self.ui.depth_path))

    def _toggle_item(self, group, name):
        if group == "unlock":
            self.unlock_toggles[name] = not self.unlock_toggles[name]
            state = "ON" if self.unlock_toggles[name] else "OFF"
        else:
            self.lock_toggles[name] = not self.lock_toggles[name]
            state = "ON" if self.lock_toggles[name] else "OFF"
        self.ui.logger.log(self.ui.depth_path, f"{name}: {state}", pygame.mouse.get_pos(), len(self.ui.depth_path))

    # 토글 스위치 그리기 + 히트박스 기록
    def _draw_toggle(self, screen, label_x, control_x, y, text, active, key):
        # 라벨
        lab = self.small_font.render(text, True, (30, 30, 30))
        screen.blit(lab, (label_x, y))

        # 스위치
        w, h = 56, 30
        rect = pygame.Rect(control_x, y - 3, w, h)
        
        knob_r = h // 2 - 3
        knob_x = rect.left + knob_r + 3 if not active else rect.right - knob_r - 3
        knob_color = (255, 255, 255)
        # pygame.draw.circle(screen, knob_color, (knob_x, rect.centery), knob_r)
        
        # 상태 텍스트
        st = self.small_font.render("ON" if active else "OFF", True, (70, 70, 70))
        screen.blit(st, (rect.right + 10, rect.y + 4))
        if active:
            pygame.draw.rect(screen, (150, 255, 150), rect, border_radius=15)
            pygame.draw.circle(screen, knob_color, (knob_x, rect.centery), knob_r)
        else:
            pygame.draw.rect(screen, (180, 180, 180), rect, border_radius=15)
            pygame.draw.circle(screen, knob_color, (knob_x, rect.centery), knob_r)

        # 클릭용 저장
        self.toggle_hitboxes[key] = rect

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 레이아웃 기준선
        label_x   = area.x + 40           # 왼쪽 라벨 열
        control_x = label_x + 200         # 오른쪽 컨트롤 열
        gap_y     = 52

        # 제목
        screen.blit(self.font.render("잠금 설정", True, (30, 30, 30)), (area.x + 20, area.y + 10))

        y = area.y + 70

        # 섹션 1: 자동 잠금 해제
        screen.blit(self.small_font.render("자동 잠금 해제", True, (30, 30, 30)), (label_x, y))
        y += 34

        # 라디오 행 배치
        bw, bh, rgap = 140, 50, 10
        for i, btn in enumerate(self.unlock_radio_btns):
            btn.rect.update(control_x + i * (bw + rgap), y, bw, bh)
            color = (150, 255, 150) if btn.text == self.selected_unlock else (230, 230, 230)
            pygame.draw.rect(screen, color, btn.rect, border_radius=10)
            t = self.small_font.render(btn.text, True, (255, 255, 255) if btn.text == self.selected_unlock else (40, 40, 40))
            screen.blit(t, t.get_rect(center=btn.rect.center))

        y += bh + 18

        # 토글들
        self.toggle_hitboxes.clear()
        for name in ["스마트 트렁크", "웰컴 사이드미러", "웰컴 라이트"]:
            self._draw_toggle(screen, label_x, control_x, y, name, self.unlock_toggles[name], ("unlock", name))
            y += gap_y

        # 섹션 2: 자동 잠금
        y += 16
        screen.blit(self.small_font.render("자동 잠금", True, (30, 30, 30)), (label_x, y))
        y += 34

        for i, btn in enumerate(self.lock_radio_btns):
            btn.rect.update(control_x + i * (bw + rgap), y, bw, bh)
            color = (150, 255, 150) if btn.text == self.selected_lock else (230, 230, 230)
            pygame.draw.rect(screen, color, btn.rect, border_radius=10)
            t = self.small_font.render(btn.text, True, (255, 255, 255) if btn.text == self.selected_lock else (40, 40, 40))
            screen.blit(t, t.get_rect(center=btn.rect.center))

        y += bh + 18
        # 이탈 시 라이트 끔
        self._draw_toggle(screen, label_x, control_x, y, "이탈 시 라이트 끔",
                          self.lock_toggles["이탈 시 라이트 끔"], ("lock", "이탈 시 라이트 끔"))

    def on_click(self, pos):
        # 라디오
        for btn in self.unlock_radio_btns:
            if btn.check_click(pos):
                btn.action()
                return True
        for btn in self.lock_radio_btns:
            if btn.check_click(pos):
                btn.action()
                return True

        # 토글
        for (group, name), rect in self.toggle_hitboxes.items():
            if rect.collidepoint(pos):
                self._toggle_item(group, name)
                return True
        return False

# 5. 시트 포지션
class SeatPositionScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Seat Position Setting", ui)
        self.ui = ui

        # --- 상단 토글 버튼 ---
        self.easy_access = False  # 초기 상태 Off

        # --- 하단 프리셋 버튼 ---
        self.presets = ["1", "2", "3", "휴식 모드"]
        self.selected_preset = None  # 선택된 프리셋 (없으면 None)

        # 버튼 리스트
        self.toggle_button = None
        self.preset_buttons = []

        self._build_buttons()

    def _build_buttons(self):
        left_w = self.ui.side.width
        base_x, base_y = left_w + 50, 120
        w, h = 180, 50

        # --- Easy Access 토글 버튼 ---
        self.toggle_button = Button(
            text="이지 엑세스",
            rect=(base_x, base_y, w, h),
            action=self._toggle_easy_access,
            font=self.ui.small_font,
            colors=self.ui.colors,
        )

        # --- 프리셋 버튼들 ---
        base_y += 120
        w, h, gap = 100, 60, 20
        x = base_x
        for name in self.presets:
            b = Button(
                text=name,
                rect=(x, base_y, w, h),
                action=lambda n=name: self._select_preset(n),
                font=self.ui.small_font,
                colors=self.ui.colors,
            )
            self.preset_buttons.append(b)
            x += w + gap

    # ======================================================
    # 버튼 동작
    # ======================================================
    def _toggle_easy_access(self):
        self.easy_access = not self.easy_access
        state = "On" if self.easy_access else "Off"
        print(f"Clicked: 이지 엑세스 ({state})")

    def _select_preset(self, name):
        self.selected_preset = name
        print(f"Clicked: 프리셋 {name}")

    # ======================================================
    # 화면 그리기
    # ======================================================
    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 제목
        title = self.ui.font.render("시트 포지션 설정", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        # --- 이지 엑세스 토글 버튼 표시 ---
        toggle_color = (150, 255, 150) if self.easy_access else (230, 230, 230)
        pygame.draw.rect(screen, toggle_color, self.toggle_button.rect, border_radius=10)
        label = self.ui.small_font.render(
            f"이지 엑세스 ({'On' if self.easy_access else 'Off'})", True, (30, 30, 30)
        )
        screen.blit(label, label.get_rect(center=self.toggle_button.rect.center))

        # --- 프리셋 버튼 제목 ---
        label = self.ui.small_font.render("운전석 프리셋", True, (30, 30, 30))
        screen.blit(label, (area.x + 20, area.y + 120))

        # --- 프리셋 버튼들 ---
        for b in self.preset_buttons:
            is_selected = (b.text == self.selected_preset)
            color = (150, 255, 150) if is_selected else (235, 235, 235)
            pygame.draw.rect(screen, color, b.rect, border_radius=10)
            label = self.ui.small_font.render(b.text, True, (30, 30, 30))
            screen.blit(label, label.get_rect(center=b.rect.center))

    # ======================================================
    # 클릭 처리
    # ======================================================
    def on_click(self, pos):
        if self.toggle_button.check_click(pos):
            self.toggle_button.trigger(self.ui, pos)
            return True

        for b in self.preset_buttons:
            if b.check_click(pos):
                b.trigger(self.ui, pos)
                return True

        return False

# 6. 공조
class ClimateScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Climate Setting", ui)
        self.ui = ui

        # 그룹별 기능 (기본 False: Off 상태)
        self.groups = {
            "실내 공기 순환": {
                "워셔액 작동": False,
                "터널 진입": False,
                "공기 질 저하": False
            },
            "공조 편의": {
                "실내 과열 방지": False,
                "에어컨 자동 건조": False,
                "뒷좌석 공조 잠금": False,
                "탑승 전 온도 설정": False
            }
        }

        # 버튼 리스트
        self.toggle_buttons = []
        self._build_buttons()

    # ======================================================
    # 버튼 빌드
    # ======================================================
    def _build_buttons(self):
        left_w = self.ui.side.width
        base_x = left_w + 60
        base_y = 180  
        w, h, gap = 260, 45, 15

        # 그룹 순서대로 버튼 생성
        y = base_y
        for group_name, items in self.groups.items():
            for name in items.keys():
                rect = (base_x, y, w, h)
                b = Button(
                    text=name,
                    rect=rect,
                    action=lambda n=name, g=group_name: self._toggle_item(g, n),
                    font=self.ui.small_font,
                    colors=self.ui.colors
                )
                self.toggle_buttons.append((group_name, b))
                y += h + gap
            y += 40  # 그룹 간 간격

    # ======================================================
    # 클릭 시 상태 토글
    # ======================================================
    def _toggle_item(self, group, name):
        """버튼 클릭 시 On/Off 전환"""
        self.groups[group][name] = not self.groups[group][name]
        state = "On" if self.groups[group][name] else "Off"
        print(f"Clicked: {name} ({state})")

    # ======================================================
    # 화면 그리기
    # ======================================================
    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 60)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 제목
        title = self.ui.font.render("공조 설정", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        # 그룹 제목 표시용
        group_positions = {}  # {group_name: y 좌표}

        # 버튼 그룹별 위치 계산
        for group_name, b in self.toggle_buttons:
            if group_name not in group_positions:
                group_positions[group_name] = b.rect.y - 40

        # 그룹 제목 렌더링
        for group_name, y_pos in group_positions.items():
            label = self.ui.small_font.render(group_name, True, (30, 30, 30))
            screen.blit(label, (area.x + 20, y_pos))

        # 버튼 표시
        for group_name, b in self.toggle_buttons:
            name = b.text
            is_on = self.groups[group_name][name]
            color = (150, 255, 150) if is_on else (230, 230, 230)
            pygame.draw.rect(screen, color, b.rect, border_radius=10)
            label = self.ui.small_font.render(f"{name} ({'On' if is_on else 'Off'})", True, (30, 30, 30))
            screen.blit(label, label.get_rect(center=b.rect.center))

    # ======================================================
    # 클릭 처리
    # ======================================================
    def on_click(self, pos):
        for group_name, b in self.toggle_buttons:
            if b.check_click(pos):
                b.trigger(self.ui, pos)
                return True
        return False


# 7. 충전
class ChargingScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Charging", ui)
        self.ui = ui
        self.amp = 48
        self.display_mode = "km"  # 잔량 표시 단위 ('km' 또는 '%')

    # -------------------------------------------------
    # 동작 함수
    # -------------------------------------------------
    def dec_amp(self):
        self.amp = max(6, self.amp - 2)
        self.ui.logger.log(
            self.ui.depth_path,
            "-2A",
            pygame.mouse.get_pos(),
            len(self.ui.depth_path),
        )

    def inc_amp(self):
        self.amp = min(80, self.amp + 2)
        self.ui.logger.log(
            self.ui.depth_path,
            "+2A",
            pygame.mouse.get_pos(),
            len(self.ui.depth_path),
        )

    def set_mode(self, mode):
        self.display_mode = mode
        self.ui.logger.log(
            self.ui.depth_path,
            f"{mode}",
            pygame.mouse.get_pos(),
            len(self.ui.depth_path),
        )
    # -------------------------------------------------
    # 화면 표시
    # -------------------------------------------------
    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (250, 250, 250), area, border_radius=14)

        # --- 제목 ---
        range_txt = f"{int(self.ui.vehicle_state['range_km'])} km"
        title = self.ui.font.render(range_txt, True, (20, 20, 20))
        screen.blit(title, (area.x + 10, area.y + 10))

        # --- 게이지 ---
        bar = pygame.Rect(area.x + 10, area.y + 60, area.w - 20, 40)
        fill = bar.copy(); fill.width = int(bar.width * 0.9)
        pygame.draw.rect(screen, (150, 255, 150), fill, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), bar, 2, border_radius=10)
        gauge_txt = self.ui.small_font.render("충전 한도: 100%", True, (30, 30, 30))
        screen.blit(gauge_txt, (area.x + 15, area.y + 110))

        # --- 전류 설정 ---
        txt = self.ui.small_font.render("충전 전류", True, (20, 20, 20))
        screen.blit(txt, (area.x + 10, area.y + 160))

        # ✅ 클릭 영역 정의 (draw마다 최신 rect 생성 — 이게 가장 안전함)
        self._minus_rect = pygame.Rect(area.x + 130, area.y + 148, 50, 40)
        self._plus_rect  = pygame.Rect(area.x + 260, area.y + 148, 50, 40)

        pygame.draw.rect(screen, (235, 235, 235), self._minus_rect, border_radius=8)
        pygame.draw.rect(screen, (235, 235, 235), self._plus_rect,  border_radius=8)

        mtxt = self.ui.font.render("-", True, (40, 40, 40))
        ptxt = self.ui.font.render("+", True, (40, 40, 40))
        screen.blit(mtxt, mtxt.get_rect(center=self._minus_rect.center))
        screen.blit(ptxt, ptxt.get_rect(center=self._plus_rect.center))

        cur = self.ui.small_font.render(f"{self.amp}A", True, (20, 20, 20))
        screen.blit(cur, (area.x + 205, area.y + 158))

        # --- 잔량 표시 단위 토글 ---
        mode_label = self.ui.small_font.render("충전 잔량 표시", True, (20, 20, 20))
        screen.blit(mode_label, (area.x + 10, area.y + 230))

        self._km_rect = pygame.Rect(area.x + 150, area.y + 220, 70, 35)
        self._pct_rect = pygame.Rect(area.x + 230, area.y + 220, 70, 35)

        km_color = (150, 255, 150) if self.display_mode == "km" else (235, 235, 235)
        pct_color = (150, 255, 150) if self.display_mode == "%" else (235, 235, 235)

        pygame.draw.rect(screen, km_color, self._km_rect, border_radius=8)
        pygame.draw.rect(screen, pct_color, self._pct_rect, border_radius=8)

        screen.blit(self.ui.small_font.render("km", True, (30, 30, 30)),
                    self.ui.small_font.render("km", True, (30, 30, 30)).get_rect(center=self._km_rect.center))
        screen.blit(self.ui.small_font.render("%", True, (30, 30, 30)),
                    self.ui.small_font.render("%", True, (30, 30, 30)).get_rect(center=self._pct_rect.center))

    # -------------------------------------------------
    # 클릭 처리
    # -------------------------------------------------
    def on_click(self, pos):
        """마우스 클릭 시 버튼 판정"""
        if hasattr(self, "_minus_rect") and self._minus_rect.collidepoint(pos):
            self.dec_amp()
            return True

        if hasattr(self, "_plus_rect") and self._plus_rect.collidepoint(pos):
            self.inc_amp()
            return True

        if hasattr(self, "_km_rect") and self._km_rect.collidepoint(pos):
            self.set_mode("km")
            return True

        if hasattr(self, "_pct_rect") and self._pct_rect.collidepoint(pos):
            self.set_mode("%")
            return True

        return False


# 8. 내비게이션
class NavigationSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Navigation Setting", ui)

        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        # 1️⃣ 토글 상태 (유지됨)
        self.toggle_states = {
            "EV 경로 플래너": False,
            "현대자동차(E-pit)": False,
            "에버온": False,
            "GS차지비": False,
            "파워큐브": False,
            "한국전력공사": False,
            "환경부": False,
            "LG유플러스": False,
            "채비": False,
            "이지차저": False,
            "SK일렉링크": False,
            "플러그링크": False,
            "한국전자금융": False,
            "투루차저": False,
            "스타코프": False,
        }

        # 2️⃣ 버튼 구성
        self._build_buttons()

    # --------------------------------------------------
    def _build_buttons(self):
        """내비게이션 설정 버튼 생성"""
        left_w = self.ui.side.width
        start_x = left_w + 60
        start_y = 120
        bw, bh = 180, 46
        gap_x, gap_y = 18, 18
        x, y = start_x, start_y

        # EV 경로 플래너 (단독)
        self.buttons.append(
            Button("EV 경로 플래너", (x, y, bw, bh),
                   lambda: self.toggle("EV 경로 플래너"),
                   self.small_font, self.colors)
        )

        # 선호 충전소 (토글)
        y += bh + 40
        count = 0
        for label in list(self.toggle_states.keys())[1:]:
            self.buttons.append(
                Button(label, (x, y, bw, bh),
                       lambda t=label: self.toggle(t),
                       self.small_font, self.colors)
            )
            x += bw + gap_x
            count += 1
            if count % 4 == 0:  # 4개씩 줄바꿈
                x = start_x
                y += bh + gap_y

        # 더보기 버튼
        self.buttons.append(
            Button("더보기", (x, y, bw, bh),
                   lambda: print("Clicked: more"),
                   self.small_font, self.colors)
        )

    # --------------------------------------------------
    def toggle(self, name):
        """토글 상태 반전 + 로그 기록"""
        if name in self.toggle_states:
            self.toggle_states[name] = not self.toggle_states[name]
            state = "ON" if self.toggle_states[name] else "OFF"
            # 로그 남기기
            mouse_pos = pygame.mouse.get_pos()
            # self.ui.logger.log(self.ui.depth_path, f"{name} ({state})", mouse_pos, len(self.ui.depth_path))
            # print(f"[NAV] {name}: {state}")

    # --------------------------------------------------
    def draw(self, screen, mouse_pos):
        """화면 표시"""
        left_w = self.ui.side.width
        area = pygame.Rect(
            left_w + 20, 70,
            self.ui.width - left_w - 40,
            self.ui.height - self.ui.bottom.h - 90
        )

        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)
        title = self.font.render("내비게이션 설정", True, (30, 30, 30))
        screen.blit(title, (area.x + 20, area.y + 10))

        # 버튼 (ON/OFF 색상만 변경)
        for btn in self.buttons:
            label = btn.text
            if label in self.toggle_states:
                active = self.toggle_states[label]
                color = (150, 255, 150) if active else (200, 200, 200)
                pygame.draw.rect(screen, color, btn.rect, border_radius=8)
                txt = self.small_font.render(label, True, (20, 20, 20))
                screen.blit(txt, txt.get_rect(center=btn.rect.center))
            else:
                btn.draw(screen, mouse_pos)

        version = self.small_font.render("내비게이션 \r 2.1.2-rc", True, (80, 80, 80))
        screen.blit(version, (area.x + 20, area.bottom - 35))

    # --------------------------------------------------
    def on_click(self, pos):
        """버튼 클릭 처리 (로그 포함)"""
        for btn in self.buttons:
            if btn.check_click(pos):
                btn.action()
                self.ui.logger.log(self.ui.depth_path, btn.text, pos, len(self.ui.depth_path))
                return True
        return False


# 9. GLEO AI
class GleoAIScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Gleo AI", ui)
        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        self.selected_voice = "음성1"
        self.selected_style = "정중함"
        self.call_toggle = False

        self._build_buttons()

    def _build_buttons(self):
        left_w = self.ui.side.width
        base_x = left_w + 40
        base_y = 130
        bw, bh = 110, 45
        gap_x = 15

        # 1️⃣ 음성 버튼
        self.voice_buttons = []
        x = base_x
        for v in ["음성1", "음성2", "음성3", "음성4", "음성5", "음성6"]:
            rect = pygame.Rect(x, base_y + 30, bw, bh)  # ← Y를 +30 내려줌
            self.voice_buttons.append(
                Button(v, rect, lambda val=v: self.select_voice(val),
                       self.small_font, self.colors)
            )
            x += bw + gap_x

        # 2️⃣ 대화 스타일 버튼
        self.style_buttons = []
        sx = base_x
        style_y = base_y + 130  # ← 확실히 아래로 떨어뜨림
        for s in ["정중함", "친근함"]:
            rect = pygame.Rect(sx, style_y + 30, 120, bh)
            self.style_buttons.append(
                Button(s, rect, lambda val=s: self.select_style(val),
                       self.small_font, self.colors)
            )
            sx += 140

        # 3️⃣ 호출 토글
        self.call_toggle_rect = pygame.Rect(base_x + 110, style_y + 130, 60, 30)

    def select_voice(self, voice):
        self.selected_voice = voice
        self.ui.logger.log(self.ui.depth_path, f"Voice: {voice}",
                           pygame.mouse.get_pos(), len(self.ui.depth_path))

    def select_style(self, style):
        self.selected_style = style
        self.ui.logger.log(self.ui.depth_path, f"Style: {style}",
                           pygame.mouse.get_pos(), len(self.ui.depth_path))

    def toggle_call(self):
        self.call_toggle = not self.call_toggle
        state = "ON" if self.call_toggle else "OFF"
        self.ui.logger.log(self.ui.depth_path, f"CallTrigger: {state}",
                           pygame.mouse.get_pos(), len(self.ui.depth_path))

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 제목
        screen.blit(self.font.render("Gleo AI", True, (30, 30, 30)), (area.x + 20, area.y + 10))

        # === 음성 유형 ===
        label_voice_y = self.voice_buttons[0].rect.y - 28  # ← 버튼보다 위쪽
        screen.blit(self.small_font.render("음성 유형", True, (30, 30, 30)),
                    (area.x + 20, label_voice_y))
        for btn in self.voice_buttons:
            color = (150, 255, 150) if btn.text == self.selected_voice else (220, 220, 220)
            pygame.draw.rect(screen, color, btn.rect, border_radius=8)
            screen.blit(self.small_font.render(btn.text, True, (25, 25, 25)),
                        self.small_font.render(btn.text, True, (25, 25, 25)).get_rect(center=btn.rect.center))

        # === 대화 스타일 ===
        label_style_y = self.style_buttons[0].rect.y - 28
        screen.blit(self.small_font.render("대화 스타일", True, (30, 30, 30)),
                    (area.x + 20, label_style_y))
        for btn in self.style_buttons:
            color = (150, 255, 150) if btn.text == self.selected_style else (220, 220, 220)
            pygame.draw.rect(screen, color, btn.rect, border_radius=8)
            screen.blit(self.small_font.render(btn.text, True, (25, 25, 25)),
                        self.small_font.render(btn.text, True, (25, 25, 25)).get_rect(center=btn.rect.center))

        # === 호출 방법 ===
        label_call_y = self.call_toggle_rect.y - 30
        screen.blit(self.small_font.render("호출 방법", True, (30, 30, 30)),
                    (area.x + 20, label_call_y))

        # 토글
        toggle_rect = self.call_toggle_rect
        knob_radius = toggle_rect.height // 2 - 2
        knob_x = toggle_rect.left + knob_radius + 2 if not self.call_toggle else toggle_rect.right - knob_radius - 2
        knob_color = (255, 255, 255)

        if self.call_toggle:
            pygame.draw.rect(screen, (150, 255, 150), toggle_rect, border_radius=15)
            pygame.draw.circle(screen, knob_color, (knob_x, toggle_rect.centery), knob_radius)
        else:
            pygame.draw.rect(screen, (180, 180, 180), toggle_rect, border_radius=15)
            pygame.draw.circle(screen, knob_color, (knob_x, toggle_rect.centery), knob_radius)

        # 오른쪽 텍스트
        screen.blit(self.small_font.render("'글레오'라고 부르기", True, (40, 40, 40)),
                    (toggle_rect.right + 10, toggle_rect.y + 4))

    def on_click(self, pos):
        for btn in self.voice_buttons + self.style_buttons:
            if btn.check_click(pos):
                btn.action()
                return True
        if self.call_toggle_rect.collidepoint(pos):
            self.toggle_call()
            return True
        return False

# 10. 화면
class DisplaySettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Display Setting", ui)

        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        self.themes = ["라이트", "다크"]
        self.selected_theme = "라이트"

        self.brightness = 0.5
        self.dragging_slider = False
        self.slider_rect = None
        self.knob_rect = None

        # 테마 버튼 영역 정의
        self.theme_buttons = []
        self._build_buttons()

    def _build_buttons(self):
        left_w = self.ui.side.width
        base_x = left_w + 40
        base_y = 130
        bw, bh = 140, 70
        gap = 20
        x = base_x

        for t in self.themes:
            rect = pygame.Rect(x, base_y, bw, bh)
            self.theme_buttons.append((t, rect))
            x += bw + gap

    def select_theme(self, name):
        self.selected_theme = name
        self.ui.logger.log(self.ui.depth_path, f"Theme: {name}",
                           pygame.mouse.get_pos(), len(self.ui.depth_path))
        print(f"Clicked: {name}")

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        title = self.font.render("화면 설정", True, (30, 30, 30))
        screen.blit(title, (area.x + 20, area.y + 10))

        y_label = area.y + 70
        screen.blit(self.small_font.render("테마", True, (30, 30, 30)),
                    (area.x + 20, y_label))

        for t, rect in self.theme_buttons:
            color = (150, 255, 150) if t == self.selected_theme else (225, 225, 225)
            pygame.draw.rect(screen, color, rect, border_radius=12)
            txt = self.small_font.render(t, True, (25, 25, 25))
            screen.blit(txt, txt.get_rect(center=rect.center))

        y_slider_label = self.theme_buttons[0][1].bottom + 100
        screen.blit(self.small_font.render("밝기 조절", True, (30, 30, 30)),
                    (area.x + 20, y_slider_label))

        slider_x = area.x + 140
        slider_y = y_slider_label + 20
        slider_w = 300
        slider_h = 8
        self.slider_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)

        pygame.draw.rect(screen, (210, 210, 210), self.slider_rect, border_radius=4)
        fill_w = int(self.slider_rect.width * self.brightness)
        pygame.draw.rect(screen, (150, 255, 150),
                         (slider_x, slider_y, fill_w, slider_h), border_radius=4)

        knob_x = slider_x + fill_w
        knob_y = slider_y + slider_h // 2
        knob_r = 10
        self.knob_rect = pygame.Rect(knob_x - knob_r, knob_y - knob_r, knob_r * 2, knob_r * 2)
        pygame.draw.circle(screen, (80, 80, 80), self.knob_rect.center, knob_r)

        percent_text = self.small_font.render(f"{int(self.brightness * 100)}%", True, (40, 40, 40))
        screen.blit(percent_text, (slider_x + slider_w + 20, slider_y - 6))

    def on_click(self, pos):
        for t, rect in self.theme_buttons:
            if rect.collidepoint(pos):
                self.select_theme(t)
                return True
        if self.knob_rect and self.knob_rect.collidepoint(pos):
            self.dragging_slider = True
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_slider:
                self.dragging_slider = False
                self.ui.logger.log(self.ui.depth_path,
                                   f"Brightness: {self.brightness:.2f}",
                                   event.pos, len(self.ui.depth_path))
        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            if self.slider_rect:
                rel_x = max(self.slider_rect.left, min(event.pos[0], self.slider_rect.right))
                self.brightness = (rel_x - self.slider_rect.left) / self.slider_rect.width


    # -------------------------------------------------
    def handle_event(self, event):
        """슬라이더 클릭/드래그 제어"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect and self.knob_rect.collidepoint(event.pos):
                self.dragging_slider = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_slider:
                self.dragging_slider = False
                self.ui.logger.log(self.ui.depth_path, f"Brightness: {self.brightness:.2f}",
                                   event.pos, len(self.ui.depth_path))
        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            if self.slider_rect:
                # 슬라이더 위치에 맞게 밝기 갱신
                rel_x = max(self.slider_rect.left, min(event.pos[0], self.slider_rect.right))
                self.brightness = (rel_x - self.slider_rect.left) / self.slider_rect.width

# 11. 보안
class SecurityScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Sec Setting", ui)

        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        # 상태값
        self.record_modes = ["꺼짐", "수동", "자동"]
        self.selected_mode = "꺼짐"
        self.onhook_enabled = False  # 토글형

        # 버튼들
        self.action_buttons = []  # 클립 삭제 / USB 포맷

        self._build_buttons()

    # -------------------------------------------------
    def _build_buttons(self):
        left_w = self.ui.side.width
        base_x = left_w + 40
        base_y = 130
        bw, bh = 120, 50
        gap_x = 20

        # 녹화모드 버튼
        self.mode_buttons = []
        x = base_x
        for m in self.record_modes:
            rect = pygame.Rect(x, base_y, bw, bh)
            self.mode_buttons.append(
                Button(m, rect, lambda val=m: self.select_mode(val), self.small_font, self.colors)
            )
            x += bw + gap_x

        # 온후크 토글 위치
        self.onhook_rect = pygame.Rect(base_x + 420, base_y + 8, 60, 30)

        # 하단 액션 버튼 (클립 삭제, USB 포맷)
        y_bottom = base_y + 120
        x2 = base_x
        for label in ["클립 삭제", "USB 포맷"]:
            rect = pygame.Rect(x2, y_bottom, 140, 50)
            self.action_buttons.append(
                Button(label, rect, lambda name=label: self.log_action(name), self.small_font, self.colors)
            )
            x2 += 160

    # -------------------------------------------------
    def select_mode(self, name):
        self.selected_mode = name
        self.ui.logger.log(self.ui.depth_path, f"RecordMode: {name}", pygame.mouse.get_pos(), len(self.ui.depth_path))
        print(f"[Clicked: {name}")

    def toggle_onhook(self):
        self.onhook_enabled = not self.onhook_enabled
        state = "ON" if self.onhook_enabled else "OFF"
        self.ui.logger.log(self.ui.depth_path, f"OnHook: {state}", pygame.mouse.get_pos(), len(self.ui.depth_path))
        print(f"Clicked: {state}")

    def log_action(self, name):
        self.ui.logger.log(self.ui.depth_path, f"Action: {name}", pygame.mouse.get_pos(), len(self.ui.depth_path))
        print(f"Clicked: {name}")

    # -------------------------------------------------
    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                        self.ui.width - left_w - 40,
                        self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 타이틀
        title = self.font.render("블랙박스", True, (30, 30, 30))
        screen.blit(title, (area.x + 20, area.y + 10))

        # === 1️⃣ 녹화 모드 ===
        label_y = area.y + 70
        screen.blit(self.small_font.render("녹화 모드", True, (30, 30, 30)), (area.x + 20, label_y))
        for btn in self.mode_buttons:
            color = (150, 255, 150) if btn.text == self.selected_mode else (225, 225, 225)
            pygame.draw.rect(screen, color, btn.rect, border_radius=10)
            txt = self.small_font.render(btn.text, True, (25, 25, 25))
            screen.blit(txt, txt.get_rect(center=btn.rect.center))

        # === 2️⃣ 온후크 토글 ===
        toggle_label_x = self.onhook_rect.right + 10
        toggle_label_y = self.onhook_rect.y + 5
        screen.blit(self.small_font.render("온후크", True, (40, 40, 40)), (toggle_label_x, toggle_label_y))
        toggle_rect = self.onhook_rect
        knob_radius = toggle_rect.height // 2 - 2
        knob_x = toggle_rect.left + knob_radius + 2 if not self.onhook_enabled else toggle_rect.right - knob_radius - 2
        knob_color = (255, 255, 255)
        

        if self.onhook_enabled:
            pygame.draw.rect(screen, (150, 255, 150), toggle_rect, border_radius=15)
            pygame.draw.circle(screen, knob_color, (knob_x, toggle_rect.centery), knob_radius)
        else:
            pygame.draw.rect(screen, (180, 180, 180), toggle_rect, border_radius=15)
            pygame.draw.circle(screen, knob_color, (knob_x, toggle_rect.centery), knob_radius)

        # === 3️⃣ 하단 기능 버튼 ===
        for btn in self.action_buttons:
            btn.draw(screen, mouse_pos)

    # -------------------------------------------------
    def on_click(self, pos):
        # 녹화 모드 버튼
        for btn in self.mode_buttons:
            if btn.check_click(pos):
                btn.action()
                return True

        # 온후크 토글
        if self.onhook_rect.collidepoint(pos):
            self.toggle_onhook()
            return True

        # 하단 버튼
        for btn in self.action_buttons:
            if btn.check_click(pos):
                btn.action()
                return True

        return False


# 12. 사운드
class SoundScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Sound Setting", ui)
        self.ui = ui
        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        # 주행 사운드 강도 (라디오 버튼)
        self.modes = ["약하게", "보통", "강하게"]
        self.selected_mode = "보통"

        # 톤 설정 슬라이더 (0.0 ~ 1.0)
        self.tones = {"고음": 0.5, "중음": 0.5, "저음": 0.5}
        self.slider_rects = {}
        self.dragging = None
        self.dragging_last_value = None  # 마지막 값 저장

    def _select_mode(self, mode):
        if mode != self.selected_mode:
            self.selected_mode = mode
            self.ui.logger.log(
                self.ui.depth_path,
                f"DrivingSound: {mode}",
                pygame.mouse.get_pos(),
                len(self.ui.depth_path),
            )

    def _set_tone_value(self, tone, value):
        self.tones[tone] = max(0.0, min(1.0, value))
        self.ui.logger.log(
            self.ui.depth_path,
            f"Tone-{tone}: {self.tones[tone]:.2f}",
            pygame.mouse.get_pos(),
            len(self.ui.depth_path),
        )

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # --- 제목 ---
        title = self.font.render("주행 사운드", True, (30, 30, 30))
        screen.blit(title, (area.x + 20, area.y + 10))

        # --- 주행 사운드 강도 ---
        y_mode_title = area.y + 70
        label = self.small_font.render("사운드 강도 설정", True, (30, 30, 30))
        screen.blit(label, (area.x + 30, y_mode_title))

        bw, bh, gap = 120, 50, 15
        x = area.x + 30
        y_btn = y_mode_title + 40
        self.mode_buttons = []

        for m in self.modes:
            rect = pygame.Rect(x, y_btn, bw, bh)
            color = (150, 255, 150) if m == self.selected_mode else (230, 230, 230)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            txt = self.small_font.render(
                m, True, (255, 255, 255) if m == self.selected_mode else (40, 40, 40)
            )
            screen.blit(txt, txt.get_rect(center=rect.center))
            self.mode_buttons.append((m, rect))
            x += bw + gap

        # --- 톤 설정 ---
        y_tone_title = y_btn + bh + 80
        tone_title = self.small_font.render("톤 설정", True, (30, 30, 30))
        screen.blit(tone_title, (area.x + 30, y_tone_title))

        self.slider_rects.clear()
        slider_x = area.x + 180
        slider_w, slider_h = 300, 8
        knob_r = 10
        y = y_tone_title + 50

        for tone, val in self.tones.items():
            # 라벨
            label = self.small_font.render(tone, True, (30, 30, 30))
            screen.blit(label, (area.x + 50, y - 6))

            # 트랙 + 채움
            slider_rect = pygame.Rect(slider_x, y, slider_w, slider_h)
            pygame.draw.rect(screen, (210, 210, 210), slider_rect, border_radius=4)
            fill_w = int(slider_w * val)
            pygame.draw.rect(screen, (150, 255, 150), (slider_x, y, fill_w, slider_h), border_radius=4)

            # 노브
            knob_x = slider_x + fill_w
            knob_y = y + slider_h // 2
            pygame.draw.circle(screen, (60, 60, 60), (knob_x, knob_y), knob_r)

            # 값 표시 (%)
            percent = int(val * 100)
            txt = self.small_font.render(f"{percent}%", True, (40, 40, 40))
            screen.blit(txt, (slider_rect.right + 20, y - 6))

            self.slider_rects[tone] = (slider_rect, knob_r)
            y += 70

    def handle_event(self, event):
        # --- 버튼 클릭 (한 번만) ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for mode, rect in self.mode_buttons:
                if rect.collidepoint(event.pos):
                    self._select_mode(mode)
                    return

            # 슬라이더 드래그 시작
            for tone, (rect, knob_r) in self.slider_rects.items():
                knob_x = rect.x + int(rect.width * self.tones[tone])
                knob_y = rect.y + rect.height // 2
                knob_rect = pygame.Rect(knob_x - knob_r, knob_y - knob_r, knob_r * 2, knob_r * 2)
                if knob_rect.collidepoint(event.pos):
                    self.dragging = tone
                    self.dragging_last_value = self.tones[tone]
                    return

        # --- 드래그 중 (값 변경만 반영, 로그 X) ---
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            tone = self.dragging
            rect, _ = self.slider_rects[tone]
            rel_x = max(rect.left, min(event.pos[0], rect.right))
            val = (rel_x - rect.left) / rect.width
            self.tones[tone] = val

        # --- 드래그 종료 (값 변경 시 로그 기록) ---
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                tone = self.dragging
                rect, _ = self.slider_rects[tone]
                rel_x = max(rect.left, min(event.pos[0], rect.right))
                val = (rel_x - rect.left) / rect.width
                # 로그는 실제로 값이 바뀐 경우만
                if abs(val - (self.dragging_last_value or 0)) > 0.01:
                    self._set_tone_value(tone, val)
                self.tones[tone] = val
                self.dragging = None
                self.dragging_last_value = None


# 13. 프로필
class ProfileScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Profile Setting", ui)
        self.ui = ui
        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        # 입력 상태 관리
        self.text_input = ""
        self.input_active = False
        self.keyboard_visible = False

        # 현재 활성 프로필 이름
        self.current_profile = None

        # 제어 버튼
        self.controls = ["사이드미러 각도", "운전자 위치"]
        self.control_buttons = []

        # 가상 키보드 정의
        self.keys = [
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
        ]
        self.special_keys = ["Space", "Back", "Enter"]

    # ------------------------
    # 프로필 추가 로직
    # ------------------------
    def _add_profile(self):
        if self.text_input.strip():
            # 기존: self.current_profile = self.text_input.strip()
            self.ui.current_profile = self.text_input.strip()  # 전역 상태로 저장
            self.ui.logger.log(
                self.ui.depth_path,
                f"ProfileAdded: {self.ui.current_profile}",
                pygame.mouse.get_pos(),
                len(self.ui.depth_path),
            )
            self.text_input = ""
            self.keyboard_visible = False
            self.input_active = False

    def _toggle_keyboard(self, visible=True):
        self.keyboard_visible = visible
        self.input_active = visible
        self.ui.logger.log(
            self.ui.depth_path,
            f"Keyboard {'Shown' if visible else 'Hidden'}",
            pygame.mouse.get_pos(),
            len(self.ui.depth_path),
        )

    # ------------------------
    # 메인 그리기
    # ------------------------
    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(
            left_w + 20,
            70,
            self.ui.width - left_w - 40,
            self.ui.height - self.ui.bottom.h - 90,
        )
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # --- 제목 ---
        title = self.font.render("프로필 설정", True, (30, 30, 30))
        screen.blit(title, (area.x + 20, area.y + 10))

        # --- 입력창 + 추가 버튼 ---
        input_rect = pygame.Rect(area.x + 30, area.y + 70, 220, 50)
        add_btn_rect = pygame.Rect(input_rect.right + 20, area.y + 70, 120, 50)

        pygame.draw.rect(screen, (255, 255, 255), input_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), input_rect, 2, border_radius=10)

        # 텍스트 표시
        txt = self.small_font.render(self.text_input or "이름 입력...", True, (50, 50, 50))
        screen.blit(txt, (input_rect.x + 10, input_rect.y + 15))

        # 버튼
        pygame.draw.rect(screen, (230, 230, 230), add_btn_rect, border_radius=10)
        t = self.small_font.render("프로필 추가", True, (0, 0, 0))
        screen.blit(t, t.get_rect(center=add_btn_rect.center))

        # --- 제어 섹션 ---
        y = area.y + 180
        label = self.small_font.render("제어", True, (30, 30, 30))
        screen.blit(label, (area.x + 30, y))
        y += 50

        self.control_buttons.clear()
        for name in self.controls:
            rect = pygame.Rect(area.x + 40, y, 220, 45)

            # Hover 감지
            hovered = rect.collidepoint(mouse_pos)
            base_color = (230, 230, 230)
            hover_color = (210, 215, 225)
            color = hover_color if hovered else base_color

            pygame.draw.rect(screen, color, rect, border_radius=10)
            text = self.small_font.render(name, True, (40, 40, 40))
            screen.blit(text, text.get_rect(center=rect.center))

            self.control_buttons.append((name, rect))
            y += 65

        # --- 가상 키보드 ---
        if self.keyboard_visible:
            self._draw_keyboard(screen)

    # ------------------------
    # 키보드 그리기
    # ------------------------
    def _draw_keyboard(self, screen):
        kb_height = 240
        kb_y = self.ui.height - kb_height - self.ui.bottom.h
        pygame.draw.rect(screen, (235, 235, 235), (0, kb_y, self.ui.width, kb_height))

        key_w, key_h, gap = 60, 50, 10
        start_x = 80
        y = kb_y + 20
        self.key_buttons = []

        for row in self.keys:
            x = start_x
            for key in row:
                rect = pygame.Rect(x, y, key_w, key_h)
                pygame.draw.rect(screen, (250, 250, 250), rect, border_radius=8)
                pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=8)
                t = self.small_font.render(key, True, (30, 30, 30))
                screen.blit(t, t.get_rect(center=rect.center))
                self.key_buttons.append((key, rect))
                x += key_w + gap
            y += key_h + gap
            start_x += 30

        # 스페셜 키들
        specials_y = y
        x = 100
        for special in self.special_keys:
            w = 200 if special == "Space" else 100
            rect = pygame.Rect(x, specials_y, w, key_h)
            pygame.draw.rect(screen, (220, 220, 220), rect, border_radius=10)
            text = self.small_font.render(special, True, (30, 30, 30))
            screen.blit(text, text.get_rect(center=rect.center))
            self.key_buttons.append((special, rect))
            x += w + 20

    # ------------------------
    # 이벤트 처리
    # ------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # 입력창 클릭 → 키보드 표시
            left_w = self.ui.side.width
            area = pygame.Rect(left_w + 20, 70, self.ui.width - left_w - 40,
                               self.ui.height - self.ui.bottom.h - 90)
            input_rect = pygame.Rect(area.x + 30, area.y + 70, 220, 50)
            add_btn_rect = pygame.Rect(input_rect.right + 20, area.y + 70, 120, 50)

            if input_rect.collidepoint(pos):
                self._toggle_keyboard(True)
                return

            # 프로필 추가 버튼
            if add_btn_rect.collidepoint(pos):
                self._add_profile()
                return

            # 제어 버튼 클릭
            for name, rect in self.control_buttons:
                if rect.collidepoint(pos):
                    self.ui.logger.log(self.ui.depth_path, f"ControlButton: {name}", pos, len(self.ui.depth_path))
                    return

            # 키보드 클릭 처리
            if self.keyboard_visible:
                clicked_key = None
                for key, rect in self.key_buttons:
                    if rect.collidepoint(pos):
                        clicked_key = key
                        break

                if clicked_key:
                    self._handle_key_input(clicked_key)
                    self.ui.logger.log(self.ui.depth_path, f"KeyPress: {clicked_key}", pos, len(self.ui.depth_path))
                    return

                # 키보드 외부 클릭 시 닫기
                kb_height = 240
                kb_y = self.ui.height - kb_height - self.ui.bottom.h
                if pos[1] < kb_y:
                    self._toggle_keyboard(False)

    def _handle_key_input(self, key):
        if key == "Back":
            self.text_input = self.text_input[:-1]
        elif key == "Space":
            self.text_input += " "
        elif key == "Enter":
            self._toggle_keyboard(False)
        else:
            self.text_input += key


# 14. 편의 기능
class ConvenienceScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Conv Setting", ui)
        self.ui = ui
        self.font = ui.font
        self.small_font = ui.small_font
        self.colors = ui.colors

        # 모드 상태 (True = ON, False = OFF)
        self.modes = {
            "세차 모드": False,
            "유틸리티 모드": False,
            "펫 케어 모드": False,
            "발레 모드": False
        }

        # 카드 클릭 영역 저장용
        self.card_buttons = {}

    def _toggle_mode(self, name):
        self.modes[name] = not self.modes[name]
        state = "ON" if self.modes[name] else "OFF"
        self.ui.logger.log(
            self.ui.depth_path,
            f"{name}: {state}",
            pygame.mouse.get_pos(),
            len(self.ui.depth_path)
        )

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                        self.ui.width - left_w - 40,
                        self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # --- 대제목 ---
        title = self.ui.font.render("편의 기능", True, (30, 30, 30))
        screen.blit(title, (area.x + 20, area.y + 10))

        # --- 카드 크기 및 간격 조정 ---
        x, y = area.x + 30, area.y + 80
        card_w, card_h = 360, 140
        gap_x, gap_y = 60, 50

        self.card_buttons.clear()

        for i, (name, state) in enumerate(self.modes.items()):
            card = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(screen, (245, 245, 245), card, border_radius=14)
            pygame.draw.rect(screen, (220, 220, 220), card, 1, border_radius=14)

            # 제목
            label = self.small_font.render(name, True, (30, 30, 30))
            screen.blit(label, (card.x + 20, card.y + 18))

            # 설명 여러 줄
            desc_lines = []
            if "세차" in name:
                desc_lines = ["세차 시 차량 손상 방지를 위해", "일부 기능을 제한합니다."]
            elif "유틸리티" in name:
                desc_lines = ["주차 중에도 오디오나 조명 등 전기 장치를", "계속 사용할 수 있습니다."]
            elif "펫" in name:
                desc_lines = ["반려 동물이 차 안에서 안전하게 있을 수 있도록", "실내 온도를 유지하고 도어와 창문을 잠급니다."]
            elif "발레" in name:
                desc_lines = ["주행에 필요한 기능은 그대로 작동하며,", "개인정보 보호를 위해 일부 기능이 차단됩니다."]

            line_y = card.y + 48
            for line in desc_lines:
                desc_text = self.ui.tiny_font.render(line, True, (80, 80, 80))
                screen.blit(desc_text, (card.x + 20, line_y))
                line_y += 20

            # 버튼
            btn_rect = pygame.Rect(card.right - 90, card.bottom - 45, 70, 32)
            active = self.modes[name]
            hover = btn_rect.collidepoint(mouse_pos)
            base_color = (150, 255, 150) if active else (200, 200, 200)
            hover_color = (150, 255, 150) if active else (180, 180, 180)
            color = hover_color if hover else base_color

            pygame.draw.rect(screen, color, btn_rect, border_radius=8)
            txt = self.ui.tiny_font.render("끄기" if active else "켜기", True, (20, 20, 20))
            screen.blit(txt, txt.get_rect(center=btn_rect.center))

            self.card_buttons[name] = btn_rect

            # 2열 배치
            x += card_w + gap_x
            if (i + 1) % 2 == 0:
                x = area.x + 30
                y += card_h + gap_y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.card_buttons.items():
                if rect.collidepoint(event.pos):
                    self._toggle_mode(name)
                    return


# 15. 연결
class ConnectivityScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Connectivity Setting", ui)
        self.ui = ui

        # 항목과 상태값
        self.items = {
            "블루투스": False,
            "Wi-Fi": False,
            "Wi-Fi 핫스팟": False,
            "모바일 데이터": False
        }

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70, self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 대제목
        title = self.ui.font.render("연결 설정", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        # 각 항목 그리기
        y = area.y + 70
        self.toggle_rects = {}  # 토글 버튼 영역 저장

        for name, state in self.items.items():
            # 텍스트
            label = self.ui.small_font.render(name, True, (30, 30, 30))
            screen.blit(label, (area.x + 20, y + 4))

            # 토글 위치 계산
            toggle_rect = pygame.Rect(area.right - 90, y, 50, 26)
            self.toggle_rects[name] = toggle_rect

            # 토글 색상
            color_bg = (150, 255, 150) if state else (180, 180, 180)
            knob_x = toggle_rect.x + (28 if state else 2)

            # 토글 그리기
            pygame.draw.rect(screen, color_bg, toggle_rect, border_radius=13)
            pygame.draw.circle(screen, (255, 255, 255),
                               (knob_x + 10, toggle_rect.centery), 10)

            y += 60

    def on_click(self, pos):
        for name, rect in self.toggle_rects.items():
            if rect.collidepoint(pos):
                # 상태 반전
                self.items[name] = not self.items[name]
                state = "On" if self.items[name] else "Off"

                # 로그 남기기
                self.ui.logger.log(self.ui.depth_path, f"{name}: {state}", pos, len(self.ui.depth_path))
                return True
        return False


# 16. 앱
class AppsSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("App Setting", ui)
        self.ui = ui

        self.apps = [
            "(s)내비게이션", "Android Auto", "App Market",
            "Chromium", "Gleo AI", "라디오", "전화", "차량"
        ]

        self.buttons = []  # 버튼 객체 저장용

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 제목
        title = self.ui.font.render("기본 앱", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        y = area.y + 70
        self.buttons = []

        for app in self.apps:
            # 앱 이름 박스
            app_rect = pygame.Rect(area.x + 20, y, 240, 50)
            pygame.draw.rect(screen, (235, 235, 235), app_rect, border_radius=10)
            t = self.ui.small_font.render(app, True, (40, 40, 40))
            screen.blit(t, (app_rect.x + 20, app_rect.y + 12))

            # 강제 종료 버튼
            btn_rect = pygame.Rect(area.right - 120, y + 12, 90, 28)
            hovered = btn_rect.collidepoint(mouse_pos)
            color = (180, 180, 180) if hovered else (200, 200, 200)
            pygame.draw.rect(screen, color, btn_rect, border_radius=8)

            en = self.ui.tiny_font.render("강제 종료", True, (40, 40, 40))
            screen.blit(en, en.get_rect(center=btn_rect.center))

            # 클릭 감지를 위해 저장
            self.buttons.append((app, btn_rect))
            y += 60

    def on_click(self, pos):
        for app, rect in self.buttons:
            if rect.collidepoint(pos):
                # 로그 남기기
                self.ui.logger.log(self.ui.depth_path, f"{app}: 강제 종료", pos, len(self.ui.depth_path))
                return True
        return False


# 17. 일반 설정
class GeneralSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("General Setting", ui)
        self.ui = ui

        # 보조 속도 표시 (토글)
        self.show_subspeed = False

        # 단위 선택 (기본값)
        self.unit_options = {
            "거리": ["km", "mile"],
            "온도": ["°C", "°F"],
            "연비": ["km/kWh", "kWh/100km"],
            "타이어 공기압": ["psi", "kPa", "bar"]
        }
        self.selected_units = {
            "거리": "km",
            "온도": "°C",
            "연비": "km/kWh",
            "타이어 공기압": "psi"
        }

        self.toggle_rect = None
        self.unit_button_rects = {}  # {항목: [rect, rect, ...]}

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 대제목
        title = self.ui.font.render("단위", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        # 보조 속도 표시 토글
        label = self.ui.small_font.render("보조 속도 표시", True, (30, 30, 30))
        screen.blit(label, (area.x + 20, area.y + 60))
        toggle_rect = pygame.Rect(area.x + 200, area.y + 55, 50, 26)
        self.toggle_rect = toggle_rect

        color_bg = (150, 255, 150) if self.show_subspeed else (180, 180, 180)
        knob_x = toggle_rect.x + (28 if self.show_subspeed else 2)
        pygame.draw.rect(screen, color_bg, toggle_rect, border_radius=13)
        pygame.draw.circle(screen, (255, 255, 255),
                           (knob_x + 10, toggle_rect.centery), 10)

        # 단위 항목
        start_y = area.y + 110
        gap_y = 70
        self.unit_button_rects = {}

        for i, (category, options) in enumerate(self.unit_options.items()):
            y = start_y + i * gap_y

            # 항목 라벨
            label = self.ui.small_font.render(f"{category}", True, (30, 30, 30))
            screen.blit(label, (area.x + 20, y))

            # 버튼들
            btn_x = area.x + 200
            btn_w, btn_h = 90, 36
            self.unit_button_rects[category] = []

            for opt in options:
                rect = pygame.Rect(btn_x, y - 4, btn_w, btn_h)
                is_selected = (self.selected_units[category] == opt)
                color = (150, 255, 150) if is_selected else (230, 230, 230)
                pygame.draw.rect(screen, color, rect, border_radius=10)

                text = self.ui.tiny_font.render(opt, True, (0, 0, 0))
                screen.blit(text, text.get_rect(center=rect.center))
                self.unit_button_rects[category].append((opt, rect))
                btn_x += btn_w + 10

    def on_click(self, pos):
        # 보조 속도 표시 토글 클릭
        if self.toggle_rect and self.toggle_rect.collidepoint(pos):
            self.show_subspeed = not self.show_subspeed
            state = "On" if self.show_subspeed else "Off"
            self.ui.logger.log(self.ui.depth_path, f"보조 속도 표시: {state}", pos, len(self.ui.depth_path))
            return True

        # 단위 버튼 클릭
        for category, rects in self.unit_button_rects.items():
            for opt, rect in rects:
                if rect.collidepoint(pos):
                    self.selected_units[category] = opt
                    self.ui.logger.log(self.ui.depth_path, f"{category}: {opt}", pos, len(self.ui.depth_path))
                    return True
        return False


# 18. 차량 정보
class VehicleInfoScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Veh Info", ui)
        self.ui = ui

        # 상태 변수
        self.software_version = "RELEASE.sdvplatform.v0.00.00"
        self.auto_update = False
        self.vin = "invalid"

        # 버튼/토글 위치 저장용
        self.toggle_rect = None
        self.reset_button_rect = None

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70,
                           self.ui.width - left_w - 40,
                           self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248, 248, 248), area, border_radius=14)

        # 대제목
        title = self.ui.font.render("Connect", True, (30, 30, 30))
        screen.blit(title, (area.x + 16, area.y + 12))

        # 소제목
        sub = self.ui.small_font.render("소프트웨어 정보", True, (60, 60, 60))
        screen.blit(sub, (area.x + 20, area.y + 60))

        # 소프트웨어 버전
        version_txt = self.ui.tiny_font.render(self.software_version, True, (40, 40, 40))
        screen.blit(version_txt, (area.x + 40, area.y + 100))

        # 업데이트 자동 다운로드 토글
        y = area.y + 150
        label = self.ui.small_font.render("업데이트 자동 다운로드", True, (30, 30, 30))
        screen.blit(label, (area.x + 20, y))

        toggle_rect = pygame.Rect(area.x + 280, y - 2, 50, 26)
        self.toggle_rect = toggle_rect

        color_bg = (150, 255, 150) if self.auto_update else (180, 180, 180)
        knob_x = toggle_rect.x + (28 if self.auto_update else 2)
        pygame.draw.rect(screen, color_bg, toggle_rect, border_radius=13)
        pygame.draw.circle(screen, (255, 255, 255),
                           (knob_x + 10, toggle_rect.centery), 10)

        # 차대번호
        y += 70
        vin_label = self.ui.small_font.render("차대번호", True, (30, 30, 30))
        screen.blit(vin_label, (area.x + 20, y))
        vin_value = self.ui.tiny_font.render(self.vin, True, (40, 40, 40))
        screen.blit(vin_value, (area.x + 280, y + 5))

        # 공장 초기화
        y += 70
        reset_label = self.ui.small_font.render("공장 초기화", True, (30, 30, 30))
        screen.blit(reset_label, (area.x + 20, y))

        btn_rect = pygame.Rect(area.x + 280, y - 4, 100, 34)
        self.reset_button_rect = btn_rect

        hovered = btn_rect.collidepoint(mouse_pos)
        color = (200, 200, 200) if not hovered else (180, 180, 180)
        pygame.draw.rect(screen, color, btn_rect, border_radius=8)
        btn_text = self.ui.tiny_font.render("초기화", True, (40, 40, 40))
        screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    def on_click(self, pos):
        # 토글 클릭
        if self.toggle_rect and self.toggle_rect.collidepoint(pos):
            self.auto_update = not self.auto_update
            state = "On" if self.auto_update else "Off"
            self.ui.logger.log(self.ui.depth_path, f"업데이트 자동 다운로드: {state}", pos, len(self.ui.depth_path))
            return True

        # 초기화 버튼 클릭
        if self.reset_button_rect and self.reset_button_rect.collidepoint(pos):
            self.ui.logger.log(self.ui.depth_path, "공장 초기화: 실행", pos, len(self.ui.depth_path))
            print("Clicked: 공장 초기화")
            return True

        return False




# 라디오/뮤직/내비/앱스는 간단 카드 + 버튼
class SimpleListScreen(ScreenBase):
    def __init__(self, name, ui, items):
        super().__init__(name, ui)
        self.items = items

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70, self.ui.width - left_w - 40, self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (248,248,248), area, border_radius=14)
        t = self.ui.font.render(self.name, True, (30,30,30))
        screen.blit(t, (area.x+16, area.y+16))
        x, y = area.x+16, area.y+60
        for label in self.items:
            r = pygame.Rect(x, y, 240, 48)
            pygame.draw.rect(screen, (235,235,235), r, border_radius=10)
            s = self.ui.small_font.render(label, True, (20,20,20))
            screen.blit(s, s.get_rect(center=r.center))
            self.buttons.append(Button(label, r, lambda L=label: None, self.ui.small_font, self.ui.colors))
            y += 56

class AppsScreen(SimpleListScreen):
    def __init__(self, ui):
        super().__init__("Apps", ui, ["(s)내비게이션", "Android Auto", "App Market", "Chromium",
                                      "Gleo AI", "라디오", "전화", "차량"])

class RadioScreen(SimpleListScreen):
    def __init__(self, ui):
        super().__init__("Radio", ui, ["Select Channel", "이전", "다음"])

class MusicScreen(SimpleListScreen):
    def __init__(self, ui):
        super().__init__("Music", ui, ["Bluetooth", "USB", "Streaming"])

class NavigationScreen(SimpleListScreen):
    def __init__(self, ui):
        super().__init__("Navigation", ui, ["Destination", "즐겨찾기", "최근 목적지"])

# -------------------------------
# helper
# -------------------------------
def _fit_into(src_size, max_size):
    sw, sh = src_size; mw, mh = max_size
    k = min(mw/sw, mh/sh)
    return (max(1, int(sw*k)), max(1, int(sh*k)))
