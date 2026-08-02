[app]

# (str) 앱 이름
title = Basketball Scoreboard

# (str) 패키지 이름 (영문 소문자/숫자만)
package.name = basketballscoreboard

# (str) 패키지 도메인 (android 패키징에 필요, 역방향 도메인 형식)
package.domain = com.example.basketballscoreboard

# (str) main.py 가 있는 소스 폴더
source.dir = .

# (list) 앱에 포함할 파일 확장자 (이미지/소리 리소스 포함)
source.include_exts = py,png,jpg,jpeg,gif,bmp,kv,atlas,mp3,wav,ogg

# (list) APK 에 넣지 않을 폴더
#   venv: 가상환경(수천 개 .py) / BasketBall_ScoreBoard: 예전 버전 사본
#   이걸 빼지 않으면 APK 가 수십 MB 로 불어난다.
source.exclude_dirs = venv, .venv, .buildozer, bin, _git_trash, .github, .vscode, __pycache__, BasketBall_ScoreBoard

# (list) APK 에 넣지 않을 파일
#   Buzzer.mp3: 10분짜리 6.9MB 구버전 부저 (NBA_Buzzer.wav 로 대체됨)
#   generated-image.png: 아이콘/스플래시로만 쓰이므로 소스에 중복 포함할 필요 없음
source.exclude_patterns = Buzzer.mp3, generated-image.png, ScoreBoard_Image.bmp, main_v1.py, BBall_SB_v1.py

# (str) 앱 버전
version = 2.3

# (list) 앱이 필요로 하는 파이썬 패키지
#   - kivy: UI 프레임워크
#   - pyjnius: 안드로이드 진동(Vibrator) 등 자바 API 호출에 필요
requirements = python3,kivy,pyjnius

# (str) python-for-android 을 "안정 릴리스" 로 고정한다.
#   고정하지 않으면 buildozer 가 p4a master(개발판)를 받아, Python 3.14 등
#   최신 조합을 쓰다가 libffi(autoreconf) 등에서 깨진다.
#   v2024.01.21 은 buildozer 1.5.0 / NDK 25b / Python 3.11 과 검증된 조합.
p4a.branch = v2024.01.21

# (str) 화면 방향 (landscape = 가로)
orientation = landscape

# (bool) 전체화면 여부 (1 = 전체화면)
fullscreen = 1

# (str) 앱 실행 시 뜨는 스플래시 이미지
presplash.filename = %(source.dir)s/generated-image.png

# (str) 앱 아이콘 (512x512 GBC 로고)
icon.filename = %(source.dir)s/GBC_Icon.png

# (list) 지원 아키텍처
android.archs = arm64-v8a, armeabi-v7a

# (bool) 안드로이드 자동 백업 기능 (API >= 23)
android.allow_backup = True


[android]

# (str) 안드로이드 진입점 (Kivy 기본값 유지)
android.entrypoint = org.kivy.android.PythonActivity

# (list) 요청할 안드로이드 권한
#   부저 대체 진동 기능을 위해 VIBRATE 필요
android.permissions = VIBRATE

# (int) 타겟 안드로이드 API (가능한 높게)
android.api = 33

# (int) 최소 지원 API
android.minapi = 21

# (str) 사용할 NDK 버전
android.ndk = 25b

# (bool) SDK 라이선스 자동 동의 (CI 자동 빌드에 필요)
android.accept_sdk_license = True

# (str) release 모드 패키지 형식 (aab 또는 apk)
android.release_artifact = aab

# (str) debug 모드 패키지 형식 (apk 또는 aab)
android.debug_artifact = apk


[buildozer]

# (int) 로그 레벨 (0=에러만, 1=정보, 2=디버그)
log_level = 2

# (int) root 로 실행 시 경고 표시 (CI 컨테이너에서는 0 권장)
warn_on_root = 0
