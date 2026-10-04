"""
API Service - word details and pronunciation
اطلاعات کلمه (تلفظ + مثال) و پخش صدا از Free Dictionary API

Uses https://dictionaryapi.dev (free, no API key). Only the standard library
is used for HTTP, so no extra buildozer requirement is needed besides
openssl/certifi for HTTPS on Android.
"""

import json
import os
import ssl
import tempfile
import urllib.parse
import urllib.request

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
TIMEOUT = 6  # seconds


def _default_cache_dir():
    """پوشه‌ی داده‌ی اپ (روی اندروید قابل نوشتن و ماندگار)؛ در غیر این صورت temp"""
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app is not None:
            return os.path.join(app.user_data_dir, "audio_cache")
    except Exception:
        pass
    return os.path.join(tempfile.gettempdir(), "vocab_audio")


def _ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


class APIService:
    def __init__(self, cache_dir=None):
        self._details_cache = {}
        self._audio_url_cache = {}
        self._sound = None
        self._ctx = _ssl_context()
        self.cache_dir = cache_dir or _default_cache_dir()
        os.makedirs(self.cache_dir, exist_ok=True)

    def _fetch(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": "VocabApp/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=self._ctx) as resp:
            return resp.read()

    def _entries(self, word):
        url = API_URL.format(urllib.parse.quote(word.strip().lower()))
        return json.loads(self._fetch(url).decode("utf-8"))

    def get_word_details(self, word):
        """
        Returns {'phonetic': str, 'examples': [str, ...], 'audio_url': str|None}
        or None if the word was not found / there is no connection.
        """
        key = word.strip().lower()
        if key in self._details_cache:
            return self._details_cache[key]

        try:
            entries = self._entries(key)
        except Exception:
            return None
        if not isinstance(entries, list) or not entries:
            return None

        phonetic, audio_url, examples = "", None, []
        for entry in entries:
            phonetic = phonetic or entry.get("phonetic", "")
            for ph in entry.get("phonetics", []):
                phonetic = phonetic or ph.get("text", "")
                audio_url = audio_url or (ph.get("audio") or None)
            for meaning in entry.get("meanings", []):
                for definition in meaning.get("definitions", []):
                    ex = definition.get("example")
                    if ex and ex not in examples:
                        examples.append(ex)

        data = {
            "phonetic": phonetic.strip("/"),
            "examples": examples[:5],
            "audio_url": audio_url,
        }
        self._details_cache[key] = data
        if audio_url:
            self._audio_url_cache[key] = audio_url
        return data

    def _audio_file(self, word):
        key = word.strip().lower()
        path = os.path.join(self.cache_dir, f"{urllib.parse.quote(key, safe='')}.mp3")
        if os.path.exists(path):
            return path

        url = self._audio_url_cache.get(key)
        if url is None:
            details = self.get_word_details(key)
            url = details.get("audio_url") if details else None
        if not url:
            return None
        if url.startswith("//"):
            url = "https:" + url

        data = self._fetch(url)
        tmp = path + ".part"  # اگه دانلود نصفه بمونه، فایل خراب کش نمی‌شه
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
        return path

    def download_audio(self, word):
        """Downloads (or reuses the cached) pronunciation file. Safe to call
        from a background thread. Returns the local path or None."""
        try:
            return self._audio_file(word)
        except Exception:
            return None

    def play_audio(self, word):
        """Downloads and plays the word's pronunciation; returns True on success.
        Blocks while downloading - prefer download_audio() in a thread +
        play_file() on the main thread inside the UI."""
        return self.play_file(self.download_audio(word))

    def play_file(self, path):
        """Plays a local audio file (call from the Kivy main thread)."""
        try:
            if not path:
                return False
            from kivy.core.audio import SoundLoader
            if self._sound is not None:
                self._sound.stop()
            self._sound = SoundLoader.load(path)
            if self._sound is None:
                return False
            self._sound.play()
            return True
        except Exception:
            return False
