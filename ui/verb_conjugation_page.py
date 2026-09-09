from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

'''
VerbConjugationPage 模組負責顯示日語動詞變化頁面。
使用者輸入日語動詞後，會呼叫 VerbConjugator 解析並顯示不同的變化形態。
同時提供返回模式選擇頁面的按鈕。
'''

class VerbConjugationPage(QWidget):
    def __init__(self, i18n_system, verb_conjugator, main_window):
        super().__init__()
        self.i18n_system = i18n_system
        self.verb_conjugator = verb_conjugator
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
        
        self.input_field = QLineEdit()
        font = QFont()
        font.setPointSize(24)
        self.input_field.setFont(font)
        self.input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_field.setMinimumHeight(60)
        self.input_field.textChanged.connect(self._on_input_changed)
        layout.addWidget(self.input_field)
        
        hint = QLabel()
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        hint.setFont(font)
        layout.addWidget(hint)
        
        self.conjugation_labels = []
        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setContentsMargins(20, 20, 20, 20)
        
        positions = [
            (0, 0), (0, 1), (0, 2), (0, 3),
            (1, 0), (1, 1), (1, 2), (1, 3)
        ]
        
        for row, col in positions:
            container = QVBoxLayout()
            
            label_title = QLabel()
            label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            label_title.setFont(font)
            container.addWidget(label_title)
            
            label_value = QLabel("—")
            label_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_value.setMinimumHeight(50)
            font = QFont()
            font.setPointSize(16)
            label_value.setFont(font)
            label_value.setStyleSheet("border: 2px solid; padding: 10px;")
            container.addWidget(label_value)
            
            self.conjugation_labels.append((label_title, label_value))
            grid.addLayout(container, row, col)
        
        layout.addLayout(grid)
        
        btn_return = QPushButton()
        btn_return.setMinimumHeight(50)
        btn_return.clicked.connect(lambda: self.main_window.show_page("mode"))
        layout.addWidget(btn_return)
        
        self.setLayout(layout)
        
        self.title_label = title
        self.hint_label = hint
        self.return_button = btn_return
        self.update_texts()

    def update_texts(self):
        self.title_label.setText(self.i18n_system.get_text("page_VC_title"))
        self.hint_label.setText(self.i18n_system.get_text("page_VC_entry"))
        self.return_button.setText(self.i18n_system.get_text("common_btn_return"))
        
        conjugation_keys = [
            "page_VC_PF", "page_VC_NF", "page_VC_PaF", "page_VC_CF",
            "page_VC_PoF", "page_VC_VF", "page_VC_IF", "page_VC_CoF"
        ]
        
        for idx, (label_title, label_value) in enumerate(self.conjugation_labels):
            if idx < len(conjugation_keys):
                label_title.setText(self.i18n_system.get_text(conjugation_keys[idx]))

    def _on_input_changed(self, text):
        if self.verb_conjugator.is_japanese(text):
            conjugations = self.verb_conjugator.conjugate_verb(text)
            conjugation_order = [
                "ます形", "ない形", "た形", "て形",
                "可能形", "意志形", "命令形", "条件形"
            ]
            
            for idx, (label_title, label_value) in enumerate(self.conjugation_labels):
                if idx < len(conjugation_order):
                    key = conjugation_order[idx]
                    label_value.setText(conjugations.get(key, "—"))
        else:
            for label_title, label_value in self.conjugation_labels:
                label_value.setText("—")
