from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt

'''
MainWindow 模組負責整合各個頁面並管理主要視窗。
這個模組會建立 QStackedWidget 作為中央元件，並提供頁面切換功能。
它也會保存語言系統與音訊播放器實例，方便在視窗關閉時做資源清理。
'''

class MainWindow(QMainWindow):
    def __init__(self, i18n_system, data_loader, audio_player):
        super().__init__()
        self.i18n_system = i18n_system
        self.data_loader = data_loader
        self.audio_player = audio_player
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.setMinimumSize(600, 500)
        self.pages = {}
        self.update_title()

    def add_page(self, name, page_widget):
        self.stacked_widget.addWidget(page_widget)
        self.pages[name] = page_widget

    def show_page(self, name):
        if name in self.pages:
            index = self.stacked_widget.indexOf(self.pages[name])
            if index != -1:
                self.stacked_widget.setCurrentIndex(index)

    def update_title(self):
        self.setWindowTitle(self.i18n_system.get_text("common_ui_title"))

    def closeEvent(self, event):
        self.audio_player.cleanup_all()
        super().closeEvent(event)
