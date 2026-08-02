from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.audio import SoundLoader
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import os
from pathlib import Path


# main.py 가 있는 폴더(안드로이드에서는 앱 소스 루트)를 기준으로 리소스 경로를 만든다.
# 이렇게 하면 Windows / macOS / Android 어디서든 동일하게 동작한다.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(filename):
    """SCRIPT_DIR 기준으로 리소스 파일의 절대경로를 반환한다."""
    return os.path.join(SCRIPT_DIR, filename)


class ScoreboardApp(App):
    
    def build(self):
        # 안드로이드/iOS 에서는 창 크기를 강제하지 않고 폰의 실제 해상도를 그대로 쓴다.
        # (데스크톱에서 테스트할 때만 16:9 창을 띄운다.)
        if platform not in ('android', 'ios'):
            Window.size = (1280, 720)
        Window.clearcolor = (0, 0, 0, 1)  # 검은색 배경
        SCRIPT_DIR = Path(__file__).resolve().parent
        main = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # ===== 상단 컨트롤 영역 =====
        top = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=20)

        # 팀명 입력 (화이트/블랙)
        team_box = BoxLayout(orientation='horizontal', spacing=6)
        # self.get_jersey_path = "D:/Python_work_Space/Practice/BasketBall_ScoreBoard/"
        self.team1_input = TextInput(
            text='WHITE', multiline=False, font_size='50sp',
            size_hint_x=0.3, background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.team2_input = TextInput(
            text='BLACK', multiline=False, font_size='50sp',
            size_hint_x=0.3, background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(0.8, 0.8, 0.8, 1)
        )

        # --- build() in top control bar ---
        # SWITCH 는 가로 폭을 좁게 (size_hint_x 작게)
        self.switch_btn = Button(text='SWITCH', background_color=(0.5,0.5,0.5,1),
                                 size_hint_x=0.2)
        self.switch_btn.bind(on_press=lambda *_: self.swap_teams())
        top.add_widget(self.switch_btn)
        
        
        # team_box.add_widget(self.team1_input)
        # team_box.add_widget(Label(text='VS', size_hint_x=0.08, color=(1, 1, 1, 1)))
        # team_box.add_widget(self.team2_input)

        # 쿼터 선택
        self.quarter_spinner = Spinner(
            text='1Q', values=('1Q', '2Q', '3Q', '4Q', 'OT'),
            size_hint_x=0.15, background_color=(0.25, 0.25, 0.25, 1)
        )

        # 게임 타이머 컨트롤 (Save BMP 제거됨) - 남는 폭을 넉넉히 차지
        timer_ctrl = BoxLayout(orientation='horizontal', size_hint_x=0.65, spacing=10)
        self.start_btn = Button(text='START', background_color=(0, 0.6, 0, 1))
        self.pause_btn = Button(text='PAUSE', background_color=(0.6, 0.6, 0, 1))
        #self.restart_btn = Button(text='RESTART', background_color=(0, 0.4, 0.6, 1))
        self.reset_btn = Button(text='RESET', background_color=(0.6, 0, 0, 1))
        #self.buzzer_btn = Button(text='BUZZER', background_color=(0.4, 0, 0.5, 1))

        self.start_btn.bind(on_press=self.start_timer)
        self.pause_btn.bind(on_press=self.pause_timer)
        #self.restart_btn.bind(on_press=self.restart_timer)
        self.reset_btn.bind(on_press=self.reset_timer)
        #self.buzzer_btn.bind(on_press=self.select_buzzer_file)

        for b in (self.start_btn, self.pause_btn, self.reset_btn):
            timer_ctrl.add_widget(b)

        # team_box 는 비어 있어(팀명 입력 미사용) 상단에 넣지 않는다 → 빈 공간 제거
        top.add_widget(self.quarter_spinner)
        top.add_widget(timer_ctrl)
        main.add_widget(top)

        # ===== 전광판 영역 =====
        board = GridLayout(cols=3, spacing=10)

        # 왼쪽 팀 (WHITE) - 유니폼 이미지 포함
        left = BoxLayout(orientation='vertical', spacing=8)
        
        # 유니폼 이미지 + 팀명
        left_team_header = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)
        # --- 스크립트가 있는 폴더의 절대 경로 ---
        
        #SCRIPT_DIR = Path(__file__).resolve().parent
        # --- assets 폴더 안의 icon.png 경로 지정 ---
        IMAGE_PATH = SCRIPT_DIR
        # os 모듈 사용 시: ICON_PATH = os.path.join(SCRIPT_DIR, "assets", "icon.png")
        IMAGE_PATH = os.path.join(SCRIPT_DIR, "White.jpg")

        self.team1_jersey = Image(
            source=self.get_jersey_path(IMAGE_PATH),
            size_hint_x=0.3,
            allow_stretch=True,
            keep_ratio=True
        )

        self.team1_name = Label(
            text='WHITE', color=(1, 1, 1, 1), font_size='50sp', 
            size_hint_x=0.7
        )
        left_team_header.add_widget(self.team1_jersey)
        left_team_header.add_widget(self.team1_name)
        
        # 3배 큰 점수 폰트
        self.team1_score_lbl = Label(
            text='0', color=(1, 1, 0, 1), font_size='350sp', size_hint_y=0.6
        )
        
        left_btns = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=6)
        l_plus1 = Button(text='+2', background_color=(0, 0.5, 0, 1))
        l_plus3 = Button(text='+3', background_color=(0, 0.5, 0, 1))
        l_minus1 = Button(text='-1', background_color=(0.5, 0, 0, 1))

        l_plus1.bind(on_press=lambda *_: self.update_score(1, 2))
        l_plus3.bind(on_press=lambda *_: self.update_score(1, 3))
        l_minus1.bind(on_press=lambda *_: self.update_score(1, -1))
        
        left_btns.add_widget(l_plus1)
        left_btns.add_widget(l_plus3)
        left_btns.add_widget(l_minus1)

        left.add_widget(left_team_header)
        left.add_widget(self.team1_score_lbl)
        left.add_widget(left_btns)

        # 중앙 (타이머 + 중앙 로고)
        center = BoxLayout(orientation='vertical', spacing=10)

        # 점수 초기화 버튼 (쿼터 표시 위 중앙) - 양팀 점수를 0으로.
        # 높이는 아래에서 상단 SWITCH 버튼과 동일하게 바인딩한다.
        self.score_reset_btn = Button(
            text='Score Reset', background_color=(0.2, 0.2, 0.6, 1),
            size_hint_y=None
        )
        self.score_reset_btn.bind(on_press=self.reset_scores)

        # 쿼터 표시 - 폰트를 키운다 (size_hint_y 확대 + autofont hfactor 상향)
        self.q_label = Label(
            text='1Q', color=(1, 1, 1, 1), font_size='40sp', size_hint_y=0.22
        )

        # 중앙 전광판 이미지
        self.center_logo = Image(
            source=self.get_center_logo_path(),
            size_hint_y=1,
            allow_stretch=True,
            keep_ratio=True
        )
        '''
        center_logo_btn = Button(
            text='CENTER LOGO', background_color=(0, 0.5, 0.7, 1),
            size_hint_y=0.08, font_size='12sp'
        )
        '''
        #center_logo_btn.bind(on_press=self.select_center_logo)

        # 2배 큰 타이머 폰트 (Shot Clock 제거됨)
        self.timer_lbl = Label(
            text='10:00.0', color=(1, 1, 1, 1), font_size='120sp', size_hint_y=0.4
        )

        # 타이머 설정 버튼들
        timer_set_btns = BoxLayout(orientation='horizontal', size_hint_y=0.12, spacing=5)
        set_10min = Button(text='10:00', background_color=(0.3, 0.3, 0.3, 1))
        set_5min = Button(text='5:00', background_color=(0.3, 0.3, 0.3, 1))
        set_1min = Button(text='1:00', background_color=(0.3, 0.3, 0.3, 1))
        
        set_10min.bind(on_press=lambda *_: self.set_timer(600))
        set_5min.bind(on_press=lambda *_: self.set_timer(300))
        set_1min.bind(on_press=lambda *_: self.set_timer(60))
        
        timer_set_btns.add_widget(set_10min)
        timer_set_btns.add_widget(set_5min)
        timer_set_btns.add_widget(set_1min)

        center.add_widget(self.score_reset_btn)
        center.add_widget(self.q_label)
        center.add_widget(self.center_logo)
        #center.add_widget(center_logo_btn)
        center.add_widget(self.timer_lbl)
        center.add_widget(timer_set_btns)

        # 오른쪽 팀 (BLACK) - 유니폼 이미지 포함
        right = BoxLayout(orientation='vertical', spacing=8)
        IMAGE_PATH = SCRIPT_DIR
        # 유니폼 이미지 + 팀명
        IMAGE_PATH = os.path.join(SCRIPT_DIR, "Black.jpg")
        right_team_header = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)
        self.team2_jersey = Image(
            source=self.get_jersey_path(IMAGE_PATH),
            size_hint_x=0.3,
            allow_stretch=True,
            keep_ratio=True
        )
        self.team2_name = Label(
            text='BLACK', color=(0.8, 0.8, 0.8, 1), font_size='50sp',
            size_hint_x=0.7
        )
        right_team_header.add_widget(self.team2_jersey)
        right_team_header.add_widget(self.team2_name)
        
        # 3배 큰 점수 폰트
        self.team2_score_lbl = Label(
            text='0', color=(1, 1, 0, 1), font_size='350sp', size_hint_y=0.6
        )
        
        right_btns = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=6)
        r_plus1 = Button(text='+2', background_color=(0, 0.5, 0, 1))
        r_plus3 = Button(text='+3', background_color=(0, 0.5, 0, 1))
        r_minus1 = Button(text='-1', background_color=(0.5, 0, 0, 1))

        r_plus1.bind(on_press=lambda *_: self.update_score(2, 2))
        r_plus3.bind(on_press=lambda *_: self.update_score(2, 3))
        r_minus1.bind(on_press=lambda *_: self.update_score(2, -1))
        
        right_btns.add_widget(r_plus1)
        right_btns.add_widget(r_plus3)
        right_btns.add_widget(r_minus1)

        right.add_widget(right_team_header)
        right.add_widget(self.team2_score_lbl)
        right.add_widget(right_btns)

        board.add_widget(left)
        board.add_widget(center)
        board.add_widget(right)
        main.add_widget(board)

        # ===== 상태 초기화 =====
        self.team1_score = 0
        self.team2_score = 0
        self.timer_seconds = 600.0  # 10:00.0
        self.timer_running = False
        self.timer_event = None
        self.buzzer_sound = None
        self.buzzer_path = None
        self._buzzer_fired = False  # 00.0초에서 부저가 반복 재생되지 않도록

        # 기본 파일 로드
        self.load_default_buzzer()

        # 바인딩
        self.team1_input.bind(text=self._on_team1_name)
        self.team2_input.bind(text=self._on_team2_name)
        self.quarter_spinner.bind(text=lambda _, v: self.q_label.setter('text')(self.q_label, v))

        # ===== 글자 크기 자동 맞춤 =====
        # 고정 font_size(예: 350sp) 대신, 위젯 크기에 비례해 글자 크기를 계산하도록
        # 바인딩한다. 이러면 폰 해상도가 무엇이든 점수/타이머/팀명이 화면을 넘지 않는다.
        self._autofont(self.team1_score_lbl, 0.85)
        self._autofont(self.team2_score_lbl, 0.85)
        self._autofont(self.timer_lbl, 0.85)
        self._autofont(self.team1_name, 0.55)
        self._autofont(self.team2_name, 0.55)
        self._autofont(self.q_label, 0.9)   # 쿼터 표시 폰트 크게

        # 상단 컨트롤 버튼/스피너: 글자가 버튼보다 커서 겹치던 문제 수정.
        # 세로는 버튼 높이의 0.4, 가로는 글자 수를 넉넉히 고려(char_w=0.8)해
        # 버튼 폭 안에 들어오게 한다. Score Reset 도 같은 규칙 → 폰트가 상단과 동일해짐.
        for _btn in (self.switch_btn, self.start_btn, self.pause_btn,
                     self.reset_btn, self.quarter_spinner, self.score_reset_btn):
            self._autofont(_btn, 0.4, char_w=0.8)

        # Score Reset 버튼 높이를 상단 SWITCH 버튼과 정확히 동일하게 맞춘다.
        self.switch_btn.bind(
            height=lambda _inst, h: setattr(self.score_reset_btn, 'height', h))
        self.score_reset_btn.height = self.switch_btn.height

        return main

    def _autofont(self, label, hfactor, char_w=0.62):
        """label 의 글자 크기를 위젯 크기에 맞춰 자동 계산해준다.
        - 세로: 위젯 높이 * hfactor
        - 가로: 글자 수를 고려해 폭을 넘지 않도록 제한
        둘 중 작은 값을 써서 어떤 해상도에서도 텍스트가 잘리거나 넘치지 않게 한다.
        """
        def _upd(inst, *_):
            w, h = inst.size
            if w <= 0 or h <= 0:
                return
            n = max(len(inst.text), 1)
            fs = min(h * hfactor, w / (char_w * n))
            inst.font_size = max(8, fs)
        label.bind(size=_upd, text=_upd)
        _upd(label)

    
    # ===== 파일 경로 설정 (여기서 수정 가능) =====
    def get_jersey_path(self, team_color):
        """유니폼 이미지 경로 반환.

        build()에서 이미 SCRIPT_DIR 기준 절대경로(White.jpg / Black.jpg)를
        넘겨주므로, 파일이 존재하면 그대로 반환하고 없으면 빈 문자열을 반환한다.
        (기존의 하드코딩된 Windows 경로 'D:/...' 는 제거함)
        """
        if team_color and os.path.exists(team_color):
            return team_color
        return ''  # 파일이 없으면 빈 이미지

    def get_center_logo_path(self):
        """중앙 로고 이미지 경로 반환 - SCRIPT_DIR 기준 GBC_Image.png"""
        image_path = resource_path("GBC_Image.png")
        if os.path.exists(image_path):
            return image_path
        return ''  # 파일이 없으면 빈 이미지

    # ===== 팀명 및 점수 관리 =====
    def _on_team1_name(self, instance, value):
        self.team1_name.text = value[:10]

    def _on_team2_name(self, instance, value):
        self.team2_name.text = value[:10]

    def update_score(self, team, delta):
        if team == 1:
            self.team1_score = max(0, self.team1_score + delta)
            self.team1_score_lbl.text = str(self.team1_score)
        else:
            self.team2_score = max(0, self.team2_score + delta)
            self.team2_score_lbl.text = str(self.team2_score)

    def reset_scores(self, *_):
        """양팀 점수를 0으로 초기화한다 (Score Reset 버튼)."""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_score_lbl.text = '0'
        self.team2_score_lbl.text = '0'

    # ===== 게임 타이머 (음성 카운트다운 제거됨) =====
    def start_timer(self, *_):
        if not self.timer_running:
            if self.timer_seconds > 0:
                self._buzzer_fired = False
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self._tick_timer, 0.1)

    def pause_timer(self, *_):
        if self.timer_running:
            self.timer_running = False
            self.pause_btn.text='RESUME'
            if self.timer_event:
                self.timer_event.cancel()
        else:
            if self.timer_seconds > 0:
                self.timer_running = True
                self.pause_btn.text='PAUSE'
                self.timer_event = Clock.schedule_interval(self._tick_timer, 0.1)

    '''
    def restart_timer(self, *_):
        """새로 추가된 재시작 버튼 - 일시정지된 타이머를 재개"""
        if not self.timer_running and self.timer_seconds > 0:
            self.timer_running = True
            self.timer_event = Clock.schedule_interval(self._tick_timer, 0.1)
    '''
    def reset_timer(self, *_):
        #self.pause_timer()
        self.timer_seconds = 600.0
        self._buzzer_fired = False
        self._render_timer()

    def set_timer(self, seconds):
        #self.pause_timer()
        self.timer_seconds = float(seconds)
        self._buzzer_fired = False
        self._render_timer()

    def _tick_timer(self, dt):
        if self.timer_seconds > 0:
            self.timer_seconds = max(0.0, self.timer_seconds - 0.1)
            self._render_timer()
        else:
            self.timer_seconds = 0.0
            #self.pause_timer()
            self._render_timer()
            # 00.0 이 된 순간 딱 한 번만 부저를 울린다 (0.1초마다 재생되던 문제 수정)
            if not self._buzzer_fired:
                self._buzzer_fired = True
                self.play_buzzer()

    def _render_timer(self):
        """2분 남음 알림 제거됨"""
        mins = int(self.timer_seconds // 60)
        secs = int(self.timer_seconds % 60)
        tenths = int((self.timer_seconds % 1) * 10)
        self.timer_lbl.text = f"{mins:02d}:{secs:02d}.{tenths}"
        
        # 1분 이하일 때 빨간색으로 표시
        if self.timer_seconds <= 60:
            self.timer_lbl.color = (1, 0, 0, 1)
        else:
            self.timer_lbl.color = (1, 1, 1, 1)

    # ===== 부져 관리 =====
    def load_default_buzzer(self):
        # 기존 코드는 'for path in Buzzer_PATH:' 로 경로 문자열을 한 글자씩
        # 순회하는 버그가 있어 부저가 로드되지 않았음. 파일을 직접 로드하도록 수정.
        # NBA 아레나식 경기종료 혼을 우선 사용하고, 없으면 기존 Buzzer.mp3 로 폴백한다.
        for filename in ("NBA_Buzzer.wav", "Buzzer.mp3"):
            buzzer_path = resource_path(filename)
            if not os.path.exists(buzzer_path):
                continue
            snd = SoundLoader.load(buzzer_path)
            if snd:
                snd.volume = 1.0
                self.buzzer_sound = snd
                self.buzzer_path = buzzer_path
                break

    def select_buzzer_file(self, *_):
        content = BoxLayout(orientation='vertical', spacing=10)
        chooser = FileChooserListView(filters=['*.mp3', '*.wav', '*.ogg'])
        btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=8)
        
        choose = Button(text='Select', background_color=(0, 0.6, 0, 1))
        test = Button(text='Test', background_color=(0, 0, 0.6, 1))
        cancel = Button(text='Cancel', background_color=(0.6, 0, 0, 1))
        
        btns.add_widget(choose)
        btns.add_widget(test)
        btns.add_widget(cancel)
        
        content.add_widget(Label(text='Select Buzzer Sound (MP3/WAV/OGG)', size_hint_y=None, height=28))
        content.add_widget(chooser)
        content.add_widget(btns)
        
        pop = Popup(title='Buzzer Sound', content=content, size_hint=(0.86, 0.86))

        def do_select(*_):
            if chooser.selection:
                fp = chooser.selection[0]
                self._load_buzzer(fp)
                pop.dismiss()

        def do_test(*_):
            if chooser.selection:
                snd = SoundLoader.load(chooser.selection[0])
                if snd:
                    snd.play()

        choose.bind(on_press=do_select)
        test.bind(on_press=do_test)
        cancel.bind(on_press=lambda *_: pop.dismiss())
        pop.open()

    '''
    def _load_buzzer(self, file_path):
        try:
            snd = SoundLoader.load(file_path)
            if snd:
                self.buzzer_sound = snd
                self.buzzer_path = file_path
                name = os.path.basename(file_path)
                self.buzzer_btn.text = name if len(name) <= 10 else (name[:7] + '...')
            else:
                self.buzzer_btn.text = 'BUZZER'
        except Exception as e:
            print('Buzzer load error:', e)
            self.buzzer_sound = None
            self.buzzer_btn.text = 'BUZZER'
    '''
    def play_buzzer(self):
        if self.buzzer_sound:
            # 이미 재생 중이면 처음부터 다시 울리도록 정지 후 재생
            if self.buzzer_sound.state == 'play':
                self.buzzer_sound.stop()
            self.buzzer_sound.play()
        else:
            # 안드로이드에서 진동 지원
            try:
                from android.runnable import run_on_ui_thread
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                vibrator = PythonActivity.mActivity.getSystemService(Context.VIBRATOR_SERVICE)
                vibrator.vibrate(500)  # 0.5초 진동
            except ImportError:
                # Windows에서는 beep 소리
                try:
                    import winsound
                    winsound.Beep(3000, 3000)
                except Exception:
                    pass

    # ===== 중앙 로고 관리 =====
    def select_center_logo(self, *_):
        content = BoxLayout(orientation='vertical', spacing=10)
        chooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg', '*.gif'])
        
        # 미리보기
        preview_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=10)
        preview_image = Image(size_hint_x=0.3, allow_stretch=True, keep_ratio=True)
        info_label = Label(text='Select image to preview', size_hint_x=0.7)
        preview_layout.add_widget(preview_image)
        preview_layout.add_widget(info_label)

        def update_preview(instance, selection):
            if selection:
                try:
                    preview_image.source = selection[0]
                    info_label.text = f"File: {os.path.basename(selection[0])}"
                except:
                    preview_image.source = ''
                    info_label.text = 'Cannot preview this file'
            else:
                preview_image.source = ''
                info_label.text = 'No file selected'

        chooser.bind(selection=update_preview)

        btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=8)
        select_btn = Button(text='Select', background_color=(0, 0.6, 0, 1))
        clear_btn = Button(text='Clear', background_color=(0.6, 0.6, 0, 1))
        cancel_btn = Button(text='Cancel', background_color=(0.6, 0, 0, 1))
        
        btns.add_widget(select_btn)
        btns.add_widget(clear_btn)
        btns.add_widget(cancel_btn)

        content.add_widget(Label(text='Select Center Logo (PNG/JPG/GIF)', size_hint_y=None, height=28))
        content.add_widget(chooser)
        content.add_widget(preview_layout)
        content.add_widget(btns)

        pop = Popup(title='Center Logo', content=content, size_hint=(0.9, 0.9))

        def do_select(*_):
            if chooser.selection:
                self.center_logo.source = chooser.selection[0]
                pop.dismiss()

        def do_clear(*_):
            self.center_logo.source = ''
            pop.dismiss()

        select_btn.bind(on_press=do_select)
        clear_btn.bind(on_press=do_clear)
        cancel_btn.bind(on_press=lambda *_: pop.dismiss())
        pop.open()

    def swap_teams(self):
            # Swap scores
        self.team1_score, self.team2_score = self.team2_score, self.team1_score
        self.team1_score_lbl.text, self.team2_score_lbl.text = (
            str(self.team1_score),
            str(self.team2_score)
        )
        
        if self.team1_name.text == 'WHITE':
            self.team1_name.text = 'BLACK'
            self.team2_name.text = 'WHITE'
            self.team1_jersey.source,self.team2_jersey.source = (
            str(self.team2_jersey.source),
            str(self.team1_jersey.source) 
            )
        
        else :
            self.team1_name.text ='WHITE'
            self.team2_name.text = 'BLACK'
            self.team2_jersey.source,self.team1_jersey.source = (
            str(self.team1_jersey.source),
            str(self.team2_jersey.source) 
            )
      


if __name__ == '__main__':
    ScoreboardApp().run()