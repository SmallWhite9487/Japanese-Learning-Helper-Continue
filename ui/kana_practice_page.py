from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class UI:
    margins = (40, 20, 40, 20)
    spacing = 10
    title_font_size = 20
    title_style = "font-size: 24px; font-weight: 800; color: #172033; padding: 4px;"
    body_font_size = 14
    kana_font_size = 60
    button_min_height = 50
    surface_style = "background: #f7f8fa; border: 1px solid #e2e8f0; border-radius: 24px; padding: 20px; color: #172033;"
    option_style = "QPushButton { background: #ffffff; border: 1px solid #d9dee8; border-radius: 14px; color: #172033; padding: 8px; } QPushButton:hover { background: #edf2f7; border-color: #94a3b8; }"

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
        layout.setSpacing(UI.spacing)
        layout.setContentsMargins(*UI.margins)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(UI.title_font_size)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet(UI.title_style)
        layout.addWidget(title)

        direction_label = QLabel()
        direction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        direction_label.setStyleSheet(f"font-size: {UI.body_font_size}px; color: #718096; font-style: italic;")
        layout.addWidget(direction_label)
        
        kana_label = QLabel()
        kana_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(UI.kana_font_size)
        kana_label.setFont(font)
        kana_label.setMinimumHeight(210)
        kana_label.setStyleSheet(UI.surface_style)
        layout.addWidget(kana_label)
        
        score_label = QLabel()
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(UI.body_font_size + 2)
        score_label.setFont(font)
        score_label.setStyleSheet(f"font-size: {UI.body_font_size + 2}px; color: #172033; font-weight: bold;")
        layout.addWidget(score_label)
        
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout()
        self.options_container.setLayout(self.options_layout)
        self.options_container.setStyleSheet(UI.option_style)
        layout.addWidget(self.options_container)
        
        btn_return = QPushButton()
        btn_return.setMinimumHeight(UI.button_min_height)
        btn_return.clicked.connect(lambda: self.main_window.show_page("mode"))
        layout.addWidget(btn_return)
        
        self.setLayout(layout)
        
        self.title_label = title
        self.direction_label = direction_label
        self.kana_label = kana_label
        self.score_label = score_label
        self.return_button = btn_return
        self.option_buttons = []
        self.text_input = None

    def update_texts(self):
        self.return_button.setText(self.i18n_system.get_text("common_btn_return"))
        self.direction_label.setText(self._direction_text())

    def _direction_text(self):
        labels = {"h": "kana_hiragana", "k": "kana_katakana", "r": "kana_romaji"}
        source = self.i18n_system.get_text(labels[self.kana_practice.source_type])
        target = self.i18n_system.get_text(labels[self.kana_practice.target_type])
        return f"{source}  →  {target}"

    def start_practice(self, mode, difficulty, source_type=None, target_type=None):
        if source_type is not None and target_type is not None:
            self.kana_practice.set_types(source_type, target_type)
        else:
            self.kana_practice.set_mode(mode)
        self.kana_practice.set_difficulty(difficulty)
        self.kana_practice.reset_score()
        self.title_label.setText(self.i18n_system.get_text("page_kana_practice_title"))
        self.direction_label.setText(self._direction_text())
        
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
                        font.setPointSize(20)
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
