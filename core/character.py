import pygame
import math
import time

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   255, 0)
RED    = (255, 0,   0)
BLUE   = (0,   0,   255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32,  240)
CYAN   = (0,   255, 255)

SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 600

class SwingHitbox:
    def __init__(self, owner, radius, start_angle_deg, arc_deg,
                 box_w, box_h, damage, total_frames, knockback, color):
        self.owner       = owner
        self.radius      = radius
        self.start_angle = math.radians(start_angle_deg)
        self.arc         = math.radians(arc_deg)
        self.box_w       = box_w
        self.box_h       = box_h
        self.damage      = damage
        self.total_frames= total_frames
        self.knockback   = knockback
        self.color       = color

        self.frame_count   = 0
        self.active        = False
        self.hit_targets   = set()
        self._current_rect = None

    def activate(self): ...
    def deactivate(self): ...
    def get_rect(self): ...
    def update(self): ...
    def draw(self, screen): ...

class StaticHitbox:
    def __init__(self, owner, offset_x, offset_y, width, height,
                 damage, active_frames, knockback, color):
        self.owner        = owner
        self.offset_x     = offset_x
        self.offset_y     = offset_y
        self.width        = width
        self.height       = height
        self.damage       = damage
        self.active_frames= active_frames
        self.knockback    = knockback
        self.color        = color

        self.frame_count  = 0
        self.active       = False
        self.hit_targets  = set()

    def activate(self): ...
    def deactivate(self): ...
    def get_rect(self): ...
    def update(self): ...
    def draw(self, screen): ...

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing, damage, speed, color):
        super().__init__()
        # self.image, self.rect, self.facing, self.damage, self.speed
        self.hit_target = False  # prevents hitting the same target twice

    def update(self): ...   # move, kill if off-screen


# ---------------------------------------------------------------------------
#  ATTACK_DEFS  (default / template values)
#
#  Each entry is one move. Fields:
#    type          'swing' or 'static'
#    startup       frames before hitbox activates  ← PER-CHARACTER override goes here
#    recovery      frames after hitbox expires     ← PER-CHARACTER override goes here
#    crouch        (optional) shrink character rect while active
#
#  Per-character timing example:
#    VYOMI_ATTACKS = { 'neutral': {**ATTACK_DEFS['neutral'], 'startup': 9, 'recovery': 14} }
#    Character('Vyomi', ..., attack_defs=VYOMI_ATTACKS)
# ---------------------------------------------------------------------------
ATTACK_DEFS = {
    VYOMI: {
        'neutral':     { 'type': 'static', 'startup': 5, 'recovery': 10, ... },
        'up':          { 'type': 'swing',  'startup': 4, 'recovery': 12, ... },
        'down':        { 'type': 'static', 'startup': 5, 'recovery': 8,  'crouch': True, ... },
        'air_forward': { 'type': 'swing',  'startup': 4, 'recovery': 8,  ... },
        'air_back':    { 'type': 'swing',  'startup': 5, 'recovery': 10, ... },
        'air_down':    { 'type': 'static', 'startup': 6, 'recovery': 12, ... },
        'air_up':      { 'type': 'swing',  'startup': 4, 'recovery': 8,  ... },
    },
    STARRY: {
        'neutral':     { 'type': 'static', 'startup': 5, 'recovery': 10, ... },
        'up':          { 'type': 'swing',  'startup': 4, 'recovery': 12, ... },
        'down':        { 'type': 'static', 'startup': 5, 'recovery': 8,  'crouch': True, ... },
        'air_forward': { 'type': 'swing',  'startup': 4, 'recovery': 8,  ... },
        'air_back':    { 'type': 'swing',  'startup': 5, 'recovery': 10, ... },
        'air_down':    { 'type': 'static', 'startup': 6, 'recovery': 12, ... },
        'air_up':      { 'type': 'swing',  'startup': 4, 'recovery': 8,  ... },
    },
    ABACUS: {
        'neutral':     { 'type': 'static', 'startup': 5, 'recovery': 5, ... },
        'up':          { 'type': 'swing',  'startup': 4, 'recovery': 5, ... },
        'down':        { 'type': 'static', 'startup': 5, 'recovery': 5,  'crouch': True, ... },
        'air_forward': { 'type': 'swing',  'startup': 4, 'recovery': 5,  ... },
        'air_back':    { 'type': 'static',  'startup': 5, 'recovery': 5, ... },
        'air_down':    { 'type': 'static', 'startup': 6, 'recovery': 7, ... },
        'air_up':      { 'type': 'swing',  'startup': 4, 'recovery': 5,  ... },
    },
}


# ---------------------------------------------------------------------------
#  Character
# ---------------------------------------------------------------------------
class Character(pygame.sprite.Sprite):

    # State constants
    IDLE      = 'idle'
    ATTACKING = 'attacking'
    BLOCKING  = 'blocking'
    HIT       = 'hit'
    AIRBORNE  = 'airborne'

    def __init__(self, name, health, attack_power,
                 is_vyomi=False, color=(255,0,0),
                 attack_defs=ATTACK_DEFS[name]):   # <-- per-character timing lives here
        super().__init__()
        self.name         = name
        self.max_health   = health
        self.health       = health
        self.attack_power = attack_power
        self.base_attack  = attack_power
        self.base_color   = color
        self.base_width   = 40
        self.base_height  = 60

        self.image = pygame.Surface([self.base_width, self.base_height])
        self.rect  = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0
        self.facing   = 1       # 1=right, -1=left
        self.grounded = False
        self.level    = None

        self.state       = self.IDLE
        self.state_timer = 0
        self.hit_flash   = 0    # frames of white flash remaining

        # Block / parry
        self.is_blocking  = False
        self.parry_active = False
        self.block_timer  = 120
        self.block_startup= 3   # frames of parry window at block start

        # Active attack state
        self.attack_defs     = attack_defs or ATTACK_DEFS
        self.active_hitbox   = None   # SwingHitbox or StaticHitbox, or None
        self.current_attack  = None   # key into self.attack_defs
        self._atk_startup    = 0
        self._atk_recovery   = 0

        # Projectiles fired by this character
        self.projectile_group = pygame.sprite.Group()

        self.is_vyomi      = is_vyomi
        self.super_meter    = 0
        self.super_max      = 100
        self.super_active   = False
        self.super_timer    = 0
        self.super_duration = 300   # frames

    # ── Movement ────────────────────────────────────────────────────────────
    def go_left(self): ...

    def go_right(self): ...
    
    def stop(self): ...
    
    def jump(self): ...

    # ── Actions ─────────────────────────────────────────────────────────────
    def start_attack(self, held_up=False, held_down=False): ...
        # Picks attack key from self.attack_defs based on grounded + direction,
        # sets state=ATTACKING, stores startup/recovery from the chosen def.

    def start_block(self): ...
    def stop_block(self): ...
    def activate_super(self): ...   # char X only, requires full meter
    def fire_projectile(self): ...

    # ── Damage ──────────────────────────────────────────────────────────────
    def receive_hit(self, damage, knockback): ...
        # Returns False if parried, True otherwise.
        # Applies 30% damage if blocking, full damage otherwise.

    def _apply_damage(self, amount): ...
    def _gain_super(self, amount): ...  # no-op if not is_vyomi

    # ── Internal ────────────────────────────────────────────────────────────
    def _build_hitbox(self, attack_key): ...
        # Reads self.attack_defs[attack_key], returns SwingHitbox or StaticHitbox.

    def _crouch_on(self): ...   # shrink rect height, keep bottom fixed
    def _crouch_off(self): ...  # restore rect height, keep bottom fixed
    def _set_color(self, color): ...
    def _deactivate_super(self): ...

    # ── Update ──────────────────────────────────────────────────────────────
    def update(self): ...
        # 1. calc_grav
        # 2. move x, resolve platform collisions
        # 3. move y, resolve platform collisions, set self.grounded
        # 4. clamp to screen bounds
        # 5. _update_state
        # 6. tick active_hitbox
        # 7. tick projectile_group
        # 8. tick super timer
        # 9. update color (hit flash / super / normal)

    def _update_state(self): ...
        # ATTACKING: activate hitbox at startup+1, clear at startup+active+recovery
        # HIT:       clear after 20 frames
        # BLOCKING:  close parry window after block_startup frames

    def calc_grav(self): ...

    def is_alive(self): ...
    def draw_hitboxes(self, screen): ... # debug: draws active_hitbox + projectiles


# ---------------------------------------------------------------------------
#  HealthBar
# ---------------------------------------------------------------------------
class HealthBar:
    def __init__(self, character, align='left', has_super=False):
        # align='left' for player, 'right' for enemy
        self.character = character
        self.align     = align
        self.has_super = has_super  # draws second bar for char X

    def draw(self, screen): ...
        # health bar (green→yellow→red), name label
        # if has_super: second bar below (purple→orange when active)





# ---------------------------------------------------------------------------
#  AI Controller
# ---------------------------------------------------------------------------
class AIController:
    ATTACK_RANGE   = 80
    APPROACH_STOP  = 55
    REACTION_DELAY = 6

    def __init__(self, ai_character, target_character):
        self.ai              = ai_character
        self.target          = target_character
        self._reaction_queue = []
        self._frame          = 0
        self._block_cooldown = 0

    def _queue(self, delay, fn):
        self._reaction_queue.append([delay, fn])

    def update(self):
        self._frame += 1
        self._block_cooldown = max(0, self._block_cooldown - 1)

        still_pending = []
        for item in self._reaction_queue:
            item[0] -= 1
            if item[0] <= 0:
                item[1]()
            else:
                still_pending.append(item)
        self._reaction_queue = still_pending

        ai, tgt = self.ai, self.target
        if not ai.is_alive() or not tgt.is_alive():
            return

        dx   = tgt.rect.centerx - ai.rect.centerx
        dist = abs(dx)
        ai.facing = 1 if dx > 0 else -1

        if tgt.state == Character.ATTACKING and self._block_cooldown == 0:
            if dist < self.ATTACK_RANGE + 40:
                self._queue(self.REACTION_DELAY, lambda: ai.start_block())
                self._block_cooldown = 45

        if ai.state == Character.BLOCKING and ai.block_timer > 20:
            ai.stop_block()

        if dist <= self.ATTACK_RANGE:
            # print(f"AI: Queuing attack at frame {self._frame}")
            self._queue(self.REACTION_DELAY, lambda: ai.start_attack())
        elif dist > self.APPROACH_STOP and ai.state == Character.IDLE:
            ai.go_right() if dx > 0 else ai.go_left()
        elif dist <= self.APPROACH_STOP and ai.state == Character.IDLE:
            ai.stop()

        if tgt.rect.top < ai.rect.top - 60 and dist < 200 and ai.state == Character.IDLE:
            self._queue(self.REACTION_DELAY, lambda: ai.jump())


# ---------------------------------------------------------------------------
#  Combat resolution  — call once per frame per (attacker, defender) pair
# ---------------------------------------------------------------------------
def resolve_combat(attacker, defender):
    hb = attacker.active_hitbox
    if hb and hb.active:
        r = hb.get_rect()
        if r and id(defender) not in hb.hit_targets:
            if r.colliderect(defender.rect):
                if defender.receive_hit(hb.damage, hb.knockback):
                    hb.hit_targets.add(id(defender))
                    attacker._gain_super(hb.damage // 2)

    for proj in list(attacker.projectile_group):
        if proj.rect.colliderect(defender.rect) and not proj.hit_target:
            proj.hit_target = True
            defender.receive_hit(proj.damage, (4, -2))
            proj.kill()

# ---------------------------------------------------------------------------
#  SwingHitbox
#  Travels along an arc each frame. The box position is recomputed every tick
#  so it visually sweeps through space rather than snapping into place.
#
#  Angles follow pygame/math convention: 0=right, -90=up, 90=down, 180=left.
#  arc_deg is the total angular sweep. Negative = counter-clockwise (upward).
#  The sweep is mirrored on the x-axis when facing == -1.
# ---------------------------------------------------------------------------
class SwingHitbox:
    def __init__(self, owner, radius, start_angle_deg, arc_deg,
                 box_w, box_h, damage, total_frames, knockback=(5, -3),
                 color=YELLOW):
        self.owner       = owner
        self.radius      = radius
        self.start_angle = math.radians(start_angle_deg)
        self.arc         = math.radians(arc_deg)
        self.box_w       = box_w
        self.box_h       = box_h
        self.damage      = damage
        self.total_frames= total_frames
        self.knockback   = knockback
        self.color       = color

        self.frame_count   = 0
        self.active        = False
        self.hit_targets   = set()
        self._current_rect = None

    def activate(self):
        self.active      = True
        self.frame_count = 0
        self.hit_targets = set()

    def deactivate(self):
        self.active        = False
        self._current_rect = None

    def get_rect(self):
        return self._current_rect

    def update(self):
        if not self.active:
            return
        self.frame_count += 1
        t      = self.frame_count / self.total_frames
        facing = getattr(self.owner, 'facing', 1)
        # All attacks are defined facing right (facing=1).
        # When facing left, reflect across the vertical axis using (pi - angle),
        # which flips the x-component so attacks correctly appear on the right side.
        base_angle = self.start_angle + self.arc * t
        angle = base_angle if facing == 1 else math.pi - base_angle
        cx = self.owner.rect.centerx + math.cos(angle) * self.radius
        cy = self.owner.rect.centery + math.sin(angle) * self.radius
        self._current_rect = pygame.Rect(
            cx - self.box_w // 2,
            cy - self.box_h // 2,
            self.box_w, self.box_h
        )
        if self.frame_count >= self.total_frames:
            self.deactivate()

    def draw(self, screen):
        if not self.active:
            return
        if self._current_rect:
            pygame.draw.rect(screen, self.color, self._current_rect, 2)
        facing = getattr(self.owner, 'facing', 1)
        for i in range(0, self.frame_count, 2):
            t          = i / self.total_frames
            base_angle = self.start_angle + self.arc * t
            angle      = base_angle if facing == 1 else math.pi - base_angle
            px = self.owner.rect.centerx + math.cos(angle) * self.radius
            py = self.owner.rect.centery + math.sin(angle) * self.radius
            pygame.draw.circle(screen, self.color, (int(px), int(py)), 2)


# ---------------------------------------------------------------------------
#  StaticHitbox
#  A fixed rectangle placed relative to the character for the full active window.
#  offset_x is always applied in the facing direction so it stays in front/below.
# ---------------------------------------------------------------------------
class StaticHitbox:
    def __init__(self, owner, offset_x, offset_y, width, height,
                 damage, active_frames, knockback=(5, -3), color=YELLOW):
        self.owner        = owner
        self.offset_x     = offset_x
        self.offset_y     = offset_y
        self.width        = width
        self.height       = height
        self.damage       = damage
        self.active_frames= active_frames
        self.knockback    = knockback
        self.color        = color

        self.frame_count  = 0
        self.active       = False
        self.hit_targets  = set()

    def activate(self):
        self.active      = True
        self.frame_count = 0
        self.hit_targets = set()

    def deactivate(self):
        self.active = False

    def get_rect(self):
        facing = getattr(self.owner, 'facing', 1)
        if facing == 1:
            x = self.owner.rect.right + self.offset_x
        else:
            x = self.owner.rect.left - self.offset_x - self.width
        y = self.owner.rect.y + self.offset_y
        return pygame.Rect(x, y, self.width, self.height)

    def update(self):
        if not self.active:
            return
        self.frame_count += 1
        if self.frame_count >= self.active_frames:
            self.deactivate()

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.get_rect(), 2)


# ---------------------------------------------------------------------------
#  Projectile
# ---------------------------------------------------------------------------
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing, damage, speed=8, color=ORANGE):
        super().__init__()
        self.image = pygame.Surface([16, 8])
        self.image.fill(color)
        self.rect       = self.image.get_rect(center=(x, y))
        self.facing     = facing
        self.damage     = damage
        self.speed      = speed
        self.hit_target = False

    def update(self):
        self.rect.x += self.speed * self.facing
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


# ---------------------------------------------------------------------------
#  HealthBar  (+  optional SuperBar for character X)
# ---------------------------------------------------------------------------
class HealthBar:
    BAR_W, BAR_H = 350, 22
    SUPER_H      = 10
    MARGIN       = 20

    def __init__(self, character, align='left', has_super=False):
        self.character = character
        self.align     = align
        self.has_super = has_super

    def draw(self, screen):
        c   = self.character
        pct = max(0, c.health / c.max_health)
        x   = self.MARGIN if self.align == 'left' else SCREEN_WIDTH - self.MARGIN - self.BAR_W
        y   = self.MARGIN

        pygame.draw.rect(screen, (60, 0, 0), (x, y, self.BAR_W, self.BAR_H))
        col = GREEN if pct > 0.5 else (YELLOW if pct > 0.25 else RED)
        pygame.draw.rect(screen, col,        (x, y, int(self.BAR_W * pct), self.BAR_H))
        pygame.draw.rect(screen, WHITE,      (x, y, self.BAR_W, self.BAR_H), 2)

        font = pygame.font.SysFont("Arial", 14, bold=True)
        screen.blit(font.render(c.name, True, WHITE), (x, y + self.BAR_H + 2))

        if self.has_super:
            sy = y + self.BAR_H + 18
            sp = min(1.0, c.super_meter / c.super_max)
            active_col = ORANGE if c.super_active else PURPLE

            pygame.draw.rect(screen, (30, 0, 60), (x, sy, self.BAR_W, self.SUPER_H))
            pygame.draw.rect(screen, active_col,   (x, sy, int(self.BAR_W * sp), self.SUPER_H))
            pygame.draw.rect(screen, WHITE,        (x, sy, self.BAR_W, self.SUPER_H), 1)

            if c.super_active:
                screen.blit(font.render("SUPER ACTIVE", True, ORANGE),
                            (x, sy + self.SUPER_H + 2))
            elif sp >= 1.0:
                screen.blit(font.render("PRESS S to ACTIVATE", True, PURPLE),
                            (x, sy + self.SUPER_H + 2))


# ---------------------------------------------------------------------------
#  ATTACK_DEFS
#  Central data table for every attack move.
#
#  type          'swing' or 'static'
#  startup       frames before the hitbox activates (wind-up)
#  recovery      frames after the hitbox expires before returning to idle
#  crouch        (static only) True shrinks the character height while active
#
#  swing fields: radius, start_angle_deg, arc_deg, active_frames
#  static fields: offset_x, offset_y, width, height, active_frames
#
#  Angle reference: 0=right  -90=up  90=down  180/−180=left
#  arc_deg negative = counter-clockwise sweep (upward direction)
# ---------------------------------------------------------------------------
ATTACK_DEFS = {

    # Ground neutral — horizontal box in front
    'neutral': {
        'type': 'static', 'startup': 5, 'recovery': 10,
        'offset_x': 5, 'offset_y': 10, 'width': 45, 'height': 30,
        'active_frames': 8, 'damage': 10, 'knockback': (6, -4),
    },

    # Ground up-tilt — starts in front (0°) and sweeps counter-clockwise up and over head
    'up': {
        'type': 'swing', 'startup': 4, 'recovery': 12,
        'radius': 48, 'start_angle_deg': 0, 'arc_deg': -180,
        'active_frames': 18, 'damage': 9, 'knockback': (2, -8),
    },

    # Ground down-tilt — low box, character crouches
    'down': {
        'type': 'static', 'startup': 5, 'recovery': 8, 'crouch': True,
        'offset_x': 5, 'offset_y': 35, 'width': 45, 'height': 20,
        'active_frames': 8, 'damage': 8, 'knockback': (5, -2),
    },

    # Air forward — arc from above, sweeping downward (top-to-bottom)
    'air_forward': {
        'type': 'swing', 'startup': 4, 'recovery': 8,
        'radius': 50, 'start_angle_deg': -60, 'arc_deg': 140,
        'active_frames': 16, 'damage': 11, 'knockback': (7, -3),
    },

    # Air back — starts behind and below (-210°), sweeps upward behind the character.
    # facing multiplier in SwingHitbox mirrors this to always go behind, not in front.
    'air_back': {
        'type': 'swing', 'startup': 5, 'recovery': 10,
        'radius': 50, 'start_angle_deg': 120, 'arc_deg': -140,
        'active_frames': 16, 'damage': 14, 'knockback': (-7, -6),
    },

    # Air down — tiny critical spike directly below; high damage, downward knockback
    'air_down': {
        'type': 'static', 'startup': 6, 'recovery': 12,
        'offset_x': -10, 'offset_y': 62, 'width': 18, 'height': 18,
        'active_frames': 6, 'damage': 18, 'knockback': (0, 8),
        'color': CYAN,
    },

    # Air up — starts directly below (90°) and sweeps counter-clockwise up and over (−200° sweep)
    'air_up': {
        'type': 'swing', 'startup': 4, 'recovery': 8,
        'radius': 48, 'start_angle_deg': 90, 'arc_deg': -200,
        'active_frames': 18, 'damage': 10, 'knockback': (2, -9),
    },
}


# ---------------------------------------------------------------------------
#  Character
# ---------------------------------------------------------------------------
class Character(pygame.sprite.Sprite):

    IDLE      = 'idle'
    ATTACKING = 'attacking'
    BLOCKING  = 'blocking'
    HIT       = 'hit'
    AIRBORNE  = 'airborne'

    def __init__(self, name, health, attack_power, sheet="",
                 is_vyomi=False, color=RED):
        super().__init__()

        self.name         = name
        self.max_health   = health
        self.health       = health
        self.attack_power = attack_power
        self.base_attack  = attack_power
        self.sprite_sheet = sheet
        self.base_color   = color
        self.current_color= color

        self.base_height  = 60
        self.base_width   = 40

        self.image = pygame.Surface([self.base_width, self.base_height])
        self.image.fill(self.current_color)
        self.rect  = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0
        self.facing   = 1       # 1=right, -1=left
        self.level    = None
        self.grounded = False

        self.state       = self.IDLE
        self.state_timer = 0
        self.hit_flash   = 0

        self.block_startup = 3
        self.is_blocking   = False
        self.parry_active  = False
        self.block_timer   = 0

        # Set when an attack begins, cleared when it ends
        self.active_hitbox   = None
        self.current_attack  = None
        self._attack_startup = 0
        self._attack_recovery= 0

        self.projectile_group = pygame.sprite.Group()

        self.is_vyomi      = is_vyomi
        self.super_meter    = 99
        self.super_max      = 100
        self.super_active   = False
        self.super_timer    = 0
        self.super_duration = 300

        self.on_third_block_time = None

    # -----------------------------------------------------------------------
    #  Internal helpers
    # -----------------------------------------------------------------------

    def _set_color(self, color):
        self.current_color = color
        self.image.fill(color)

    def _build_hitbox(self, attack_key):
        d   = ATTACK_DEFS[attack_key]
        dmg = int(self.attack_power * (1.5 if self.super_active else 1.0))
        if d['type'] == 'swing':
            return SwingHitbox(
                owner=self, radius=d['radius'],
                start_angle_deg=d['start_angle_deg'], arc_deg=d['arc_deg'],
                box_w=22, box_h=22, damage=dmg,
                total_frames=d['active_frames'], knockback=d['knockback'],
                color=d.get('color', YELLOW),
            )
        return StaticHitbox(
            owner=self, offset_x=d['offset_x'], offset_y=d['offset_y'],
            width=d['width'], height=d['height'], damage=dmg,
            active_frames=d['active_frames'], knockback=d['knockback'],
            color=d.get('color', YELLOW),
        )

    def _crouch_on(self):
        new_h = self.base_height // 2
        if self.rect.height == new_h:
            return
        bottom = self.rect.bottom
        self.image = pygame.Surface([self.base_width, new_h])
        self.image.fill(self.current_color)
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom

    def _crouch_off(self):
        if self.rect.height == self.base_height:
            return
        bottom = self.rect.bottom
        self.image = pygame.Surface([self.base_width, self.base_height])
        self.image.fill(self.current_color)
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom

    # -----------------------------------------------------------------------
    #  Public action API
    # -----------------------------------------------------------------------

    def go_left(self):
        if self.state != self.HIT:
            self.change_x = -6
            if self.grounded:
                self.facing = -1

    def go_right(self):
        if self.state != self.HIT:
            self.change_x = 6
            if self.grounded:
                self.facing = 1

    def stop(self):
        self.change_x = 0

    def jump(self):
        if self.state in (self.HIT, self.BLOCKING):
            return
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
        if hits or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -12
            self.grounded = False
            self.state    = self.AIRBORNE

    def start_attack(self, held_up=False, held_down=False):
        if self.state in (self.ATTACKING, self.HIT, self.BLOCKING):
            return

        if not self.grounded:
            # Air attack selection:
            # down-held = spike, up-held = up-air,
            # forward direction = forward-air, backward direction = back-air
            if held_down:
                key = 'air_down'
            elif held_up:
                key = 'air_up'
            else:
                key = 'air_forward' if (self.change_x * self.facing) > 0 else 'air_back'
        else:
            key = 'up' if held_up else ('down' if held_down else 'neutral')

        d = ATTACK_DEFS[key]
        self.current_attack   = key
        self._attack_startup  = d['startup']
        self._attack_recovery = d['recovery']
        self.active_hitbox    = None
        self.state            = self.ATTACKING
        self.state_timer      = 0
        self.stop()

        if d.get('crouch'):
            self._crouch_on()

    def start_block(self):
        if self.state == self.ATTACKING:
            return
        self.state        = self.BLOCKING
        self.is_blocking  = True
        self.parry_active = True
        self.block_timer  = 0

    def stop_block(self):
        self.is_blocking  = False
        self.parry_active = False
        if self.state == self.BLOCKING:
            self.state = self.IDLE

    def activate_super(self):
        if not self.is_vyomi or self.super_active:
            return
        if self.super_meter < self.super_max:
            return
        self.super_active = True
        self.super_timer  = 0
        self.attack_power = int(self.base_attack * 1.5)

    def fire_projectile(self):
        px  = self.rect.right if self.facing == 1 else self.rect.left
        p   = Projectile(px, self.rect.centery, self.facing,
                         self.attack_power // 2,
                         color=PURPLE if self.super_active else ORANGE)
        self.projectile_group.add(p)

    # -----------------------------------------------------------------------
    #  Damage reception
    # -----------------------------------------------------------------------

    def receive_hit(self, damage, knockback=(5, -3)):
        if self.parry_active:
            return False
        if self.is_blocking:
            reduced = max(1, int(damage * 0.3))
            self._apply_damage(reduced)
            self._gain_super(reduced)
            return True
        self._apply_damage(damage)
        self._gain_super(damage)
        self.change_x   = knockback[0] * -self.facing
        self.change_y   = knockback[1]
        self.state      = self.HIT
        self.state_timer= 0
        self.hit_flash  = 20
        self._crouch_off()
        return True

    def _apply_damage(self, damage):
        self.health = max(0, self.health - damage)

    def _gain_super(self, amount):
        if not self.is_vyomi or self.super_active:
            return
        self.super_meter = min(self.super_max, self.super_meter + amount)

    # -----------------------------------------------------------------------
    #  Physics
    # -----------------------------------------------------------------------

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35

    # -----------------------------------------------------------------------
    #  Main update
    # -----------------------------------------------------------------------

    def update(self):
        self.calc_grav()

        self.rect.x += self.change_x
        for block in pygame.sprite.spritecollide(self, self.level.platform_list, False):
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left  = block.rect.right

        self.grounded = False
        self.rect.y  += self.change_y
        for block in pygame.sprite.spritecollide(self, self.level.platform_list, False):
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.grounded    = True
            elif self.change_y < 0:
                self.rect.top    = block.rect.bottom
            self.change_y = 0

        if self.grounded and self.state == self.AIRBORNE:
            self.state = self.IDLE

        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))

        self._update_state()

        if self.active_hitbox:
            self.active_hitbox.update()

        self.projectile_group.update()

        if self.super_active:
            self.super_timer += 1
            if self.super_timer >= self.super_duration:
                self._deactivate_super()

        if self.hit_flash > 0:
            self.hit_flash -= 1
            self._set_color(WHITE if (self.hit_flash % 4 < 2) else self.base_color)
        elif self.super_active:
            self._set_color(PURPLE)
        else:
            self._set_color(self.base_color)

    def _update_state(self):
        self.state_timer += 1

        if self.state == self.ATTACKING:
            d        = ATTACK_DEFS[self.current_attack]
            startup  = self._attack_startup
            af       = d['active_frames']
            recovery = self._attack_recovery
            total    = startup + af + recovery

            # Activate hitbox on the first frame of the active window
            if self.state_timer == startup + 1:
                self.active_hitbox = self._build_hitbox(self.current_attack)
                self.active_hitbox.activate()
                if self.super_active:
                    self.fire_projectile()

            if self.state_timer >= total:
                if self.active_hitbox:
                    self.active_hitbox.deactivate()
                    self.active_hitbox = None
                self._crouch_off()
                self.state        = self.IDLE if self.grounded else self.AIRBORNE
                self.state_timer  = 0
                self.current_attack = None

        elif self.state == self.HIT:
            if self.state_timer >= 20:
                self.state       = self.IDLE if self.grounded else self.AIRBORNE
                self.state_timer = 0

        elif self.state == self.BLOCKING:
            self.block_timer += 1
            if self.block_timer > self.block_startup:
                self.parry_active = False

    def _deactivate_super(self):
        self.super_active = False
        self.super_timer  = 0
        self.super_meter  = 0
        self.attack_power = self.base_attack

    def is_alive(self):
        return self.health > 0

    def draw_hitboxes(self, screen):
        if self.active_hitbox:
            self.active_hitbox.draw(screen)
        for p in self.projectile_group:
            screen.blit(p.image, p.rect)
