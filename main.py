import random
import pyxel


SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120

PLAYER_SPEED = 2.5
PLAYER_SIZE = 4
PLAYER_MAX_HP = 5

BULLET_SPEED = -4
ENEMY_BULLET_SPEED = 2

ENEMY_MIN_SPEED = 0.8
ENEMY_MAX_SPEED = 2.0

SPAWN_INTERVAL_MIN = 8
SPAWN_INTERVAL_MAX = 24


class Game:
    def __init__(self):
        # Pyxel ウィンドウ初期化
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Shooting Game")

        # ゲーム全体の状態
        self.scene = "TITLE"  # "TITLE", "PLAY", "GAME_OVER"
        self.frame_count = 0

        # スクロール用の星
        self.stars = []
        self.init_stars()

        # プレイヤー・弾・敵など
        self.player = {}
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.explosions = []

        # スコアや難易度
        self.score = 0
        self.high_score = 0
        self.spawn_timer = 0
        self.spawn_interval = 20

        self.reset_game()

        pyxel.run(self.update, self.draw)

    # ---------------------------
    # 初期化系
    # ---------------------------

    def init_stars(self):
        """背景の星をランダムに配置（ただの飾り）"""
        self.stars.clear()
        for _ in range(60):
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT - 1)
            speed = random.choice([0.5, 1, 1.5])
            color = random.choice([6, 7, 13])  # ちょっと違う色の星
            self.stars.append({"x": x, "y": y, "speed": speed, "color": color})

    def reset_game(self):
        """ゲーム開始時・リスタート時の共通リセット処理"""
        # プレイヤー初期位置と状態
        self.player = {
            "x": SCREEN_WIDTH // 2,
            "y": SCREEN_HEIGHT - 16,
            "hp": PLAYER_MAX_HP,
            "cooltime": 0,  # 弾を連射しすぎないためのクールタイム
        }

        self.bullets.clear()
        self.enemies.clear()
        self.enemy_bullets.clear()
        self.explosions.clear()

        self.score = 0
        self.spawn_timer = 0
        self.spawn_interval = 20
        self.frame_count = 0

    # ---------------------------
    # メインループ
    # ---------------------------

    def update(self):
        """毎フレーム呼び出される更新処理"""
        self.frame_count += 1
        self.update_stars()

        if self.scene == "TITLE":
            self.update_title()
        elif self.scene == "PLAY":
            self.update_play()
        elif self.scene == "GAME_OVER":
            self.update_game_over()

    def draw(self):
        """毎フレーム呼び出される描画処理"""
        pyxel.cls(0)
        self.draw_stars()

        if self.scene == "TITLE":
            self.draw_title()
        elif self.scene == "PLAY":
            self.draw_play()
        elif self.scene == "GAME_OVER":
            self.draw_game_over()

    # ---------------------------
    # 背景（星）
    # ---------------------------

    def update_stars(self):
        """星を下方向にスクロールさせる"""
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] >= SCREEN_HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, SCREEN_WIDTH - 1)

    def draw_stars(self):
        """星を描画"""
        for star in self.stars:
            pyxel.pset(star["x"], star["y"], star["color"])

    # ---------------------------
    # シーン：タイトル
    # ---------------------------

    def update_title(self):
        """タイトル画面の更新処理"""
        # Enter または スペースで開始
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.reset_game()
            self.scene = "PLAY"

    def draw_title(self):
        """タイトル画面の描画"""
        title = "PYXEL SHOOTING"
        sub = "Press ENTER or SPACE to start"
        info1 = "Move: Arrow keys"
        info2 = "Shot: Z key"

        pyxel.text(
            (SCREEN_WIDTH - len(title) * 4) // 2,
            40,
            title,
            10,
        )
        pyxel.text(
            (SCREEN_WIDTH - len(sub) * 4) // 2,
            60,
            sub,
            7,
        )
        pyxel.text(10, 90, info1, 7)
        pyxel.text(10, 100, info2, 7)

        if self.high_score > 0:
            hs_text = f"HIGH SCORE: {self.high_score}"
            pyxel.text(
                (SCREEN_WIDTH - len(hs_text) * 4) // 2,
                10,
                hs_text,
                11,
            )

    # ---------------------------
    # シーン：ゲームプレイ
    # ---------------------------

    def update_play(self):
        """プレイ中の更新処理"""
        self.update_player()
        self.update_bullets()
        self.update_enemies()
        self.update_enemy_bullets()
        self.update_explosions()
        self.check_collisions()
        self.update_difficulty()

        # ESC でタイトルに戻る
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.scene = "TITLE"

        # プレイヤーのHPが0になったらゲームオーバー
        if self.player["hp"] <= 0:
            self.scene = "GAME_OVER"
            if self.score > self.high_score:
                self.high_score = self.score

    def draw_play(self):
        """プレイ中の描画"""
        # プレイヤー
        self.draw_player()
        # 弾
        for b in self.bullets:
            pyxel.rect(b["x"] - 1, b["y"] - 3, 2, 4, 10)
        # 敵
        for e in self.enemies:
            self.draw_enemy(e)
        # 敵弾
        for eb in self.enemy_bullets:
            pyxel.circ(eb["x"], eb["y"], 1, 8)
        # 爆発
        for ex in self.explosions:
            self.draw_explosion(ex)

        # UI（スコア・HP）
        pyxel.text(4, 4, f"SCORE: {self.score}", 7)
        pyxel.text(4, 12, f"HP: {self.player['hp']}/{PLAYER_MAX_HP}", 8)

    # ---------------------------
    # シーン：ゲームオーバー
    # ---------------------------

    def update_game_over(self):
        """ゲームオーバー時の更新"""
        # R でもう一度
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.KEY_RETURN):
            self.reset_game()
            self.scene = "PLAY"
        # ESC でタイトルへ
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.scene = "TITLE"

        # 爆発アニメだけは動かしておく
        self.update_explosions()

    def draw_game_over(self):
        """ゲームオーバー画面の描画"""
        self.draw_play()  # 背景として最後の状態を描く

        msg = "GAME OVER"
        sub = "Press R or ENTER to retry"
        esc = "Press ESC to go back to title"

        pyxel.text(
            (SCREEN_WIDTH - len(msg) * 4) // 2,
            40,
            msg,
            8,
        )
        pyxel.text(
            (SCREEN_WIDTH - len(sub) * 4) // 2,
            58,
            sub,
            7,
        )
        pyxel.text(
            (SCREEN_WIDTH - len(esc) * 4) // 2,
            70,
            esc,
            7,
        )

    # ---------------------------
    # プレイヤー
    # ---------------------------

    def update_player(self):
        """プレイヤーの移動と攻撃"""
        # 移動処理
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player["x"] -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player["x"] += PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_UP):
            self.player["y"] -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player["y"] += PLAYER_SPEED

        # 画面外に出ないように制限
        self.player["x"] = max(PLAYER_SIZE, min(SCREEN_WIDTH - PLAYER_SIZE, self.player["x"]))
        self.player["y"] = max(PLAYER_SIZE, min(SCREEN_HEIGHT - PLAYER_SIZE, self.player["y"]))

        # ショット（Zキー）
        if self.player["cooltime"] > 0:
            self.player["cooltime"] -= 1

        if pyxel.btn(pyxel.KEY_Z) and self.player["cooltime"] == 0:
            self.spawn_bullet()
            self.player["cooltime"] = 6  # クールタイム（少しだけ連射）

    def draw_player(self):
        """プレイヤーを描画（簡易な三角形っぽい形）"""
        x = self.player["x"]
        y = self.player["y"]
        # 中心を軸にした三角形＋本体
        pyxel.tri(x, y - 6, x - 4, y + 4, x + 4, y + 4, 11)
        pyxel.rect(x - 2, y, 4, 4, 12)

    def spawn_bullet(self):
        """プレイヤーの弾を発射"""
        self.bullets.append(
            {
                "x": self.player["x"],
                "y": self.player["y"] - 6,
                "vy": BULLET_SPEED,
            }
        )

    # ---------------------------
    # プレイヤー弾
    # ---------------------------

    def update_bullets(self):
        """プレイヤー弾の移動と画面外処理"""
        new_bullets = []
        for b in self.bullets:
            b["y"] += b["vy"]
            if b["y"] > -10:
                new_bullets.append(b)
        self.bullets = new_bullets

    # ---------------------------
    # 敵
    # ---------------------------

    def spawn_enemy(self):
        """敵を1体生成"""
        x = random.randint(10, SCREEN_WIDTH - 10)
        y = -10
        speed = random.uniform(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)
        hp = random.choice([1, 1, 1, 2])  # たまにHP2の敵
        shoot_chance = random.uniform(0.002, 0.01)

        enemy = {
            "x": x,
            "y": y,
            "vy": speed,
            "hp": hp,
            "shoot_chance": shoot_chance,
            "size": 5,
        }
        self.enemies.append(enemy)

    def update_enemies(self):
        """敵の移動・出現・攻撃処理"""
        # 新しい敵を出すタイミング
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        new_enemies = []
        for e in self.enemies:
            # 下方向に移動
            e["y"] += e["vy"]

            # 時々弾を撃つ
            if random.random() < e["shoot_chance"]:
                self.spawn_enemy_bullet(e["x"], e["y"])

            # 画面内にいる敵だけ残す
            if e["y"] < SCREEN_HEIGHT + 10 and e["hp"] > 0:
                new_enemies.append(e)
            else:
                # 画面下に抜けた敵も特にペナルティなしで消す
                pass

        self.enemies = new_enemies

    def draw_enemy(self, e):
        """敵を描画"""
        x = e["x"]
        y = e["y"]
        size = e["size"]
        color = 8 if e["hp"] == 1 else 2  # HPが高い敵は色を変える
        pyxel.circ(x, y, size, color)
        pyxel.circ(x, y, size - 2, 0)

    # ---------------------------
    # 敵弾
    # ---------------------------

    def spawn_enemy_bullet(self, x, y):
        """敵から弾を発射"""
        # プレイヤーの方向に向けて少しだけ狙う
        px = self.player["x"]
        py = self.player["y"]
        dx = px - x
        dy = py - y
        length = (dx ** 2 + dy ** 2) ** 0.5 + 1e-6
        vx = dx / length * ENEMY_BULLET_SPEED
        vy = dy / length * ENEMY_BULLET_SPEED

        self.enemy_bullets.append({"x": x, "y": y, "vx": vx, "vy": vy})

    def update_enemy_bullets(self):
        """敵弾の移動と画面外処理"""
        new_enemy_bullets = []
        for eb in self.enemy_bullets:
            eb["x"] += eb["vx"]
            eb["y"] += eb["vy"]
            # 画面内なら残す
            if -10 < eb["x"] < SCREEN_WIDTH + 10 and -10 < eb["y"] < SCREEN_HEIGHT + 10:
                new_enemy_bullets.append(eb)
        self.enemy_bullets = new_enemy_bullets

    # ---------------------------
    # 爆発エフェクト
    # ---------------------------

    def spawn_explosion(self, x, y):
        """敵やプレイヤーがダメージを受けたときの爆発"""
        self.explosions.append(
            {
                "x": x,
                "y": y,
                "radius": 1,
                "max_radius": 10,
            }
        )

    def update_explosions(self):
        """爆発のアニメーション更新"""
        new_explosions = []
        for ex in self.explosions:
            ex["radius"] += 0.7
            if ex["radius"] < ex["max_radius"]:
                new_explosions.append(ex)
        self.explosions = new_explosions

    def draw_explosion(self, ex):
        """爆発描画"""
        x = ex["x"]
        y = ex["y"]
        r = ex["radius"]
        pyxel.circ(x, y, int(r), 9)
        pyxel.circ(x, y, max(int(r) - 2, 0), 10)

    # ---------------------------
    # 衝突判定
    # ---------------------------

    def check_collisions(self):
        """弾と敵 / 敵・敵弾とプレイヤーの当たり判定"""
        # プレイヤー弾と敵
        new_bullets = []
        for b in self.bullets:
            hit = False
            for e in self.enemies:
                if self.is_hit_circle(b["x"], b["y"], e["x"], e["y"], e["size"]):
                    e["hp"] -= 1
                    self.spawn_explosion(b["x"], b["y"])
                    self.score += 10
                    hit = True
                    break
            if not hit:
                new_bullets.append(b)
        self.bullets = new_bullets

        # HPが0以下の敵を削除し、追加スコア
        new_enemies = []
        for e in self.enemies:
            if e["hp"] <= 0:
                self.spawn_explosion(e["x"], e["y"])
                self.score += 20
            else:
                new_enemies.append(e)
        self.enemies = new_enemies

        # 敵・敵弾とプレイヤー
        px = self.player["x"]
        py = self.player["y"]

        # 敵本体との衝突
        for e in self.enemies:
            if self.is_hit_circle(px, py, e["x"], e["y"], e["size"] + 3):
                self.player_damage(e["x"], e["y"])

        # 敵弾との衝突
        new_enemy_bullets = []
        for eb in self.enemy_bullets:
            if self.is_hit_circle(px, py, eb["x"], eb["y"], 3):
                self.player_damage(eb["x"], eb["y"])
            else:
                new_enemy_bullets.append(eb)
        self.enemy_bullets = new_enemy_bullets

    def is_hit_circle(self, x1, y1, x2, y2, r):
        """2点の距離が半径r以内かどうか"""
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy <= r * r

    def player_damage(self, hit_x, hit_y):
        """プレイヤーがダメージを受けたときの処理"""
        self.player["hp"] -= 1
        self.spawn_explosion(hit_x, hit_y)
        # ダメージを受けた瞬間、少しだけプレイヤーを下に押す
        self.player["y"] += 2

    # ---------------------------
    # 難易度調整
    # ---------------------------

    def update_difficulty(self):
        """スコアに応じて敵の出現間隔やスピードを調整"""
        # スコアが上がるほど敵の出現間隔を短くする
        self.spawn_interval = max(
            SPAWN_INTERVAL_MIN,
            SPAWN_INTERVAL_MAX - self.score // 50,
        )

        # 敵のスピードも少しずつ上げる
        global ENEMY_MIN_SPEED, ENEMY_MAX_SPEED
        ENEMY_MIN_SPEED = 0.8 + self.score / 500.0
        ENEMY_MAX_SPEED = 2.0 + self.score / 400.0


# 実行
Game()
