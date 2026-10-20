[app]
title = Japanese Sensei AI
package.name = japanesesensei
package.domain = org.sensei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml,txt,ttc,ogg,mdl,fst,conf,int,dubm,ie,mat,stats
source.exclude_dirs = assets/openjlpt,dist,build,models,tests,docs,sessions
version = 0.3.0
requirements = python3,kivy,pyjnius,vosk
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO
android.extra_manifest_application_arguments = android/extra_manifest_application_arguments.xml
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
