from PySide6.QtWidgets import QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor

def apply_fade(widget, start=0.0, end=1.0, duration=400):
    """Applies a smooth opacity transition safely without C++ object deletion crashes."""
    # 1. Check if animation exists and is valid in C++
    try:
        if hasattr(widget, '_fade_anim') and widget._fade_anim.state() == QPropertyAnimation.State.Running:
            widget._fade_anim.stop()
    except RuntimeError:
        # C++ object was deleted by the engine, we can safely ignore and proceed
        pass

    # 2. Reuse existing effect
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    # 3. Create and start animation (Removed DeleteWhenStopped to keep Python/C++ in sync)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    widget._fade_anim = anim 
    anim.start() # Default is KeepWhenStopped

def apply_shake(widget):
    """Applies a quick left-right shake effect."""
    try:
        if hasattr(widget, '_shake_anim') and widget._shake_anim.state() == QPropertyAnimation.State.Running:
            widget._shake_anim.stop()
    except RuntimeError:
        pass

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
    anim.start()

def apply_glow(widget, color_hex: str):
    """Applies a glowing drop-shadow effect safely."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(QColor(color_hex))
    effect.setBlurRadius(30)
    effect.setOffset(0, 0)
    widget.setGraphicsEffect(effect)

def clear_effects(widget):
    """Safely stops running animations before clearing graphical effects."""
    try:
        if hasattr(widget, '_fade_anim'): 
            widget._fade_anim.stop()
    except RuntimeError: pass
    
    try:
        if hasattr(widget, '_shake_anim'): 
            widget._shake_anim.stop()
    except RuntimeError: pass
        
    widget.setGraphicsEffect(None)