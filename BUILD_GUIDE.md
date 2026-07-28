# 농구 전광판 앱 — 실행 & 안드로이드 APK 빌드 가이드

이 프로젝트는 **Kivy**로 만든 파이썬 앱이고, **Buildozer**로 안드로이드 APK를 만듭니다.

> 중요: **Buildozer는 리눅스 전용**입니다. macOS / Windows에서는 직접 빌드가 안 되므로,
> 아래에서는 **GitHub Actions(클라우드 자동 빌드)** 방식을 사용합니다. Mac에 아무것도 설치할 필요가 없습니다.

---

## 1단계. Mac에서 프로그램 먼저 실행해 보기 (테스트)

APK를 만들기 전에, 데스크톱에서 잘 동작하는지 확인합니다.

```bash
# 프로젝트 폴더로 이동
cd "/Users/freddy/Desktop/Work/02. Project/BasketBall_ScoreBoard"

# (권장) 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# Kivy 설치
pip install --upgrade pip
pip install kivy

# 실행
python main.py
```

창이 뜨고 점수 +1/+3/-1, 타이머 10:00 / 5:00 / 1:00, START/PAUSE/RESET,
SWITCH(팀 교체)가 동작하면 정상입니다.

> `White.jpg`, `Black.jpg`, `GBC_Image.png`, `Buzzer.mp3` 파일이 `main.py`와
> **같은 폴더**에 있어야 유니폼 이미지·중앙 로고·부저가 정상 표시/재생됩니다.
> (이번 수정으로 파일이 없어도 앱이 죽지는 않고, 해당 리소스만 빈 상태로 뜹니다.)

---

## 2단계. GitHub Actions로 APK 자동 빌드하기 (추천)

### 준비물
- GitHub 계정
- Mac에 `git` (터미널에서 `git --version` 으로 확인, 없으면 `xcode-select --install`)

### 2-1. 저장소 만들고 코드 올리기

```bash
cd "/Users/freddy/Desktop/Work/02. Project/BasketBall_ScoreBoard"

git init
git add .
git commit -m "농구 전광판 앱 초기 커밋"

# 아래 URL은 본인이 GitHub에서 새로 만든 저장소 주소로 바꾸세요
git branch -M main
git remote add origin https://github.com/<본인아이디>/basketball-scoreboard.git
git push -u origin main
```

> GitHub에서 저장소는 **비어 있는 상태(README 등 체크 해제)** 로 새로 만들면 됩니다.

### 2-2. 빌드 자동 실행

`push` 하는 순간, 포함된 워크플로 파일(`.github/workflows/build.yml`)이
자동으로 리눅스 클라우드에서 빌드를 시작합니다.

- GitHub 저장소 페이지 → **Actions** 탭에서 진행 상황을 볼 수 있습니다.
- **처음 빌드는 안드로이드 SDK/NDK를 내려받느라 20~40분** 정도 걸립니다.
  (다음 빌드부터는 캐시 덕분에 몇 분이면 끝납니다.)

### 2-3. APK 내려받기

- 빌드가 초록색 체크(✓)로 끝나면, 해당 실행 화면 맨 아래
  **Artifacts → `basketball-scoreboard-apk`** 를 클릭해 zip을 내려받습니다.
- 압축을 풀면 `.apk` 파일이 나옵니다. 이걸 안드로이드 기기에 복사해 설치하면 됩니다.
  (설정에서 "출처를 알 수 없는 앱 설치 허용" 필요)

### 수동으로 다시 빌드하고 싶을 때
Actions 탭 → 왼쪽 **Build Android APK** → 오른쪽 **Run workflow** 버튼.

---

## 3단계. (선택) 스토어 배포용 서명된 AAB 만들기

지금 워크플로는 **테스트용 debug APK**를 만듭니다. 기기에 바로 설치해 쓰기엔 충분합니다.
구글 플레이 스토어에 올리려면 서명된 **release AAB**가 필요하며, 키스토어 생성과
서명 설정이 추가로 필요합니다. 필요해지면 그때 알려주세요 — 워크플로를 확장해 드리겠습니다.

---

## 참고: 무엇을 고쳤나

- `main.py` 의 하드코딩된 Windows 경로(`D:/Python_work_Space/...`)를 제거하고,
  `main.py` 위치를 기준으로 리소스를 찾도록 바꿔서 **Mac·안드로이드 모두에서 이미지가 뜨도록** 했습니다.
- 부저(`Buzzer.mp3`) 로딩이 경로 문자열을 한 글자씩 순회하던 버그를 고쳐
  **부저가 실제로 로드/재생**되도록 했습니다.
- 중복·충돌·오타(`arm64-v8aogg`)로 엉켜 있던 `buildozer.spec`을 **하나의 깔끔한 설정**으로 정리했습니다.

---

## 자주 나는 오류 & 해결

- **빌드가 Cython 관련 에러로 실패** → 워크플로에 Cython 0.29.36을 고정해 두었습니다.
  그래도 나면 `buildozer.spec`의 `requirements` 를 확인하세요.
- **`aidl` / SDK license 에러** → `android.accept_sdk_license = True` 로 이미 처리되어 있습니다.
- **APK는 설치됐는데 앱이 바로 꺼짐** → 대부분 리소스 파일 누락입니다.
  `White.jpg / Black.jpg / GBC_Image.png / Buzzer.mp3` 가 저장소에 함께 커밋됐는지 확인하세요.
  (`git status` 로 확인)
