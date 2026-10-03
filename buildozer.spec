[app]
title = Hardware Tester
package.name = hwtester
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE,BATTERY_STATS
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 33
android.minapi = 24
android.ndk_api = 24
