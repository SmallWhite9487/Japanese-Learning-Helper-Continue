import re
from janome.tokenizer import Tokenizer

'''
VerbConjugator 模組負責解析日語動詞，並產生主要的變化形態。
它會使用 janome 斷詞與活用タイプ資訊，針對一段動詞、五段動詞與不規則動詞作出對應變化。
'''

class VerbConjugator:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.godan_rules = {
            "う": {"ます": "います", "ない": "わない", "た": "った", "て": "って", "可能": "える", "意志": "おう", "命令": "え", "条件": "えば"},
            "く": {"ます": "きます", "ない": "かない", "た": "いた", "て": "いて", "可能": "ける", "意志": "こう", "命令": "け", "条件": "けば"},
            "ぐ": {"ます": "ぎます", "ない": "がない", "た": "いだ", "て": "いで", "可能": "げる", "意志": "ごう", "命令": "げ", "条件": "げば"},
            "す": {"ます": "します", "ない": "さない", "た": "した", "て": "して", "可能": "せる", "意志": "そう", "命令": "せ", "条件": "せば"},
            "つ": {"ます": "ちます", "ない": "たない", "た": "った", "て": "って", "可能": "てる", "意志": "とう", "命令": "て", "条件": "てば"},
            "る": {"ます": "ります", "ない": "らない", "た": "った", "て": "って", "可能": "れる", "意志": "ろう", "命令": "れ", "条件": "れば"},
            "む": {"ます": "みます", "ない": "まない", "た": "んだ", "て": "んで", "可能": "める", "意志": "もう", "命令": "め", "条件": "めば"},
            "ぶ": {"ます": "びます", "ない": "ばない", "た": "んだ", "て": "んで", "可能": "べる", "意志": "ぼう", "命令": "べ", "条件": "べば"},
            "ぬ": {"ます": "にます", "ない": "なない", "た": "んだ", "て": "んで", "可能": "ねる", "意志": "のう", "命令": "ね", "条件": "ねば"},
        }
        self.irregular = {
            "する": {"ます形": "します", "ない形": "しない", "た形": "した", "て形": "して", "可能形": "できる", "意志形": "しよう", "命令形": "しろ／せよ", "条件形": "すれば"},
            "来る": {"ます形": "来ます", "ない形": "来ない", "た形": "来た", "て形": "来て", "可能形": "来られる", "意志形": "来よう", "命令形": "来い", "条件形": "来れば"},
        }

    def is_japanese(self, text):
        try:
            pattern = re.compile(r"^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF]+$")
            return bool(pattern.match(text))
        except Exception as e:
            print(f"Error checking Japanese: {e}")
            return False

    def conjugate_verb(self, verb):
        try:
            if verb in self.irregular:
                return self.irregular[verb]
            
            tokens = list(self.tokenizer.tokenize(verb))
            if not tokens:
                return {}
            
            token = tokens[0]
            base = token.base_form
            infl_type = token.infl_type
            pos = token.part_of_speech

            if "一段" in infl_type:
                stem = base[:-1]
                return {
                    "ます形": stem + "ます",
                    "ない形": stem + "ない",
                    "た形": stem + "た",
                    "て形": stem + "て",
                    "可能形": stem + "られる",
                    "意志形": stem + "よう",
                    "命令形": stem + "ろ／よ",
                    "条件形": stem + "れば"
                }
            
            if "五段" in infl_type:
                stem = base[:-1]
                last = base[-1]
                if last in self.godan_rules:
                    r = self.godan_rules[last]
                    return {
                        "ます形": stem + r["ます"],
                        "ない形": stem + r["ない"],
                        "た形": stem + r["た"],
                        "て形": stem + r["て"],
                        "可能形": stem + r["可能"],
                        "意志形": stem + r["意志"],
                        "命令形": stem + r["命令"],
                        "条件形": stem + r["条件"]
                    }
            return {}
        except Exception as e:
            print(f"Error conjugating verb: {e}")
            return {}
