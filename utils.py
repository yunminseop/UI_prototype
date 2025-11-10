# utils.py
import pygame, csv, time, os

# -------------------------------
# 0) 공통 유틸/로거
# -------------------------------
class Logger:
    def __init__(self, file_path: str):
        self.file = file_path
        os.makedirs(os.path.dirname(self.file), exist_ok=True)
        with open(self.file, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Time(UNIX)", "Path", "Target", "Pos(x,y)", "Depth"])

    def log(self, path_list, target, pos, depth: int):
        now_unix = time.time()  # UNIX timestamp
        with open(self.file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([now_unix, " / ".join(path_list), target, tuple(pos), depth])

# -------------------------------
# 1) 기본 UI 위젯
# -------------------------------
class Button:
    def __init__(self, text, rect, action, font, colors, icon=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.action = action
        self.font = font
        self.colors = colors
        self.icon = icon
        self.is_pressed = False  # 🔸 클릭 상태 추가

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        if self.is_pressed:
            color = self.colors.get("BUTTON_PRESSED", (190, 195, 205))  # 클릭 중 색상
        elif hovered:
            color = self.colors.get("BUTTON_HOVER", (215, 220, 230))
        else:
            color = self.colors.get("BUTTON", (232, 235, 240))

        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        # 텍스트/아이콘 표시
        if self.icon:
            ir = self.icon.get_rect(center=(self.rect.centerx, self.rect.centery - 8))
            surface.blit(self.icon, ir)
            label = self.font.render(self.text, True, self.colors["TEXT"])
            surface.blit(label, label.get_rect(midtop=(self.rect.centerx, self.rect.centery + 2)))
        else:
            label = self.font.render(self.text, True, self.colors["TEXT"])
            surface.blit(label, label.get_rect(center=self.rect.center))

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# -------------------------------
# 2) 상/좌/하 바
# -------------------------------
class TopBar:
    def __init__(self, width, height, colors, font, tiny_font, ui):
        self.w, self.h = width, height
        self.colors, self.font, self.tiny_font = colors, font, tiny_font
        self.ui = ui

    def draw(self, screen):
        pygame.draw.rect(screen, self.colors["TOP"], (0, 0, self.w, self.h))
        # 좌측: 현재 기어
        gear_txt = self.font.render(self.ui.vehicle_state["gear"], True, self.colors["TEXT"])
        screen.blit(gear_txt, (10, 4))
        # 가운데: 경로(depth path)
        path = " / ".join(self.ui.depth_path)
        screen.blit(self.tiny_font.render(path, True, self.colors["TEXT"]), (120, 6))
        # 우측: 배터리/주행가능거리 + 시간
        r = self.ui.vehicle_state
        right = f'{int(r["range_km"])}km  |  {time.strftime("%p %I:%M", time.localtime())}'
        rt = self.tiny_font.render(right, True, self.colors["TEXT"])
        screen.blit(rt, (self.w - rt.get_width() - 12, 7))

class SidePanel:
    # (PLEOS 좌측의 차량 3D 섬네일 영역 느낌만 단순 표현)
    def __init__(self, width, top_h, bottom_h, colors, height, ui):
        self.width, self.top_h, self.bottom_h, self.h = width, top_h, bottom_h, height
        self.colors, self.ui = colors, ui
        self.car_img = None

    def load_image(self, path, max_w=280, max_h=220):
        try:
            img = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(img, _fit_into(img.get_size(), (max_w, max_h)))
            self.car_img = img
        except Exception:
            self.car_img = None

    def draw(self, screen):
        area = (0, self.top_h, self.width, self.h - self.top_h - self.bottom_h)
        pygame.draw.rect(screen, self.colors["LEFT"], area)
        # 차량 미니 카드
        x0, y0, w, h = 20, self.top_h + 30, self.width - 40, 240
        pygame.draw.rect(screen, (240, 240, 240), (x0, y0, w, h), border_radius=16)
        if self.car_img:
            ir = self.car_img.get_rect(center=(x0 + w//2, y0 + h//2))
            screen.blit(self.car_img, ir)
        else:
            # 대체 그림(차량 실루엣)
            pygame.draw.rect(screen, (210, 210, 210), (x0+30, y0+60, w-60, 90), border_radius=45)
            pygame.draw.circle(screen, (210,210,210), (x0+70, y0+150), 24)
            pygame.draw.circle(screen, (210,210,210), (x0+w-70, y0+150), 24)

class BottomBar:
    def __init__(self, width, height, ui, colors, small_font):
        self.w, self.h, self.ui, self.colors, self.small_font = width, height, ui, colors, small_font
        self.buttons = []
        self._build()

    # def _build(self):
    #     # 하단바 버튼 구성(레이블 → 행동)
    #     row_y = self.ui.height - self.h + 5
    #     x, gap, bw, bh = 10, 112, 102, self.h - 10

    def _build(self):
        row_y = self.ui.height - self.h + 5
        bw, bh = 90, self.h - 10
        gap = 4
        x = 8

        def add(label, action):
            rect = pygame.Rect(x, row_y, bw, bh)
            self.buttons.append(Button(label, rect, action, self.small_font, self.colors))
            return rect

        order = [
            ("차량 설정", lambda: self.ui.open_screen("Quick Settings")),
            ("앞유리 성에제거", lambda: self._log_only("FrontDefrost")),
            ("뒷유리 성에제거", lambda: self._log_only("RearDefrost")),
            ("운전석 시트 열선", lambda: self._log_only("SeatHeat_L")),
            ("내비게이션", lambda: self.ui.open_screen("Navigation")),
            ("앱", lambda: self.ui.open_screen("Apps")),
            ("전화", lambda: self._log_only("Phone")),
            ("메뉴", lambda: self._log_only("Menu")),
            ("인터넷", lambda: self._log_only("Internet")),
            ("음악", lambda: self.ui.open_screen("Music")),
            ("운전석 시트 통풍", lambda: self._log_only("SeatVent_L")),
            ("조수석 시트 열선", lambda: self._log_only("SeatHeat_R")),
            ("조수석 시트 통풍", lambda: self._log_only("SeatVent_R")),
        ]

        for label, action in order:
            add(label, action)
            x += bw + gap

    def _log_only(self, name):
        # 상태 토글 대신 로깅만 해두고, 필요시 UI 상태값 연결하면 됨
        self.ui.logger.log(self.ui.depth_path, name, pygame.mouse.get_pos(), len(self.ui.depth_path))

    def draw(self, screen):
        y0 = self.ui.height - self.h
        pygame.draw.rect(screen, self.colors["BOTTOM"], (0, y0, self.w, self.h))
        mp = pygame.mouse.get_pos()
        for b in self.buttons:
            b.draw(screen, mp)

# -------------------------------
# 3) 화면(스크린) 베이스/구현체
# -------------------------------
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

# 빠른설정(사진처럼 여러 타일)
class QuickSettingsScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Quick Settings", ui)
        self.scroll_offset = 0         # 스크롤 위치
        self.menu_rects = []           # 좌측 메뉴 버튼들
        self.grid = []                 # 우측 타일 버튼들
        self._build_tiles()

    def _build_tiles(self):
        # 좌측 카테고리 (스크롤 영역)
        self.left_menu = [
            ("빠른 설정", None),
            ("라이트", None),
            ("주행 보조", None),
            ("잠금", None),
            ("시트 포지션", None),
            ("공조", None),
            ("충전", "Charging"),
            ("내비게이션", "Navigation"),
            ("Gleo AI", None),
            ("화면", None),
            ("보안", None),
            ("사운드", None),
            ("프로필", None),
            ("편의 기능", None),
            ("연결", "Apps"),
            ("앱", "Apps"),
            ("일반 설정", None),
            ("차량 정보", None),
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
        w, h, gap = 180, 70, 12
        labels = [
            "도어 잠금", "창문 열림", "창문 잠금", "어린이 보호 잠금",
            "글로브박스", "프렁크", "트렁크", "사이드미러",
            "충전구", "선루프"
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
        # 🔸 마우스 휠 스크롤
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset += event.y * 20  # 휠 속도
            max_scroll = max(0, (len(self.left_menu) * 44) - (self.ui.height - 200))
            # 범위 제한
            self.scroll_offset = max(-max_scroll, min(0, self.scroll_offset))

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        panel = pygame.Rect(
            left_w + 20, 70,
            self.ui.width - left_w - 40,
            self.ui.height - self.ui.bottom.h - 90
        )
        pygame.draw.rect(screen, (250, 250, 250), panel, border_radius=14)

        # === (1) 좌측 메뉴 (스크롤 적용) ===
        for rect, name, goto in self.menu_rects:
            moved_rect = rect.move(0, self.scroll_offset)
            if moved_rect.bottom < panel.top or moved_rect.top > panel.bottom:
                continue
            pygame.draw.rect(screen, (235, 235, 235), moved_rect, border_radius=10)
            t = self.ui.small_font.render(name, True, (30, 30, 30))
            screen.blit(t, t.get_rect(center=moved_rect.center))

        # === (2) 스크롤바 표시 ===
        total_h = len(self.menu_rects) * 44
        visible_h = panel.height
        if total_h > visible_h:
            scrollbar_h = visible_h * (visible_h / total_h)
            max_scroll = total_h - visible_h
            scroll_ratio = -self.scroll_offset / max_scroll if max_scroll > 0 else 0
            scrollbar_y = panel.y + scroll_ratio * (visible_h - scrollbar_h)
            scrollbar_rect = pygame.Rect(panel.x + 192, scrollbar_y, 6, scrollbar_h)
            pygame.draw.rect(screen, (180, 180, 180), scrollbar_rect, border_radius=3)

        # === (3) 우측 타일 ===
        for rect, label in self.grid:
            pygame.draw.rect(screen, (245, 245, 245), rect, border_radius=12)
            s = self.ui.small_font.render(label, True, (40, 40, 40))
            screen.blit(s, s.get_rect(center=rect.center))

        # === (4) 충전 상태 바 ===
        charge = pygame.Rect(panel.right - 360, panel.y, 340, 70)
        pygame.draw.rect(screen, (235, 235, 235), charge, border_radius=14)
        bar = pygame.Rect(charge.x + 18, charge.y + 22, int(0.95 * (charge.w - 36)), 26)
        fill = bar.copy()
        fill.width = int(bar.width * self.ui.vehicle_state["soc"])
        pygame.draw.rect(screen, (180, 220, 120), fill, border_radius=8)
        pygame.draw.rect(screen, (190, 190, 190), bar, 2, border_radius=8)
        txt = self.ui.small_font.render(
            f"{int(self.ui.vehicle_state['range_km'])} km  (충전 100%)",
            True, (20, 20, 20)
        )
        screen.blit(txt, (charge.x + 20, charge.y + 4))

    def on_click(self, pos):
        # === 좌측 메뉴 클릭 ===
        for rect, name, goto in self.menu_rects:
            moved_rect = rect.move(0, self.scroll_offset)
            if moved_rect.collidepoint(pos):
                self.ui.logger.log(self.ui.depth_path, name, pos, len(self.ui.depth_path))
                if goto:
                    self.ui.open_screen(goto)
                return True

        # === 우측 타일 클릭 ===
        for rect, label in self.grid:
            if rect.collidepoint(pos):
                self.ui.logger.log(self.ui.depth_path, label, pos, len(self.ui.depth_path))
                return True

        return False

# 충전 상세(Depth 3 예시)
class ChargingScreen(ScreenBase):
    def __init__(self, ui):
        super().__init__("Charging", ui)
        self.dec = Button("-", (0,0,0,0), self.dec_amp, ui.font, ui.colors)
        self.inc = Button("+", (0,0,0,0), self.inc_amp, ui.font, ui.colors)
        self.amp = 48

    def dec_amp(self): self.amp = max(6, self.amp-2)
    def inc_amp(self): self.amp = min(80, self.amp+2)

    def draw(self, screen, mouse_pos):
        left_w = self.ui.side.width
        area = pygame.Rect(left_w + 20, 70, self.ui.width - left_w - 40, self.ui.height - self.ui.bottom.h - 90)
        pygame.draw.rect(screen, (250,250,250), area, border_radius=14)

        title = self.ui.font.render(f"{int(self.ui.vehicle_state['range_km'])} km", True, (20,20,20))
        screen.blit(title, (area.x+10, area.y+10))
        # 게이지
        bar = pygame.Rect(area.x+10, area.y+60, area.w-20, 40)
        fill = bar.copy(); fill.width = int(bar.width * 0.9)
        pygame.draw.rect(screen, (110,210,120), fill, border_radius=10)
        pygame.draw.rect(screen, (200,200,200), bar, 2, border_radius=10)

        # 전류 설정
        txt = self.ui.small_font.render("충전 전류", True, (20,20,20))
        screen.blit(txt, (area.x+10, area.y+130))
        minus = pygame.Rect(area.x+130, area.y+118, 50, 40)
        plus  = pygame.Rect(area.x+260, area.y+118, 50, 40)
        cur   = self.ui.small_font.render(f"{self.amp}A", True, (20,20,20))
        pygame.draw.rect(screen, (235,235,235), minus, border_radius=8)
        pygame.draw.rect(screen, (235,235,235), plus,  border_radius=8)
        mtxt = self.ui.font.render("-", True, (40,40,40)); screen.blit(mtxt, mtxt.get_rect(center=minus.center))
        ptxt = self.ui.font.render("+", True, (40,40,40)); screen.blit(ptxt, ptxt.get_rect(center=plus.center))
        screen.blit(cur, (area.x+200, area.y+128))

        self._minus_rect, self._plus_rect = minus, plus

    def on_click(self, pos):
        if self._minus_rect.collidepoint(pos):
            self.dec_amp(); self.ui.logger.log(self.ui.depth_path, "ChargeAmp-", pos, len(self.ui.depth_path)); return True
        if self._plus_rect.collidepoint(pos):
            self.inc_amp(); self.ui.logger.log(self.ui.depth_path, "ChargeAmp+", pos, len(self.ui.depth_path)); return True
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
