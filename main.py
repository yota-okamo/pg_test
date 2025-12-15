import pyxel
import random

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="Simple Pyxel Game")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player_x = 80
        self.player_y = 100
        self.enemy_x = random.randint(0, 152)
        self.enemy_y = 0
        self.game_over = False

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        # プレイヤー操作
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x += 2

        # 画面外に出ないようにする
        self.player_x = max(0, min(self.player_x, 152))

        # 敵を落とす
        self.enemy_y += 2
        if self.enemy_y > 120:
            self.enemy_x = random.randint(0, 152)
            self.enemy_y = 0

        # 当たり判定
        if (
            abs(self.player_x - self.enemy_x) < 8 and
            abs(self.player_y - self.enemy_y) < 8
        ):
            self.game_over = True

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(50, 50, "GAME OVER", 8)
            pyxel.text(40, 60, "Press R to Restart", 7)
            return

        # プレイヤー（四角）
        pyxel.rect(self.player_x, self.player_y, 8, 8, 11)

        # 敵（四角）
        pyxel.rect(self.enemy_x, self.enemy_y, 8, 8, 8)


Game()
