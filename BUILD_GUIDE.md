# 농구 전광판 — 안드로이드 앱(APK) 만들기 가이드

이 프로젝트는 **Kivy**(파이썬 UI 프레임워크)로 만들었고, **Buildozer**로 안드로이드 APK를 만듭니다.

> **핵심 제약**: Buildozer 는 **리눅스 전용**입니다. macOS 에서는 직접 빌드가 되지 않습니다.
> 그래서 **GitHub Actions(무료 클라우드 리눅스)** 에서 빌드합니다. Mac 에는 아무것도 설치하지 않아도 됩니다.

---

## 0단계. Mac 에서 먼저 실행해 확인

APK 를 만들기 전에 데스크톱에서 정상 동작하는지 확인합니다.

```bash
cd "/Users/freddy/Desktop/Work/02. Project/BasketBall_ScoreBoard" && ./venv/bin/python main.py
```

점수 +1/+3/-1, 타이머 10:00 / 5:00 / 1:00, START/PAUSE/RESET, SWITCH(팀 교체),
그리고 **00.0 초에서 부저(NBA_Buzzer.wav)** 가 울리면 정상입니다.

---

## 1단계. GitHub 저장소 만들기

1. <https://github.com/new> 접속
2. **Repository name**: `basketball-scoreboard`
3. **Private** 선택 (공개해도 무방)
4. **README / .gitignore / license 는 모두 체크 해제** (빈 저장소로 생성)
5. **Create repository** 클릭

---

## 2단계. 코드 올리기(push)

현재 이 폴더는 이미 `git init` 이 되어 있고 커밋도 1개 있습니다.
**원격 저장소(remote)만 연결되어 있지 않은 상태**입니다.

```bash
cd "/Users/freddy/Desktop/Work/02. Project/BasketBall_ScoreBoard" && git add -A && git commit -m "NBA 부저로 교체 + 안드로이드 빌드 설정 수정"
```

```bash
cd "/Users/freddy/Desktop/Work/02. Project/BasketBall_ScoreBoard" && git branch -M main && git remote add origin https://github.com/<본인아이디>/basketball-scoreboard.git && git push -u origin main
```

> `<본인아이디>` 는 실제 GitHub 아이디로 바꾸세요.
> push 할 때 비밀번호를 물으면 **GitHub 비밀번호가 아니라 Personal Access Token** 이 필요합니다.
> <https://github.com/settings/tokens> → *Generate new token (classic)* → `repo` 권한 체크 → 생성된 토큰을 비밀번호 자리에 붙여넣기.

---

## 3단계. 빌드 자동 실행

`push` 하는 순간 `.github/workflows/build.yml` 이 리눅스 클라우드에서 자동 실행됩니다.

- 저장소 페이지 → **Actions** 탭에서 진행 상황 확인
- **첫 빌드는 안드로이드 SDK/NDK 다운로드 때문에 25~45분** 소요
- 두 번째 빌드부터는 캐시 덕분에 **5~10분**

수동 재실행: Actions 탭 → 왼쪽 **Build Android APK** → 오른쪽 **Run workflow**

---

## 4단계. APK 내려받아 폰에 설치

1. 빌드가 초록 체크(✓)로 끝나면 실행 화면 맨 아래 **Artifacts** 섹션
2. **`basketball-scoreboard-apk`** 클릭 → zip 다운로드
3. 압축 풀면 `basketballscoreboard-2.0-arm64-v8a_armeabi-v7a-debug.apk` 같은 파일이 나옵니다
4. 이 파일을 폰으로 옮깁니다 (카톡 나에게 보내기 / 구글 드라이브 / USB 케이블 아무거나)
5. 폰에서 파일 탭 → 설치
   - **"출처를 알 수 없는 앱"** 경고가 뜨면 → *설정 허용* → 다시 설치
   - Play 프로텍트 경고는 *무시하고 설치* 선택 (서명 안 된 debug 빌드라 정상)

설치 후 앱을 열면 **가로 전체화면**으로 전광판이 뜹니다.

---

## 이번에 고친 것 (이거 안 고치면 빌드 실패)

| 파일 | 문제 | 조치 |
|---|---|---|
| `.github/workflows/build.yml` | `libtinfo5` 는 우분투 24.04 에 없어서 **의존성 설치 단계에서 빌드 전체가 실패**. `ubuntu-latest` 는 현재 24.04 | 필수 패키지만 먼저 설치하고, `libtinfo5` 는 실패해도 넘어가도록 분리 |
| 〃 | 러너 기본 JDK 버전에 따라 빌드가 깨질 수 있음 | `setup-java@v4` 로 **JDK 17 고정** |
| 〃 | 캐시에 `restore-keys` 가 없어 spec 을 한 글자만 고쳐도 SDK/NDK 30분 재다운로드 | `restore-keys` 추가 |
| `buildozer.spec` | `source.dir = .` 이라 **`venv/`(.py 1,425개, 51MB)** 와 예전 버전 사본 폴더까지 APK 에 포함 | `source.exclude_dirs` 추가 |
| 〃 | 안 쓰는 `Buzzer.mp3`(6.9MB), `generated-image.png`(1.4MB) 가 APK 에 중복 포함 | `source.exclude_patterns` 로 제외 (약 **8MB 절감**) |
| 〃 | 앱 아이콘·스플래시가 주석 처리되어 기본 Kivy 로고로 나옴 | 아이콘은 **`GBC_Icon.png`(512×512 GBC 로고)**, 스플래시는 `generated-image.png` 로 지정 |
| `.gitignore` | `_git_trash/` 가 커밋될 뻔함 | 무시 목록 추가 |

---

## 자주 나는 오류 & 해결

**빌드가 `Install system dependencies` 에서 실패**
→ 이번 수정으로 해결됨. 그래도 나면 `build.yml` 의 `runs-on: ubuntu-latest` 를 `ubuntu-22.04` 로 바꿔보세요.

**Cython 관련 에러**
→ 워크플로에 `cython==0.29.36` 고정해 두었습니다. 그래도 나면 `0.29.33` 으로 낮춰보세요.

**APK 는 설치됐는데 앱이 켜자마자 꺼짐**
→ 대부분 리소스 누락입니다. `White.jpg / Black.jpg / GBC_Image.png / NBA_Buzzer.wav` 가 저장소에 커밋됐는지 `git status` 로 확인하세요.
→ 원인을 정확히 보려면 USB 연결 후 `adb logcat | grep python`.

**소리가 안 남**
→ 폰 미디어 볼륨 확인. 무음/진동 모드에서도 미디어 볼륨은 별도입니다.

**화면이 세로로 뜸**
→ `buildozer.spec` 의 `orientation = landscape` 확인. 폰의 *화면 회전 잠금* 도 풀어야 합니다.

---

## (선택) 플레이스토어 배포

지금 워크플로는 **테스트용 debug APK** 를 만듭니다. 폰에 직접 넣어 쓰는 데는 충분합니다.

스토어에 올리려면 추가로 필요한 것:
- **서명 키스토어**(`keytool` 로 생성) + GitHub Secrets 에 등록
- `buildozer android release` 로 **AAB** 빌드 (`android.release_artifact = aab` 이미 설정됨)
- `android.api` 를 구글 정책상 요구 버전으로 상향 (현재 33)

필요해지면 말씀해 주세요 — 워크플로를 확장해 드리겠습니다.
