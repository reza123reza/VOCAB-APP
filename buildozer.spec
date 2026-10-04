[app]
title = Vocab Learning
package.name = vocabapp
package.domain = org.vocabapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin,.buildozer,.github
version = 1.0
# kivymd: main.py روی KivyMD 1.x نوشته شده | sqlite3: برای database.py
# openssl + certifi: برای HTTPS (دیکشنری و صدای تلفظ)
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,sqlite3,openssl,certifi
orientation = portrait
fullscreen = 0

# اینترنت برای مثال‌ها و تلفظ؛ دیتابیس توی پوشه‌ی خصوصی اپه، دسترسی حافظه لازم نیست
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# نسخه‌ی ثابت python-for-android: نسخه‌ی master همیشه آخرین پایتون رو
# می‌سازه و Kivy قدیمی‌تر روش build نمی‌شه. این نسخه با Kivy 2.3.0 و NDK 25b
# سازگاره.
p4a.branch = v2024.01.21
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
