# 📚 Vocabulary Master

**English** · [فارسی](#فارسی)

A flashcard app for learning English words with Persian meanings, built with Python, [Kivy](https://kivy.org) and [KivyMD](https://kivymd.readthedocs.io). Words and progress are stored locally in an SQLite database.

## Features

- **Daily practice** — a set of words due today (10 by default; changeable in Settings), shown as flip cards: see the English word, reveal the answer, then mark whether you knew it
- **Simple spaced repetition** — a word you got right comes back after 3 days and counts as *learned* after three correct answers in a row; a word you got wrong comes back the next day
- **Your own words** — add a word with its Persian meaning at any time
- **Word list** — browse every word you have, with a pronunciation button
- **Statistics** — number of learned words and words still being learned
- **Starter list** — 20 common words are added the first time the app runs

## Run it

```bash
pip install kivy kivymd
python main.py
```

The database file `vocabulary.db` is created next to the app on first run.

> **Note:** word details and pronunciation audio come from an `APIService` helper (`api_service.py`), which is not part of this repository yet.

## Build an Android APK

The project includes a `buildozer.spec` and a GitHub Actions workflow (**Actions → Build APK → Run workflow**) that builds an APK with [Buildozer](https://buildozer.readthedocs.io).

## Files

- `main.py` — the app and its screens (home, practice, word list)
- `database.py` — the SQLite storage and the review schedule
- `buildozer.spec` — Android build settings
- `.github/workflows/build.yml` — the APK build workflow

---

<div dir="rtl">

## فارسی

# 📚 استاد لغت

برنامهٔ فلش‌کارت برای یادگیری لغت‌های انگلیسی با معنی فارسی، ساخته‌شده با پایتون، [Kivy](https://kivy.org) و [KivyMD](https://kivymd.readthedocs.io). لغت‌ها و پیشرفتت به‌صورت محلی در یک پایگاه دادهٔ SQLite ذخیره می‌شوند.

## امکانات

- **تمرین روزانه** — مجموعه‌ای از لغت‌هایی که امروز موعد مرورشان است (پیش‌فرض ۱۰ تا؛ در تنظیمات قابل تغییر) به‌شکل کارت برگردان: لغت انگلیسی را می‌بینی، جواب را نشان می‌دهی و مشخص می‌کنی بلد بودی یا نه
- **مرور فاصله‌دار ساده** — لغتی که درست جواب بدهی ۳ روز بعد برمی‌گردد و بعد از سه جواب درست پشت‌سرهم «یادگرفته‌شده» حساب می‌شود؛ لغتی که غلط جواب بدهی فردا دوباره می‌آید
- **لغت‌های خودت** — هر وقت خواستی یک لغت را با معنی فارسی‌اش اضافه کن
- **فهرست لغت‌ها** — همهٔ لغت‌هایت را ببین، با دکمهٔ تلفظ
- **آمار** — تعداد لغت‌های یادگرفته‌شده و لغت‌هایی که هنوز در حال یادگیری‌اند
- **لغت‌های اولیه** — بار اول اجرای برنامه ۲۰ لغت پرکاربرد اضافه می‌شود

## اجرا

```bash
pip install kivy kivymd
python main.py
```

فایل پایگاه داده `vocabulary.db` بار اول اجرا کنار برنامه ساخته می‌شود.

> **نکته:** جزئیات لغت و صدای تلفظ از یک کمکی به نام `APIService` (فایل `api_service.py`) می‌آید که هنوز در این مخزن نیست.

## ساخت APK اندروید

پروژه یک فایل `buildozer.spec` و یک Workflow در GitHub Actions دارد (**Actions ← Build APK ← Run workflow**) که با [Buildozer](https://buildozer.readthedocs.io) فایل APK می‌سازد.

## فایل‌ها

- `main.py` — برنامه و صفحه‌هایش (خانه، تمرین، فهرست لغت‌ها)
- `database.py` — ذخیره‌سازی SQLite و برنامهٔ مرور
- `buildozer.spec` — تنظیمات ساخت برای اندروید
- `.github/workflows/build.yml` — Workflow ساخت APK

</div>
