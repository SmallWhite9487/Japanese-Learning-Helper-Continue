from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class UI:
    page_margins = (40, 40, 40, 40)
    page_spacing = 20
    title_font_size = 20
    button_height = 64
    button_min_height = 50
    combo_min_height = 48
    combo_style = "QComboBox { padding: 8px 12px; border: 1px solid #d9dee8; border-radius: 12px; background: #ffffff; font-size: 15px; }"

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
        layout.setSpacing(UI.page_spacing)
        layout.setContentsMargins(*UI.page_margins)
        
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(UI.title_font_size)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        direction_layout = QHBoxLayout()
        self.source_combo = QComboBox()
        self.target_combo = QComboBox()
        for combo in (self.source_combo, self.target_combo):
            combo.setMinimumHeight(UI.combo_min_height)
            combo.setStyleSheet(UI.combo_style)
        direction_layout.addWidget(self.source_combo)
        direction_layout.addWidget(self.target_combo)
        layout.addLayout(direction_layout)
        
        btn_easy = QPushButton()
        btn_easy.setMinimumHeight(UI.button_height)
        btn_easy.clicked.connect(lambda: self._select_difficulty("e"))
        
        btn_medium = QPushButton()
        btn_medium.setMinimumHeight(UI.button_height)
        btn_medium.clicked.connect(lambda: self._select_difficulty("m"))
        
        btn_hard = QPushButton()
        btn_hard.setMinimumHeight(UI.button_height)
        btn_hard.clicked.connect(lambda: self._select_difficulty("h"))
        
        btn_return = QPushButton()
        btn_return.setMinimumHeight(UI.button_min_height)
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
        self.source_combo.currentIndexChanged.connect(self._keep_directions_distinct)
        self.target_combo.currentIndexChanged.connect(self._keep_directions_distinct)
        self._populate_type_combos()
        self.update_texts()

    def _populate_type_combos(self):
        types = [("h", "kana_hiragana"), ("k", "kana_katakana"), ("r", "kana_romaji")]
        for combo in (self.source_combo, self.target_combo):
            combo.blockSignals(True)
            combo.clear()
            for value, key in types:
                combo.addItem(self.i18n_system.get_text(key), value)
            combo.blockSignals(False)
        self.source_combo.setCurrentIndex(0)
        self.target_combo.setCurrentIndex(2)

    def _keep_directions_distinct(self):
        if self.source_combo.currentData() == self.target_combo.currentData():
            next_index = (self.target_combo.currentIndex() + 1) % self.target_combo.count()
            self.target_combo.blockSignals(True)
            self.target_combo.setCurrentIndex(next_index)
            self.target_combo.blockSignals(False)

    def update_texts(self):
        self.title_label.setText(self.i18n_system.get_text("page_difficulty_title"))
        self.source_combo.setToolTip(self.i18n_system.get_text("kana_source_hint"))
        self.target_combo.setToolTip(self.i18n_system.get_text("kana_target_hint"))
        self.buttons["easy"].setText(self.i18n_system.get_text("difficulty_easy"))
        self.buttons["medium"].setText(self.i18n_system.get_text("difficulty_medium"))
        self.buttons["hard"].setText(self.i18n_system.get_text("difficulty_hard"))
        self.buttons["return"].setText(self.i18n_system.get_text("common_btn_return"))

    def set_mode(self, mode):
        self.current_mode = mode

    def _select_difficulty(self, difficulty):
        practice_page = self.main_window.pages.get("kana_practice")
        if practice_page:
            practice_page.start_practice(
                self.current_mode,
                difficulty,
                self.source_combo.currentData(),
                self.target_combo.currentData(),
            )
        self.main_window.show_page("kana_practice")
