import sys
import csv
import os
from datetime import datetime
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt


LOG_FILE = "touch_log.csv"


class PLEOSPrototype(QWidget):
    def __init__(self):
        super().__init__()

        # 기본 상태
        self.depth_path = ["홈"]  # 현재 경로
        self.depth_max = 3  # 총 뎁스 수 가정

        # 기본 UI 세팅
        self.setWindowTitle("PLEOS Prototype")
        self.setGeometry(200, 200, 600, 400)

        # 상단: 현재 위치 표시
        self.path_label = QLabel(self.get_path_text())
        self.path_label.setAlignment(Qt.AlignRight)

        # 메인 버튼
        self.nav_button = QPushButton("내비게이션")
        self.search_button = QPushButton("검색")
        self.route_button = QPushButton("길찾기")
        self.back_button = QPushButton("뒤로가기")
        self.view_log_button = QPushButton("로그 보기")

        # 버튼 클릭 시 슬롯 연결
        self.nav_button.clicked.connect(lambda: self.navigate_to("내비게이션"))
        self.search_button.clicked.connect(lambda: self.navigate_to("검색"))
        self.route_button.clicked.connect(lambda: self.navigate_to("길찾기"))
        self.back_button.clicked.connect(self.go_back)
        self.view_log_button.clicked.connect(self.show_log)

        # 로그 표시용 텍스트창
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setVisible(False)

        # 레이아웃 구성
        button_layout = QHBoxLayout()
        for b in [self.nav_button, self.search_button, self.route_button, self.back_button, self.view_log_button]:
            button_layout.addWidget(b)

        layout = QVBoxLayout()
        layout.addWidget(self.path_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.log_view)
        self.setLayout(layout)

        # 클릭 로깅 이벤트
        self.setMouseTracking(True)

        # 로그 파일 초기화
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["시간", "디렉토리", "클릭 대상", "좌표(x,y)", "뎁스"])

    def get_path_text(self):
        return f"현재 위치: {' / '.join(self.depth_path)}  ({len(self.depth_path)} / {self.depth_max})"

    def navigate_to(self, dest):
        if len(self.depth_path) < self.depth_max:
            self.depth_path.append(dest)
            self.update_path_label()
            self.log_click(dest, f"버튼: {dest}", None)
        else:
            self.log_view.append("⚠️ 더 이상 하위 메뉴 없음")

    def go_back(self):
        if len(self.depth_path) > 1:
            prev = self.depth_path.pop()
            self.update_path_label()
            self.log_click("뒤로가기", f"이전: {prev}", None)

    def update_path_label(self):
        self.path_label.setText(self.get_path_text())

    def log_click(self, target, description, pos):
        """로그 파일에 클릭 내용 저장"""
        x, y = (pos.x(), pos.y()) if pos else ("-", "-")
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                " / ".join(self.depth_path),
                description,
                f"({x}, {y})",
                f"{len(self.depth_path)}/{self.depth_max}",
            ])

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트: 클릭 좌표 및 대상 기록"""
        widget = self.childAt(event.pos())
        if isinstance(widget, QPushButton):
            target_name = widget.text()
        else:
            target_name = "화면(빈 공간)"
        self.log_click(target_name, f"클릭: {target_name}", event.pos())

    def show_log(self):
        """CSV 로그 조회"""
        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
            self.log_view.setVisible(True)
            self.log_view.setText(df.to_string(index=False))
        else:
            self.log_view.setVisible(True)
            self.log_view.setText("로그 파일이 없습니다.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PLEOSPrototype()
    window.show()
    sys.exit(app.exec_())
