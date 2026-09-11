from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QScrollArea, QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class UI:
    margins = (20, 20, 20, 20)
    spacing = 10
    chart_spacing = 20
    title_font_size = 20
    button_height = 50

'''
ChartPage 模組負責顯示五十音表與對應讀音的頁面。
它會從 DataLoader 取得平假名、片假名與羅馬字轉換資料，並以按鈕形式呈現。
使用者點擊假名按鈕時，會呼叫 AudioPlayer 播放日語發音。
'''

class ChartPage(QWidget):
    def __init__(self, i18n_system, data_loader, audio_player, main_window):
        super().__init__()
        self.i18n_system = i18n_system
        self.data_loader = data_loader
        self.audio_player = audio_player
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(UI.spacing)
        layout.setContentsMargins(*UI.margins)
        
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(UI.title_font_size)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(UI.chart_spacing)
        scroll_content.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        btn_return = QPushButton()
        btn_return.setMinimumHeight(UI.button_height)
        btn_return.clicked.connect(lambda: self.main_window.show_page("mode"))
        layout.addWidget(btn_return)
        
        self.setLayout(layout)
        
        self.title_label = title
        self.return_button = btn_return
        self.update_texts()

    def update_texts(self):
        self.title_label.setText(self.i18n_system.get_text("page_GC_title"))
        self.return_button.setText(self.i18n_system.get_text("common_btn_return"))
        self._render_chart()

    def _render_chart(self):
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
        
        format_kana_list = [
            ["あ", "い", "う", "え", "お"],
            ["か", "き", "く", "け", "こ"],
            ["さ", "し", "す", "せ", "そ"],
            ["た", "ち", "つ", "て", "と"],
            ["な", "に", "ぬ", "ね", "の"],
            ["は", "ひ", "ふ", "へ", "ほ"],
            ["ま", "み", "む", "め", "も"],
            ["や", None, "ゆ", None, "よ"],
            ["ら", "り", "る", "れ", "ろ"],
            ["わ", None, None, None, "を"],
            ["ん", None, None, None, None]
        ]
        
        hiragana_to_romaji = self.data_loader.get_hiragana_to_romaji()
        hiragana_to_katakana = self.data_loader.get_hiragana_to_katakana()
        
        main_layout = QHBoxLayout()
        
        left_grid = QGridLayout()
        left_grid.setSpacing(5)
        for row_idx, row in enumerate(format_kana_list):
            for col_idx, hira in enumerate(row):
                if hira is None:
                    widget = QFrame()
                    widget.setMinimumSize(70, 70)
                    left_grid.addWidget(widget, row_idx, col_idx)
                else:
                    kata = hiragana_to_katakana.get(hira, "")
                    romaji = hiragana_to_romaji.get(hira, "")
                    text = f"{hira}   {kata}\n{romaji}"
                    btn = QPushButton(text)
                    btn.setMinimumSize(70, 70)
                    btn.setStyleSheet("text-align: center;")
                    btn.clicked.connect(lambda checked, h=hira: self._play_sound(h))
                    left_grid.addWidget(btn, row_idx, col_idx)
        
        left_widget = QWidget()
        left_widget.setLayout(left_grid)
        main_layout.addWidget(left_widget)
        
        right_grid = QGridLayout()
        right_grid.setSpacing(5)
        hiragana_list = self.data_loader.get_hiragana_list()
        remaining = hiragana_list[46:]
        
        for idx, hira in enumerate(remaining):
            row = idx // 5
            col = idx % 5
            kata = hiragana_to_katakana.get(hira, "")
            romaji = hiragana_to_romaji.get(hira, "")
            text = f"{hira}   {kata}\n{romaji}"
            btn = QPushButton(text)
            btn.setMinimumSize(70, 70)
            btn.setStyleSheet("text-align: center;")
            btn.clicked.connect(lambda checked, h=hira: self._play_sound(h))
            right_grid.addWidget(btn, row, col)
        
        right_widget = QWidget()
        right_widget.setLayout(right_grid)
        main_layout.addWidget(right_widget)
        
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.scroll_layout.addWidget(main_widget)

    def _play_sound(self, text):
        self.audio_player.play_sound(text)
