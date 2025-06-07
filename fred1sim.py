## A kind of scuffed (for now teehee) replication of the hit game Five Nights At Freddy's ##

import pygame # may God bless whoever made this code
import time # used for the game timer
import sys # for closing the whole script when the game is done
from pygame import Surface # this is just for some variable notation later
from random import choice, randint # used for movements, random number checks, as well as a surprise later
from copy import copy # for some location update checks later in the main game loop

DEBUG = False
FPS = 60
WIDTH, HEIGHT = 1920, 1080
RESOLUTION = (WIDTH, HEIGHT)
BLACK, WHITE, RED, GREEN = (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0)
MOVE_TIME = {'bunny': int(4.97 * 1000), 'chicken': int(4.98 * 1000), 'bear': int(3.02 * 1000), 'fox': int(5.01 * 1000)}
AIS = {'bunny': 20, 'chicken': 20, 'bear': 20, 'fox': 20}
BONNIE_MOVES = {0: [1, 2], 1: [2, 3], 2: [1, 3], 3: [4, 5, 1], 4: [3, 5], 5: [3, 4, 6]}
CHICA_MOVES = {0: [1], 1: [7, 8], 7: [8, 9], 8: [7, 9], 9: [1, 10], 10: [9, 11]}
FREDDY_MOVES = {0: 1, 1: 7, 7: 8, 8: 9, 9: 10}
CAMS_TRANS = {
    "CAM1A": 0,
    "CAM1B": 1,
    "CAM5": 2,
    "CAM2A": 3,
    "CAM3": 4,
    "CAM2B": 5,
    "CAM7": 7,
    "CAM6": 8,
    "CAM4A": 9,
    "CAM4B": 10,
    "CAM1C": 20}
TIME_LIMIT = 535 # 8 minute 55 second long nights
pygame.init()
screen = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("Five Nights At Freddy's Python Edition")
clock = pygame.time.Clock()
EVENT_ID = pygame.USEREVENT
POWERDRAIN = EVENT_ID
PASSIVEDRAIN = EVENT_ID + 1
BONNIECHECK = EVENT_ID + 2
CHICACHECK = EVENT_ID + 3
FREDDYCHECK = EVENT_ID + 4
PULLDOWNCAMS = EVENT_ID + 5
FOXYCHECK = EVENT_ID + 6
FOXYKILL = EVENT_ID + 7
LOCKFOXY = EVENT_ID + 8

class GameState:
    def __init__(self):
        self.r_door = False
        self.l_door = False
        self.door_rects = {'left': pygame.Rect(100, (HEIGHT // 2) - 150, 120, 120), 'right': pygame.Rect(WIDTH - 170, (HEIGHT // 2) - 150, 120, 120)}
        self.r_light = False
        self.l_light = False
        self.light_rects = {'left': pygame.Rect(100, HEIGHT // 2, 120, 120), 'right': pygame.Rect(WIDTH - 170, HEIGHT // 2, 120, 120)}
        self.cam_active = False
        self.current_cam = "CAM1A"
        self.cam_toggle_rect = pygame.Rect((WIDTH // 2) - 400, HEIGHT - 100, 800, 80)
        self.hover_ready = True
        self.cam_buttons = {
            "CAM1A": pygame.Rect(WIDTH - 400, HEIGHT - 600, 80, 60),
            "CAM1B": pygame.Rect(WIDTH - 425, HEIGHT - 500, 80, 60),
            "CAM1C": pygame.Rect(WIDTH - 450, HEIGHT - 400, 80, 60),
            "CAM7": pygame.Rect(WIDTH - 200, HEIGHT - 500, 80, 60),
            "CAM5": pygame.Rect(WIDTH - 550, HEIGHT - 480, 80, 60),
            "CAM2A": pygame.Rect(WIDTH - 400, HEIGHT - 300, 80, 60),
            "CAM3": pygame.Rect(WIDTH - 500, HEIGHT - 250, 80, 60),
            "CAM2B": pygame.Rect(WIDTH - 400, HEIGHT - 200, 80, 60),
            "CAM6": pygame.Rect(WIDTH - 250, HEIGHT - 400, 80, 60),
            "CAM4A": pygame.Rect(WIDTH - 300, HEIGHT - 300, 80, 60),
            "CAM4B": pygame.Rect(WIDTH - 300, HEIGHT - 200, 80, 60)
        }
        self.power = 999
        self.usage = 1

    def power_update(self):
        self.power -= self.usage

    def additional_drain(self):
        self.power -= 1

    def draw_office_view(self, surface: Surface, enemies: list['Enemy']):
        surface.fill((18, 100, 55))
        for d_side, door_rect in self.door_rects.items():
            if d_side == 'left':
                if self.l_door:
                    pygame.draw.rect(surface, RED, door_rect)
                else:
                    pygame.draw.rect(surface, GREEN, door_rect)
            elif d_side == 'right':
                if self.r_door:
                    pygame.draw.rect(surface, RED, door_rect)
                else:
                    pygame.draw.rect(surface, GREEN, door_rect)
        for l_side, light_rect in self.light_rects.items():
            if l_side == 'left':
                if self.l_light:
                    pygame.draw.rect(surface, WHITE, light_rect)
                else:
                    pygame.draw.rect(surface, (220, 220, 220), light_rect)
            elif l_side == 'right':
                if self.r_light:
                    pygame.draw.rect(surface, WHITE, light_rect)
                else:
                    pygame.draw.rect(surface, (220, 220, 220), light_rect)
        animatronic_font = pygame.font.SysFont(None, 54)
        for char in enemies:
            animatronic_label = animatronic_font.render(f"{char.name} at door", True, WHITE)
            if char.name == Enemy.BUNNY:
                if char.curloc == 6 and self.l_light:
                    surface.blit(animatronic_label, (100, 120))
            elif char.name == Enemy.CHICKEN:
                if char.curloc == 11 and self.r_light:
                    surface.blit(animatronic_label, (WIDTH - 400, 120))

    def draw_camera_view(self, surface: Surface, enemies: list['Enemy']):
        surface.fill(BLACK)
        animatronic_font = pygame.font.SysFont(None, 54)
        cam_font = pygame.font.SysFont(None, 30)
        cam_label = cam_font.render(f"Viewing {self.current_cam}", True, WHITE)
        surface.blit(cam_label, (20, 20))
        offset = 0
        for char in enemies:
            if char.curloc == CAMS_TRANS[self.current_cam]: # character locations are integers, so the camera string gets converted to the appropriate integer
                animatronic_label = animatronic_font.render(f"{char.name} present", True, WHITE)
                surface.blit(animatronic_label, (WIDTH // 2, 300 + offset))
            offset += 80
        for name, rect in self.cam_buttons.items():
            pygame.draw.rect(surface, (230, 230, 230), rect) if name == self.current_cam else pygame.draw.rect(surface, (80, 80, 80), rect)
            label = cam_font.render(name, True, WHITE)
            surface.blit(label, rect.move(2, 2))

    def draw(self, surface: Surface, seconds: int):
        power_font = pygame.font.SysFont(None, 48)
        power_text = power_font.render(f"{round(self.power / 10)}%", True, WHITE)
        screen.blit(power_text, (80, HEIGHT - 170))
        offset = 0
        for bar in range(self.usage):
            pygame.draw.rect(surface, RED, pygame.Rect(80 + offset, HEIGHT - 120, 20, 35))
            offset += 25
        if self.hover_ready:
            pygame.draw.rect(surface, (50, 50, 50), game.cam_toggle_rect)
        if 0 <= seconds < 90:
            time_string = "12AM"
        elif 90 <= seconds < 179:
            time_string = "1AM"
        elif 179 <= seconds < 268:
            time_string = "2AM"
        elif 268 <= seconds < 357:
            time_string = "3AM"
        elif 357 <= seconds < 446:
            time_string = "4AM"
        elif 446 <= seconds < 535:
            time_string = "5AM"
        else:
            time_string = "6AM"
        time_font = pygame.font.SysFont(None, 48)
        time_text = time_font.render(time_string, True, WHITE)
        screen.blit(time_text, (WIDTH - 300, 50))

    def update_usage(self):
        usage = 1
        if self.r_door:
            usage += 1
        if self.l_door:
            usage += 1
        if self.l_light:
            usage += 1
        if self.r_light:
            usage += 1
        if self.cam_active:
            if self.l_light:
                self.l_light = False
                usage -= 1
            if self.r_light:
                self.r_light = False
                usage -= 1
            usage += 1
        self.usage = usage

    def handle_input(self, event_trigger, m_pos: tuple[int, int], enemies: list['Enemy']):
        bunny, chicken = enemies[0], enemies[1]
        if event_trigger.type == pygame.MOUSEBUTTONDOWN:
            if self.cam_active:
                for cam_name, cam_rect in self.cam_buttons.items():
                    if cam_rect.collidepoint(m_pos):
                        self.current_cam = cam_name
            elif not self.cam_active:
                for d_side, door_rect in self.door_rects.items():
                    if door_rect.collidepoint(m_pos):
                        if d_side == 'left' and not bunny.got_you:
                            self.l_door = not self.l_door
                        elif d_side == 'right' and not chicken.got_you:
                            self.r_door = not self.r_door
                for l_side, light_rect in self.light_rects.items():
                    if light_rect.collidepoint(m_pos):
                        if l_side == 'left' and not bunny.got_you:
                            if self.r_light and not self.l_light:
                                self.r_light = False
                            self.l_light = not self.l_light
                        elif l_side == 'right' and not chicken.got_you:
                            if self.l_light and not self.r_light:
                                self.l_light = False
                            self.r_light = not self.r_light

class Enemy:
    # Freddy is special, and meant to be far more mysterious than the others, so the constants below are very important
    BUNNY = 'bunny'
    CHICKEN = 'chicken'
    BEAR = 'bear'
    FOX = 'fox'
    def __init__(self, name: str):
        self.curloc = 0 if name != self.FOX else 100 # every animatronic (minus foxy, he starts at stage 0 in pirate's cove) starts at the show stage
        self.name = name
        self.lvl = AIS[self.name] # the AI levels are constants, as this is just emulating the custom night only for now
        self.got_you = False
        self.stage = False
        self.locked = False
        self.cooldown = 0
        self.setup()

    def setup(self):
        if self.name == self.FOX:
            self.stage = 0

    def progress(self):
        self.stage += 1
        if 0 < self.stage < 3:
            self.curloc = 20
        elif self.stage == 3:
            self.curloc = 3

    def attack(self, gamestate: GameState, l_door: bool):
        if l_door:
            gamestate.power -= 50
            self.stage = randint(0, 1)
            self.curloc = 20 if self.stage == 1 else 100 # foxy drains some power then returns to either stage 0 or 1 at pirate's cove
        else:
            self.got_you = True

    def move(self, door: bool, cams: bool, active_cam: int, friends: list['Enemy']): # The door value will be the respective state of the door for the animatronic's side, and the cams value will obviously be whether the cams are open
        if self.name == self.BUNNY:
            if self.curloc == 6 and not door:
                self.got_you = True # if bonnie is at the left door and succeeds the movement opportunity while the door is open, the player's fate is sealed
                pygame.time.set_timer(BONNIECHECK, 0)
            elif self.curloc == 6 and door:
                self.curloc = 3 # if bonnie is at the door and moves while the door is closed, then he moves back to the hallway
            else:
                self.curloc = choice(BONNIE_MOVES.get(self.curloc, [6])) # if bonnie is not at the door, move randomly to a new valid location
        elif self.name == self.CHICKEN: # all of the above logic for bonnie also gets applied to chica
            if self.curloc == 11 and not door:
                self.got_you = True
                pygame.time.set_timer(CHICACHECK, 0)
            elif self.curloc == 11 and door:
                self.curloc = 9
            else:
                self.curloc = choice(CHICA_MOVES.get(self.curloc, [11]))
        elif self.name == self.BEAR:
            if self.curloc == 10:
                if not door and cams:
                    if active_cam != self.curloc:
                        self.curloc = 11
                        pygame.time.set_timer(FREDDYCHECK, 0) # disable freddy's movement check
                        self.got_you = True # freddy is special where he only gets into your office when you put up the cameras
                elif door:
                    self.curloc = 9 # he goes back to the hall if the door is shut
            else:
                if cams and active_cam == self.curloc: # Freddy only moves if the cams are open, and he's not being looked at on the specific frame
                    pass
                else:
                    for friend in friends:
                        if friend.name != self.BEAR and friend.name != self.FOX:
                            if self.curloc == 0 and friend.curloc == self.curloc:
                                return # the function stops (freddy doesn't move) if he's on the main stage and either bonnie or chica are also there
                    self.curloc = FREDDY_MOVES[self.curloc] # this is a linear movement path, I'll decide at a later time if I want to make this unique
        else:
            raise ValueError(f"Invalid name ID of {self.name}") # basic error handling

game = GameState()
bonnie, chica, freddy, foxy = Enemy(Enemy.BUNNY), Enemy(Enemy.CHICKEN), Enemy(Enemy.BEAR), Enemy(Enemy.FOX)
animatronics = [bonnie, chica, freddy, foxy]
start_time = time.monotonic()
dead = False # intended to be triggered if bonnie or chica are going to kill the player, but they're in the cams, so that way when the cameras drop then they actually kill the player
foxy_run = False
running = True
timers = {POWERDRAIN: 1000, # the usage is subtracted
          PASSIVEDRAIN: 3000, # the passive drain happens every 3 seconds during the custom night in the original game
          BONNIECHECK: MOVE_TIME[bonnie.name],
          CHICACHECK: MOVE_TIME[chica.name],
          FREDDYCHECK: MOVE_TIME[freddy.name],
          FOXYCHECK: MOVE_TIME[foxy.name],
          PULLDOWNCAMS: 1000}
for event, milli in timers.items():
    if event is not PULLDOWNCAMS:
        pygame.time.set_timer(event, milli)
while running:
    clock.tick(FPS)
    cur_time = round(time.monotonic() - start_time)
    if cur_time == TIME_LIMIT:
        print(f"Night survived with {game.power} power left")
        running = False
    if game.power <= 0:
        print("Ran out of power")
        running = False
    game.update_usage()  # update the usage first to ensure power calculations are as accurate as possible
    if bonnie.got_you:
        game.l_light = False
    if chica.got_you:
        game.r_light = False

    if foxy.stage == 3 and not foxy_run:
        if game.cam_active and game.current_cam == "CAM2A":
            foxy_run = True
            pygame.time.set_timer(FOXYKILL, 0)
            pygame.time.set_timer(FOXYKILL, 3000)

    mouse_pos = pygame.mouse.get_pos()

    if freddy.got_you and not game.cam_active: # this may be redundant, but since Freddy is ignored in the bottom check, him killing you is left up to random chance
        if randint(1, 20) == 1:
            dead = True # Freddy killing the player is a five percent chance every frame

    for enemy in animatronics:
        if enemy.got_you:
            if game.cam_active:
                if not dead:
                    if enemy.name not in [Enemy.BEAR, Enemy.FOX]: # bonnie and chica can pull the player's camera down to kill them, but not freddy, for some reason, and foxy just kills you anyway
                        dead = True
                        pygame.time.set_timer(PULLDOWNCAMS, timers[PULLDOWNCAMS])
            else:
                if dead:
                    print(f"Killed by {enemy.name}")
                    running = False

    if game.cam_toggle_rect.collidepoint(mouse_pos):
        if game.hover_ready:
            game.cam_active = not game.cam_active
            if game.cam_active:
                if foxy.stage != 3:
                    foxy.locked = True
                    pygame.time.set_timer(LOCKFOXY, 0)
            else:
                if foxy.stage != 3:
                    duration = randint(830, 16670)
                    pygame.time.set_timer(LOCKFOXY, duration)
                    if DEBUG:
                        print(f"Foxy locked for {duration}ms")
            game.hover_ready = False
    else:
        game.hover_ready = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("Esc key pressed")
                running = False
        if event.type == PULLDOWNCAMS:
            if randint(1, 5) == 1:
                game.cam_active = False
                print("You can't escape death")
        game.handle_input(event, mouse_pos, animatronics)
        if event.type == POWERDRAIN:
            game.power_update()
        if event.type == PASSIVEDRAIN:
            game.additional_drain()
        if event.type == BONNIECHECK:
            if randint(1, 20) <= bonnie.lvl:
                temp_loc = copy(bonnie.curloc)
                bonnie.move(game.l_door, game.cam_active, CAMS_TRANS[game.current_cam], animatronics)
                if DEBUG:
                    if bonnie.curloc != temp_loc:
                        print(f"Bonnie moved to {bonnie.curloc}")
        if event.type == CHICACHECK:
            if randint(1, 20) <= chica.lvl:
                temp_loc = copy(chica.curloc)
                chica.move(game.r_door, game.cam_active, CAMS_TRANS[game.current_cam], animatronics)
                if DEBUG:
                    if chica.curloc != temp_loc:
                        print(f"Chica moved to {chica.curloc}")
        if event.type == FREDDYCHECK:
            if randint(1, 20) <= freddy.lvl:
                temp_loc = copy(freddy.curloc)
                freddy.move(game.r_door, game.cam_active, CAMS_TRANS[game.current_cam], animatronics)
                if DEBUG:
                    if freddy.curloc != temp_loc:
                        print(f"Freddy moved to {freddy.curloc}")
        if event.type == FOXYCHECK:
            if not foxy.locked:
                if randint(1, 20) <= foxy.lvl:
                    foxy.progress()
                    if DEBUG:
                        print(f"Foxy moved to stage {foxy.stage}")
                if foxy.stage == 3:
                    pygame.time.set_timer(FOXYCHECK, 0)
                    pygame.time.set_timer(FOXYKILL, 25*1000)
        if event.type == FOXYKILL:
            pygame.time.set_timer(FOXYKILL, 0)
            foxy.attack(game, game.l_door)
            if foxy.got_you:
                print("Foxy killed you")
                running = False
            if DEBUG:
                print(f"Foxy returned to stage {foxy.stage}")
            foxy_run = False
            pygame.time.set_timer(FOXYCHECK, MOVE_TIME[foxy.name])
        if event.type == LOCKFOXY:
            foxy.locked = False

    if game.cam_active:
        game.draw_camera_view(screen, animatronics)
    else:
        game.draw_office_view(screen, animatronics)
    game.draw(screen, cur_time)

    pygame.display.flip()

pygame.quit()
sys.exit()