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