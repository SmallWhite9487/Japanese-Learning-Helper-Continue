import random

'''
KanaPractice 模組負責管理假名練習題目、答題邏輯與分數。
根據不同模式與難度，生成問題與選項，並驗證使用者答案。
'''

class KanaPractice:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        self.correct_times = 0
        self.wrong_times = 0
        self.current_answer = None
        self.current_options = []
        self.mode = "RFH"
        self.source_type = "h"
        self.target_type = "r"
        self.difficulty = "e"

    def reset_score(self):
        # 重置正確與錯誤次數
        self.correct_times = 0
        self.wrong_times = 0

    def get_score(self):
        # 回傳目前答題分數
        return self.correct_times, self.wrong_times

    def set_mode(self, mode):
        self.mode = mode
        mode_axes = {
            "RFH": ("h", "r"), "RFK": ("k", "r"),
            "HFR": ("r", "h"), "KFR": ("r", "k"), "KFH": ("h", "k")
        }
        self.source_type, self.target_type = mode_axes.get(mode, ("h", "r"))

    def set_types(self, source_type, target_type):
        if source_type == target_type:
            raise ValueError("Source and target types must be different")
        self.source_type = source_type
        self.target_type = target_type
        self.mode = self._types_to_mode(source_type, target_type)

    def _types_to_mode(self, source_type, target_type):
        return {
            ("h", "r"): "RFH", ("k", "r"): "RFK",
            ("r", "h"): "HFR", ("r", "k"): "KFR",
            ("h", "k"): "KFH", ("k", "h"): "KHF"
        }.get((source_type, target_type), "RFH")

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def get_options_count(self):
        if self.difficulty == "e":
            return 4
        elif self.difficulty == "m":
            return 8
        else:
            return 12

    def generate_question(self):
        list_using, answer_lookup = self._get_practice_data()

        answer = random.choice(list_using)
        self.current_answer = answer

        if self.difficulty != "h":
            correct = answer_lookup[answer]

            wrong_choices = []
            for t in list_using:
                if t != answer:
                    wrong_choices.append(answer_lookup[t])

            count = self.get_options_count() - 1
            options = [correct] + random.sample(wrong_choices, count)
            random.shuffle(options)
            self.current_options = options

        return answer

    def check_answer(self, user_answer):
        _, answer_lookup = self._get_practice_data()
        real_answer = answer_lookup[self.current_answer]

        is_correct = user_answer.strip() == real_answer

        if is_correct:
            self.correct_times += 1
        else:
            self.wrong_times += 1

        return is_correct, real_answer

    def get_current_options(self):
        return self.current_options

    def _get_practice_data(self):
        source_lists = {
            "h": self.data_loader.get_hiragana_list(),
            "k": self.data_loader.get_katakana_list(),
            "r": self.data_loader.get_romaji_list(),
        }
        source_list = source_lists[self.source_type]
        if self.source_type == "h" and self.target_type == "r":
            lookup = self.data_loader.get_hiragana_to_romaji()
        elif self.source_type == "k" and self.target_type == "r":
            lookup = self.data_loader.get_katakana_to_romaji()
        elif self.source_type == "r" and self.target_type in ("h", "k"):
            values = self.data_loader.get_romaji_to_kana()
            index = 0 if self.target_type == "h" else 1
            lookup = {key: value[index] for key, value in values.items()}
        elif self.source_type == "h" and self.target_type == "k":
            lookup = self.data_loader.get_hiragana_to_katakana()
        elif self.source_type == "k" and self.target_type == "h":
            hira_to_kata = self.data_loader.get_hiragana_to_katakana()
            lookup = {kata: hira for hira, kata in hira_to_kata.items()}
        else:
            raise ValueError("Unsupported kana practice direction")
        valid = [(item, lookup[item]) for item in source_list if item in lookup]
        return [item[0] for item in valid], dict(valid)
