
import tempfile
import threading
import os
import time
from gtts import gTTS
import pygame

'''
AudioPlayer 模組負責將日語文字轉為語音，並以 pygame 播放音訊。
使用 gTTS 產生臨時 MP3 檔案，播放後立即刪除，避免暫存檔堆積。
'''

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.temp_files = []

    def play_sound(self, text):
        # 使用背景執行緒播放語音，避免阻塞 GUI 主迴圈。
        def _play():
            temp_path = None
            try:
                tts = gTTS(text=text, lang='ja')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    temp_path = fp.name
                    self.temp_files.append(temp_path)
                    tts.save(temp_path)
                
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
                time.sleep(0.1)
                
                self._cleanup_temp_file(temp_path)
            except Exception as e:
                print(f"Error playing sound: {e}")
                if temp_path:
                    self._cleanup_temp_file(temp_path)

        thread = threading.Thread(target=_play, daemon=True)
        thread.start()

    def _cleanup_temp_file(self, file_path):
        # 清理臨時 MP3 檔案，如果檔案正在使用則重試刪除。
        try:
            if file_path in self.temp_files:
                self.temp_files.remove(file_path)
            if os.path.exists(file_path):
                max_attempts = 5
                for attempt in range(max_attempts):
                    try:
                        os.remove(file_path)
                        break
                    except PermissionError:
                        if attempt < max_attempts - 1:
                            time.sleep(0.2)
                        else:
                            print(f"Could not delete file after {max_attempts} attempts: {file_path}")
        except Exception as e:
            print(f"Error cleaning up temp file: {e}")

    def cleanup_all(self):
        # 關閉正在播放的音訊並清理所有尚未刪除的暫存檔。
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except:
            pass
        
        for file_path in self.temp_files[:]:
            self._cleanup_temp_file(file_path)
