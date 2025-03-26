from pynput import keyboard

class ChessStateMachine:
    def __init__(self):
        self.state = 'WAITING'
        self.last_key = ""

    def waiting_state(self):
        print("请输入命令: 1. 放置黑棋子 2. 放置指定颜色棋子 3. 旋转后放置棋子 4. 人机对弈")
        # 等待用户输入
        listener = keyboard.Listener(on_press=self.on_key_press)
        listener.start()
        listener.join()

    def on_key_press(self, key):
        print(f"当前状态: {self.state}, 输入的键: {key}")
        try:
            self.last_key = key  # 记录用户输入的键

            if key.char == '/':
                self.state = 'WAITING'
                return

            if self.state == 'WAITING':
                print("改变状态")
                self.transition(self.last_key)
                return
            
        except AttributeError:
            print("无法识别按键")
            pass

    def transition(self, last_key):
        if last_key.char == '7':
            print("从输入的键:", last_key, "改变状态")
            self.state = 'PLACE_BLACK_PIECE'
            self.place_black_piece()

        elif last_key.char == '8':
            self.state = 'PLACE_COLORED_PIECES'
            self.place_colored_pieces()

        elif last_key.char == '9':
            self.state = 'PLAY_AGAINST_HUMAN'
            self.play_against_human()
    
    def place_black_piece(self):
        print("输入坐标后回车, 将任意黑棋子放置到 5 号方格中")
        # 识别棋盘坐标、识别黑棋位置等实现代码

        while self.state != 'WAITING':
            pass
            # 识别棋盘坐标
            # 识别黑棋位置

        self.state = 'WAITING'

    def place_colored_pieces(self):
        print("请输入颜色和方格号后回车, 将棋子放置到对应方格中")
        # 识别棋子位置，机器拾取对应颜色棋子

        while self.state != 'WAITING':
            pass
            # 识别棋盘坐标
            # 识别黑棋位置

        self.state = 'WAITING'
    
    def play_against_human(self):
        print("人机对弈模式, 输入数字后回车机器执黑棋先手, 放置黑棋后回车人类先手")

        while self.state != 'WAITING':
            pass
            # 识别棋盘坐标
            # 识别黑棋位置

        self.state = 'WAITING'


if __name__ == "__main__":
    chess_fsm = ChessStateMachine()
    chess_fsm.waiting_state()