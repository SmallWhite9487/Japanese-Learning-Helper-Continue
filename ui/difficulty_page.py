from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

'''
DifficultyPage 模組負責顯示練習題目難度選擇頁面。
根據使用者選擇的模式與難度，將控制權交給 KanaPracticePage 進行題目生成。
'''

class DifficultyPage(QWidget):
    def __init__(self, i18n_system, main_window):
        super().__init__()
        self.i18n_system = i18n_system
        self.main_window = main_window
        self.current_mode = "RFH"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        btn_easy = QPushButton()
        btn_easy.setMinimumHeight(60)
        btn_easy.clicked.connect(lambda: self._select_difficulty("e"))
        
        btn_medium = QPushButton()
        btn_medium.setMinimumHeight(60)
        btn_medium.clicked.connect(lambda: self._select_difficulty("m"))
        
        btn_hard = QPushButton()
        btn_hard.setMinimumHeight(60)
        btn_hard.clicked.connect(lambda: self._select_difficulty("h"))
        
        btn_return = QPushButton()
        btn_return.setMinimumHeight(50)
        btn_return.clicked.connect(lambda: self.main_window.show_page("mode"))
        
        layout.addWidget(btn_easy)
        layout.addWidget(btn_medium)
        layout.addWidget(btn_hard)
        layout.addWidget(btn_return)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.title_label = title
        self.buttons = {
            "easy": btn_easy,
            "medium": btn_medium,
            "hard": btn_hard,
            "return": btn_return
        }
        self.update_texts()

    def update_texts(self):
        self.title_label.setText(self.i18n_system.get_text("page_difficulty_title"))
        self.buttons["easy"].setText(self.i18n_system.get_text("difficulty_easy"))
        self.buttons["medium"].setText(self.i18n_system.get_text("difficulty_medium"))
        self.buttons["hard"].setText(self.i18n_system.get_text("difficulty_hard"))
        self.buttons["return"].setText(self.i18n_system.get_text("common_btn_return"))

    def set_mode(self, mode):
        self.current_mode = mode

    def _select_difficulty(self, difficulty):
        practice_page = self.main_window.pages.get("kana_practice")
        if practice_page:
            practice_page.start_practice(self.current_mode, difficulty)
        self.main_window.show_page("kana_practice")
