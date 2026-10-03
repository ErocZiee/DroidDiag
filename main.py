import time
import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import platform

if platform == "android":
    from jnius import autoclass
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
    Intent = autoclass("android.content.Intent")
    IntentFilter = autoclass("android.content.IntentFilter")
    BatteryManager = autoclass("android.os.BatteryManager")


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        layout.add_widget(Label(
            text="[b]Hardware Diagnostics[/b]",
            markup=True,
            font_size="22sp",
            size_hint=(1, 0.15)
        ))

        grid = GridLayout(cols=2, spacing=12, size_hint=(1, 0.85))
        grid.add_widget(Button(text="Battery Health", on_press=lambda x: self.go("battery")))
        grid.add_widget(Button(text="Dead Pixels", on_press=lambda x: self.go("display")))
        grid.add_widget(Button(text="Vibrator / Haptics", on_press=lambda x: self.go("vibrate")))
        grid.add_widget(Button(text="CPU Benchmark", on_press=lambda x: self.go("cpu")))

        layout.add_widget(grid)
        self.add_widget(layout)

    def go(self, name):
        self.manager.current = name


class BatteryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        self.lbl = Label(text="Reading battery...", font_size="18sp")
        layout.add_widget(self.lbl)
        layout.add_widget(Button(
            text="Back",
            size_hint=(1, 0.2),
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        ))
        self.add_widget(layout)

    def on_enter(self):
        if platform == "android":
            try:
                act = PythonActivity.mActivity
                filt = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
                status = act.registerReceiver(None, filt)
                level = status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                scale = status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                temp = status.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) / 10.0
                pct = int((level / float(scale)) * 100) if scale > 0 else -1
                self.lbl.text = f"Battery: {pct}%\nTemperature: {temp}°C"
            except Exception as e:
                self.lbl.text = f"Sensor Error:\n{e}"
        else:
            self.lbl.text = "Desktop / Simulator Mode"


class DisplayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colors = [
            (1, 0, 0, 1),
            (0, 1, 0, 1),
            (0, 0, 1, 1),
            (1, 1, 1, 1),
            (0, 0, 0, 1)
        ]
        self.idx = 0
        self.btn = Button(text="Tap anywhere to cycle colors", on_press=self.cycle)
        self.add_widget(self.btn)

    def cycle(self, *args):
        self.idx += 1
        if self.idx >= len(self.colors):
            self.idx = 0
            self.manager.current = "dashboard"
            return
        self.btn.background_color = self.colors[self.idx]
        self.btn.text = ""


class VibrateScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        self.lbl = Label(text="Test Haptic Motor", font_size="18sp")
        layout.add_widget(self.lbl)
        layout.add_widget(Button(text="Buzz (300ms)", on_press=self.vibrate))
        layout.add_widget(Button(
            text="Back",
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        ))
        self.add_widget(layout)

    def vibrate(self, *args):
        if platform == "android":
            try:
                act = PythonActivity.mActivity
                vib = act.getSystemService(Context.VIBRATOR_SERVICE)
                vib.vibrate(300)
                self.lbl.text = "Motor pulsed 300ms"
            except Exception as e:
                self.lbl.text = f"Vibrator error: {e}"
        else:
            self.lbl.text = "Simulated buzz"


class CpuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        self.lbl = Label(text="Ready to benchmark CPU", font_size="18sp")
        layout.add_widget(self.lbl)
        layout.add_widget(Button(text="Run Benchmark", on_press=self.run_test))
        layout.add_widget(Button(
            text="Back",
            on_press=lambda x: setattr(self.manager, 'current', 'dashboard')
        ))
        self.add_widget(layout)

    def run_test(self, *args):
        self.lbl.text = "Benchmarking (1.5M calculations)..."
        Clock.schedule_once(self._calc, 0.05)

    def _calc(self, dt):
        start = time.perf_counter()
        tot = sum(math.sqrt(i) for i in range(1, 1500000))
        elapsed = time.perf_counter() - start
        score = int(10000 / elapsed)
        self.lbl.text = f"Time: {elapsed:.2f}s\nScore: {score} pts"


class DiagnosticApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(BatteryScreen(name="battery"))
        sm.add_widget(DisplayScreen(name="display"))
        sm.add_widget(VibrateScreen(name="vibrate"))
        sm.add_widget(CpuScreen(name="cpu"))
        return sm


if __name__ == "__main__":
    DiagnosticApp().run()
