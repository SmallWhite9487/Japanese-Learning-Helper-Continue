import re
from janome.tokenizer import Tokenizer

'''
SentenceParser 模組負責分析日文句子結構。
它會呼叫 janome 的 Tokenizer 進行斷詞，並將每個詞彙轉換成可讀取的字典格式。
輸出結果會包含表層形、基本形、詞性、活用型態、讀音，以及助詞類別與助詞意義。
'''

class SentenceParser:
    """SentenceParser 主要功能:
    1. 初始化 janome Tokenizer
    2. 對日文句子進行斷詞與品詞分析
    3. 為常見日語助詞補上語法類別與中文說明
    4. 提供格式化輸出方便 GUI 或終端顯示
    """

    def __init__(self):
        self.tokenizer = Tokenizer()
        self.language_tool = None
        self.language_tool_available = False
        self._init_language_tool()
        self.particle_dict = {
            "は": ("格助詞", "主題標記 (主題)") ,
            "が": ("格助詞", "主詞標記"),
            "を": ("格助詞", "受詞標記"),
            "に": ("格助詞", "方向 / 間接受詞 / 時間"),
            "で": ("格助詞", "地點 / 手段"),
            "へ": ("格助詞", "方向"),
            "から": ("格助詞", "起點 / 原因"),
            "まで": ("格助詞", "終點 / 限制"),
            "より": ("格助詞", "比較 / 起點"),
            "と": ("格助詞", "和 / 與 / 引用"),
            "の": ("格助詞", "所有 / 修飾"),
            "ので": ("接續助詞", "因為 / 由於"),
            "けれど": ("接續助詞", "雖然 / 但是"),
            "けど": ("接續助詞", "雖然 / 但是"),
            "のに": ("接續助詞", "儘管 / 但是"),
            "ながら": ("接續助詞", "一邊...一邊... / 但是"),
            "て": ("接續助詞", "並列 / 然後"),
            "ても": ("接續助詞", "即使...也..."),
            "たら": ("接續助詞", "如果 / 當...時"),
            "なら": ("接續助詞", "如果 / 假設"),
            "ば": ("接續助詞", "如果 / 假設"),
            "ね": ("終助詞", "確認 / 同意"),
            "よ": ("終助詞", "強調 / 斷定"),
            "かな": ("終助詞", "疑問 / 猜測"),
            "かしら": ("終助詞", "疑問 (女性語氣)"),
            "ぞ": ("終助詞", "強調 (男性語氣)"),
            "ぜ": ("終助詞", "強調 (男性語氣)"),
            "さ": ("終助詞", "口語強調"),
            "も": ("副助詞", "也 / 甚至"),
            "しか": ("副助詞", "只有 (與否定連用)"),
            "ばかり": ("副助詞", "只是 / 剛剛"),
            "だけ": ("副助詞", "只有 / 僅僅"),
            "ほど": ("副助詞", "程度 / 越...越..."),
            "くらい": ("副助詞", "大約 / 程度"),
            "など": ("副助詞", "等等 / 類似"),
            "でも": ("副助詞", "即使 / 但是"),
            "こそ": ("副助詞", "強調"),
        }

    def _get_particle_info(self, surface, pos=""):
        """(優化) 根據助詞文字與品詞回傳語法類別與說明，避免終助詞被當成格助詞。"""
        if surface == "で" and "終助詞" in pos:
            return ("終助詞", "方言/口語強調 (標準語建議改為 です 或 よ)")
        return self.particle_dict.get(surface, ("", ""))

    def _is_particle(self, surface):
        """判斷表層文字是否為常見助詞。"""
        return surface in self.particle_dict

    def _init_language_tool(self):
        """嘗試初始化 language-tool-python 後端。"""
        try:
            import language_tool_python
            self.language_tool = language_tool_python.LanguageTool("ja-JP")
            self.language_tool_available = True
        except Exception:
            self.language_tool = None
            self.language_tool_available = False

    def is_language_tool_available(self):
        return self.language_tool_available

    def _token_to_dict(self, token):
        """(優化) 傳入 pos 進行精準助詞比對"""
        surface = getattr(token, "surface", "")
        base_form = getattr(token, "base_form", surface)
        part_of_speech = getattr(token, "part_of_speech", "")
        infl_type = getattr(token, "infl_type", "")
        infl_form = getattr(token, "infl_form", "")
        reading = getattr(token, "reading", "")

        # 傳入完整的品詞資訊 (part_of_speech)
        category, meaning = self._get_particle_info(surface, part_of_speech)

        return {
            "surface": surface,
            "base": base_form,
            "pos": part_of_speech,
            "infl_type": infl_type,
            "infl_form": infl_form,
            "reading": reading,
            "particle_category": category,
            "particle_meaning": meaning,
        }

    def _has_predicate(self, parsed):
        """判斷句子是否已包含動詞、助動詞或形容詞等謂語。"""
        for item in parsed:
            pos = item.get("pos", "")
            base = item.get("base", "")
            if pos.startswith("動詞") or pos.startswith("形容詞") or pos.startswith("形容動詞") or pos.startswith("助動詞"):
                return True
            if base in {"です", "だ", "ます", "ました", "ません", "ない", "ある", "いる", "する", "れる", "られる"}:
                return True
        return False

    def _detect_particle_errors(self, parsed, sentence):
        """偵測助詞連續、尾部助詞等常見文法問題。"""
        issues = []
        suggestion = None

        for idx in range(len(parsed) - 1):
            current = parsed[idx]["surface"]
            next_surface = parsed[idx + 1]["surface"]
            if self._is_particle(current) and self._is_particle(next_surface):
                issues.append(
                    f"助詞“{current}”之後緊接助詞“{next_surface}”，可能存在用法錯誤。"
                )
                if current == next_surface:
                    suggestion = sentence.replace(current + next_surface, current, 1)
                elif current == "は" and next_surface == "が":
                    suggestion = sentence.replace("はが", "が", 1)
                elif current == "が" and next_surface == "は":
                    suggestion = sentence.replace("がは", "は", 1)
                break

        if not issues and parsed:
            last_surface = parsed[-1]["surface"]
            if self._is_particle(last_surface):
                issues.append(
                    f"句子尾部以助詞“{last_surface}”結束，可能缺少謂語或標點。"
                )
                suggestion = sentence + "。" if not sentence.endswith(("。", "！", "？")) else sentence

        return issues, suggestion

    def _detect_missing_predicate(self, parsed, sentence):
        """偵測句子是否缺少謂語，例如主題指示後未補上 です/動詞。"""
        if self._has_predicate(parsed):
            return None, None

        last = parsed[-1]
        pos = last.get("pos", "")
        if pos.startswith("名詞") or pos.startswith("形容詞") or pos.startswith("形容動詞"):
            if any(item["surface"] in {"は", "が", "を", "に", "で", "へ", "と", "から", "まで"} for item in parsed):
                if sentence.endswith(("。", "！", "？")):
                    return (
                        "句子似乎缺少謂語，建議補上“です”。",
                        sentence[:-1] + "です。",
                    )
                return (
                    "句子似乎缺少謂語，建議補上“です”。",
                    sentence + "です。",
                )

        return None, None

    def _detect_custom_learning_errors(self, parsed):
        """【自訂核心雷區攔截器】專門抓學習過程中容易犯的特定錯誤。"""
        issues = []
        suggestions = []

        if not parsed:
            return issues, suggestions

        for idx in range(len(parsed)):
            current = parsed[idx]

            # 💡 攔截點 1：時間名詞 + で (例如：未来で、明日で)
            time_words = {"未来", "明日", "今日", "昨日", "日常"}
            if current["base"] in time_words and (idx + 1 < len(parsed)):
                next_token = parsed[idx + 1]
                if next_token["surface"] == "で":
                    issues.append(f"時間名詞“{current['surface']}”後面誤用了表示地點/手段的“で”。")
                    suggestions.append((current['surface'] + 'で', current['surface'] + 'に'))

            # 💡 攔截點 2：想做某事 ～たい 結尾誤用 で
            if current["base"] == "たい" and (idx + 1 < len(parsed)):
                next_token = parsed[idx + 1]
                if next_token["surface"] == "で":
                    issues.append(f"表達願望的“{current['surface']}”後面誤加了“で”。")
                    suggestions.append(("たいで", "たいです"))

        return issues, suggestions

    def _check_grammar_language_tool(self, sentence):
        if not self.language_tool_available:
            return {
                "is_correct": False,
                "errors": ["LanguageTool 后端不可用。"],
                "suggestion": "",
            }

        try:
            matches = self.language_tool.check(sentence)
            errors = []
            for match in matches:
                message = getattr(match, "message", "")
                if message:
                    errors.append(message)
            suggestion = sentence
            if matches:
                try:
                    suggestion = self.language_tool.correct(sentence)
                except Exception:
                    suggestion = sentence
            return {
                "is_correct": len(matches) == 0,
                "errors": errors,
                "suggestion": suggestion if suggestion != sentence else "",
            }
        except Exception as e:
            return {
                "is_correct": False,
                "errors": [f"LanguageTool 检查失败：{str(e)}"],
                "suggestion": "",
            }

    def _check_grammar_local(self, sentence):
        sentence = str(sentence).strip()
        if not sentence:
            return {
                "is_correct": False,
                "errors": ["句子為空，請輸入日文句子。"],
                "suggestion": "",
            }

        parsed = self.parse_sentence(sentence)
        if not parsed:
            return {
                "is_correct": False,
                "errors": ["句子解析失敗，可能含有文法或字元問題。"],
                "suggestion": "",
            }

        errors, suggestion = self._detect_particle_errors(parsed, sentence)
        if not errors:
            missing_error, missing_suggestion = self._detect_missing_predicate(parsed, sentence)
            if missing_error:
                errors.append(missing_error)
                suggestion = missing_suggestion

        return {
            "is_correct": len(errors) == 0,
            "errors": errors,
            "suggestion": suggestion or "",
        }

    def check_grammar(self, sentence, engine="hybrid"):
        """進行日語文法檢測。
        推薦使用 "hybrid" 模式：先用本地自訂規則精準攔截，再用 LanguageTool 補漏。
        """
        sentence = str(sentence).strip()
        parsed = self.parse_sentence(sentence)

        # 1. 先跑本地的基礎結構檢查 (助詞連續、缺少謂語)
        local_res = self._check_grammar_local(sentence)
        errors = local_res["errors"][:]
        suggestion = local_res["suggestion"]

        # 2. 跑我們特製的「個人雷區攔截器」
        custom_errors, custom_sug = self._detect_custom_learning_errors(parsed)
        if custom_errors:
            errors.extend(custom_errors)
            if "たいで" in sentence:
                suggestion = sentence.replace("たいで", "たいです")
            elif "未来で" in sentence:
                suggestion = sentence.replace("未来で", "未来に")

        # 3. 如果是 hybrid 且本地沒發現嚴重錯誤，或者使用者指定要用 LanguageTool
        if (engine == "language_tool" or engine == "hybrid") and self.language_tool_available:
            lt_res = self._check_grammar_language_tool(sentence)
            if lt_res["errors"]:
                errors.extend(lt_res["errors"])
                if lt_res["suggestion"]:
                    suggestion = lt_res["suggestion"]

        return {
            "is_correct": len(errors) == 0,
            "errors": errors,
            "suggestion": suggestion or "",
        }

    def parse_sentence(self, sentence):
        """解析日文句子，返回每個詞的詳細字典清單。"""
        sentence = str(sentence).strip()
        if not sentence:
            return []

        try:
            tokens = self.tokenizer.tokenize(sentence)
            return [self._token_to_dict(token) for token in tokens]
        except Exception as e:
            print(f"Error parsing sentence: {e}")
            return []

    def is_japanese(self, text):
        """檢查輸入是否為日語字符。若包含標點或空白仍會視為日語句子。"""
        pattern = re.compile(r"^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF\s。、！？]+$")
        try:
            return bool(pattern.match(str(text)))
        except Exception:
            return False

    def format_parsed_sentence(self, sentence):
        """將解析結果格式化為多行文字，方便顯示在 GUI 或日誌中。"""
        parsed = self.parse_sentence(sentence)
        lines = [
            f"{item['surface']} | 基本形: {item['base']} | 品詞: {item['pos']} | "
            f"活用: {item['infl_type']}/{item['infl_form']} | 讀音: {item['reading']} | "
            f"助詞類別: {item['particle_category']} | 意義: {item['particle_meaning']}"
            for item in parsed
        ]
        return lines
