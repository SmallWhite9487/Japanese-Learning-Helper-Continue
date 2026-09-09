import json
import os
import sys

'''
DataLoader 模組負責從 data 資料夾載入五十音與語言對照表。
這個模組會讀取 JSON 與 TXT 檔案，提供給練習題目、五十音圖與翻譯功能使用。
'''

class DataLoader:
    def __init__(self, base_path=None):
        self.base_path = base_path or self._get_base_path()
        self.hkr_dict = {"h": {}, "k": {}, "r": {}}
        self.hkr_list = {"h": [], "k": [], "r": []}
        self.htk_dict = {}
        self._load_data()

    def _get_base_path(self):
        # 在 bundling 環境下（例如 PyInstaller），使用 _MEIPASS 來定位資源路徑。
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _load_data(self):
        # 讀取主要資料檔案，並依據檔案類型存入對應字典。
        try:
            files = {
                "hiragana_to_romaji.json": "h",
                "katakana_to_romaji.json": "k",
                "romaji_to_kana.json": "r",
                "HKR_list.txt": "",
                "hiragana_to_katakana.json": "",
            }
            for fname, key in files.items():
                path = os.path.join(self.base_path, "data", "hkr", fname)
                with open(path, "r", encoding="utf-8") as f:
                    if fname.endswith(".json"):
                        if key in ("h", "k", "r"):
                            self.hkr_dict[key] = json.load(f)
                        elif key == "":
                            self.htk_dict = json.load(f)
                    elif fname.endswith(".txt"):
                        lines = []
                        for line in f:
                            line = line.strip()
                            if line:
                                lines.append(line)
                        if len(lines) >= 3:
                            self.hkr_list["h"] = lines[0].split(",")
                            self.hkr_list["k"] = lines[1].split(",")
                            self.hkr_list["r"] = lines[2].split(",")
        except Exception as e:
            print(f"Error loading data: {e}")

    def get_hiragana_list(self):
        return self.hkr_list["h"]

    def get_katakana_list(self):
        return self.hkr_list["k"]

    def get_romaji_list(self):
        return self.hkr_list["r"]

    def get_hiragana_to_romaji(self):
        return self.hkr_dict["h"]

    def get_katakana_to_romaji(self):
        return self.hkr_dict["k"]

    def get_romaji_to_kana(self):
        return self.hkr_dict["r"]

    def get_hiragana_to_katakana(self):
        return self.htk_dict
