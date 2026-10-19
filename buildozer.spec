[app]
title = Japanese Sensei AI
package.name = japanesesensei
package.domain = org.sensei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml,txt,ttc
version = 0.1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
