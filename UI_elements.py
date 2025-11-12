import pygame, csv, time, os

# -------------------------------
# 0) 공통 유틸/로거
# -------------------------------
# class Logger:
#     def __init__(self, file_path: str):
#         self.file = file_path
#         os.makedirs(os.path.dirname(self.file), exist_ok=True)
#         with open(self.file, "w", newline="", encoding="utf-8") as f:
#             w = csv.writer(f)
#             w.writerow(["Time(UNIX)", "Path", "Target", "Pos(x,y)", "Depth"])

#     def log(self, path_list, target, pos, depth: int):
#         now_unix = time.time()  # UNIX timestamp
#         with open(self.file, "a", newline="", encoding="utf-8") as f:
#             w = csv.writer(f)
#             w.writerow([now_unix, " / ".join(path_list), target, tuple(pos), depth])

class Logger:
    def __init__(self, file_path: str):
        self.file = file_path
        dir_path = os.path.dirname(self.file)
        if dir_path:  # 디렉터리 경로가 있을 때만 생성
            os.makedirs(dir_path, exist_ok=True)
        with open(self.file, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Timestamp", "Path", "Target", "Pos", "Depth"])

    def log(self, path_list, target, pos, depth: int):
        now_unix = time.time()  # UNIX timestamp
        with open(self.file, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([now_unix, " / ".join(path_list), target, tuple(pos), depth])

# -------------------------------
# 1) 기본 UI 위젯
# -------------------------------
class Button:
    def __init__(self, text, rect, action, font, colors, log_name=None, icon=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.action = action
        self.font = font
        self.colors = colors
        self.icon = icon
        self.is_pressed = False  # 클릭 상태 추가
        self.log_name = log_name  # ← 추가

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
        """좌표가 버튼 영역 안에 있는지 확인"""
        return self.rect.collidepoint(pos)

    def trigger(self, ui, pos):
        """버튼 클릭 시 공통 동작 (로그 + 액션 실행)"""
        # 로그 기록
        ui.logger.log(ui.depth_path, self.text, pos, len(ui.depth_path))

        # 연결된 액션이 있으면 실행
        if callable(self.action):
            self.action()


    def trigger(self, ui, pos=None):

        # 기존 text 대신 log_name이 있으면 그걸 사용
        log_target = self.log_name if self.log_name else self.text
        ui.logger.log(ui.depth_path, log_target, pos or pygame.mouse.get_pos(), len(ui.depth_path))

        if callable(self.action):
            self.action()
            

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

        gears = ["P", "R", "N", "D"]
        x = 10
        for g in gears:
            if g == self.ui.vehicle_state["gear"]:
                # 현재 선택된 기어 강조
                color = (0, 0, 0)
                bg_color = (180, 220, 255)  # 밝은 파랑톤 강조 배경
                pygame.draw.rect(screen, bg_color, (x - 3, 3, 25, self.h - 6), border_radius=4)
            else:
                color = (120, 120, 120)
            text = self.font.render(g, True, color)
            screen.blit(text, (x, 4))
            x += 30  # 문자 간격 조정

        # --- 가운데: 경로(depth path) ---
        path = " / ".join(self.ui.depth_path)
        screen.blit(self.tiny_font.render(path, True, self.colors["TEXT"]), (150, 6))

        # --- 우측: 배터리 및 주행 가능 거리 ---
        r = self.ui.vehicle_state
        right = f'{int(r["range_km"])}km  |  {time.strftime("%p %I:%M", time.localtime())}'
        rt = self.tiny_font.render(right, True, self.colors["TEXT"])
        screen.blit(rt, (self.w - rt.get_width() - 12, 7))

        # --- 현재 프로필 표시 (있을 때만) ---
        if self.ui.current_profile:
            prof_txt = self.tiny_font.render(self.ui.current_profile, True, self.colors["TEXT"])
            screen.blit(prof_txt, (self.w - 300, 7))

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

    def handle_event(self, event):
        """사이드패널 클릭이 상위 메뉴로 전달되도록 유지"""
        pass

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
        bw, bh = 94, self.h - 10
        gap = 4
        x = 8

        def add(label, action):
            rect = pygame.Rect(x, row_y, bw, bh)
            self.buttons.append(Button(label, rect, action, self.small_font, self.colors))
            return rect

        order = [
            ("Setting", lambda: self.ui.open_screen("Quick Settings")),
            ("F.Defrost", lambda: self._log_only("FrontDefrost")),
            ("R.Defrost", lambda: self._log_only("RearDefrost")),
            ("L.SeatHeat", lambda: self._log_only("SeatHeat_L")),
            ("Navi", lambda: self.ui.open_screen("Navigation")),
            ("Apps", lambda: self.ui.open_screen("Apps")),
            ("Phone", lambda: self._log_only("Phone")),
            ("Menu", lambda: self._log_only("Menu")),
            ("Internet", lambda: self._log_only("Internet")),
            ("Music", lambda: self.ui.open_screen("Music")),
            ("L.SeatVent", lambda: self._log_only("SeatVent_L")),
            ("R.SeatHeat", lambda: self._log_only("SeatHeat_R")),
            ("R.SeatVent", lambda: self._log_only("SeatVent_R")),
        ]

        for label, action in order:
            add(label, action)
            x += bw + gap

    def _log_only(self, name):
        # 상태 토글 대신 로깅만 해두고, 필요시 UI 상태값 연결하면 됨
        # self.ui.logger.log(self.ui.depth_path, name, pygame.mouse.get_pos(), len(self.ui.depth_path))
        print(f"Clicked: {name}")

    def draw(self, screen):
        y0 = self.ui.height - self.h
        pygame.draw.rect(screen, self.colors["BOTTOM"], (0, y0, self.w, self.h))
        mp = pygame.mouse.get_pos()
        for b in self.buttons:
            b.draw(screen, mp)
    
def _fit_into(src_size, max_size):
    sw, sh = src_size; mw, mh = max_size
    k = min(mw/sw, mh/sh)
    return (max(1, int(sw*k)), max(1, int(sh*k)))
