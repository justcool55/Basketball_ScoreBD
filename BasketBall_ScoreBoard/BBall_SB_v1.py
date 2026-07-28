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
from kivy.core.audio import SoundLoader
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from datetime import datetime
import os

# ---------- App ----------
class ScoreboardApp(App):
    def build(self):
        # 16:9 black stage (good for 1280x720 or 1920x1080)
        Window.size = (1280, 720)
        Window.clearcolor = (0, 0, 0, 1)

        main = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # ===== Top controls =====
        top = BoxLayout(orientation='horizontal', size_hint_y=0.13, spacing=8)

        # Team name inputs (left: White / right: Black)
        team_box = BoxLayout(orientation='horizontal', spacing=6)

        self.team1_input = TextInput(
            text='White', multiline=False, font_size='18sp',
            size_hint_x=0.34, background_color=(0.15,0.15,0.15,1),
            foreground_color=(1,1,1,1)
        )
        self.team2_input = TextInput(
            text='Black', multiline=False, font_size='18sp',
            size_hint_x=0.34, background_color=(0.15,0.15,0.15,1),
            foreground_color=(0.8,0.8,0.8,1)   # light gray text
        )

        team_box.add_widget(self.team1_input)
        team_box.add_widget(Label(text='VS', size_hint_x=0.08, color=(1,1,1,1)))
        team_box.add_widget(self.team2_input)

        # Quarter
        self.quarter_spinner = Spinner(
            text='1Q', values=('1Q','2Q','3Q','4Q','OT'),
            size_hint_x=0.12, background_color=(0.25,0.25,0.25,1)
        )

        # Game timer controls
        timer_ctrl = BoxLayout(orientation='horizontal', size_hint_x=0.42, spacing=6)
        self.start_btn = Button(text='START', background_color=(0,0.6,0,1))
        self.pause_btn = Button(text='PAUSE', background_color=(0.6,0.6,0,1))
        self.reset_btn = Button(text='RESET', background_color=(0.6,0,0,1))
        self.buzzer_btn = Button(text='BUZZER', background_color=(0.4,0,0.5,1))
        self.save_btn = Button(text='SAVE BMP', background_color=(0.2,0.2,0.2,1))

        self.start_btn.bind(on_press=self.start_timer)
        self.pause_btn.bind(on_press=self.pause_timer)
        self.reset_btn.bind(on_press=self.reset_timer)
        self.buzzer_btn.bind(on_press=self.select_buzzer_file)
        self.save_btn.bind(on_press=self.save_scoreboard_bmp)

        for b in (self.start_btn, self.pause_btn, self.reset_btn, self.buzzer_btn, self.save_btn):
            timer_ctrl.add_widget(b)

        top.add_widget(team_box)
        top.add_widget(self.quarter_spinner)
        top.add_widget(timer_ctrl)
        main.add_widget(top)

        # ===== Scoreboard area =====
        board = GridLayout(cols=3, spacing=10)

        # Left team (White)
        left = BoxLayout(orientation='vertical', spacing=8)
        self.team1_name = Label(text='White', color=(1,1,1,1), font_size='28sp', size_hint_y=0.18)
        self.team1_score_lbl = Label(text='0', color=(1,1,0,1), font_size='100sp', size_hint_y=0.6)
        left_btns = BoxLayout(orientation='horizontal', size_hint_y=0.22, spacing=6)
        l_plus1 = Button(text='+1'); l_plus3 = Button(text='+3'); l_minus1 = Button(text='-1')
        for w in (l_plus1, l_plus3, l_minus1):
            w.background_color = (0.25,0.25,0.25,1)
        l_plus1.bind(on_press=lambda *_: self.update_score(1, 1))
        l_plus3.bind(on_press=lambda *_: self.update_score(1, 3))
        l_minus1.bind(on_press=lambda *_: self.update_score(1,-1))
        left_btns.add_widget(l_plus1); left_btns.add_widget(l_plus3); left_btns.add_widget(l_minus1)

        left.add_widget(self.team1_name)
        left.add_widget(self.team1_score_lbl)
        left.add_widget(left_btns)

        # Center (Timers + alerts)
        center = BoxLayout(orientation='vertical', spacing=10)

        self.q_label = Label(text='1Q', color=(1,1,1,1), font_size='32sp', size_hint_y=0.16)

        # Main game timer (yellow)
        self.timer_lbl = Label(text='10:00.0', color=(1,1,0,1), font_size='66sp', size_hint_y=0.38)

        # Shot clock line
        shot_line = BoxLayout(orientation='horizontal', size_hint_y=0.20, spacing=8)
        self.shot_lbl = Label(text='24.0', font_size='46sp', color=(1,0.2,0.2,1))  # red-ish
        sc_start = Button(text='SC START'); sc_pause = Button(text='SC PAUSE')
        sc_reset = Button(text='SC RESET'); sc_24 = Button(text='24s'); sc_14 = Button(text='14s')
        for b in (sc_start, sc_pause, sc_reset, sc_24, sc_14):
            b.background_color = (0.2,0.2,0.2,1)
        sc_start.bind(on_press=self.shot_start)
        sc_pause.bind(on_press=self.shot_pause)
        sc_reset.bind(on_press=lambda *_: self.set_shot_clock(24.0))
        sc_24.bind(on_press=lambda *_: self.set_shot_clock(24.0))
        sc_14.bind(on_press=lambda *_: self.set_shot_clock(14.0))
        shot_line.add_widget(Label(text='SHOT', color=(1,1,1,1), size_hint_x=0.2))
        shot_line.add_widget(self.shot_lbl)
        for b in (sc_start, sc_pause, sc_reset, sc_24, sc_14):
            shot_line.add_widget(b)

        # 2-minute remaining banner
        self.alert_lbl = Label(text='', color=(1,1,1,1), font_size='28sp', size_hint_y=0.16)

        center.add_widget(self.q_label)
        center.add_widget(self.timer_lbl)
        center.add_widget(shot_line)
        center.add_widget(self.alert_lbl)

        # Right team (Black)
        right = BoxLayout(orientation='vertical', spacing=8)
        self.team2_name = Label(text='Black', color=(0.8,0.8,0.8,1), font_size='28sp', size_hint_y=0.18)
        self.team2_score_lbl = Label(text='0', color=(1,1,0,1), font_size='100sp', size_hint_y=0.6)
        right_btns = BoxLayout(orientation='horizontal', size_hint_y=0.22, spacing=6)
        r_plus1 = Button(text='+1'); r_plus3 = Button(text='+3'); r_minus1 = Button(text='-1')
        for w in (r_plus1, r_plus3, r_minus1):
            w.background_color = (0.25,0.25,0.25,1)
        r_plus1.bind(on_press=lambda *_: self.update_score(2, 1))
        r_plus3.bind(on_press=lambda *_: self.update_score(2, 3))
        r_minus1.bind(on_press=lambda *_: self.update_score(2,-1))
        right_btns.add_widget(r_plus1); right_btns.add_widget(r_plus3); right_btns.add_widget(r_minus1)

        right.add_widget(self.team2_name)
        right.add_widget(self.team2_score_lbl)
        right.add_widget(right_btns)

        board.add_widget(left); board.add_widget(center); board.add_widget(right)
        main.add_widget(board)

        # ===== State & bindings =====
        self.team1_score = 0
        self.team2_score = 0

        self.timer_seconds = 600.0  # 10:00.0
        self.timer_running = False
        self.timer_event = None

        self.shot_seconds = 24.0
        self.shot_running = False
        self.shot_event = None

        self.buzzer_sound = None
        self.buzzer_path = None

        self.load_default_buzzer()

        self.team1_input.bind(text=self._on_team1_name)
        self.team2_input.bind(text=self._on_team2_name)
        self.quarter_spinner.bind(text=lambda _,v: self.q_label.setter('text')(self.q_label, v))

        return main

    # ---------- Team & score ----------
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

    # ---------- Game timer ----------
    def start_timer(self, *_):
        if not self.timer_running:
            self.timer_running = True
            # Auto-reset shot clock to 24s and start/continue with game timer
            self.set_shot_clock(24.0)
            self.shot_start()
            self.timer_event = Clock.schedule_interval(self._tick_timer, 0.1)

    def pause_timer(self, *_):
        if self.timer_running:
            self.timer_running = False
            if self.timer_event:
                self.timer_event.cancel()
        # Auto-pause shot clock with main timer
        self.shot_pause()

    def reset_timer(self, *_):
        self.pause_timer()
        self.timer_seconds = 600.0
        self._render_timer()

    def set_timer(self, seconds: float):
        self.pause_timer()
        self.timer_seconds = float(seconds)
        self._render_timer()

    def _tick_timer(self, dt):
        if self.timer_seconds > 0:
            self.timer_seconds = max(0.0, self.timer_seconds - 0.1)
            self._render_timer()
        else:
            self.timer_seconds = 0.0
            self.pause_timer()
            self._render_timer()
            self.play_buzzer()

    def _render_timer(self):
        mins = int(self.timer_seconds // 60)
        secs = int(self.timer_seconds % 60)
        tenths = int((self.timer_seconds % 1) * 10)
        self.timer_lbl.text = f"{mins:02d}:{secs:02d}.{tenths}"

        # 2-minute alert banner
        if 0 < self.timer_seconds <= 120:
            self.alert_lbl.text = "⏰ 2분 남음!"
            self.alert_lbl.color = (1,1,1,1) if self.timer_seconds % 1 < 0.5 else (0.75,0.75,0.75,1)
        else:
            self.alert_lbl.text = ""

    # ---------- Shot clock ----------
    def set_shot_clock(self, seconds: float):
        self.shot_seconds = float(seconds)
        self._render_shot()

    def shot_start(self, *_):
        if not self.shot_running:
            self.shot_running = True
            self.shot_event = Clock.schedule_interval(self._tick_shot, 0.1)

    def shot_pause(self, *_):
        if self.shot_running:
            self.shot_running = False
            if self.shot_event:
                self.shot_event.cancel()

    def _tick_shot(self, dt):
        if self.shot_seconds > 0:
            self.shot_seconds = max(0.0, self.shot_seconds - 0.1)
            self._render_shot()
        else:
            self.shot_seconds = 0.0
            self.shot_pause()
            self._render_shot()
            self.play_buzzer()

    def _render_shot(self):
        # Show one decimal (e.g., 24.0)
        self.shot_lbl.text = f"{self.shot_seconds:0.1f}"
        # Turn red when <= 5s, green otherwise
        self.shot_lbl.color = (1,0.2,0.2,1) if self.shot_seconds <= 5.0 else (0,1,0,1)

    # ---------- Buzzer ----------
    def load_default_buzzer(self):
        for path in ['buzzer.mp3', 'assets/buzzer.mp3', 'sounds/buzzer.mp3']:
            if os.path.exists(path):
                self.buzzer_sound = SoundLoader.load(path)
                self.buzzer_path = path
                name = os.path.basename(path)
                self.buzzer_btn.text = name if len(name) <= 10 else (name[:7] + '...')
                break

    def select_buzzer_file(self, *_):
        content = BoxLayout(orientation='vertical', spacing=10)
        chooser = FileChooserListView(filters=['*.mp3','*.wav','*.ogg'])
        btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=8)
        choose = Button(text='Select', background_color=(0,0.6,0,1))
        test = Button(text='Test', background_color=(0,0,0.6,1))
        cancel = Button(text='Cancel', background_color=(0.6,0,0,1))
        btns.add_widget(choose); btns.add_widget(test); btns.add_widget(cancel)
        content.add_widget(Label(text='Select Buzzer Sound File (MP3/WAV/OGG)', size_hint_y=None, height=28))
        content.add_widget(chooser); content.add_widget(btns)
        pop = Popup(title='Buzzer', content=content, size_hint=(0.86,0.86))

        def do_select(*_):
            if chooser.selection:
                fp = chooser.selection[0]
                self._load_buzzer(fp)
                pop.dismiss()
        def do_test(*_):
            if chooser.selection:
                snd = SoundLoader.load(chooser.selection[0])
                if snd: snd.play()
        choose.bind(on_press=do_select)
        test.bind(on_press=do_test)
        cancel.bind(on_press=lambda *_: pop.dismiss())
        pop.open()

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

    def play_buzzer(self):
        if self.buzzer_sound:
            self.buzzer_sound.play()
        else:
            try:
                import winsound
                winsound.Beep(1000, 500)
            except Exception:
                pass

    # ---------- Save BMP ----------
    def save_scoreboard_bmp(self, *_):
        # First save a PNG using Kivy's screenshot
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        png_name = f'scoreboard_{ts}.png'
        Window.screenshot(name=png_name)

        # Convert to BMP if Pillow is available
        try:
            from PIL import Image as PILImage
            img = PILImage.open(png_name)
            bmp_name = f'scoreboard_{ts}.bmp'
            img.save(bmp_name, format='BMP')
            msg = f"Saved {bmp_name}"
        except Exception:
            msg = f"Pillow not available; saved {png_name} (PNG)."

        print(msg)


if __name__ == '__main__':
    ScoreboardApp().run()