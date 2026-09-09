# SentenceParserPage 模組負責顯示日文句子分析頁面。
# 使用者可在此頁面輸入日文句子，系統會進行斷詞、品詞分析、
# 並以表格或列表形式顯示每個詞彙的詳細資訊與助詞說明。

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SentenceParserPage(QWidget):
    """SentenceParserPage 主要功能:
    1. 提供日文句子輸入欄位
    2. 呼叫 SentenceParser 進行斷詞與分析
    3. 以易讀格式顯示分析結果（表層形、基本形、品詞、助詞說明）
    4. 提供返回按鈕與清空功能
    """

    def __init__(self, i18n_system, sentence_parser, main_window):
        # 初始化頁面元件與事件連接
        super().__init__()
        self.i18n_system = i18n_system
        self.sentence_parser = sentence_parser
        self.main_window = main_window
        self.grammar_engine = "hybrid"
        self.init_ui()

    def init_ui(self):
        # 建立頁面主版面與所有 UI 元件
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # 標題標籤
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # 輸入欄位區域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        input_label = QLabel()
        input_label.setMinimumWidth(80)
        input_layout.addWidget(input_label)
        
        # 日文句子輸入欄位
        self.input_field = QLineEdit()
        font = QFont()
        font.setPointSize(14)
        self.input_field.setFont(font)
        self.input_field.setMinimumHeight(50)
        self.input_field.setPlaceholderText("輸入日文句子...")
        self.input_field.returnPressed.connect(self._on_parse_clicked)
        input_layout.addWidget(self.input_field)
        
        # 引擎切換按鈕
        self.btn_engine = QPushButton()
        self.btn_engine.setMinimumHeight(50)
        self.btn_engine.setMinimumWidth(150)
        self.btn_engine.clicked.connect(self._on_toggle_engine)
        input_layout.addWidget(self.btn_engine)

        # 分析按鈕
        btn_parse = QPushButton()
        btn_parse.setMinimumHeight(50)
        btn_parse.setMinimumWidth(100)
        btn_parse.clicked.connect(self._on_parse_clicked)
        input_layout.addWidget(btn_parse)
        
        layout.addLayout(input_layout)
        
        # 提示信息
        hint = QLabel()
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        hint.setFont(font)
        layout.addWidget(hint)
        
        # 結果顯示區域（使用 QTextEdit 支援多行格式化文字）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(11)
        self.result_text.setFont(font)
        scroll.setWidget(self.result_text)
        layout.addWidget(scroll)
        
        # 底部按鈕區域
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 清空按鈕
        btn_clear = QPushButton()
        btn_clear.setMinimumHeight(50)
        btn_clear.clicked.connect(self._on_clear_clicked)
        bottom_layout.addWidget(btn_clear)
        
        # 返回按鈕
        btn_return = QPushButton()
        btn_return.setMinimumHeight(50)
        btn_return.clicked.connect(lambda: self.main_window.show_page("mode"))
        bottom_layout.addWidget(btn_return)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # 保存元件引用以便更新文字
        self.title_label = title
        self.input_label = input_label
        self.hint_label = hint
        self.btn_engine = self.btn_engine
        self.btn_parse = btn_parse
        self.btn_clear = btn_clear
        self.btn_return = btn_return
        
        self.update_texts()

    def update_texts(self):
        # 根據語言系統更新所有文字標籤
        self.title_label.setText(self.i18n_system.get_text("page_SP_title"))
        self.input_label.setText(self.i18n_system.get_text("page_SP_input"))
        self.hint_label.setText(self.i18n_system.get_text("page_SP_hint"))
        self.btn_parse.setText(self.i18n_system.get_text("common_btn_parse"))
        self.btn_clear.setText(self.i18n_system.get_text("common_btn_clear"))
        self.btn_return.setText(self.i18n_system.get_text("common_btn_return"))
        self._update_engine_button_text()
        self.btn_engine.setEnabled(self.sentence_parser.is_language_tool_available())

    def _get_engine_display_text(self):
        if self.grammar_engine == "language_tool":
            return self.i18n_system.get_text("page_SP_engine_language_tool")
        if self.grammar_engine == "hybrid":
            return self.i18n_system.get_text("page_SP_engine_hybrid")
        return self.i18n_system.get_text("page_SP_engine_local")

    def _update_engine_button_text(self):
        engine_text = self._get_engine_display_text()
        button_label = self.i18n_system.get_text("page_SP_engine_button")
        self.btn_engine.setText(f"{button_label}: {engine_text}")

    def _on_toggle_engine(self):
        engines = ["local", "hybrid"]
        if self.sentence_parser.is_language_tool_available():
            engines.append("language_tool")

        if self.grammar_engine not in engines:
            self.grammar_engine = "hybrid"
        else:
            current_index = engines.index(self.grammar_engine)
            self.grammar_engine = engines[(current_index + 1) % len(engines)]

        self._update_engine_button_text()

    def _on_parse_clicked(self):
        # 取得使用者輸入，進行日文句子分析
        sentence = self.input_field.text().strip()
        
        if not sentence:
            self.result_text.setText(
                self.i18n_system.get_text("page_SP_empty")
            )
            return
        
        # 檢查是否為日文
        if not self.sentence_parser.is_japanese(sentence):
            self.result_text.setText(
                self.i18n_system.get_text("page_SP_not_japanese")
            )
            return
        
        try:
            # 進行句子分析
            parsed = self.sentence_parser.parse_sentence(sentence)
            
            if not parsed:
                self.result_text.setText(
                    self.i18n_system.get_text("page_SP_parse_error")
                )
                return
            
            # 格式化輸出結果
            output_lines = []
            output_lines.append(f"【原句】{sentence}\n")
            output_lines.append(f"【{self.i18n_system.get_text('page_SP_engine_title')}】 {self._get_engine_display_text()}\n")

            # 進行文法檢測
            grammar_title = self.i18n_system.get_text('page_SP_grammar_title')
            grammar_error_label = self.i18n_system.get_text('page_SP_grammar_error')
            grammar_suggestion_label = self.i18n_system.get_text('page_SP_grammar_suggestion')

            grammar = self.sentence_parser.check_grammar(sentence, engine=self.grammar_engine)
            if grammar and not grammar.get("is_correct", True):
                output_lines.append(f"【{grammar_title}】")
                output_lines.append(grammar_error_label)
                for error in grammar.get("errors", []):
                    output_lines.append(f"- {error}")
                suggestion = grammar.get("suggestion", "")
                if suggestion:
                    output_lines.append(f"{grammar_suggestion_label} {suggestion}")
                output_lines.append("")
            else:
                output_lines.append(
                    f"【{grammar_title}】 {self.i18n_system.get_text('page_SP_grammar_ok')}"
                )
                output_lines.append("")

            output_lines.append("【分析結果】\n")
            output_lines.append("-" * 120)
            output_lines.append("")

            # 逐個詞彙顯示分析結果
            for idx, item in enumerate(parsed, 1):
                surface = item.get("surface", "")
                base = item.get("base", surface)
                pos = item.get("pos", "N/A")
                reading = item.get("reading", "")
                infl_type = item.get("infl_type", "")
                infl_form = item.get("infl_form", "")
                particle_cat = item.get("particle_category", "")
                particle_mean = item.get("particle_meaning", "")

                # 組建詞彙資訊行
                info_line = f"{idx}. 【{surface}】"
                info_line += f"\n   基本形: {base}"
                info_line += f" | 品詞: {pos}"
                info_line += f" | 讀音: {reading}"

                if infl_type:
                    info_line += f" | 活用型: {infl_type}/{infl_form}"

                if particle_cat:
                    info_line += f"\n   助詞類別: {particle_cat}"
                    if particle_mean:
                        info_line += f" | 意義: {particle_mean}"

                output_lines.append(info_line)
                output_lines.append("")

            # 顯示結果
            self.result_text.setText("\n".join(output_lines))
            
        except Exception as e:
            self.result_text.setText(
                f"【錯誤】\n分析過程中發生錯誤：{str(e)}"
            )

    def _on_clear_clicked(self):
        # 清空輸入欄位與結果顯示區
        self.input_field.clear()
        self.result_text.clear()
        self.input_field.setFocus()
