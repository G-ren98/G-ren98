import sys
import math
from PyQt6 import QtCore, QtGui, QtWidgets


IS_WINDOWS = sys.platform.startswith("win")

# Soft UI palette (light, smooth, rounded)
BGCOLOR = QtGui.QColor(236, 240, 243)  # #ECF0F3
SHADOW_DARK = QtGui.QColor(163, 177, 198, 160)
SHADOW_LIGHT = QtGui.QColor(255, 255, 255, 220)
TEXT_PRIMARY = QtGui.QColor(46, 52, 64)
TEXT_MUTED = QtGui.QColor(90, 98, 110)
ACCENT = QtGui.QColor(66, 133, 244)  # soft blue
ACCENT_GREEN = QtGui.QColor(52, 168, 83)
ACCENT_ORANGE = QtGui.QColor(251, 188, 5)


def soft_font(point_size: int, weight: QtGui.QFont.Weight = QtGui.QFont.Weight.Medium) -> QtGui.QFont:
    font = QtGui.QFont()
    font.setFamilies([
        "Inter", "SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", "sans-serif"
    ])
    font.setPointSize(point_size)
    font.setWeight(weight.value if isinstance(weight, QtGui.QFont.Weight) else int(weight))
    return font


class TitleBar(QtWidgets.QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setFont(soft_font(12, QtGui.QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: #2E3440;")

        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.min_btn = self._make_btn("—")
        self.max_btn = self._make_btn("▢")
        self.close_btn = self._make_btn("✕")
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.min_btn.clicked.connect(lambda: self.window().showMinimized())
        self.max_btn.clicked.connect(self._toggle_max)
        self.close_btn.clicked.connect(lambda: self.window().close())

        self._drag_pos = None

    def _make_btn(self, text: str) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(text)
        btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(36, 28)
        btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #5A626E; }"
            "QPushButton:hover { background: rgba(0,0,0,0.06); border-radius: 8px; }"
        )
        return btn

    def _toggle_max(self):
        w = self.window()
        w.showNormal() if w.isMaximized() else w.showMaximized()

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


class SoftCard(QtWidgets.QWidget):
    def __init__(self, radius: int = 18, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(240, 160)

    def _rounded_rect(self) -> QtGui.QPainterPath:
        rect = self.rect().adjusted(8, 8, -8, -8)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(rect), self.radius, self.radius)
        return path

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), BGCOLOR)

        rect = self.rect().adjusted(10, 10, -10, -10)

        # Soft raised shadows (very cheap to draw)
        offset = 8
        dark = QtGui.QColor(SHADOW_DARK)
        light = QtGui.QColor(SHADOW_LIGHT)

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(dark)
        painter.drawRoundedRect(QtCore.QRectF(rect).translated(+offset, +offset), self.radius, self.radius)
        painter.setBrush(light)
        painter.drawRoundedRect(QtCore.QRectF(rect).translated(-offset, -offset), self.radius, self.radius)

        # Main face
        painter.setBrush(BGCOLOR)
        painter.drawRoundedRect(QtCore.QRectF(rect), self.radius, self.radius)


class StatCard(SoftCard):
    def __init__(self, title: str, value: str, accent: QtGui.QColor, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setFont(soft_font(11, QtGui.QFont.Weight.DemiBold))
        title_lbl.setStyleSheet("color: #5A626E;")

        value_lbl = QtWidgets.QLabel(value)
        value_lbl.setFont(soft_font(26, QtGui.QFont.Weight.Bold))
        value_lbl.setStyleSheet("color: #2E3440;")

        progress = SoftProgress(accent)

        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addWidget(progress)


class SoftProgress(QtWidgets.QWidget):
    def __init__(self, accent: QtGui.QColor, parent=None):
        super().__init__(parent)
        self.accent = accent
        self._value = 0.7
        self.setFixedHeight(16)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), BGCOLOR)
        rect = self.rect().adjusted(2, 3, -2, -3)
        radius = rect.height() / 2

        # Track (neumorphic recess)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(245, 248, 250))
        painter.drawRoundedRect(rect, radius, radius)

        # Fill
        fill_rect = QtCore.QRectF(rect)
        fill_rect.setWidth(rect.width() * self._value)
        grad = QtGui.QLinearGradient(float(rect.left()), float(rect.top()), float(rect.right()), float(rect.top()))
        grad.setColorAt(0.0, QtGui.QColor(self.accent.red(), self.accent.green(), self.accent.blue(), 230))
        grad.setColorAt(1.0, QtGui.QColor(self.accent.red(), self.accent.green(), self.accent.blue(), 170))
        painter.setBrush(QtGui.QBrush(grad))
        painter.drawRoundedRect(fill_rect, radius, radius)


class MiniLine(QtWidgets.QWidget):
    def __init__(self, color: QtGui.QColor, parent=None):
        super().__init__(parent)
        self.color = color
        self.points = [0.5 + 0.3 * math.sin(i * 0.25) for i in range(60)]
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        # lower frequency for smooth but light animation
        self.timer.start(80)
        self.setFixedHeight(120)

    def _tick(self):
        self.points.pop(0)
        self.points.append(self.points[-1] * 0.85 + 0.15 * (0.5 + 0.3 * math.sin(len(self.points) * 0.25)))
        self.update()

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), BGCOLOR)
        rect = self.rect().adjusted(24, 20, -24, -20)

        # soft frame
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(SHADOW_LIGHT)
        painter.drawRoundedRect(QtCore.QRectF(rect).translated(-6, -6), 16, 16)
        painter.setBrush(SHADOW_DARK)
        painter.drawRoundedRect(QtCore.QRectF(rect).translated(+6, +6), 16, 16)
        painter.setBrush(BGCOLOR)
        painter.drawRoundedRect(QtCore.QRectF(rect), 16, 16)

        # line
        pen = QtGui.QPen(self.color)
        pen.setWidthF(2.0)
        painter.setPen(pen)
        step_x = rect.width() / (len(self.points) - 1)
        pts = []
        for i, v in enumerate(self.points):
            x = rect.left() + i * step_x
            y = rect.top() + (1.0 - v) * rect.height()
            pts.append(QtCore.QPointF(x, y))
        for i in range(1, len(pts)):
            painter.drawLine(pts[i - 1], pts[i])


class SoftButton(QtWidgets.QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setStyleSheet(
            "QPushButton { background: #ECF0F3; border: none; border-radius: 14px; color: #2E3440; font-weight: 600; }"
            "QPushButton:hover { background: #E8EDF1; }"
            "QPushButton:pressed { background: #E2E8ED; }"
        )


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soft UI Dashboard")
        # Use standard window (avoid translucent for better stability on Windows)
        self.resize(1100, 700)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(12)

        # Background color (no heavy gradients)
        pal = self.palette()
        pal.setColor(QtGui.QPalette.ColorRole.Window, BGCOLOR)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        # Top bar
        self.titlebar = TitleBar("Soft UI Dashboard")
        outer.addWidget(self.titlebar)

        # Body
        body = QtWidgets.QWidget()
        body_layout = QtWidgets.QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(12)

        # Side pane (soft card)
        side = SoftCard()
        side_layout = QtWidgets.QVBoxLayout(side)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(10)
        side_title = QtWidgets.QLabel("Menu")
        side_title.setFont(soft_font(12, QtGui.QFont.Weight.DemiBold))
        side_title.setStyleSheet("color: #5A626E;")
        for name in ["Overview", "Sales", "Users", "Settings"]:
            btn = SoftButton(name)
            side_layout.addWidget(btn)
        side_layout.addStretch(1)
        body_layout.addWidget(side, 1)

        # Main content
        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # Stats row
        stats_row = QtWidgets.QHBoxLayout()
        stats_row.setSpacing(12)
        stats_row.addWidget(StatCard("Revenue", "$128,430", ACCENT_GREEN), 1)
        stats_row.addWidget(StatCard("Active Users", "24,891", ACCENT), 1)
        stats_row.addWidget(StatCard("Conversion", "3.72%", ACCENT_ORANGE), 1)
        main_layout.addLayout(stats_row)

        # Chart + actions
        mid = QtWidgets.QHBoxLayout()
        mid.setSpacing(12)

        chart_card = SoftCard()
        chart_layout = QtWidgets.QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(20, 18, 20, 18)
        chart_title = QtWidgets.QLabel("Traffic")
        chart_title.setFont(soft_font(12, QtGui.QFont.Weight.DemiBold))
        chart_title.setStyleSheet("color: #5A626E;")
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(MiniLine(ACCENT), 1)
        mid.addWidget(chart_card, 2)

        actions = SoftCard()
        actions_layout = QtWidgets.QVBoxLayout(actions)
        actions_layout.setContentsMargins(20, 18, 20, 18)
        actions_title = QtWidgets.QLabel("Quick Actions")
        actions_title.setFont(soft_font(12, QtGui.QFont.Weight.DemiBold))
        actions_title.setStyleSheet("color: #5A626E;")
        actions_layout.addWidget(actions_title)
        actions_layout.addWidget(SoftButton("Generate Report"))
        actions_layout.addWidget(SoftButton("Export CSV"))
        actions_layout.addWidget(SoftButton("Sync"))
        actions_layout.addStretch(1)
        mid.addWidget(actions, 1)

        main_layout.addLayout(mid, 1)

        body_layout.addWidget(main, 3)
        outer.addWidget(body, 1)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setFont(soft_font(11, QtGui.QFont.Weight.Medium))
    app.setStyle("Fusion")
    # global palette
    pal = app.palette()
    pal.setColor(QtGui.QPalette.ColorRole.Window, BGCOLOR)
    pal.setColor(QtGui.QPalette.ColorRole.WindowText, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.Button, BGCOLOR)
    pal.setColor(QtGui.QPalette.ColorRole.ButtonText, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.Base, BGCOLOR)
    pal.setColor(QtGui.QPalette.ColorRole.AlternateBase, BGCOLOR)
    pal.setColor(QtGui.QPalette.ColorRole.Text, TEXT_PRIMARY)
    pal.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(252, 252, 252))
    pal.setColor(QtGui.QPalette.ColorRole.ToolTipText, TEXT_PRIMARY)
    app.setPalette(pal)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

