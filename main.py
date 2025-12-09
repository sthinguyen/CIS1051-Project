import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c


#initialise pygame
pg.init()

#background music
pg.mixer.music.load('/Users/staceynguyen/Documents/audio/background.wav')
pg.mixer.music.play(-1)

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Etherion TD")

#pause screen
pause = False
#mute/unmute music button
mute_image = pg.image.load('/Users/staceynguyen/Documents/gui/mute.PNG').convert_alpha()
unmute_image = pg.image.load('/Users/staceynguyen/Documents/gui/unmute.PNG').convert_alpha()
mute_button = Button(c.SCREEN_WIDTH + 220, 645, mute_image, True)
mute = False

def toggle_mute():
  global mute
  mute = not mute
  if mute:
    pg.mixer.music.set_volume(0)
    mute_button.image = mute_image
  else:
    pg.mixer.music.set_volume(0.25)
    mute_button.image = unmute_image
    
#game variables
game_over = False
game_outcome = 0 #-1 is a loss & 1 is a win
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

#load images
#menu
menu_bg = pg.image.load("/Users/staceynguyen/Documents/menu/title.PNG").convert_alpha()
menu_bg = pg.transform.scale(menu_bg, (c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
#map
map_image = pg.image.load('/Users/staceynguyen/Documents/levels/level.png').convert_alpha()
#turret spritesheets
turret1_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
  turret1_sheet = pg.image.load(f'/Users/staceynguyen/Documents/turrets/turret_{x}.PNG').convert_alpha()
  turret1_spritesheets.append(turret1_sheet)
  
turret2_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
  turret2_sheet = pg.image.load(f'/Users/staceynguyen/Documents/turrets/turret2_{x}.PNG').convert_alpha()
  turret2_spritesheets.append(turret2_sheet)
turret_spritesheets = [turret1_spritesheets, turret2_spritesheets]
#individual turret image for mouse cursor
cursor_turret = pg.image.load('/Users/staceynguyen/Documents/turrets/cursor_turret.PNG').convert_alpha()
#enemies
enemy_images = {
  "weak": pg.image.load('/Users/staceynguyen/Documents/sprites/enemy_1.PNG').convert_alpha(),
  "medium": pg.image.load('/Users/staceynguyen/Documents/sprites/enemy_2.PNG').convert_alpha(),
  "strong": pg.image.load('/Users/staceynguyen/Documents/sprites/enemy_3.PNG').convert_alpha(),
  "speedy": pg.image.load('/Users/staceynguyen/Documents/sprites/enemy_4.PNG').convert_alpha(),
  "boss": pg.image.load('//Users/staceynguyen/Documents/sprites/rosennn.png').convert_alpha(),
  "cat": pg.image.load('//Users/staceynguyen/Documents/sprites/enemy_5.png').convert_alpha(),
}
#buttons
buy_turret_image = pg.image.load('/Users/staceynguyen/Documents/buttons/buy_turret.PNG').convert_alpha()
cancel_image = pg.image.load('/Users/staceynguyen/Documents/buttons/cancel.PNG').convert_alpha()
upgrade_turret_image = pg.image.load('/Users/staceynguyen/Documents/buttons/upgrade_turret.PNG').convert_alpha()
begin_image = pg.image.load('/Users/staceynguyen/Documents/buttons/begin.PNG').convert_alpha()
restart_image = pg.image.load('/Users/staceynguyen/Documents/buttons/restart.PNG').convert_alpha()
fast_forward_image = pg.image.load('/Users/staceynguyen/Documents/buttons/fast_forward.PNG').convert_alpha()

#menu buttons
play_image = pg.image.load('/Users/staceynguyen/Documents/menu/play.PNG').convert_alpha()
settings_image = pg.image.load('/Users/staceynguyen/Documents/menu/settings.PNG').convert_alpha()
quit_image = pg.image.load('/Users/staceynguyen/Documents/menu/quit.PNG').convert_alpha()

#gui
heart_image = pg.image.load("/Users/staceynguyen/Documents/gui/heart.PNG").convert_alpha()
coin_image = pg.image.load("/Users/staceynguyen/Documents/gui/coin.PNG").convert_alpha()
logo_image = pg.image.load("/Users/staceynguyen/Documents/gui/logo.PNG").convert_alpha()

#load sounds
shot_fx = pg.mixer.Sound("/Users/staceynguyen/Documents/audio/shot.wav")
shot_fx.set_volume(0.5)
upgrade_fx = pg.mixer.Sound("/Users/staceynguyen/Documents/audio/upgrade.wav")
upgrade_fx.set_volume(0.4)

#options for turrets
buy_turret_images = [
  pg.image.load('/Users/staceynguyen/Documents/turrets/cursor_turret.PNG').convert_alpha(),
  pg.image.load('/Users/staceynguyen/Documents/turrets/cursor_turret2.PNG').convert_alpha()
]
selected_turret_type = 0

#load json data for level
with open('/Users/staceynguyen/Documents/levels/level.tmj') as file:
  world_data = json.load(file)

#load fonts for displaying text on the screen
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#function for outputting text on screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x,y))

def display_data():
  #draw panel
  pg.draw.rect(screen, "darkcyan", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
  pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
  screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
  #display data
  draw_text("WAVE: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
  screen.blit(heart_image, (c.SCREEN_WIDTH -10, 15))
  draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
  screen.blit(coin_image, (c.SCREEN_WIDTH - 10, 55))
  draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 80)
  
def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calculate the sequential number of the tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if that tile is grass
  if (mouse_tile_x, mouse_tile_y) in world.placeable_tiles:
    #check that there isn't already a turret there
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    #if it is a free space then create turret
    if space_is_free == True:
      new_turret = Turret(turret_spritesheets[selected_turret_type], mouse_tile_x, mouse_tile_y, shot_fx, upgrade_fx, turret_type=selected_turret_type)
      turret_group.add(new_turret)


def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      return turret

def clear_selection():
  for turret in turret_group:
    turret.selected = False
    
#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()


#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 30,180,cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 30,180,upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300,begin_image, True)
restart_button = Button(360, 280,restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

#main menu
def main_menu(screen):
    menu_running = True

    play_button = Button(415, 400, play_image, True)
    settings_button = Button(415, 500, settings_image, True)
    quit_button = Button(415, 600, quit_image, True)

    while menu_running:
        screen.blit(menu_bg, (0, 0))

        # draw buttons
        if play_button.draw(screen):
            return "start"

        if settings_button.draw(screen):
            pass  #do nothing for now b/c i don't know how to change settings yet

        if quit_button.draw(screen):
            pg.quit()
            exit()
        # handle quit event
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        pg.display.update()

while True:
    menu_action = main_menu(screen)

    if menu_action == "start":
        break

#game loop
run = True
while run:

  clock.tick(c.FPS)

  #draw level
  world.draw(screen)

  if game_over == False:
    #check if player has lost
    if world.health <= 0:
      game_over = True
      game_outcome = -1
    #check if player has won
    if world.level > c.TOTAL_LEVELS:
      game_over = True
      game_outcome = 1 #win
    #update groups
    if not pause:
      enemy_group.update(world)
      turret_group.update(enemy_group, world)
    
    #highlight selected turret
    if selected_turret:
      selected_turret.selected = True

  #draw groups
  for enemy in enemy_group:
    enemy.draw(screen)
  for turret in turret_group:
    turret.draw(screen)

  display_data()

  if game_over == False:
    #check if the level has been started or not
    if level_started == False:
        if begin_button.draw(screen):
            level_started = True
    else:
      #fast forward option
        world.game_speed = 1
        if fast_forward_button.draw(screen):
          world.game_speed = 2
        #spawn enemies only after start
        if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
            if world.spawned_enemies < len(world.enemy_list):
                enemy_type = world.enemy_list[world.spawned_enemies]
                enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                enemy_group.add(enemy)
                world.spawned_enemies += 1
                last_enemy_spawn = pg.time.get_ticks()

    #check if the wave is finished
    if world.check_level_complete() == True:
      world.money += c.LEVEL_COMPLETE_REWARD
      world.level += 1
      level_started = False
      last_enemy_spawn = pg.time.get_ticks()
      world.reset_level()
      result = world.process_enemies()
      if result == "WIN":
        game_over = True
        game_outcome = 1


    #draw buttons
    #button for placing turrets
    #for the turret button, show cost of turret and draw button
    #if the player doesn't have enough money, the text will show red  
    if world.money >= c.BUY_COST[selected_turret_type]:
      color = "grey100"
    else:
      color = "red"
      
    draw_text(str(c.BUY_COST[selected_turret_type]), text_font, color, c.SCREEN_WIDTH + 140, 155)
    screen.blit(coin_image, (c.SCREEN_WIDTH + 175, 130))
    if turret_button.draw(screen):
      placing_turrets = True
      selected_turret_type = (selected_turret_type + 1) % len(buy_turret_images)
      turret_button.image = buy_turret_images[selected_turret_type]
      #if placing turret, then show the cancel button as well
    if placing_turrets == True:
      cursor_rect = cursor_turret.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.SCREEN_WIDTH:
        cursor_rect = buy_turret_images[selected_turret_type].get_rect(center=cursor_pos)
        screen.blit(buy_turret_images[selected_turret_type], cursor_rect)
      if cancel_button.draw(screen):
        placing_turrets = False
      #if a turret is selected then show the upgrade button
    if selected_turret:
      #if a turret can be upgraded, then show the upgrade button
      if selected_turret.upgrade_level < c.TURRET_LEVELS:
        if world.money >= c.UPGRADE_COST:
          color = "grey100"
        else:
          color = "red"
        draw_text(str(c.UPGRADE_COST), text_font, color, c.SCREEN_WIDTH + 140, 220)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 175, 195))
        if upgrade_button.draw(screen):
          if world.money >= c.UPGRADE_COST:
            selected_turret.upgrade()
            world.money -= c.UPGRADE_COST
  else:
    pg.draw.rect(screen, "dodgerblue", (200,200,400,200),border_radius = 30)
    if game_outcome == -1:
      draw_text("GAME OVER", large_font, "grey0", 310, 230)
    elif game_outcome == 1:
      draw_text("YOU WIN!", large_font, "grey0", 315, 230)

    #restart level
    if restart_button.draw(screen):
      game_over = False
      level_started = False
      placing_turrets = False
      selected_turret = None
      last_enemy_spawn = pg.time.get_ticks()
      world = World(world_data, map_image)
      world.process_data()
      world.process_enemies()
      #empty groups
      enemy_group.empty()
      turret_group.empty()

  #event handler
  for event in pg.event.get():
    #quit program
    if event.type == pg.QUIT:
      run = False
    #pause screen
    if event.type == pg.KEYDOWN:
      if event.key == pg.K_ESCAPE:
        pause = not pause
    #mouse click
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      #check if mouse is on mute button
      if mute_button.rect.collidepoint(mouse_pos):
        toggle_mute()
      #check if mouse is on the game area
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        selected_turret = None
        clear_selection()
        if placing_turrets:
          #check if there is enough money for a turret
          turret_cost = c.BUY_COST[selected_turret_type]
          if world.money >= turret_cost:
            create_turret(mouse_pos)
            world.money -= turret_cost
        else:
          selected_turret = select_turret(mouse_pos)
          
  #draw mute button
  mute_button.draw(screen)
  #pause overlay
  if pause:
    overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    #makes the screen transparent
    overlay.set_alpha(180)
    overlay.fill((0,0,0))
    screen.blit(overlay, (0,0))
    #pause text that appears over the darkened screen
    pause_text = large_font.render("PAUSED", True, (255,255,255))
    screen.blit(pause_text, pause_text.get_rect(center=(c.SCREEN_WIDTH//2, c.SCREEN_HEIGHT//2)))

  #update display
  pg.display.flip()

pg.quit()
