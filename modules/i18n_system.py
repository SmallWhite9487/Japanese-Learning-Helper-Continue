import json
import os
import sys

from PyQt6.QtCore import QLocale


class I18nSystem:
    def __init__(self, base_path=None):
        self.base_path = base_path or self._get_base_path()
        self.i18n_dict = {"en-us": {}, "zh-cn": {}, "zh-tw": {}}
        self._load_i18n()
        self.current_i18n = self._detect_system_i18n()

    def _get_base_path(self):
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _detect_system_i18n(self):
        locale = QLocale.system()
        candidates = [locale.name(), *locale.uiLanguages()]
        normalized = [value.lower().replace("_", "-") for value in candidates]
        if any(value.startswith(("zh-tw", "zh-hk", "zh-mo")) for value in normalized):
            return "zh-tw"
        if any(value.startswith("zh") for value in normalized):
            return "zh-cn"
        return "en-us"

    def _load_i18n(self):
        files = {
            "lang_en-us.json": "en-us",
            "lang_zh-cn.json": "zh-cn",
            "lang_zh-tw.json": "zh-tw",
        }
        for filename, i18n_code in files.items():
            path = os.path.join(self.base_path, "data", "i18n", filename)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    self.i18n_dict[i18n_code] = json.load(file)
            except (OSError, json.JSONDecodeError):
                continue

    def set_i18n(self, i18n_code):
        if i18n_code in self.i18n_dict:
            self.current_i18n = i18n_code
            return True
        return False

    def get_i18n_text(self, key):
        return self.i18n_dict[self.current_i18n].get(key, key)

    def get_available_i18n(self):
        return list(self.i18n_dict.keys())

    def get_i18n_name(self, i18n_code):
        if i18n_code in self.i18n_dict:
            return self.i18n_dict[i18n_code].get(f"lang_{i18n_code}", i18n_code)
        return i18n_code

    # Compatibility aliases for pages not yet migrated.
    current_lang = property(lambda self: self.current_i18n)
    get_text = get_i18n_text
    get_available_languages = get_available_i18n
    get_language_name = get_i18n_name
    set_language = set_i18n
