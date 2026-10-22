[app]
title = AKANE
package.name = akane
package.domain = com.hivepulse
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml,txt,otf,ogg,onnx
source.exclude_dirs = assets/openjlpt,assets/store_screenshots,dist,build,models,tests,docs,sessions,data
version = 1.0.0
requirements = python3,kivy,pyjnius,sherpa_onnx,charset_normalizer
p4a.local_recipes = p4a-recipes
orientation = portrait
fullscreen = 0
android.permissions = RECORD_AUDIO
android.extra_manifest_application_arguments = android/extra_manifest_application_arguments.xml
icon.filename = %(source.dir)s/assets/brand/icon.png
android.presplash_color = #12141c
android.presplash_image = %(source.dir)s/assets/brand/splash.png
android.api = 36
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
p4a.bootstrap = sdl2
# Google Play requires new apps to be published as an App Bundle (.aab),
# and the debug APK is 137 MB which is over the 100 MB APK upload limit.
android.release_artifact = aab
# Development signing key. REPLACE with a private release key before the
# Play upload - see docs/playstore/listing.md.
android.keystore = .keystore/sensei-debug.keystore
android.keyalias = sensei
android.keystore_password = sensei123
android.keyalias_password = sensei123

[buildozer]
log_level = 2
warn_on_root = 1
