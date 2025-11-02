import pygame
import sys
import csv
import os
import pandas as pd
from datetime import datetime

pygame.init()

# 화면 크기
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PLEOS Prototype (pygame ver.)")

# 색상
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)

# 폰트
font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 18)

# CSV 파일 초기화
LOG_FILE = "touch_log.csv"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["시간", "디렉토리", "클릭 대상", "좌표(x,y)", "뎁스"])

# 버튼 정의
class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=10)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# 기본 버튼들
buttons = [
    Button("Navigation", 100, 150, 200, 60),
    Button("Search", 100, 230, 200, 60),
    Button("Find Route", 100, 310, 200, 60),
    Button("Back", 350, 150, 200, 60),
    Button("log", 350, 230, 200, 60)
]

# 상태
depth_path = ["Home"]
depth_max = 3


# 함수들
def get_path_text():
    return f"{' / '.join(depth_path)} ({len(depth_path)}/{depth_max})"


def log_click(target, pos):
    """클릭 이벤트를 CSV에 기록"""
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            " / ".join(depth_path),
            target,
            f"({pos[0]}, {pos[1]})",
            f"{len(depth_path)}/{depth_max}"
        ])


def navigate_to(dest):
    global depth_path
    if len(depth_path) < depth_max:
        depth_path.append(dest)
        log_click(f"버튼: {dest}", (0, 0))


def go_back():
    global depth_path
    if len(depth_path) > 1:
        prev = depth_path.pop()
        log_click(f"뒤로가기(이전: {prev})", (0, 0))


def show_log():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        print("\n===== [CSV LOG 조회] =====")
        print(df.to_string(index=False))
        print("===========================\n")
    else:
        print("로그 파일이 없습니다.")


# 메인 루프
running = True
while running:
    screen.fill(WHITE)

    # 현재 위치 표시
    path_text = small_font.render(f"Curr_dir: {get_path_text()}", True, BLACK)
    screen.blit(path_text, (WIDTH - path_text.get_width() - 20, 20))

    # 버튼 그리기
    for b in buttons:
        b.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            clicked_button = None

            for b in buttons:
                if b.is_clicked(pos):
                    clicked_button = b.text
                    break

            if clicked_button:
                if clicked_button == "뒤로가기":
                    go_back()
                elif clicked_button == "로그 보기":
                    show_log()
                else:
                    navigate_to(clicked_button)
            else:
                log_click("화면(빈 공간)", pos)

    pygame.display.flip()

pygame.quit()
sys.exit()
