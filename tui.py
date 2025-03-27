from textual.app import App
from textual.containers import Container
from textual.widgets import Button, Log
from textual.reactive import reactive

import chess

class ChessApp(App):
    current_mode = reactive("模式选择")  # 当前模式

    def compose(self):
        return Container(
            Log(),
            Button("切换到模式 1", id="mode1"),
            Button("切换到模式 2", id="mode2"),
            Button("切换到模式 3", id="mode3"),
        )

    async def on_button_pressed(self, event):
        if event.button.id == "mode1":
            self.current_mode = "模式 1"
            await self.log_message("切换到模式 1")
            # 实现模式 1 的逻辑
            
        elif event.button.id == "mode2":
            self.current_mode = "模式 2"
            await self.log_message("切换到模式 2")
            # 实现模式 2 的逻辑
            
        elif event.button.id == "mode3":
            self.current_mode = "模式 3"
            await self.log_message("切换到模式 3")
            # 实现模式 3 的逻辑

    async def log_message(self, message):
        log_widget = self.get_widget(Log)
        log_widget.write(f"[bold cyan]{self.current_mode}: {message}\n")

if __name__ == "__main__":
    chess_app = ChessApp()
    chess_app.run()