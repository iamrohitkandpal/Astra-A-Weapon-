"""
UI helper utilities for smooth UI transitions and animations
"""
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, Qt
from PyQt6.QtGui import QColor

def fade_in_widget(widget, duration=250):
    """Fade in a widget with animation"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    # Create the animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
    animation.start()
    return animation

def fade_out_widget(widget, duration=250):
    """Fade out a widget with animation"""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    
    # Create the animation
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(1)
    animation.setEndValue(0)
    animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
    animation.start()
    return animation

def slide_in_widget(widget, direction="right", duration=350):
    """Slide in a widget from a direction (left, right, top, bottom)"""
    pos = widget.pos()
    start_x, start_y = pos.x(), pos.y()
    width, height = widget.width(), widget.height()
    
    # Set the start position based on direction
    if direction == "left":
        widget.move(start_x - width, start_y)
    elif direction == "right":
        widget.move(start_x + width, start_y)
    elif direction == "top":
        widget.move(start_x, start_y - height)
    elif direction == "bottom":
        widget.move(start_x, start_y + height)
    
    # Create the animation
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setEndValue(pos)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.start()
    return animation

def create_color_transition(start_color, end_color, steps=20):
    """Create a list of colors for smooth color transition"""
    colors = []
    for i in range(steps + 1):
        ratio = i / steps
        r = int(start_color.red() * (1 - ratio) + end_color.red() * ratio)
        g = int(start_color.green() * (1 - ratio) + end_color.green() * ratio)
        b = int(start_color.blue() * (1 - ratio) + end_color.blue() * ratio)
        colors.append(QColor(r, g, b))
    return colors

def pulse_widget(widget, duration=1000, color1=None, color2=None):
    """Create a pulsing highlight effect on a widget"""
    if color1 is None:
        color1 = QColor(widget.palette().color(widget.backgroundRole()))
    if color2 is None:
        color2 = QColor(255, 255, 0, 100)  # Default highlight color
    
    colors = create_color_transition(color1, color2, 10) + create_color_transition(color2, color1, 10)
    
    # Create a timer to cycle through colors
    timer = QTimer(widget)
    color_index = [0]  # Using list for nonlocal access
    
    def update_color():
        style = f"background-color: rgba({colors[color_index[0]].red()}, {colors[color_index[0]].green()}, {colors[color_index[0]].blue()}, {colors[color_index[0]].alpha()})"
        widget.setStyleSheet(style)
        color_index[0] = (color_index[0] + 1) % len(colors)
    
    timer.timeout.connect(update_color)
    timer.start(duration // len(colors))
    return timer
