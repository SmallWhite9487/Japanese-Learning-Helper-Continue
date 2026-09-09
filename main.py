import base64
import json
import os
import sys

from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication
from modules import (
    DataLoader, I18nSystem, AudioPlayer, 
    VerbConjugator, SentenceParser, KanaPractice
)
from ui import (
    MainWindow, ModePage, DifficultyPage,
    KanaPracticePage, ChartPage, VerbConjugationPage, SentenceParserPage
)

'''
主程式

功能說明:
這個主程式會建立整個 Japanese Learning Helper 的 GUI 應用程式。
會呼叫以下模組與元件:
- DataLoader: 讀取五十音與語言文字資料
- I18nSystem: 負責多國語系文字翻譯與語言切換
- AudioPlayer: 透過文字轉語音播放日語音檔
- VerbConjugator: 解析並變化日語動詞
- SentenceParser: 提供日文句子斷詞與品詞分析功能
- KanaPractice: 管理五十音練習題目與答題邏輯

輸出:
- 啟動一個 PyQt6 GUI 視窗
- 提供使用者切換模式、語言、難度，練習假名、查看五十音表、動詞變化、句子分析
- 由主視窗串接各頁面，最終輸出為互動式學習介面
'''

def _load_app_icon():
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_path, "data", "images.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            encoded_icon = json.load(file).get("icon", "")
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(encoded_icon))
        return QIcon(pixmap)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return QIcon()


def main():
    # 建立 QApplication，管理整個 GUI 事件循環
    app = QApplication(sys.argv)
    app.setApplicationName("Japanese Learning Helper")
    app_icon = _load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    
    # 初始化資料與功能模組
    data_loader = DataLoader()
    i18n_system = I18nSystem()
    audio_player = AudioPlayer()
    verb_conjugator = VerbConjugator()
    kana_practice = KanaPractice(data_loader)
    sentence_parser = SentenceParser()
    
    # 建立主視窗並註冊各頁面
    main_window = MainWindow(i18n_system, data_loader, audio_player)
    
    # 模式選擇頁面
    mode_page = ModePage(i18n_system, main_window)
    main_window.add_page("mode", mode_page)
    
    # 難度選擇頁面
    difficulty_page = DifficultyPage(i18n_system, main_window)
    main_window.add_page("difficulty", difficulty_page)
    
    # 假名練習頁面
    kana_practice_page = KanaPracticePage(i18n_system, data_loader, kana_practice, main_window)
    main_window.add_page("kana_practice", kana_practice_page)
    
    # 五十音表頁面
    chart_page = ChartPage(i18n_system, data_loader, audio_player, main_window)
    main_window.add_page("chart", chart_page)
    
    # 動詞變化頁面
    verb_conjugation_page = VerbConjugationPage(i18n_system, verb_conjugator, main_window)
    main_window.add_page("verb_conjugation", verb_conjugation_page)
    
    # 句子分析頁面
    sentence_parser_page = SentenceParserPage(i18n_system, sentence_parser, main_window)
    main_window.add_page("sentence_parser", sentence_parser_page)
    
    # 首頁預設顯示模式選擇頁面
    main_window.show_page("mode")
    main_window.show()
    
    # 開始 Qt 事件迴圈，直到視窗關閉
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
