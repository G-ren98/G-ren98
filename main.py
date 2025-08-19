import sys
import math
from PyQt6 import QtCore, QtGui, QtWidgets


IS_WINDOWS = sys.platform.startswith("win")

# Aurora Dark Neo palette
BGCOLOR = QtGui.QColor(16, 18, 25)
TEXT_PRIMARY = QtGui.QColor(235, 240, 245)
TEXT_MUTED = QtGui.QColor(200, 208, 218)
ACCENT = QtGui.QColor(0, 160, 255)
ACCENT_GREEN = QtGui.QColor(0, 220, 170)
ACCENT_ORANGE = QtGui.QColor(255, 160, 80)


def font_stack(point_size: int, weight: QtGui.QFont.Weight = QtGui.QFont.Weight.Medium) -> QtGui.QFont:
    f = QtGui.QFont()
    f.setFamilies(["Inter", "SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "sans-serif"])
    f.setPointSize(point_size)
    f.setWeight(weight.value if isinstance(weight, QtGui.QFont.Weight) else int(weight))
    return f


class AuroraBackground(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hue = 200.0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)  # ~20 FPS, smooth and light
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _tick(self):
        self._hue = (self._hue + 0.35) % 360
        self.update()

    def _color(self, offset_deg: float, s: float, v: float, a: int = 255) -> QtGui.QColor:
        hue = ((self._hue + offset_deg) % 360) / 360.0
        c = QtGui.QColor()
        c.setHsvF(hue, s, v, a / 255.0)
        return c

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Aurora diagonal gradient
        g = QtGui.QLinearGradient(0.0, 0.0, float(w), float(h))
        g.setColorAt(0.0, self._color(0, 0.55, 0.16))
        g.setColorAt(0.5, self._color(60, 0.6, 0.12))
        g.setColorAt(1.0, self._color(120, 0.65, 0.18))
        p.fillRect(self.rect(), QtGui.QBrush(g))

        # Soft neon blobs
        for cx, cy, r, off in (
            (w * 0.2, h * 0.25, w * 0.35, 0),
            (w * 0.8, h * 0.2, w * 0.25, 120),
            (w * 0.5, h * 0.75, w * 0.3, 240),
        ):
            rg = QtGui.QRadialGradient(QtCore.QPointF(cx, cy), r)
            rg.setColorAt(0.0, self._color(off, 0.85, 0.9, 110))
            rg.setColorAt(1.0, QtGui.QColor(0, 0, 0, 0))
            p.setBrush(QtGui.QBrush(rg))
            p.setPen(QtCore.Qt.PenStyle.NoPen)
            p.drawEllipse(QtCore.QPointF(cx, cy), r, r)


class GlassCard(QtWidgets.QWidget):
    def __init__(self, radius: int = 18, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(260, 160)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(rect), self.radius, self.radius)

        # Subtle shadow
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(0, 0, 0, 90))
        painter.drawRoundedRect(QtCore.QRectF(rect).translated(0, 6), self.radius + 2, self.radius + 2)

        # Glass fill
        glass = QtGui.QLinearGradient(float(rect.left()), float(rect.top()), float(rect.left()), float(rect.bottom()))
        glass.setColorAt(0.0, QtGui.QColor(255, 255, 255, 36))
        glass.setColorAt(1.0, QtGui.QColor(255, 255, 255, 18))
        painter.fillPath(path, QtGui.QBrush(glass))

        # Border
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 70))
        pen.setWidthF(1.1)
        painter.setPen(pen)
        painter.drawPath(path)


class TitleBar(QtWidgets.QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: rgba(235,240,245,0.92);")

        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self._drag_pos = None

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if self._drag_pos is not None and e.buttons() & QtCore.Qt.MouseButton.LeftButton and not self.window().isMaximized():
            delta = e.globalPosition().toPoint() - self._drag_pos
            self.window().move(self.window().pos() + delta)
            self._drag_pos = e.globalPosition().toPoint()
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(e)


class SideNav(QtWidgets.QWidget):
    currentChanged = QtCore.pyqtSignal(int)

    def __init__(self, items: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setFixedWidth(96)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(10)

        self.buttons: list[QtWidgets.QToolButton] = []
        for i, (text, emoji) in enumerate(items):
            btn = QtWidgets.QToolButton()
            btn.setText(emoji)
            btn.setToolTip(text)
            btn.setCheckable(True)
            btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(64, 56)
            btn.setStyleSheet(
                "QToolButton { border: none; border-radius: 14px; font-size: 22px; color: rgba(255,255,255,0.92);}"
                "QToolButton:hover { background: rgba(255,255,255,0.10);}"
                "QToolButton:checked { background: rgba(255,255,255,0.16);}"
            )
            btn.clicked.connect(lambda checked, idx=i: self._on_clicked(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch(1)

        self._indicator_y = 0
        self._anim = QtCore.QPropertyAnimation(self, b"indicatorY")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        if self.buttons:
            self.buttons[0].setChecked(True)
            QtCore.QTimer.singleShot(0, lambda: self._set_indicator(0))

    def _button_y(self, idx: int) -> int:
        btn = self.buttons[idx]
        return btn.y() + btn.height() // 2 - 24

    def _set_indicator(self, idx: int):
        self._indicator_y = self._button_y(idx)
        self.update()

    def _on_clicked(self, idx: int):
        for i, b in enumerate(self.buttons):
            b.setChecked(i == idx)
        start = self._indicator_y
        end = self._button_y(idx)
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()
        self._indicator_y = end
        self.currentChanged.emit(idx)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        super().paintEvent(e)
        if not self.buttons:
            return
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        x = self.width() - 10
        y = self._indicator_y
        rect = QtCore.QRectF(x - 6, y, 6, 48)
        g = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        g.setColorAt(0.0, QtGui.QColor(0, 255, 170))
        g.setColorAt(1.0, QtGui.QColor(0, 140, 255))
        p.setBrush(QtGui.QBrush(g))
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 3, 3)

    def getIndicatorY(self):
        return self._indicator_y

    def setIndicatorY(self, value):
        self._indicator_y = value
        self.update()

    indicatorY = QtCore.pyqtProperty(int, fget=getIndicatorY, fset=setIndicatorY)


class SoftProgress(QtWidgets.QWidget):
    def __init__(self, accent: QtGui.QColor, parent=None):
        super().__init__(parent)
        self.accent = accent
        self._value = 0.72
        self.setFixedHeight(12)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 3, -2, -3)
        radius = rect.height() / 2
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QColor(255, 255, 255, 28))
        p.drawRoundedRect(rect, radius, radius)
        fill_rect = QtCore.QRectF(rect)
        fill_rect.setWidth(rect.width() * self._value)
        g = QtGui.QLinearGradient(float(rect.left()), float(rect.top()), float(rect.right()), float(rect.top()))
        g.setColorAt(0.0, QtGui.QColor(self.accent.red(), self.accent.green(), self.accent.blue(), 230))
        g.setColorAt(1.0, QtGui.QColor(self.accent.red(), self.accent.green(), self.accent.blue(), 160))
        p.setBrush(QtGui.QBrush(g))
        p.drawRoundedRect(fill_rect, radius, radius)


class StatCard(GlassCard):
    def __init__(self, title: str, value: str, accent: QtGui.QColor, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(8)

        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setFont(font_stack(11, QtGui.QFont.Weight.DemiBold))
        title_lbl.setStyleSheet("color: rgba(235,240,245,0.82);")

        value_lbl = QtWidgets.QLabel(value)
        value_lbl.setFont(font_stack(26, QtGui.QFont.Weight.Bold))
        value_lbl.setStyleSheet("color: rgba(255,255,255,0.98);")

        bar = SoftProgress(accent)

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addWidget(bar)


class MiniLine(QtWidgets.QWidget):
    def __init__(self, color: QtGui.QColor, parent=None):
        super().__init__(parent)
        self.color = color
        self.points = [0.5 + 0.3 * math.sin(i * 0.25) for i in range(80)]
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(70)
        self.setFixedHeight(120)

    def _tick(self):
        self.points.pop(0)
        self.points.append(self.points[-1] * 0.85 + 0.15 * (0.5 + 0.3 * math.sin(len(self.points) * 0.24)))
        self.update()

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(20, 18, -20, -18)

        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QColor(0, 0, 0, 80))
        p.drawRoundedRect(QtCore.QRectF(rect).translated(0, 4), 16, 16)
        p.setBrush(QtGui.QColor(255, 255, 255, 26))
        p.drawRoundedRect(QtCore.QRectF(rect), 16, 16)

        pen = QtGui.QPen(self.color)
        pen.setWidthF(2.1)
        p.setPen(pen)
        step_x = rect.width() / (len(self.points) - 1)
        pts = []
        for i, v in enumerate(self.points):
            x = rect.left() + i * step_x
            y = rect.top() + (1.0 - v) * rect.height()
            pts.append(QtCore.QPointF(x, y))
        for i in range(1, len(pts)):
            p.drawLine(pts[i - 1], pts[i])


class NeonButton(QtWidgets.QPushButton):
    def __init__(self, text: str, base: QtGui.QColor = ACCENT, parent=None):
        super().__init__(text, parent)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setStyleSheet(
            "QPushButton {"
            " color: white; border: none; border-radius: 12px;"
            " background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 rgba({base.red()}, {base.green()}, {base.blue()}, 1.0),"
            f" stop:1 rgba({min(base.red()+40,255)}, {min(base.green()+40,255)}, {min(base.blue()+40,255)}, 1.0));"
            " font-weight: 600; letter-spacing: 0.3px;"
            "}"
            "QPushButton:hover { filter: brightness(1.05); }"
            "QPushButton:pressed { filter: brightness(0.95); }"
        )


class OverviewPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        stats = QtWidgets.QHBoxLayout()
        stats.setSpacing(12)
        stats.addWidget(StatCard("Revenue", "$128,430", ACCENT_GREEN), 1)
        stats.addWidget(StatCard("Active Users", "24,891", ACCENT), 1)
        stats.addWidget(StatCard("Conversion", "3.72%", ACCENT_ORANGE), 1)
        layout.addLayout(stats)

        mid = QtWidgets.QHBoxLayout()
        mid.setSpacing(12)
        chart_card = GlassCard()
        cl = QtWidgets.QVBoxLayout(chart_card)
        cl.setContentsMargins(18, 16, 18, 16)
        t = QtWidgets.QLabel("Traffic Overview")
        t.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        t.setStyleSheet("color: rgba(235,240,245,0.86);")
        cl.addWidget(t)
        cl.addWidget(MiniLine(ACCENT), 1)

        actions = GlassCard()
        al = QtWidgets.QVBoxLayout(actions)
        al.setContentsMargins(18, 16, 18, 16)
        at = QtWidgets.QLabel("Quick Actions")
        at.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        at.setStyleSheet("color: rgba(235,240,245,0.86);")
        al.addWidget(at)
        al.addWidget(NeonButton("Deploy", ACCENT_GREEN))
        al.addWidget(NeonButton("Generate Report", ACCENT))
        al.addWidget(NeonButton("Sync", ACCENT_ORANGE))
        al.addStretch(1)

        mid.addWidget(chart_card, 2)
        mid.addWidget(actions, 1)
        layout.addLayout(mid, 1)


class AnalyticsPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        left = GlassCard()
        ll = QtWidgets.QVBoxLayout(left)
        ll.setContentsMargins(18, 16, 18, 16)
        lbl = QtWidgets.QLabel("Engagement")
        lbl.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        lbl.setStyleSheet("color: rgba(235,240,245,0.86);")
        ll.addWidget(lbl)
        ll.addWidget(MiniLine(ACCENT_GREEN), 1)
        right = GlassCard()
        rl = QtWidgets.QVBoxLayout(right)
        rl.setContentsMargins(18, 16, 18, 16)
        lbl2 = QtWidgets.QLabel("Retention")
        lbl2.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        lbl2.setStyleSheet("color: rgba(235,240,245,0.86);")
        rl.addWidget(lbl2)
        rl.addWidget(MiniLine(ACCENT_ORANGE), 1)
        layout.addWidget(left, 1)
        layout.addWidget(right, 1)


class MessagesPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        list_card = GlassCard()
        l = QtWidgets.QVBoxLayout(list_card)
        l.setContentsMargins(18, 16, 18, 16)
        title = QtWidgets.QLabel("Messages")
        title.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(235,240,245,0.86);")
        l.addWidget(title)
        for i in range(6):
            row = QtWidgets.QHBoxLayout()
            user = QtWidgets.QLabel(f"User {i+1}")
            user.setStyleSheet("color: rgba(235,240,245,0.90);")
            preview = QtWidgets.QLabel("Hey, could you check the latest build?")
            preview.setStyleSheet("color: rgba(235,240,245,0.70);")
            row.addWidget(user)
            row.addStretch(1)
            row.addWidget(preview)
            l.addLayout(row)
        layout.addWidget(list_card)


class SettingsPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        card = GlassCard()
        c = QtWidgets.QVBoxLayout(card)
        c.setContentsMargins(18, 16, 18, 16)
        t = QtWidgets.QLabel("Preferences")
        t.setFont(font_stack(12, QtGui.QFont.Weight.DemiBold))
        t.setStyleSheet("color: rgba(235,240,245,0.86);")
        c.addWidget(t)
        for label in ("Dark Mode", "Email Alerts", "Auto-Update"):
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(label))
            row.addStretch(1)
            sw = QtWidgets.QCheckBox()
            sw.setStyleSheet("QCheckBox { color: rgba(235,240,245,0.90);} ")
            row.addWidget(sw)
            c.addLayout(row)
        c.addSpacing(8)
        c.addWidget(NeonButton("Apply", ACCENT))
        layout.addWidget(card)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aurora Dark Neo")
        # Frameless to remove native close/max/min buttons
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, True)
        self.resize(1180, 740)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        # Background layer
        self.setAutoFillBackground(False)
        self._bg = AuroraBackground(self)
        self._bg.lower()

        # Chrome
        chrome = QtWidgets.QWidget()
        chrome_layout = QtWidgets.QVBoxLayout(chrome)
        chrome_layout.setContentsMargins(0, 0, 0, 0)
        chrome_layout.setSpacing(0)

        self.titlebar = TitleBar("Aurora Dark Neo")
        chrome_layout.addWidget(self.titlebar)

        body = QtWidgets.QWidget()
        body_layout = QtWidgets.QHBoxLayout(body)
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)

        self.nav = SideNav([
            ("Overview", "🏠"),
            ("Analytics", "📈"),
            ("Messages", "💬"),
            ("Settings", "⚙️"),
        ])
        body_layout.addWidget(self.nav)

        self.pages = QtWidgets.QStackedWidget()
        self.pages.addWidget(OverviewPage())
        self.pages.addWidget(AnalyticsPage())
        self.pages.addWidget(MessagesPage())
        self.pages.addWidget(SettingsPage())
        body_layout.addWidget(self.pages, 1)
        chrome_layout.addWidget(body, 1)
        outer.addWidget(chrome, 1)

        self.nav.currentChanged.connect(self.pages.setCurrentIndex)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        # 便捷关闭：Ctrl+Q 或 Esc
        if (e.key() == QtCore.Qt.Key.Key_Q and e.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier) or e.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(e)

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        if hasattr(self, "_bg") and self._bg is not None:
            self._bg.setGeometry(self.rect())
        super().resizeEvent(e)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(font_stack(11, QtGui.QFont.Weight.Medium))
    app.setStyle("Fusion")

    pal = app.palette()
    pal.setColor(QtGui.QPalette.ColorRole.Window, BGCOLOR)
    pal.setColor(QtGui.QPalette.ColorRole.WindowText, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(28, 30, 40))
    pal.setColor(QtGui.QPalette.ColorRole.ButtonText, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(24, 26, 34))
    pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(28, 30, 40))
    pal.setColor(QtGui.QPalette.ColorRole.Text, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(30, 34, 42))
    pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.Highlight, ACCENT)
    pal.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
    app.setPalette(pal)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import sys
from PyQt5 import QtGui

IS_WINDOWS = sys.platform.startswith("win")

"""Prism Acrylic theme: light, pastel gradient, acrylic cards"""
BGCOLOR = QtGui.QColor(246, 247, 251)
TEXT_PRIMARY = QtGui.QColor(28, 31, 43)
TEXT_MUTED = QtGui.QColor(112, 120, 140)
ACCENT = QtGui.QColor(88, 130, 255)
ACCENT_GREEN = QtGui.QColor(46, 196, 182)
ACCENT_ORANGE = QtGui.QColor(255, 159, 67)
SHADOW_DARK = QtGui.QColor(0, 0, 0, 70)
SHADOW_LIGHT = QtGui.QColor(255, 255, 255, 210)


def soft_font(point_size: int, weight: QtGui.QFont.Weight = QtGui.QFont.Weight.Medium) -> QtGui.QFont:
    font = QtGui.QFont()
    font.setPointSize(point_size)
    font.setWeight(weight)
    return font