import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
import numpy as np

MS_SIZE = 8          # ゲームボードのサイズ
CLOSE, OPEN, FLAG = 0, 1, 2

class Game:

    def __init__(self, number_of_mines = 10):
        self.init_game_board()
        self.init_mine_map(number_of_mines)
        self.count_mines()

    def init_game_board(self):
        # game_board : CLOSE/OPEN/FLAG
        self.game_board = np.array([[CLOSE for i in range(MS_SIZE)] for i in range(MS_SIZE)])
                           

    def init_mine_map(self, number_of_mines):
        # 地雷マップ(-1: 地雷，>=0 8近傍の地雷数)
        if number_of_mines<0:
            number_of_mines = 0
        elif number_of_mines>MS_SIZE*MS_SIZE:
            number_of_mines = MS_SIZE*MS_SIZE

        self.mine_map = np.array([[0 for i in range(MS_SIZE)] for i in range(MS_SIZE)])
        point_size = MS_SIZE**2
        points = [i for i in range(point_size)]
        for _ in range(number_of_mines):
            mine_idx = random.randrange(point_size)
            y = points[mine_idx]//MS_SIZE
            x = points[mine_idx]%MS_SIZE
            self.mine_map[y][x] = -1
            point_size += -1
            del points[mine_idx]

    
    def count_mines(self):
        for y in range(MS_SIZE):
            for x in range(MS_SIZE):
                if self.mine_map[y,x]!=-1:
                    left = x if x==0 else x-1
                    right = x if x==MS_SIZE-1 else x+1
                    up = y if y==0 else y-1
                    under = y if y==MS_SIZE-1 else y+1
                    cnt = np.count_nonzero(self.mine_map[up:under+1,left:right+1]==-1)
                    self.mine_map[y,x] = cnt

    
    def open_cell(self, x, y):
        if self.mine_map[y][x]==-1: return False

        if self.game_board[y][x]!=OPEN:
            self.game_board[y][x] = OPEN
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if y+i>=0 and y+i<MS_SIZE and x+j>=0 and x+j<MS_SIZE and self.mine_map[y+i][x+j]!=-1: 
                        self.game_board[y+i][x+j] = OPEN

        return True
    
    def flag_cell(self, x, y):
        self.game_board[y][x] = FLAG if self.game_board[y][x]==CLOSE else CLOSE if self.game_board[y][x]==FLAG else OPEN
            
    def is_finished(self):
        return np.all(self.game_board[self.mine_map!=-1]==OPEN)


class MyPushButton(QPushButton):
    
    def __init__(self, text, x, y, parent):
        super(MyPushButton, self).__init__(text, parent)
        self.parent = parent # MinesweeperWindow
        self.x = x
        self.y = y
        self.setMinimumSize(25, 25)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, 
            QSizePolicy.MinimumExpanding)
        
    def set_bg_color(self, colorname):
        self.setStyleSheet("MyPushButton{{background-color: {}}}".format(colorname))
        
    def on_click(self):
        """ セルをクリックしたときの動作 """
        if QApplication.keyboardModifiers()==Qt.ShiftModifier:
            self.parent.game.flag_cell(self.x, self.y) 

        else:
            if self.parent.game.open_cell(self.x, self.y)==False:
                result = QMessageBox.information(self.parent, "OK", "G A M E  O V E R !!", QMessageBox.Ok)
                if result==QMessageBox.Ok:
                    self.parent.close()

        self.parent.show_cell_status()
        if self.parent.game.is_finished():
            result = QMessageBox.information(self.parent, "OK", "G A M E  C L E A R !!", QMessageBox.Ok)
            if result==QMessageBox.Ok:
                self.parent.close()

            
class MinesweeperWindow(QMainWindow):
    
    def __init__(self):
        super(MinesweeperWindow, self).__init__()
        self.game = Game()
        self.initUI()
    
    def initUI(self):
        self.resize(700, 700)
        self.setWindowTitle('Minesweeper')
        
        sb = self.statusBar()
        sb.showMessage("Shift + クリックでフラグをセット")

        self.buttons = [[0]*MS_SIZE for i in range(MS_SIZE)] # MyPushButton用マップ
        vbox = QVBoxLayout(spacing=0)
        for i in range(MS_SIZE):
            hbox = QHBoxLayout()
            for j in range(MS_SIZE):
                self.buttons[i][j] = MyPushButton("x", j, i, self)
                self.buttons[i][j].set_bg_color("gray")
                self.buttons[i][j].clicked.connect(self.buttons[i][j].on_click)
                hbox.addWidget(self.buttons[i][j])
            vbox.addLayout(hbox)

        container = QWidget()
        container.setLayout(vbox)

        self.setCentralWidget(container)
        self.show()
    
    def show_cell_status(self):
        for i in range(MS_SIZE):
            for j in range(MS_SIZE):
                if self.game.game_board[j, i]==CLOSE:
                    self.buttons[j][i].setText("x")
                    self.buttons[j][i].setIcon(QIcon())
                    self.buttons[j][i].set_bg_color("gray")

                elif self.game.game_board[j,i]==FLAG:
                    self.buttons[j][i].setText("")
                    self.buttons[j][i].setIconSize(QSize(64,64))
                    self.buttons[j][i].setIcon(QIcon("obake.png"))
                    self.buttons[j][i].set_bg_color("purple")
                
                elif self.game.game_board[j,i]==OPEN and self.game.mine_map[j, i]!=-1:
                    self.buttons[j][i].setText(str(self.game.mine_map[j, i]))
                    self.buttons[j][i].setIcon(QIcon())
                    self.buttons[j][i].set_bg_color("orange")
                

                 
def main():
    app = QApplication(sys.argv)
    w = MinesweeperWindow()
    app.exec_()
            
if __name__ == '__main__':
    main()