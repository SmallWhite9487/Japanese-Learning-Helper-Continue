from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

'''
KanaPracticePage 模組負責顯示假名練習題目頁面。
它會根據練習模式與難度顯示題目文字、選項按鈕或輸入欄，並更新分數。
使用者可以在此頁面答題、切換返回模式選擇頁面。
'''

class KanaPracticePage(QWidget):
    def __init__(self, i18n_system, data_loader, kana_practice, main_window):
        super().__init__()
        self.i18n_system = i18n_system
        self.data_loader = data_loader
        self.kana_practice = kana_practice
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 20, 40, 20)
        
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        kana_label = QLabel()
        kana_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(80)
        kana_label.setFont(font)
        kana_label.setStyleSheet("border: 3px solid; padding: 20px;")
        layout.addWidget(kana_label)
        
        score_label = QLabel()
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        score_label.setFont(font)
        layout.addWidget(score_label)
        
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout()
        self.options_container.setLayout(self.options_layout)
        layout.addWidget(self.options_container)
        
        btn_return = QPushButton()
        btn_return.setMinimumHeight(50)
        btn_return.clicked.connect(lambda: self.main_window.show_page("mode"))
        layout.addWidget(btn_return)
        
        self.setLayout(layout)
        
        self.title_label = title
        self.kana_label = kana_label
        self.score_label = score_label
        self.return_button = btn_return
        self.option_buttons = []
        self.text_input = None

    def update_texts(self):
        self.return_button.setText(self.i18n_system.get_text("common_btn_return"))

    def start_practice(self, mode, difficulty):
        self.kana_practice.set_mode(mode)
        self.kana_practice.set_difficulty(difficulty)
        self.kana_practice.reset_score()
        
        title_key = {
            "RFH": "page_RFH_title",
            "RFK": "page_RFK_title",
            "HFR": "page_HFR_title",
            "KFR": "page_KFR_title",
            "KFH": "page_KFH_title"
        }.get(mode, "page_RFH_title")
        self.title_label.setText(self.i18n_system.get_text(title_key))
        
        self._generate_question()

    def _generate_question(self):
        question = self.kana_practice.generate_question()
        self.kana_label.setText(question)
        
        correct, wrong = self.kana_practice.get_score()
        self.score_label.setText(f"✓ {correct}  ✗ {wrong}")
        
        self._setup_options()

    def _setup_options(self):
        self._clear_layout(self.options_layout)
        self.option_buttons = []
        self.text_input = None
        
        difficulty = self.kana_practice.difficulty
        
        if difficulty == "h":
            hbox = QHBoxLayout()
            self.text_input = QLineEdit()
            font = QFont()
            font.setPointSize(20)
            self.text_input.setFont(font)
            self.text_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.text_input.setMinimumHeight(50)
            self.text_input.returnPressed.connect(self._on_text_enter)
            hbox.addWidget(self.text_input)
            
            btn_enter = QPushButton()
            btn_enter.setText(self.i18n_system.get_text("common_btn_enter"))
            btn_enter.setMinimumHeight(50)
            btn_enter.clicked.connect(self._on_text_enter)
            hbox.addWidget(btn_enter)
            
            self.options_layout.addLayout(hbox)
        else:
            options = self.kana_practice.get_current_options()
            count = len(options)
            rows = count // 4
            
            for row in range(rows):
                hbox = QHBoxLayout()
                for col in range(4):
                    idx = row * 4 + col
                    if idx < len(options):
                        btn = QPushButton(options[idx])
                        btn.setMinimumHeight(70)
                        font = QFont()
                        font.setPointSize(24)
                        btn.setFont(font)
                        btn.clicked.connect(lambda checked, opt=options[idx]: self._on_option_click(opt))
                        self.option_buttons.append(btn)
                        hbox.addWidget(btn)
                self.options_layout.addLayout(hbox)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _on_option_click(self, option):
        self.kana_practice.check_answer(option)
        self._generate_question()

    def _on_text_enter(self):
        if self.text_input:
            text = self.text_input.text()
            self.kana_practice.check_answer(text)
            self.text_input.clear()
            self._generate_question()
