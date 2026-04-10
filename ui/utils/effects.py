from PySide6.QtWidgets import QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor

def apply_fade(widget, start=0.0, end=1.0, duration=400):
    """Applies a smooth opacity transition to a widget."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    # Attach animation to widget to prevent Python Garbage Collection
    widget._fade_anim = anim 
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

def apply_shake(widget):
    """Applies a quick left-right shake effect indicating an error or loss."""
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(400)
    anim.setLoopCount(1)
    
    pos = widget.pos()
    x, y = pos.x(), pos.y()
    
    anim.setKeyValueAt(0, QPoint(x, y))
    anim.setKeyValueAt(0.1, QPoint(x - 10, y))
    anim.setKeyValueAt(0.3, QPoint(x + 10, y))
    anim.setKeyValueAt(0.5, QPoint(x - 10, y))
    anim.setKeyValueAt(0.7, QPoint(x + 10, y))
    anim.setKeyValueAt(0.9, QPoint(x - 5, y))
    anim.setKeyValueAt(1.0, QPoint(x, y))
    
    widget._shake_anim = anim
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

def apply_glow(widget, color_hex: str):
    """Applies a glowing drop-shadow effect."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(QColor(color_hex))
    effect.setBlurRadius(30)
    effect.setOffset(0, 0)
    widget.setGraphicsEffect(effect)

def clear_effects(widget):
    """Removes any graphical effects currently applied to the widget."""
    widget.setGraphicsEffect(None)
