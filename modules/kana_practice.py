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
        list_using = []
        dict_using = {}
        temp_index = 0

        if self.mode == "RFH":
            list_using = self.data_loader.get_hiragana_list()
            dict_using = self.data_loader.get_hiragana_to_romaji()
        elif self.mode == "RFK":
            list_using = self.data_loader.get_katakana_list()
            dict_using = self.data_loader.get_katakana_to_romaji()
        elif self.mode == "HFR":
            list_using = self.data_loader.get_romaji_list()
            dict_using = self.data_loader.get_romaji_to_kana()
            temp_index = 0
        elif self.mode == "KFR":
            list_using = self.data_loader.get_romaji_list()
            dict_using = self.data_loader.get_romaji_to_kana()
            temp_index = 1
        elif self.mode == "KFH":
            list_using = self.data_loader.get_hiragana_list()
            dict_using = self.data_loader.get_hiragana_to_katakana()

        answer = random.choice(list_using)
        self.current_answer = answer

        if self.difficulty != "h":
            if self.mode in ("HFR", "KFR"):
                correct = dict_using[answer][temp_index]
            else:
                correct = dict_using[answer]

            wrong_choices = []
            for t in list_using:
                if t != answer:
                    if self.mode in ("HFR", "KFR"):
                        wrong_choices.append(dict_using[t][temp_index])
                    else:
                        wrong_choices.append(dict_using[t])

            count = self.get_options_count() - 1
            options = [correct] + random.sample(wrong_choices, count)
            random.shuffle(options)
            self.current_options = options

        return answer

    def check_answer(self, user_answer):
        dict_using = {}
        temp_index = 0

        if self.mode == "RFH":
            dict_using = self.data_loader.get_hiragana_to_romaji()
        elif self.mode == "RFK":
            dict_using = self.data_loader.get_katakana_to_romaji()
        elif self.mode == "HFR":
            dict_using = self.data_loader.get_romaji_to_kana()
            temp_index = 0
        elif self.mode == "KFR":
            dict_using = self.data_loader.get_romaji_to_kana()
            temp_index = 1
        elif self.mode == "KFH":
            dict_using = self.data_loader.get_hiragana_to_katakana()

        if self.mode in ("HFR", "KFR"):
            real_answer = dict_using[self.current_answer][temp_index]
        else:
            real_answer = dict_using[self.current_answer]

        is_correct = user_answer.strip() == real_answer

        if is_correct:
            self.correct_times += 1
        else:
            self.wrong_times += 1

        return is_correct, real_answer

    def get_current_options(self):
        return self.current_options
