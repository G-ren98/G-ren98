import sys
import math
import random
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtProperty


def create_font_stack(point_size: int = 11, weight: int = QtGui.QFont.Weight.Medium.value):
    font = QtGui.QFont()
    font.setFamilies([
        "Inter",
        "SF Pro Display",
        "SF Pro Text",
        "Segoe UI",
        "Roboto",
        "Helvetica Neue",
        "Noto Sans",
        "Arial",
        "sans-serif",
    ])
    font.setPointSize(point_size)
    font.setWeight(weight)
    return font


class TitleBar(QtWidgets.QWidget):
    height_px = 44

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.height_px)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("TitleBar")

        self._drag_pos = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        self.logo = QtWidgets.QLabel("⚡")
        self.logo.setFixedSize(28, 28)
        self.logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.title = QtWidgets.QLabel("PyQt6 Neon Glass Dashboard")
        self.title.setFont(create_font_stack(12, QtGui.QFont.Weight.DemiBold.value))

        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addStretch(1)

        self.min_btn = self._make_btn("—", "min")
        self.max_btn = self._make_btn("▢", "max")
        self.close_btn = self._make_btn("✕", "close")

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.min_btn.clicked.connect(self.on_minimize)
        self.max_btn.clicked.connect(self.on_max_restore)
        self.close_btn.clicked.connect(self.on_close)

    def _make_btn(self, text: str, object_name: str) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(text)
        btn.setObjectName(f"TitleBarButton__{object_name}")
        btn.setFixedSize(36, 28)
        btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        return btn

    def on_minimize(self):
        self.window().showMinimized()

    def on_max_restore(self):
        w = self.window()
        if w.isMaximized():
            w.showNormal()
        else:
            w.showMaximized()

    def on_close(self):
        self.window().close()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)


class GradientBackground(QtWidgets.QWidget):
    hueChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 0.0
        self._anim = QtCore.QPropertyAnimation(self, b"hue")
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(360.0)
        self._anim.setDuration(24000)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
        self._anim.setLoopCount(-1)
        self._anim.start()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(1280, 800)

    @pyqtProperty(float, notify=hueChanged)
    def hue(self) -> float:
        return self._hue

    @hue.setter
    def hue(self, value: float) -> None:
        if self._hue != value:
            self._hue = value
            self.hueChanged.emit()
            self.update()

    def _color(self, deg: float, s: float = 0.65, v: float = 0.95, a: float = 1.0) -> QtGui.QColor:
        c = QtGui.QColor()
        c.setHsvF(((self._hue + deg) % 360) / 360.0, s, v, a)
        return c

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        grad = QtGui.QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, self._color(0, 0.7, 0.20))
        grad.setColorAt(0.5, self._color(60, 0.6, 0.18))
        grad.setColorAt(1.0, self._color(120, 0.65, 0.22))
        painter.fillRect(self.rect(), grad)

        # Soft neon blobs
        for i, radius in enumerate((w * 0.35, w * 0.25, w * 0.3)):
            cx = [w * 0.2, w * 0.8, w * 0.5][i]
            cy = [h * 0.25, h * 0.2, h * 0.75][i]
            g = QtGui.QRadialGradient(QtCore.QPointF(cx, cy), radius)
            g.setColorAt(0.0, self._color(i * 120, 0.9, 1.0, 0.35))
            g.setColorAt(1.0, QtGui.QColor(0, 0, 0, 0))
            painter.setBrush(g)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawEllipse(QtCore.QPointF(cx, cy), radius, radius)


class GlassCard(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("GlassCard")
        self._shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(40)
        self._shadow.setColor(QtGui.QColor(0, 0, 0, 110))
        self._shadow.setOffset(0, 16)
        self.setGraphicsEffect(self._shadow)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        radius = 18
        rect = self.rect()
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # Background glass
        bg = QtGui.QColor(255, 255, 255, 34)
        border = QtGui.QColor(255, 255, 255, 55)

        path = QtGui.QPainterPath()
        rectf = QtCore.QRectF(rect)
        rectf = rectf.adjusted(1, 1, -1, -1)
        path.addRoundedRect(rectf, radius, radius)
        painter.fillPath(path, bg)

        # Inner gradient shine
        shine = QtGui.QLinearGradient(0, 0, 0, rect.height())
        shine.setColorAt(0.0, QtGui.QColor(255, 255, 255, 50))
        shine.setColorAt(0.2, QtGui.QColor(255, 255, 255, 25))
        shine.setColorAt(1.0, QtGui.QColor(255, 255, 255, 10))
        painter.fillPath(path, shine)

        # Border
        pen = QtGui.QPen(border)
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.drawPath(path)


class Sparkline(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = [random.uniform(0.2, 0.8) for _ in range(42)]
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(900)
        self._phase = 0.0

    def sizeHint(self):
        return QtCore.QSize(240, 60)

    def _tick(self):
        self.points.pop(0)
        self.points.append(
            max(0.05, min(0.95, self.points[-1] + random.uniform(-0.12, 0.12)))
        )
        self._phase = (self._phase + 0.06) % (2 * math.pi)
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(6, 6, -6, -6)

        # Area under curve
        path = QtGui.QPainterPath()
        path.moveTo(rect.left(), rect.bottom())
        step_x = rect.width() / (len(self.points) - 1)
        for i, val in enumerate(self.points):
            x = rect.left() + i * step_x
            y = rect.top() + (1.0 - val) * rect.height()
            path.lineTo(x, y)
        path.lineTo(rect.right(), rect.bottom())
        path.closeSubpath()

        grad = QtGui.QLinearGradient(float(rect.left()), float(rect.top()), float(rect.left()), float(rect.bottom()))
        grad.setColorAt(0.0, QtGui.QColor(0, 255, 170, 140))
        grad.setColorAt(1.0, QtGui.QColor(0, 255, 170, 10))
        painter.fillPath(path, grad)

        # Line
        pen = QtGui.QPen(QtGui.QColor(0, 255, 170))
        pen.setWidthF(2.0)
        painter.setPen(pen)
        for i, val in enumerate(self.points):
            x = rect.left() + i * step_x
            y = rect.top() + (1.0 - val) * rect.height()
            if i == 0:
                painter.drawPoint(int(x), int(y))
            else:
                prev_x = rect.left() + (i - 1) * step_x
                prev_y = rect.top() + (1.0 - self.points[i - 1]) * rect.height()
                painter.drawLine(QtCore.QPointF(prev_x, prev_y), QtCore.QPointF(x, y))

        # Glow
        glow = QtWidgets.QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(24)
        glow.setColor(QtGui.QColor(0, 255, 170, 110))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)


class NeonButton(QtWidgets.QPushButton):
    def __init__(self, text: str, color: QtGui.QColor, parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        glow = QtWidgets.QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(40)
        glow.setColor(QtGui.QColor(color.red(), color.green(), color.blue(), 130))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)


class ToggleSwitch(QtWidgets.QCheckBox):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(28)
        self._anim = QtCore.QVariantAnimation(self)
        self._anim.setDuration(180)
        self._anim.valueChanged.connect(self.update)
        self.toggled.connect(self._start_anim)

    def _start_anim(self, checked: bool):
        start = 1.0 if checked else 0.0
        end = 0.0 if checked else 1.0
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        radius = 12
        knob_radius = 10
        rect = self.rect().adjusted(0, 4, 0, -4)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        t = self._anim.currentValue() if self._anim.state() == QtCore.QAbstractAnimation.State.Running else (0.0 if self.isChecked() else 1.0)

        base_col = QtGui.QColor(110, 120, 135, 160)
        on_col = QtGui.QColor(0, 255, 170)

        # Track
        mix = lambda a, b, p: QtGui.QColor(
            int(a.red() * (1 - p) + b.red() * p),
            int(a.green() * (1 - p) + b.green() * p),
            int(a.blue() * (1 - p) + b.blue() * p),
            200,
        )
        track_col = mix(base_col, on_col, 1.0 - t)
        painter.setBrush(track_col)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Knob
        x_left = rect.left() + 4
        x_right = rect.right() - 4 - 2 * knob_radius
        x = x_left * t + x_right * (1 - t)
        knob_rect = QtCore.QRectF(x, rect.top() + (rect.height() - 2 * knob_radius) / 2, 2 * knob_radius, 2 * knob_radius)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawEllipse(knob_rect)


class AreaChart(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = [0.5 + 0.3 * math.sin(i * 0.25) for i in range(100)]
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(60)
        self._t = 0

    def sizeHint(self):
        return QtCore.QSize(520, 260)

    def _tick(self):
        self._t += 1
        self.values.pop(0)
        noise = 0.04 * math.sin(self._t * 0.12) + random.uniform(-0.02, 0.02)
        next_val = max(0.05, min(0.95, self.values[-1] + noise))
        self.values.append(next_val)
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(12, 12, -12, -12)

        # Grid
        grid_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 30))
        grid_pen.setWidthF(1.0)
        painter.setPen(grid_pen)
        for i in range(6):
            y = rect.top() + i * rect.height() / 5
            p1 = QtCore.QPointF(float(rect.left()), float(y))
            p2 = QtCore.QPointF(float(rect.right()), float(y))
            painter.drawLine(p1, p2)

        # Area and line
        path = QtGui.QPainterPath()
        path.moveTo(rect.left(), rect.bottom())
        step_x = rect.width() / (len(self.values) - 1)
        pts = []
        for i, v in enumerate(self.values):
            x = rect.left() + i * step_x
            y = rect.top() + (1.0 - v) * rect.height()
            pts.append(QtCore.QPointF(x, y))
            path.lineTo(x, y)
        path.lineTo(rect.right(), rect.bottom())
        path.closeSubpath()

        grad = QtGui.QLinearGradient(float(rect.left()), float(rect.top()), float(rect.left()), float(rect.bottom()))
        grad.setColorAt(0.0, QtGui.QColor(0, 140, 255, 110))
        grad.setColorAt(1.0, QtGui.QColor(0, 140, 255, 15))
        painter.fillPath(path, grad)

        line_pen = QtGui.QPen(QtGui.QColor(0, 160, 255))
        line_pen.setWidthF(2.2)
        painter.setPen(line_pen)
        for i in range(1, len(pts)):
            painter.drawLine(pts[i - 1], pts[i])


class SideNav(QtWidgets.QWidget):
    currentChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(88)
        self.setObjectName("SideNav")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 24, 12, 24)
        layout.setSpacing(10)

        logo = QtWidgets.QLabel("🟣")
        logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        logo.setFixedHeight(42)
        layout.addWidget(logo)

        layout.addSpacing(8)

        self.buttons: list[QtWidgets.QToolButton] = []
        for i, (text, emoji) in enumerate([
            ("Dashboard", "🏠"),
            ("Analytics", "📈"),
            ("Messages", "💬"),
            ("Settings", "⚙️"),
        ]):
            btn = QtWidgets.QToolButton()
            btn.setText(emoji)
            btn.setToolTip(text)
            btn.setObjectName("NavButton")
            btn.setIconSize(QtCore.QSize(28, 28))
            btn.setFixedSize(64, 56)
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._on_clicked(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch(1)

        self._indicator_y = 0
        self._indicator_anim = QtCore.QPropertyAnimation(self, b"indicatorY")
        self._indicator_anim.setDuration(220)
        self._indicator_anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        self.setProperty("indicatorY", 0)
        if self.buttons:
            self.buttons[0].setChecked(True)
            self._indicator_y = self._button_y(0)

    def _on_clicked(self, idx: int):
        for i, b in enumerate(self.buttons):
            b.setChecked(i == idx)
        start = self._indicator_y
        end = self._button_y(idx)
        self._indicator_anim.stop()
        self._indicator_anim.setStartValue(start)
        self._indicator_anim.setEndValue(end)
        self._indicator_anim.start()
        self._indicator_y = end
        self.currentChanged.emit(idx)

    def _button_y(self, idx: int) -> int:
        btn = self.buttons[idx]
        y = btn.y() + btn.height() // 2 - 24
        return y

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)
        if not self.buttons:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        x = self.width() - 10
        y = self._indicator_y
        rect = QtCore.QRectF(x - 6, y, 6, 48)
        grad = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, QtGui.QColor(0, 255, 170))
        grad.setColorAt(1.0, QtGui.QColor(0, 140, 255))
        painter.setBrush(grad)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 3, 3)

    def getIndicatorY(self):
        return self._indicator_y

    def setIndicatorY(self, value):
        self._indicator_y = value
        self.update()

    indicatorY = pyqtProperty(int, fget=getIndicatorY, fset=setIndicatorY)


class StatCard(GlassCard):
    def __init__(self, title: str, value: str, accent: QtGui.QColor, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setObjectName("CardTitle")
        dot = QtWidgets.QLabel("●")
        dot.setStyleSheet(f"color: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 220);")
        header.addWidget(title_lbl)
        header.addStretch(1)
        header.addWidget(dot)
        layout.addLayout(header)

        value_lbl = QtWidgets.QLabel(value)
        value_lbl.setObjectName("CardValue")
        layout.addWidget(value_lbl)

        self.spark = Sparkline()
        layout.addWidget(self.spark)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neon Glass Dashboard")
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(1180, 740)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        # Background layer
        self.background = GradientBackground(self)
        self.background.lower()

        # Window chrome container
        chrome = QtWidgets.QWidget()
        chrome.setObjectName("Chrome")
        chrome_layout = QtWidgets.QVBoxLayout(chrome)
        chrome_layout.setContentsMargins(0, 0, 0, 0)
        chrome_layout.setSpacing(0)

        self.titlebar = TitleBar()
        chrome_layout.addWidget(self.titlebar)

        body = QtWidgets.QWidget()
        body.setObjectName("Body")
        body_layout = QtWidgets.QHBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)

        self.nav = SideNav()
        body_layout.addWidget(self.nav)

        # Main content area
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # Top stats
        stats_row = QtWidgets.QHBoxLayout()
        stats_row.setSpacing(12)
        card1 = StatCard("Revenue", "$128,430", QtGui.QColor(0, 255, 170))
        card2 = StatCard("Active Users", "24,891", QtGui.QColor(0, 160, 255))
        card3 = StatCard("Conversion", "3.72%", QtGui.QColor(255, 120, 0))
        for c in (card1, card2, card3):
            c.setMinimumHeight(160)
            stats_row.addWidget(c, 1)
        content_layout.addLayout(stats_row)

        # Middle area
        middle = QtWidgets.QHBoxLayout()
        middle.setSpacing(12)

        chart_card = GlassCard()
        chart_layout = QtWidgets.QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(18, 16, 18, 16)
        chart_title = QtWidgets.QLabel("Traffic Overview")
        chart_title.setObjectName("CardTitle")
        chart_layout.addWidget(chart_title)
        chart = AreaChart()
        chart_layout.addWidget(chart, 1)
        middle.addWidget(chart_card, 2)

        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(12)

        tasks_card = GlassCard()
        tasks_layout = QtWidgets.QVBoxLayout(tasks_card)
        tasks_layout.setContentsMargins(18, 16, 18, 16)
        tasks_title = QtWidgets.QLabel("Quick Actions")
        tasks_title.setObjectName("CardTitle")
        tasks_layout.addWidget(tasks_title)
        btn_primary = NeonButton("Deploy", QtGui.QColor(0, 255, 170))
        btn_secondary = NeonButton("Generate Report", QtGui.QColor(0, 160, 255))
        tasks_layout.addWidget(btn_primary)
        tasks_layout.addWidget(btn_secondary)
        right_col.addWidget(tasks_card)

        prefs_card = GlassCard()
        prefs_layout = QtWidgets.QVBoxLayout(prefs_card)
        prefs_layout.setContentsMargins(18, 16, 18, 16)
        prefs_title = QtWidgets.QLabel("Preferences")
        prefs_title.setObjectName("CardTitle")
        prefs_layout.addWidget(prefs_title)
        for label in ("Dark Mode", "Email Alerts", "Auto-Update"):
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(label))
            row.addStretch(1)
            row.addWidget(ToggleSwitch())
            prefs_layout.addLayout(row)
        right_col.addWidget(prefs_card)

        wrapper = QtWidgets.QWidget()
        wrapper.setLayout(right_col)
        middle.addWidget(wrapper, 1)

        content_layout.addLayout(middle, 1)

        body_layout.addWidget(content, 1)
        chrome_layout.addWidget(body, 1)
        outer.addWidget(chrome, 1)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.background.setGeometry(self.rect())
        super().resizeEvent(event)


def apply_styles(app: QtWidgets.QApplication):
    app.setFont(create_font_stack(11))
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(16, 18, 25))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(240, 240, 245))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(24, 26, 34))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(28, 30, 40))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(240, 240, 245))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(28, 30, 40))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(240, 240, 245))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(0, 170, 255))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QWidget#Chrome { background: transparent; }
        QWidget#Body { background: rgba(255, 255, 255, 16); border: 1px solid rgba(255,255,255,28); border-radius: 16px; }
        QWidget#TitleBar { background: rgba(255, 255, 255, 22); border-bottom: 1px solid rgba(255,255,255,36); }
        QPushButton#TitleBarButton__min,
        QPushButton#TitleBarButton__max,
        QPushButton#TitleBarButton__close {
            border: none; border-radius: 6px; color: rgba(255,255,255,230);
            background: rgba(255,255,255,12);
        }
        QPushButton#TitleBarButton__min:hover,
        QPushButton#TitleBarButton__max:hover { background: rgba(255,255,255,22); }
        QPushButton#TitleBarButton__close:hover { background: rgba(255,60,60,0.55); }

        QLabel#CardTitle { color: rgba(255,255,255,220); font-size: 14px; font-weight: 600; }
        QLabel#CardValue { color: rgba(255,255,255,248); font-size: 28px; font-weight: 700; }

        QWidget#GlassCard { background: transparent; }

        QWidget#SideNav { background: rgba(255, 255, 255, 10); border-radius: 14px; border: 1px solid rgba(255,255,255,28); }
        QToolButton#NavButton { border: none; border-radius: 12px; font-size: 22px; }
        QToolButton#NavButton:hover { background: rgba(255,255,255,18); }
        QToolButton#NavButton:checked { background: rgba(255,255,255,24); }

        QPushButton { color: white; border: 1px solid rgba(255,255,255,28); border-radius: 10px; padding: 8px 14px; 
            background-color: rgba(255,255,255,12); font-weight: 600; letter-spacing: 0.3px; }
        QPushButton:hover { background-color: rgba(255,255,255,22); }
        QPushButton:pressed { background-color: rgba(255,255,255,30); }

        QLabel { color: rgba(255,255,255,230); }
        QToolTip { color: white; background: rgba(0,0,0,180); border: 1px solid rgba(255,255,255,40); padding: 6px 8px; }
        """
    )


def main():
    app = QtWidgets.QApplication(sys.argv)
    apply_styles(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

