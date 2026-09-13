'''
星核守卫 —— 平面 Boss 战游戏
=========================
一个 2D 横版 Boss 战小游戏，使用 pygame 实现。

玩法：
- 方向键 / WASD 移动，鼠标左键射击
- 空格键冲刺（带短暂无敌帧）
- 击败 Boss 即可获胜，被 Boss 击败则游戏结束

Boss 有三种阶段，血量越低攻击越凶猛：
- 阶段一（血量 > 66%）：环形弹幕
- 阶段二（血量 33% ~ 66%）：环形弹幕 + 追踪弹
- 阶段三（血量 < 33%）：密集环形弹幕 + 追踪弹 + 激光扫射

按 R 重新开始，Esc 退出。
'''
import math
import os
import random
import sys
import pygame

(WIDTH, HEIGHT) = (960, 640)
FPS = 60
BLACK = (10, 10, 18)
WHITE = (235, 235, 245)
RED = (230, 60, 60)
GREEN = (70, 220, 120)
BLUE = (80, 160, 255)
YELLOW = (255, 210, 80)
ORANGE = (255, 140, 60)
PURPLE = (180, 100, 255)
CYAN = (80, 220, 220)
GRAY = (120, 120, 140)
DARK_GRAY = (50, 50, 60)
STATE_PLAYING = 'playing'
STATE_WIN = 'win'
STATE_LOSE = 'lose'
STATE_SELECT = 'select'


class Skill:
    '''可选主动技能：定义名称、描述、触发条件与效果。'''
    
    def __init__(self, skill_id, name, desc, detail, color, hotkey):
        self.id = skill_id
        self.name = name
        self.desc = desc
        self.detail = detail
        self.color = color
        self.hotkey = hotkey

    def apply_passive(self, player):
        '''在开局选中后，对玩家应用被动型效果（每局仅调用一次）。'''
        pass

    def tick(self, dt):
        '''每帧递减技能冷却（仅对有冷却的技能生效）。'''
        pass

    def on_hit_boss(self, game):
        '''玩家子弹命中 Boss 时触发（返回额外伤害）。'''
        pass

    def on_dash(self, game):
        '''冲刺时触发（返回是否实际触发了效果）。'''
        return False

    def on_hit_player(self, game):
        '''玩家受伤时触发（返回 True 表示伤害被技能抵消）。'''
        return False


class SkillDoubleFire(Skill):
    def __init__(self):
        super().__init__('double_fire', '双倍火力', '射速翻倍，伤害提升', '被动：射击间隔减半，子弹伤害 +2', YELLOW, pygame.K_1)

    def apply_passive(self, player):
        player.shoot_interval /= 2
        PlayerBullet.DAMAGE += 2


class SkillLifesteal(Skill):
    def __init__(self):
        super().__init__('lifesteal', '生命汲取', '命中敌人回复生命', '触发：子弹命中 Boss 时，回复 1 点生命', GREEN, pygame.K_2)

    def on_hit_boss(self, game):
        game.player.hp = min(game.player.max_hp, game.player.hp + 1)


class SkillShockwave(Skill):
    COOLDOWN = 3
    
    def __init__(self):
        super().__init__('shockwave', '冲刺冲击', '冲刺时释放冲击波', '触发：冲刺瞬间释放冲击波摧毁弹幕，冷却 3 秒', CYAN, pygame.K_3)
        self.cooldown = 0

    def apply_passive(self, player):
        self.cooldown = 0
        player.skill_cooldown = 0

    def tick(self, dt):
        '''每帧递减技能冷却（由 Game.update 调用）。'''
        self.cooldown = max(0, self.cooldown - dt)

    def on_dash(self, game):
        if self.cooldown > 0.001:
            return False
        self.cooldown = self.COOLDOWN
        radius = 160
        for b in game.boss_bullets:
            if not b.alive:
                continue
            if math.hypot(b.x - game.player.x, b.y - game.player.y) <= radius:
                b.alive = False
        for i in range(24):
            a = i * (2 * math.pi / 24)
            game.particles.append(Particle(game.player.x, game.player.y, CYAN, math.cos(a) * 400, math.sin(a) * 400, life=0.35, size=3))
        game.shake = 0.12
        return True


class SkillShield(Skill):
    def __init__(self):
        super().__init__('shield', '能量护盾', '抵挡一次致命伤害', '触发：受到伤害时，护盾抵消本次伤害并消失', BLUE, pygame.K_4)

    def apply_passive(self, player):
        player.shield = 1

    def on_hit_player(self, game):
        if getattr(game.player, 'shield', 0) > 0:
            game.player.shield = 0
            return True
        return False


ALL_SKILLS = [
    SkillDoubleFire(),
    SkillLifesteal(),
    SkillShockwave(),
    SkillShield()
]
SOUND_ON = True


def load_sound(freq, duration, volume=0.3):
    '''动态生成一个简单的正弦音效，仅依赖标准库，避免外部音频文件。'''
    if not SOUND_ON:
        return None
    try:
        import array
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        for i in range(n_samples):
            t = i / sample_rate
            env = 1 - i / n_samples
            sample = int(math.sin(2 * math.pi * freq * t) * env * volume * 32767)
            buf.append(sample)
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception:
        return None


class SoundBank:
    '''集中管理音效。'''
    
    def __init__(self):
        self.shoot = load_sound(880, 0.06, 0.25)
        self.hit = load_sound(220, 0.12, 0.4)
        self.boss_hit = load_sound(160, 0.15, 0.4)
        self.dash = load_sound(440, 0.08, 0.3)
        self.explode = load_sound(90, 0.5, 0.5)
        self.win = load_sound(523, 0.6, 0.5)
        self.lose = load_sound(180, 0.6, 0.5)

    def play(self, name):
        if SOUND_ON:
            s = getattr(self, name, None)
            if s is not None:
                try:
                    s.play()
                except Exception:
                    pass


class Player:
    '''玩家角色：可移动、射击、冲刺。'''
    RADIUS = 14
    
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = 0
        self.speed = 300
        self.hp = 100
        self.max_hp = 100
        self.shoot_cooldown = 0
        self.shoot_interval = 0.16
        self.dash_cooldown = 0
        self.dash_time = 0
        self.dash_duration = 0.18
        self.dash_speed = 900
        self.dash_invincible = 0
        self.invincible = 0
        self.shield = 0
        self.skill = None
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.RADIUS), int(self.y - self.RADIUS), self.RADIUS * 2, self.RADIUS * 2)
    
    def update(self, dt, keys, mouse_pos):
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        self.dash_cooldown = max(0, self.dash_cooldown - dt)
        self.dash_time = max(0, self.dash_time - dt)
        self.dash_invincible = max(0, self.dash_invincible - dt)
        self.invincible = max(0, self.invincible - dt)
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        if dx != 0 or dy != 0:
            norm = math.hypot(dx, dy)
            dx /= norm
            dy /= norm
        if self.dash_time > 0:
            self.vx = dx * self.dash_speed
            self.vy = dy * self.dash_speed
        else:
            self.vx = dx * self.speed
            self.vy = dy * self.speed
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = max(self.RADIUS, min(WIDTH - self.RADIUS, self.x))
        self.y = max(self.RADIUS, min(HEIGHT - self.RADIUS, self.y))

    def try_shoot(self, mouse_pos, bullets, sounds):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_interval
            tx, ty = mouse_pos
            angle = math.atan2(ty - self.y, tx - self.x)
            bullets.append(PlayerBullet(self.x, self.y, angle))
            sounds.play('shoot')

    def try_dash(self, keys, sounds):
        '''触发冲刺，并在冲刺开始瞬间进入无敌状态。'''
        if self.dash_cooldown <= 0:
            self.dash_cooldown = 0.6
            self.dash_time = self.dash_duration
            self.dash_invincible = self.dash_duration
            sounds.play('dash')

    @property
    def is_invincible(self):
        return self.dash_invincible > 0 or self.invincible > 0
    
    def take_damage(self, amount, sounds):
        if self.is_invincible or not self.alive:
            return
        self.hp -= amount
        self.invincible = 0.5
        sounds.play('hit')
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def apply_skill(self, skill):
        '''在开局选中技能后调用，应用被动效果并保存技能引用。'''
        self.skill = skill
        if skill is not None:
            skill.apply_passive(self)

    def on_skill_dash(self, game):
        '''冲刺时触发技能钩子（如「冲刺冲击」的冲击波）。返回是否实际触发。'''
        if self.skill is not None and hasattr(self.skill, 'on_dash'):
            return self.skill.on_dash(game)
        return False

    def draw(self, surface, t, mouse_pos=None):
        if self.dash_time > 0:
            for i in range(4):
                col = (80, 160, 255)
                r = self.RADIUS - i * 2
                pygame.draw.circle(surface, col, (int(self.x - self.vx * 0.02 * i), int(self.y - self.vy * 0.02 * i)), r)
        if self.is_invincible and int(t * 20) % 2 == 0:
            color = (150, 150, 200)
        else:
            color = BLUE
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.RADIUS, 2)
        if self.shield > 0:
            pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.RADIUS + 6, 2)
        if pygame.mouse.get_focused():
            if mouse_pos is not None:
                mx, my = mouse_pos
            else:
                mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - self.y, mx - self.x)
            tip_x = self.x + math.cos(angle) * (self.RADIUS + 6)
            tip_y = self.y + math.sin(angle) * (self.RADIUS + 6)
            pygame.draw.line(surface, WHITE, (self.x, self.y), (tip_x, tip_y), 3)


class PlayerBullet:
    '''玩家的子弹。'''
    RADIUS = 4
    SPEED = 700
    BASE_DAMAGE = 4
    DAMAGE = 4
    
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * self.SPEED
        self.vy = math.sin(angle) * self.SPEED
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < -20 or self.x > WIDTH + 20 or self.y < -20 or self.y > HEIGHT + 20:
            self.alive = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.RADIUS), int(self.y - self.RADIUS), self.RADIUS * 2, self.RADIUS * 2)
    
    def draw(self, surface):
        pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.RADIUS - 1)


class BossBullet:
    '''Boss 的子弹（可追踪）。'''
    RADIUS = 6
    
    def __init__(self, x, y, vx, vy, homing=False, color=PURPLE):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.homing = homing
        self.color = color
        self.alive = True
        self.speed = math.hypot(vx, vy)
        if not homing:
            self.max_speed = self.speed
            return
        self.max_speed = 260

    def update(self, dt, target):
        if self.homing and target.alive:
            # 修复 pycdc 导致的弹 X/Y 轴反转的致命错误
            tx = target.x
            ty = target.y
            angle = math.atan2(ty - self.y, tx - self.x)
            cur_angle = math.atan2(self.vy, self.vx)
            diff = ((angle - cur_angle) + math.pi) % (2 * math.pi) - math.pi
            turn = max(-2.5, min(2.5, diff))
            new_angle = cur_angle + turn * dt * 3
            self.vx = math.cos(new_angle) * self.max_speed
            self.vy = math.sin(new_angle) * self.max_speed
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < -40 or self.x > WIDTH + 40 or self.y < -40 or self.y > HEIGHT + 40:
            self.alive = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.RADIUS), int(self.y - self.RADIUS), self.RADIUS * 2, self.RADIUS * 2)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.RADIUS)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.RADIUS - 2)


class Laser:
    '''Boss 的激光扫射（阶段三）。'''
    
    def __init__(self, boss):
        self.origin_x = boss.x
        self.origin_y = boss.y
        self.angle = 0
        self.life = 0
        self.duration = 1.8
        self.width = 18
        self.alive = True
        self.active = False
        self.warn = 0.6

    def update(self, dt):
        self.life += dt
        if self.life >= self.duration:
            self.alive = False
            return
        if self.life >= self.warn:
            self.active = True
            self.angle += dt * 2.5

    def hits(self, target):
        if not self.active:
            return False
        dx = math.cos(self.angle)
        dy = math.sin(self.angle)
        px = target.x - self.origin_x
        py = target.y - self.origin_y
        proj = px * dx + py * dy
        if proj < 0:
            return False
        perp = abs(px * dy - py * dx)
        return perp < self.width / 2 + target.RADIUS

    def draw(self, surface):
        if self.active:
            length = 2000
            ex = self.origin_x + math.cos(self.angle) * length
            ey = self.origin_y + math.sin(self.angle) * length
            pygame.draw.line(surface, RED, (self.origin_x, self.origin_y), (ex, ey), self.width)
            pygame.draw.line(surface, (255, 180, 180), (self.origin_x, self.origin_y), (ex, ey), self.width // 3)
            return
        length = 2000
        ex = self.origin_x + math.cos(self.angle) * length
        ey = self.origin_y + math.sin(self.angle) * length
        pygame.draw.line(surface, (180, 60, 60), (self.origin_x, self.origin_y), (ex, ey), 3)


class Particle:
    '''粒子特效。'''
    
    def __init__(self, x, y, color, vx=0, vy=0, life=0.5, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.98
        self.vy *= 0.98

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        size = int(self.size * alpha)
        if size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)


class Boss:
    '''Boss：三种阶段，多种攻击模式。'''
    RADIUS = 42
    
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.base_x = float(x)
        self.base_y = float(y)
        self.hp = 1500
        self.max_hp = 1500
        self.alive = True
        self.ring_cooldown = 1
        self.ring_interval = 1.6
        self.homing_cooldown = 3
        self.homing_interval = 2.2
        self.laser_cooldown = 5
        self.laser_interval = 4.5
        self.flash = 0
        self.t = 0

    @property
    def phase(self):
        ratio = self.hp / self.max_hp
        if ratio > 0.66:
            return 1
        if ratio > 0.33:
            return 2
        return 3

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.RADIUS), int(self.y - self.RADIUS), self.RADIUS * 2, self.RADIUS * 2)
    
    def update(self, dt, bullets, lasers):
        self.t += dt
        self.flash = max(0, self.flash - dt)
        self.y = self.base_y + math.sin(self.t * 1.2) * 40
        self.x = self.base_x + math.sin(self.t * 0.7) * 30
        phase = self.phase
        self.ring_cooldown -= dt
        if self.ring_cooldown <= 0:
            self.ring_cooldown = self.ring_interval
            if phase == 1:
                self._fire_ring(bullets, 12, 200, PURPLE)
            elif phase == 2:
                self._fire_ring(bullets, 16, 220, PURPLE)
            else:
                self._fire_ring(bullets, 22, 240, PURPLE)
        if phase >= 2:
            self.homing_cooldown -= dt
            if self.homing_cooldown <= 0:
                self.homing_cooldown = self.homing_interval
                for i in range(3 if phase == 2 else 5):
                    angle = random.uniform(0, 2 * math.pi)
                    vx = math.cos(angle) * 180
                    vy = math.sin(angle) * 180
                    bullets.append(BossBullet(self.x, self.y, vx, vy, homing=True, color=ORANGE))
        if phase >= 3:
            self.laser_cooldown -= dt
            if self.laser_cooldown <= 0:
                self.laser_cooldown = self.laser_interval
                laser = Laser(self)
                laser.angle = random.uniform(0, 2 * math.pi)
                lasers.append(laser)

    def _fire_ring(self, bullets, count, speed, color):
        base = random.uniform(0, 2 * math.pi)
        for i in range(count):
            angle = base + i * (2 * math.pi / count)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullets.append(BossBullet(self.x, self.y, vx, vy, color=color))

    def take_damage(self, amount, particles, sounds):
        if not self.alive:
            return
        self.hp -= amount
        self.flash = 0.1
        sounds.play('boss_hit')
        for _ in range(6):
            particles.append(Particle(self.x + random.uniform(-self.RADIUS, self.RADIUS), self.y + random.uniform(-self.RADIUS, self.RADIUS), random.choice([RED, ORANGE, YELLOW, PURPLE]), random.uniform(-150, 150), random.uniform(-150, 150), life=0.4, size=3))
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, surface):
        base_color = DARK_GRAY
        pygame.draw.circle(surface, base_color, (int(self.x), int(self.y)), self.RADIUS)
        if self.flash > 0:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.RADIUS)
        core_color = [RED, ORANGE, PURPLE][self.phase - 1]
        pygame.draw.circle(surface, core_color, (int(self.x), int(self.y)), self.RADIUS - 12)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.RADIUS - 22)
        pygame.draw.circle(surface, core_color, (int(self.x), int(self.y)), self.RADIUS, 4)
        for i in range(6):
            a = self.t * 1.5 + i * (2 * math.pi / 6)
            tip_x = self.x + math.cos(a) * (self.RADIUS + 10)
            tip_y = self.y + math.sin(a) * (self.RADIUS + 10)
            pygame.draw.line(surface, core_color, (self.x, self.y), (tip_x, tip_y), 2)
            pygame.draw.circle(surface, core_color, (int(tip_x), int(tip_y)), 3)


class Game:
    '''游戏主循环与状态管理。'''
    
    def __init__(self):
        global SOUND_ON
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            SOUND_ON = False

        self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('星核守卫')
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        self.view_scale = 1
        self.view_offset = (0, 0)
        self.is_fullscreen = False
        self.clock = pygame.time.Clock()
        self.font_big = self._load_font(56)
        self.font_mid = self._load_font(28)
        self.font_small = self._load_font(18)
        self.sounds = SoundBank()
        self.reset()

    def _compute_view(self):
        '''根据当前窗口尺寸计算缩放比例与居中偏移，保持世界宽高比不变。'''
        win_w, win_h = self.window.get_size()
        scale = min(win_w / WIDTH, win_h / HEIGHT) if win_w > 0 and win_h > 0 else 1
        if scale <= 0:
            scale = 1
        disp_w = int(WIDTH * scale)
        disp_h = int(HEIGHT * scale)
        self.view_scale = scale
        self.view_offset = ((win_w - disp_w) // 2, (win_h - disp_h) // 2)

    def _window_to_world(self, pos):
        '''把窗口（鼠标）坐标换算回世界坐标。'''
        mx, my = pos
        ox, oy = self.view_offset
        return ((mx - ox) / self.view_scale, (my - oy) / self.view_scale)

    def _present(self):
        '''将固定分辨率画布缩放后绘制到窗口，并翻转显示。'''
        win_w, win_h = self.window.get_size()
        disp_w = int(WIDTH * self.view_scale)
        disp_h = int(HEIGHT * self.view_scale)
        ox, oy = self.view_offset
        self.window.fill(BLACK)
        scaled = pygame.transform.smoothscale(self.screen, (disp_w, disp_h))
        self.window.blit(scaled, (ox, oy))
        pygame.display.flip()

    def _toggle_fullscreen(self):
        '''切换全屏，再次按下恢复窗口。'''
        if self.is_fullscreen:
            self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            self.is_fullscreen = False
        else:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
        self._compute_view()

    def _load_font(self, size):
        '''查找中文字体文件，找不到时回退到 pygame 默认字体。'''
        candidates = ('msyh.ttc', 'msyhbd.ttc', 'simhei.ttf', 'simsun.ttc', 'arial.ttf', 'segoeui.ttf')
        font_dirs = (os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts'), '/usr/share/fonts', '/System/Library/Fonts')
        for d in font_dirs:
            if not os.path.isdir(d):
                continue
            for name in candidates:
                path = os.path.join(d, name)
                if os.path.isfile(path):
                    try:
                        return pygame.font.Font(path, size)
                    except Exception:
                        pass
        return pygame.font.Font(None, size)

    def reset(self):
        self.player = Player(WIDTH // 2, HEIGHT - 120)
        self.boss = Boss(WIDTH // 2, 160)
        self.player_bullets = []
        self.boss_bullets = []
        self.lasers = []
        self.particles = []
        self.selected_skill = None
        self.state = STATE_SELECT
        self.time = 0
        self.shake = 0
        PlayerBullet.DAMAGE = PlayerBullet.BASE_DAMAGE

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            dt = min(dt, 0.05)
            self._compute_view()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self._compute_view()
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        continue
                    if event.key == pygame.K_F11:
                        self._toggle_fullscreen()
                        continue
                    if event.key == pygame.K_r:
                        self.reset()
                        continue
                    if event.key == pygame.K_SPACE and self.state == STATE_PLAYING:
                        self.player.try_dash(pygame.key.get_pressed(), self.sounds)
                        self.player.on_skill_dash(self)
                        continue
                    if self.state == STATE_SELECT:
                        self._handle_skill_select(event.key)
                        continue
                if event.type == pygame.MOUSEBUTTONDOWN and self.state == STATE_SELECT and event.button == 1:
                    self._handle_skill_click(self._window_to_world(event.pos))
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit(0)

    def update(self, dt):
        self.time += dt
        self.shake = max(0, self.shake - dt)
        if self.state == STATE_SELECT or self.state != STATE_PLAYING:
            for p in self.particles:
                p.update(dt)
            return
        
        keys = pygame.key.get_pressed()
        mouse_pos = self._window_to_world(pygame.mouse.get_pos())
        mouse_buttons = pygame.mouse.get_pressed()
        self.player.update(dt, keys, mouse_pos)
        if mouse_buttons[0]:
            self.player.try_shoot(mouse_pos, self.player_bullets, self.sounds)
            
        # 修复 pycdc is None 逻辑反转错误
        if self.selected_skill is not None:
            self.selected_skill.tick(dt)
            
        self.boss.update(dt, self.boss_bullets, self.lasers)
        for b in self.player_bullets:
            b.update(dt)
        for b in self.boss_bullets:
            b.update(dt, self.player)
        for l in self.lasers:
            l.update(dt)
        for p in self.particles:
            p.update(dt)
            
        for b in self.player_bullets:
            if b.alive and self.boss.alive and b.rect.colliderect(self.boss.rect):
                b.alive = False
                self.boss.take_damage(b.DAMAGE, self.particles, self.sounds)
                self.shake = 0.08
                self._on_skill_hit_boss()
                
        for b in self.boss_bullets:
            if b.alive and self.player.alive and b.rect.colliderect(self.player.rect):
                b.alive = False
                if not self._on_skill_hit_player():
                    self.player.take_damage(10, self.sounds)
                self._explode(self.player.x, self.player.y)
                
        for l in self.lasers:
            if l.alive and l.active and self.player.alive and l.hits(self.player):
                if not self._on_skill_hit_player():
                    self.player.take_damage(2, self.sounds)
                    
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.boss_bullets = [b for b in self.boss_bullets if b.alive]
        self.lasers = [l for l in self.lasers if l.alive]
        self.particles = [p for p in self.particles if p.alive]
        
        if not self.boss.alive:
            self.state = STATE_WIN
            self.sounds.play('win')
            self._explode(self.boss.x, self.boss.y, big=True)
            return
        if not self.player.alive:
            self.state = STATE_LOSE
            self.sounds.play('lose')
            self._explode(self.player.x, self.player.y, big=True)

    def _explode(self, x, y, big=False):
        count = 60 if big else 20
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 400)
            self.particles.append(Particle(x, y, random.choice([RED, ORANGE, YELLOW, WHITE]), math.cos(angle) * speed, math.sin(angle) * speed, life=random.uniform(0.4, 1), size=random.randint(2, 5)))

    def _handle_skill_select(self, key):
        '''通过数字键选择技能。'''
        for skill in ALL_SKILLS:
            if key == skill.hotkey:
                self._confirm_skill(skill)
                return

    def _handle_skill_click(self, pos):
        '''通过鼠标点击技能卡片选择。'''
        for i, skill in enumerate(ALL_SKILLS):
            if self._skill_card_rect(i).collidepoint(pos):
                self._confirm_skill(skill)
                return

    def _confirm_skill(self, skill):
        '''确认选择：保存技能、应用被动效果、进入战斗。'''
        self.selected_skill = skill
        self.player.apply_skill(skill)
        self.state = STATE_PLAYING
        self.sounds.play('dash')

    def _skill_card_rect(self, index):
        '''返回第 index 张技能卡片的矩形（用于点击判定）。'''
        cols = 4
        card_w = 200
        card_h = 260
        gap = 24
        total_w = cols * card_w + (cols - 1) * gap
        start_x = (WIDTH - total_w) // 2
        x = start_x + index * (card_w + gap)
        y = 220
        return pygame.Rect(x, y, card_w, card_h)

    def _on_skill_hit_boss(self):
        '''玩家子弹命中 Boss 时触发技能钩子。'''
        # 修复 pycdc is None 逻辑反转错误
        if self.selected_skill is not None and hasattr(self.selected_skill, 'on_hit_boss'):
            self.selected_skill.on_hit_boss(self)

    def _on_skill_hit_player(self):
        '''玩家受伤时触发技能钩子（如护盾抵消）。返回 True 表示伤害被技能抵消。'''
        # 修复 pycdc is None 逻辑反转错误
        if self.selected_skill is not None and hasattr(self.selected_skill, 'on_hit_player'):
            return self.selected_skill.on_hit_player(self)
        return False

    def _draw_skill_select(self):
        '''绘制技能选择界面。'''
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        title = self.font_big.render('选择本局技能', True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        sub = self.font_small.render('点击卡片 或 按数字键 1-4 选择', True, GRAY)
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 170))
        mouse_pos = self._window_to_world(pygame.mouse.get_pos())
        for i, skill in enumerate(ALL_SKILLS):
            rect = self._skill_card_rect(i)
            hovered = rect.collidepoint(mouse_pos)
            card = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            card.fill((30, 30, 45, 255))
            self.screen.blit(card, (rect.x, rect.y))
            pygame.draw.rect(self.screen, skill.color if hovered else DARK_GRAY, rect, 3 if hovered else 1)
            num = self.font_mid.render(str(i + 1), True, skill.color)
            self.screen.blit(num, (rect.x + 14, rect.y + 12))
            name = self.font_mid.render(skill.name, True, WHITE)
            self.screen.blit(name, (rect.x + rect.width // 2 - name.get_width() // 2, rect.y + 20))
            desc = self.font_small.render(skill.desc, True, skill.color)
            self.screen.blit(desc, (rect.x + rect.width // 2 - desc.get_width() // 2, rect.y + 60))
            self._draw_wrapped_text(skill.detail, rect.x + 12, rect.y + 100, rect.width - 24, self.font_small, GRAY)

    def _draw_wrapped_text(self, text, x, y, max_width, font, color):
        '''在指定宽度内自动换行绘制文本。'''
        line = ''
        for ch in text:
            test = line + ch
            if font.size(test)[0] > max_width and line:
                self.screen.blit(font.render(line, True, color), (x, y))
                y += font.get_height() + 4
                line = ch
                continue
            line = test
        if line:
            self.screen.blit(font.render(line, True, color), (x, y))

    def draw(self):
        self.screen.fill(BLACK)
        for i in range(80):
            sx = (i * 97 + int(self.time * 20)) % WIDTH
            sy = (i * 53 + int(self.time * 10)) % HEIGHT
            pygame.draw.circle(self.screen, (40, 40, 55), (sx, sy), 1)
        offset_x = random.uniform(-self.shake * 10, self.shake * 10) if self.shake > 0 else 0
        offset_y = random.uniform(-self.shake * 10, self.shake * 10) if self.shake > 0 else 0
        layer = pygame.Surface((WIDTH, HEIGHT))
        layer.fill(BLACK)
        layer.set_colorkey(BLACK)
        for l in self.lasers:
            l.draw(layer)
        if self.boss.alive:
            self.boss.draw(layer)
        if self.player.alive:
            self.player.draw(layer, self.time, self._window_to_world(pygame.mouse.get_pos()))
        for b in self.player_bullets:
            b.draw(layer)
        for b in self.boss_bullets:
            b.draw(layer)
        for p in self.particles:
            p.draw(layer)
        self.screen.blit(layer, (offset_x, offset_y))
        if self.state == STATE_SELECT:
            self._draw_skill_select()
            self._present()
            return
        self.draw_ui()
        if self.state == STATE_WIN:
            self.draw_end_screen('胜利！', '你击败了 Boss！', GREEN, '按 R 重新开始')
        elif self.state == STATE_LOSE:
            self.draw_end_screen('失败', '你被 Boss 击败了', RED, '按 R 重新开始')
        self._present()

    def draw_ui(self):
        bar_w = 220
        bar_h = 18
        py = HEIGHT - 40
        px = 20
        ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, DARK_GRAY, (px, py, bar_w, bar_h))
        pygame.draw.rect(self.screen, GREEN, (px, py, int(bar_w * ratio), bar_h))
        pygame.draw.rect(self.screen, WHITE, (px, py, bar_w, bar_h), 2)
        label = self.font_small.render(f'玩家 HP {self.player.hp}', True, WHITE)
        self.screen.blit(label, (px, py - 22))
        
        bw = 500
        bh = 22
        bx = (WIDTH - bw) // 2
        by = 24
        ratio = self.boss.hp / self.boss.max_hp
        pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, bw, bh))
        pygame.draw.rect(self.screen, RED, (bx, by, int(bw * ratio), bh))
        pygame.draw.rect(self.screen, WHITE, (bx, by, bw, bh), 2)
        name = self.font_small.render(f'BOSS 阶段 {self.boss.phase}', True, RED)
        self.screen.blit(name, (bx, by + bh + 6))
        
        cd = self.player.dash_cooldown
        cd_txt = '冲刺就绪 [空格]' if cd <= 0 else f'冲刺冷却 {cd:.1f}s'
        hint = self.font_small.render(cd_txt, True, WHITE)
        self.screen.blit(hint, (WIDTH - 200, HEIGHT - 40))
        
        skill_name = self.selected_skill.name if self.selected_skill else '无'
        skill_color = self.selected_skill.color if self.selected_skill else GRAY
        skill_txt = self.font_small.render(f'技能：{skill_name}', True, skill_color)
        self.screen.blit(skill_txt, (WIDTH - 200, 20))
        
        # 修复 pycdc is None 逻辑反转错误
        if self.selected_skill is not None and hasattr(self.selected_skill, 'cooldown'):
            cd = self.selected_skill.cooldown
            if cd > 0.001:
                cd_txt = self.font_small.render(f'冷却 {cd:.1f}s', True, ORANGE)
                self.screen.blit(cd_txt, (WIDTH - 200, 42))
                return
                
        if self.player.shield > 0:
            shield_txt = self.font_small.render(f'护盾 x{self.player.shield}', True, BLUE)
            self.screen.blit(shield_txt, (WIDTH - 200, 42))

    def draw_end_screen(self, title, subtitle, color, footer):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        t = self.font_big.render(title, True, color)
        s = self.font_mid.render(subtitle, True, WHITE)
        f = self.font_small.render(footer, True, GRAY)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 80))
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2))
        self.screen.blit(f, (WIDTH // 2 - f.get_width() // 2, HEIGHT // 2 + 50))


def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()