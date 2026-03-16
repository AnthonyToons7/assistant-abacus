import pygame

SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 600
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
GREEN = (0,   255, 0)
RED   = (255, 0,   0)
BLUE  = (0,   0,   255)


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list    = pygame.sprite.Group()
        self.player        = player
        self.background    = None
        self.third_block   = None

    def update(self):
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        screen.fill(BLUE)
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)


class Level_01(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        platforms = [
            # [width, height, x, y]
            # Full-width ground line at the very bottom
            [SCREEN_WIDTH, 4, 0, SCREEN_HEIGHT - 4],

            # Two thin platforms in the middle area
            [220, 6, 160, SCREEN_HEIGHT - 200],
            [220, 6, 620, SCREEN_HEIGHT - 300],
        ]

        for p in platforms:
            block         = Platform(p[0], p[1])
            block.rect.x  = p[2]
            block.rect.y  = p[3]
            block.player  = self.player
            self.platform_list.add(block)

        # third_block stores the data of the highest platform (used by character.py)
        self.third_block = platforms[2]


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.rect  = self.image.get_rect()