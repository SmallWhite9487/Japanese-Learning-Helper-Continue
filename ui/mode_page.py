import base64
import json
import os
import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QRect, QSize, QParallelAnimationGroup, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QBrush, QImage, QPixmap

'''
ModePage 模組負責顯示主要練習模式選擇頁面。
使用者可在此頁面切換假名練習模式、動詞變化頁面、五十音表頁面或語言設定頁面。
'''

class ModeArtwork(QWidget):
    """Small self-contained artwork for a mode card, drawn without external assets."""

    colors = {
        "RFH": ("#f08a5d", "#fff1e8"), "RFK": ("#5d9cec", "#eaf3ff"),
        "HFR": ("#61c0bf", "#e8fbfa"), "KFR": ("#9b8afb", "#f0edff"),
        "KFH": ("#f4b942", "#fff6df"), "VC": ("#e56b6f", "#fff0f0"),
        "GC": ("#42b883", "#e9fff5"), "SP": ("#64748b", "#eef2f7")
    }

    def __init__(self, mode, icon_data=None, start_callback=None, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.icon_image = self._load_image(icon_data)
        self.start_callback = start_callback
        self._art_opacity = 1.0
        self._hover_scale = 1.0
        self._hover_darkness = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

    def _animate_hover(self, entering):
        target_scale = 0.85 if entering else 1.0
        target_darkness = 0.15 if entering else 0.0
        group = QParallelAnimationGroup(self)
        for name, target in ((b"hover_scale", target_scale), (b"hover_darkness", target_darkness)):
            animation = QPropertyAnimation(self, name, group)
            animation.setStartValue(getattr(self, f"get_{name.decode()}")())
            animation.setEndValue(target)
            animation.setDuration(180)
            animation.setEasingCurve(QEasingCurve.Type.Linear)
            group.addAnimation(animation)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def enterEvent(self, event):
        self._animate_hover(True)

    def leaveEvent(self, event):
        self._animate_hover(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.start_callback:
            self.start_callback()
        super().mousePressEvent(event)

    @staticmethod
    def _load_image(icon_data):
        if not icon_data:
            return None
        try:
            image = QImage.fromData(base64.b64decode(icon_data))
            return image if not image.isNull() else None
        except (ValueError, TypeError):
            return None

    def get_art_opacity(self):
        return self._art_opacity

    def set_art_opacity(self, value):
        self._art_opacity = value
        self.update()

    art_opacity = pyqtProperty(float, get_art_opacity, set_art_opacity)

    def get_hover_scale(self):
        return self._hover_scale

    def set_hover_scale(self, value):
        self._hover_scale = value
        self.update()

    hover_scale = pyqtProperty(float, get_hover_scale, set_hover_scale)

    def get_hover_darkness(self):
        return self._hover_darkness

    def set_hover_darkness(self, value):
        self._hover_darkness = value
        self.update()

    hover_darkness = pyqtProperty(float, get_hover_darkness, set_hover_darkness)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._art_opacity)
        size = int(min(self.width(), self.height()) * self._hover_scale)
        draw_rect = QRect((self.width() - size) // 2, (self.height() - size) // 2, size, size)
        if self.icon_image is not None:
            painter.drawImage(draw_rect, self.icon_image)
        else:
            accent, background = self.colors[self.mode]
            rect = draw_rect.adjusted(4, 4, -4, -4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(background)))
            painter.drawRoundedRect(rect, 28, 28)
            painter.setBrush(QBrush(QColor(accent)))
            painter.drawEllipse(rect.center(), max(12, rect.width() // 5), max(12, rect.height() // 5))
            painter.setPen(QPen(QColor("#ffffff"), max(2, rect.width() // 24), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            cx, cy = rect.center().x(), rect.center().y()
            if self.mode in ("RFH", "RFK", "HFR", "KFR", "KFH"):
                painter.drawLine(cx - rect.width() // 7, cy, cx + rect.width() // 7, cy)
                painter.drawLine(cx, cy - rect.height() // 7, cx, cy + rect.height() // 7)
            elif self.mode == "VC":
                painter.drawArc(rect.adjusted(rect.width() // 4, rect.height() // 4, -rect.width() // 4, -rect.height() // 4), 30 * 16, 280 * 16)
                painter.drawLine(cx + rect.width() // 8, cy - rect.height() // 6, cx + rect.width() // 5, cy - rect.height() // 6)
            elif self.mode == "GC":
                painter.drawRect(rect.adjusted(rect.width() // 4, rect.height() // 4, -rect.width() // 4, -rect.height() // 4))
                painter.drawLine(cx, cy - rect.height() // 4, cx, cy + rect.height() // 4)
                painter.drawLine(cx - rect.width() // 4, cy, cx + rect.width() // 4, cy)
            else:
                painter.drawRoundedRect(rect.adjusted(rect.width() // 4, rect.height() // 3, -rect.width() // 4, -rect.height() // 3), 8, 8)
                painter.drawLine(cx - rect.width() // 10, cy, cx + rect.width() // 10, cy)
        if self._hover_darkness:
            painter.setOpacity(self._art_opacity * self._hover_darkness)
            painter.setBrush(QBrush(QColor("#000000")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(draw_rect, 28, 28)
        return


class AnimatedIconButton(QPushButton):
    """Fixed-size icon button with a linear pressed scale and darkness feedback."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._press_scale = 1.0
        self._press_darkness = 0.0
        self.setMouseTracking(True)

    def _animate_press(self, pressed):
        group = QParallelAnimationGroup(self)
        targets = ((b"press_scale", 0.85 if pressed else 1.0),
                   (b"press_darkness", 0.15 if pressed else 0.0))
        for name, target in targets:
            animation = QPropertyAnimation(self, name, group)
            animation.setStartValue(getattr(self, f"get_{name.decode()}")())
            animation.setEndValue(target)
            animation.setDuration(140)
            animation.setEasingCurve(QEasingCurve.Type.Linear)
            group.addAnimation(animation)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_press(True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._animate_press(False)
        super().mouseReleaseEvent(event)

    def get_press_scale(self):
        return self._press_scale

    def set_press_scale(self, value):
        self._press_scale = value
        self.update()

    press_scale = pyqtProperty(float, get_press_scale, set_press_scale)

    def get_press_darkness(self):
        return self._press_darkness

    def set_press_darkness(self, value):
        self._press_darkness = value
        self.update()

    press_darkness = pyqtProperty(float, get_press_darkness, set_press_darkness)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        base_rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#172033")))
        painter.drawRoundedRect(base_rect, 12, 12)
        icon_size = int(min(self.width(), self.height()) * 0.68 * self._press_scale)
        icon_rect = QRect(
            (self.width() - icon_size) // 2,
            (self.height() - icon_size) // 2,
            icon_size,
            icon_size,
        )
        self.icon().paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter, QIcon.Mode.Normal)
        if self._press_darkness:
            painter.setBrush(QBrush(QColor(0, 0, 0, int(255 * self._press_darkness))))
            painter.drawRoundedRect(base_rect, 12, 12)


class ModePage(QWidget):
    def __init__(self, i18n_system, main_window):
        super().__init__()
        self.i18n_system = i18n_system
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 8, 28, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: 800; color: #172033; "
            "padding: 2px 0 2px; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        self.modes = ["RFH", "RFK", "HFR", "KFR", "KFH", "VC", "GC", "SP"]
        self.icon_data = self._load_icon_data()
        self.current_index = 0
        self.is_animating = False
        self.carousel = QFrame()
        self.carousel.setMinimumHeight(340)
        self.carousel.setStyleSheet("QFrame { background: #f7f8fa; border-radius: 28px; }")
        carousel_layout = QHBoxLayout(self.carousel)
        carousel_layout.setContentsMargins(12, 18, 12, 18)

        self.previous_button = QPushButton("<")
        self.next_button = QPushButton(">")
        for button in (self.previous_button, self.next_button):
            button.setFixedSize(64, 108)
            button.setStyleSheet("QPushButton { background: #ffffff; border: 1px solid #e2e5ea; border-radius: 20px; color: #172033; font-size: 34px; font-weight: bold; } QPushButton:hover { background: #edf2f7; }")
        self.previous_button.clicked.connect(lambda: self._navigate(-1))
        self.next_button.clicked.connect(lambda: self._navigate(1))
        carousel_layout.addWidget(self.previous_button)

        self.art_stage = QWidget()
        self.art_stage.setMinimumSize(280, 280)
        self.art_stage.setStyleSheet("background: transparent;")
        carousel_layout.addWidget(self.art_stage, 1)
        carousel_layout.addWidget(self.next_button)
        layout.addWidget(self.carousel)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(14)
        self.language_button = AnimatedIconButton()
        self.language_button.setFixedSize(52, 52)
        self.language_button.setToolTip("Language")
        self.language_button.clicked.connect(self._cycle_language)
        info_layout.addWidget(self.language_button, 0, Qt.AlignmentFlag.AlignBottom)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.mode_title = QLabel()
        self.mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_title.setStyleSheet("font-size: 16px; color: #000000; font-weight: bold;")
        text_layout.addWidget(self.mode_title)
        self.mode_description = QLabel()
        self.mode_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_description.setStyleSheet("font-size: 14px; color: #888888; font-style: italic;")
        text_layout.addWidget(self.mode_description)
        info_layout.addLayout(text_layout, 1)
        self.language_spacer = QPushButton()
        self.language_spacer.setFixedSize(52, 52)
        self.language_spacer.setEnabled(False)
        self.language_spacer.setStyleSheet("QPushButton { background: transparent; border: none; }")
        info_layout.addWidget(self.language_spacer, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(info_layout)

        self.setLayout(layout)

        self.title_label = title
        self.current_art = None
        self._show_current_mode()
        self.update_texts()

    def _load_icon_data(self):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for filename in ("images.json",):
            path = os.path.join(base_path, "data", filename)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                return data if isinstance(data, dict) else {}
            except (OSError, json.JSONDecodeError):
                continue
        return {}

    def update_texts(self):
        self.title_label.setText(self.i18n_system.get_text("page_mode_title"))
        language_icon = self._get_icon("btn_i18")
        self.language_button.setIcon(language_icon)
        self.language_button.setText("" if not language_icon.isNull() else "文")
        self.language_button.setIconSize(self.language_button.size() - QSize(16, 16))
        self.language_button.setAccessibleName(
            f"{self.i18n_system.get_text('common_btn_language')}: "
            f"{self.i18n_system.get_language_name(self.i18n_system.current_lang)}"
        )
        self._update_mode_labels()

    def _get_icon(self, key):
        encoded = self.icon_data.get(key, "")
        if not encoded:
            return QIcon()
        try:
            image = QImage.fromData(base64.b64decode(encoded))
            if image.isNull():
                return QIcon()
            pixmap = QPixmap.fromImage(image)
            return QIcon(pixmap)
        except (ValueError, TypeError):
            return QIcon()

    def _update_mode_labels(self):
        mode = self.modes[self.current_index]
        self.mode_title.setText(self.i18n_system.get_text(f"mode_{mode}"))
        self.mode_description.setText(self.i18n_system.get_text(f"mode_{mode}_description"))

    def _show_current_mode(self):
        self.current_art = ModeArtwork(
            self.modes[self.current_index], self.icon_data.get(f"mode_{self.modes[self.current_index]}"), self._start_selected_mode, self.art_stage
        )
        self.current_art.setGeometry(self._center_geometry(256))
        self.current_art.show()
        self._update_mode_labels()
        QTimer.singleShot(0, self._position_current_art)

    def _position_current_art(self):
        if self.current_art is not None and not self.is_animating:
            self.current_art.setGeometry(self._center_geometry(256))

    def _center_geometry(self, size):
        return QRect(
            max(0, (self.art_stage.width() - size) // 2),
            max(0, (self.art_stage.height() - size) // 2),
            size,
            size,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_art is not None and not self.is_animating:
            self.current_art.setGeometry(self._center_geometry(256))

    def _navigate(self, direction):
        if self.is_animating:
            return
        old_index = self.current_index
        self.current_index = (self.current_index + direction) % len(self.modes)
        boundary_jump = direction < 0 and old_index == 0
        self._animate_to_current(direction, boundary_jump)

    def _animate_to_current(self, direction, boundary_jump):
        self.is_animating = True
        old_art = self.current_art
        new_art = ModeArtwork(
            self.modes[self.current_index], self.icon_data.get(f"mode_{self.modes[self.current_index]}"), self._start_selected_mode, self.art_stage
        )
        new_art.show()
        new_effect = QGraphicsOpacityEffect(new_art)
        new_art.setGraphicsEffect(new_effect)
        old_effect = QGraphicsOpacityEffect(old_art)
        old_art.setGraphicsEffect(old_effect)
        center = self._center_geometry(256)
        small_x = self.art_stage.width() if direction > 0 else -64
        small_y = max(0, (self.art_stage.height() - 64) // 2)
        small = QRect(small_x, small_y, 64, 64)
        old_x = -256 if direction > 0 else self.art_stage.width()
        old_target = QRect(old_x, center.y(), 256, 256)
        duration = 220 if boundary_jump else 420
        new_geometry = QPropertyAnimation(new_art, b"geometry")
        new_geometry.setStartValue(center if boundary_jump else small)
        new_geometry.setEndValue(center)
        new_geometry.setDuration(duration)
        new_geometry.setEasingCurve(QEasingCurve.Type.OutCubic)
        new_opacity = QPropertyAnimation(new_effect, b"opacity")
        new_opacity.setStartValue(0.05 if boundary_jump else 0.125)
        new_opacity.setEndValue(1.0)
        new_opacity.setDuration(duration)
        old_geometry = QPropertyAnimation(old_art, b"geometry")
        old_geometry.setStartValue(center)
        old_geometry.setEndValue(center if boundary_jump else old_target)
        old_geometry.setDuration(duration)
        old_geometry.setEasingCurve(QEasingCurve.Type.InCubic)
        old_opacity = QPropertyAnimation(old_effect, b"opacity")
        old_opacity.setStartValue(1.0)
        old_opacity.setEndValue(0.0)
        old_opacity.setDuration(duration)
        group = QParallelAnimationGroup(self)
        for animation in (new_geometry, new_opacity, old_geometry, old_opacity):
            group.addAnimation(animation)
        group.finished.connect(lambda: self._finish_animation(old_art, new_art))
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def _finish_animation(self, old_art, new_art):
        old_art.deleteLater()
        new_art.setGraphicsEffect(None)
        self.current_art = new_art
        self._update_mode_labels()
        self.is_animating = False

    def _go_to_difficulty(self, mode):
        difficulty_page = self.main_window.pages.get("difficulty")
        if difficulty_page:
            difficulty_page.set_mode(mode)
        self.main_window.show_page("difficulty")

    def _start_selected_mode(self):
        if self.is_animating:
            return
        mode = self.modes[self.current_index]
        if mode in ("RFH", "RFK", "HFR", "KFR", "KFH"):
            self._go_to_difficulty(mode)
            return
        page_names = {"VC": "verb_conjugation", "GC": "chart", "SP": "sentence_parser"}
        self.main_window.show_page(page_names[mode])

    def _cycle_language(self):
        languages = self.i18n_system.get_available_languages()
        current_index = languages.index(self.i18n_system.current_lang)
        next_language = languages[(current_index + 1) % len(languages)]
        self.i18n_system.set_language(next_language)
        self.main_window.update_title()
        for page in self.main_window.pages.values():
            if hasattr(page, "update_texts"):
                page.update_texts()
