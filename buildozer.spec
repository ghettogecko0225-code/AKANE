[app]
title = Japanese Sensei AI
package.name = japanesesensei
package.domain = org.sensei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml,txt,ttc,ogg,onnx
source.exclude_dirs = assets/openjlpt,dist,build,models,tests,docs,sessions,data
version = 0.4.0
requirements = python3,kivy,pyjnius,sherpa_onnx,charset_normalizer
p4a.local_recipes = p4a-recipes
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO
android.extra_manifest_application_arguments = android/extra_manifest_application_arguments.xml
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
