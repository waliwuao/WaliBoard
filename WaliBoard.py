import sys

from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QWidget,
    QMenu,
    QColorDialog
)


class CoverWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # 记录鼠标按下时的位置和窗口初始位置
        self.drag_start_position = QPoint()
        # 记录当前是否在拖动角
        self.resizing = False
        self.resize_direction = None
        # 定义角的检测范围
        self.corner_size = 20
        # 初始化背景颜色，使用浅灰色使界面更柔和
        self.background_color = QColor(245, 245, 245)

    def initUI(self):
        # 设置窗口无边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 设置窗口为圆角且背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置窗口初始透明度，调整为完全不透明
        self.setWindowOpacity(1)
        # 设置窗口初始大小
        self.resize(400, 300)
        # 移除阴影效果相关代码
        # 显示窗口
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 使用当前背景颜色设置画刷
        painter.setBrush(QBrush(self.background_color))
        # 设置边框为透明
        painter.setPen(QPen(Qt.transparent))
        # 绘制更大圆角的矩形
        painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 15, 15)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查是否点击了四个角
            pos = event.pos()
            if pos.x() < self.corner_size and pos.y() < self.corner_size:
                self.resizing = True
                self.resize_direction = 'top_left'
            elif pos.x() > self.width() - self.corner_size and pos.y() < self.corner_size:
                self.resizing = True
                self.resize_direction = 'top_right'
            elif pos.x() < self.corner_size and pos.y() > self.height() - self.corner_size:
                self.resizing = True
                self.resize_direction = 'bottom_left'
            elif pos.x() > self.width() - self.corner_size and pos.y() > self.height() - self.corner_size:
                self.resizing = True
                self.resize_direction = 'bottom_right'
            else:
                self.drag_start_position = event.pos()  # 修改为记录相对位置
                self.resizing = False
        elif event.button() == Qt.RightButton:
            self.close()  # 右键直接关闭窗口

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.resizing:
                global_pos = event.globalPos()
                # 使用全局位置和当前窗口几何信息来计算新的矩形
                rect = self.geometry()  # 获取窗口的全局几何信息

                if self.resize_direction == 'top_left':
                    rect.setTopLeft(global_pos)
                elif self.resize_direction == 'top_right':
                    rect.setTopRight(global_pos)
                elif self.resize_direction == 'bottom_left':
                    rect.setBottomLeft(global_pos)
                elif self.resize_direction == 'bottom_right':
                    rect.setBottomRight(global_pos)

                # 确保窗口大小不为负
                if rect.width() > 50 and rect.height() > 50:
                    self.setGeometry(rect)
            else:
                # 修改移动逻辑，使用相对位置计算
                self.move(self.mapToGlobal(event.pos() - self.drag_start_position))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.resizing = False

    # 移除右键菜单方法
    # def contextMenuEvent(self, event):
    #     # 创建右键菜单
    #     menu = QMenu(self)
    #
    #     # 添加关闭动作
    #     close_action = QAction('关闭', self)
    #     close_action.triggered.connect(self.close)
    #     menu.addAction(close_action)
    #
    #     # 显示菜单
    #     menu.exec_(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        """双击事件处理，双击选择颜色"""
        if event.button() == Qt.LeftButton:
            self.choose_color()

    def _create_color_icon(self, color):
        """创建颜色图标的辅助方法"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        if color:
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.gray, 1))
        else:
            # 取色器图标，使用十字线表示
            painter.setBrush(QBrush(Qt.transparent))
            painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(2, 2, 20, 20)
        if not color:
            painter.drawLine(12, 2, 12, 22)
            painter.drawLine(2, 12, 22, 12)
        painter.end()
        return QIcon(pixmap)

    def choose_color(self):
        # 创建自定义颜色选择菜单
        color_menu = QMenu(self)

        # 定义预设颜色，将非白黑色换成更柔和的颜色
        colors = {
            '白色': QColor(255, 255, 255),
            '黑色': QColor(0, 0, 0),
            '红色': QColor(255, 182, 193),  # 替换为粉红色
            '蓝色': QColor(173, 216, 230),  # 替换为浅蓝色
            '绿色': QColor(144, 238, 144),  # 替换为浅绿色
            '橙色': QColor(255, 218, 185),  # 替换为浅橙色
            '取色器': None
        }

        for name, color in colors.items():
            action = QAction(name, self)
            action.setIcon(self._create_color_icon(color))
            action.triggered.connect(lambda _, c=color: self._set_color(c) if c else self._show_color_dialog())
            color_menu.addAction(action)

        color_menu.exec_(self.mapToGlobal(self.rect().center()))

    def _set_color(self, color):
        self.background_color = color
        self.update()  # 触发重绘

    def _show_color_dialog(self):
        # 打开颜色选择对话框，允许选择透明度
        color = QColorDialog.getColor(
            initial=self.background_color,
            parent=self,
            options=QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self.background_color = color
            self.update()  # 触发重绘


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cover = CoverWidget()
    sys.exit(app.exec_())

# pyinstaller --windowed --onefile --icon=ico.ico --upx-dir="d:/Users/12766/Desktop/upx-5.0.1-win64" WaliBoard.py