import pygame
from core.character import Character, AIController, HealthBar, resolve_combat
from core.stage import Level, Level_01

SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 600


def start(number=1):
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption("Platformer Fighter")

    if number == 1:
        player = Character('Vyomi', 100, 10, is_vyomi=True,  color=(200, 50,  50))
        enemy  = Character('Kael',  100, 8,  is_vyomi=False, color=(50,  50, 200))

        level_list    = [Level_01(player)]
        current_level = level_list[0]

        active_sprite_list = pygame.sprite.Group()
        player.level = current_level
        enemy.level  = current_level

        player.rect.x = 150
        player.rect.y = SCREEN_HEIGHT - player.rect.height - 10
        enemy.rect.x  = 700
        enemy.rect.y  = SCREEN_HEIGHT - enemy.rect.height - 10

        active_sprite_list.add(player, enemy)

        ai         = AIController(enemy, player)
        player_hud = HealthBar(player, align='left',  has_super=player.is_vyomi)
        enemy_hud  = HealthBar(enemy,  align='right', has_super=enemy.is_vyomi)

        done  = False
        clock = pygame.time.Clock()

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.go_left()
                    if event.key == pygame.K_RIGHT:
                        player.go_right()
                    if event.key == pygame.K_UP:
                        player.jump()
                    if event.key == pygame.K_z:
                        # Pass current directional state so start_attack picks the right move
                        keys = pygame.key.get_pressed()
                        player.start_attack(
                            held_up   = keys[pygame.K_UP],
                            held_down = keys[pygame.K_DOWN],
                        )
                    if event.key == pygame.K_x:
                        player.start_block()
                    if event.key == pygame.K_s:
                        player.activate_super()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and player.change_x < 0:
                        player.stop()
                    if event.key == pygame.K_RIGHT and player.change_x > 0:
                        player.stop()
                    if event.key == pygame.K_x:
                        player.stop_block()

            ai.update()
            active_sprite_list.update()
            current_level.update()

            resolve_combat(player, enemy)
            resolve_combat(enemy,  player)

            if not enemy.is_alive():
                _show_message(screen, "YOU WIN!", clock)
                done = True
            if not player.is_alive():
                _show_message(screen, "YOU LOSE!", clock)
                done = True

            if player.rect.y >= SCREEN_HEIGHT:
                player.health = 0

            current_level.draw(screen)
            active_sprite_list.draw(screen)

            player.draw_hitboxes(screen)
            enemy.draw_hitboxes(screen)

            player_hud.draw(screen)
            enemy_hud.draw(screen)

            _draw_controls(screen)

            clock.tick(60)
            pygame.display.flip()

    pygame.quit()


def _show_message(screen, text, clock):
    font  = pygame.font.SysFont("Arial", 72, bold=True)
    label = font.render(text, True, (255, 215, 0))
    screen.blit(label, label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.wait(2500)


def _draw_controls(screen):
    font  = pygame.font.SysFont("Arial", 12)
    hints = [
        "← → Move / Air drift",
        "↑ Jump",
        "Z Attack  (hold ↑/↓ for up/down attack)",
        "  In air: fwd/back drift = fair/bair  |  ↓+Z = spike  |  ↑+Z = up-air",
        "X Block / Parry (tap for parry window)",
        "S Activate Super (when bar is full)",
    ]
    for i, h in enumerate(hints):
        screen.blit(font.render(h, True, (200, 200, 200)),
                    (10, SCREEN_HEIGHT - 16 - i * 16))