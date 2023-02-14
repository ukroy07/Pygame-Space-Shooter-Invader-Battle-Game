
# importing different modules
import pygame
import os
import time
import random
pygame.font.init()    #initialising font in pygame

from pygame import mixer     #for handling songs and effects
#-------------------------------------------------------------------------------------------------------------------

#Setting up Pygame Window size in tuples
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UJJAWAL's SPACE SHOOTER GAME")

#------------------------------------------------------------------------------------------------------------------

# Loading all images from assets ->

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")) #also we can write as pygame.image.load(assets/...)
#(from pygame module, image.load() method is loading the image located at the given path or folder.)
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# main player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers or bullets
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background Image
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
# automatically load/transform the backgroung image according to the size of widhth and height set initially

#Background Sound effects
mixer.init()
mixer.music.load(os.path.join("assets", "background.wav"))
mixer.music.play(-1)       #will play in loop untill game ends
#-------------------------------------------------------------------------------------------------------------------

# This class basically represents one laser object.
# Simple idea, is to seperate(remove dependency) the shooted laser directions from the player's movement

class Laser:
    def __init__(self, x, y, img):    #constructor definition
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):    #movements defined of laser based on velocity downwards(won't impacts in concepts either positive or negative in parameters)
        self.y += vel

    def off_screen(self, height):   #tells if the laser is off the screen based on the height of the screen.
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):    #tells if this collides with the object or not
        return collide(self, obj)

#------------------------------------------------------------------------------------------------------------------

#setting up the Ship class ->

# This class is basically behaves like ABSTRACT class.
# Enemy's ship and player's ship having some similar kind of functionalties.
# OOPs concept will be used here. all kind of ships have these characters in common.

class Ship:
    COOLDOWN = 30 #half of FPS

    def __init__(self, x, y, health=100):  
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0    #it helps to not spam the bullets directly

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:      #drawing the lasers
            laser.draw(window)

    def move_lasers(self, vel, obj):    #to check, that each laser has hit the objecr
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):    #If, Collision occurs, reduce the health by 10
                obj.health -= 10
                self.lasers.remove(laser)   #also remove that particular laser from lasers list

    def cooldown(self):      #handle counting of cool_down_counter
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:    #Means, We are not in the process of keeping cool_down_pointer
            laser = Laser(self.x, self.y, self.laser_img)   #creating new laser at the current location 
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):       #returns the width of the ship image
        return self.ship_img.get_width()

    def get_height(self):      #returns the height of the ship image from the surface
        return self.ship_img.get_height()

#---------------------------------------------------------------------------------------------------------

#This player class inherited from SHIP class.

class Player(Ship):
    def __init__(self, x, y, health=100):   #define own initialisation method to add some images and health
        super().__init__(x, y, health)      #using super to have all of SHIP class
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)    #(mask is used in pyagme for pixel perfect collision which uses 1-bit per pixel to store which parts collide)
        # taking the surface i.e. ship_image and making a mask
        # this mask tells that where the pixels are, So to do collision It tells that where collides or not.
        self.max_health = health

    def move_lasers(self, vel, objs):    #Overriding the function in child class checking if laser collide with every single objects
        self.cooldown()   
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):   
                self.lasers.remove(laser)
            else:
                for obj in objs:   #for each objects, present in the objects list, checking for collisions and each lasers
                    if laser.collision(obj):  #if, lasers collided with the object, remove the object
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):    #overriding draw method to add healthbar too player's section
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):     #draw rectangles in red and green based on the health of my player (healthbar will show below of the player) 
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))  #tells what percentage of health currently are

#--------------------------------------------------------------------------------------------------------

class Enemy(Ship):
    # Mapping of colors with the different ship's Image and the color of it's laser
    # dictionary
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)    #super constructor calling of Ship class
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)   #creating mask same as the way created in player class

    def move(self, vel):    #enemy's ship will be moving down always
        self.y += vel

    def shoot(self):     #override the shoot method for Enemy 
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


#--------------------------------------------------------------------------------------------------------

# This function tells that whether two objects are colliding or not with the help of mask property.

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    #if, both masks are overlapping between the two offsets. Then, return true.

# Mask is basically we say that it's a rectangular representation of any shapes's coverage AREA.

#--------------------------------------------------------------------------------------------------------

def main():
    run = True
    FPS = 60  #frames per second (Higher the FPS, faster the game run.)
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)  #will be using comicsans font ( draws the lives and levels in the screen )
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []    #stores where all our enemies are
    wave_length = 5  #initial amount enemies
    
    ### Every level, we generate new wave that wave will be in random position ans starts moving down based on velocity.
    enemy_vel = 1    # default enemy's velocity as 1 pixels
    
    player_vel = 5   # default velocity variable for player as 5 pixels
    laser_vel = 5    # laser velocity

    player = Player(300, 630)    #initialising new player at the given position

    clock = pygame.time.Clock()

    lost = False   #default lost value
    lost_count = 0

    #creating separte function inside main() to avoid the unnessary use of it.
    # Benefit : It can access all the variables declared inside main().
    #So, It doesn't require to pass all to perform operations.
    #------------------------------->>>>>>>>>>>>>>>>>>>
    def redraw_window():  
        WIN.blit(BG, (0,0))   #in the top left corner of the screen

        # drawing text
        # render function is used to create a surface object from the text.
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,0,255))   #this way of showing labels will work in python3.6+
        level_label = main_font.render(f"Level: {level}", 1, (255,0,255))   #(255,255,255) = (R,G,B) = (Red,green,blue)

        WIN.blit(lives_label, (10, 10))   #10 pixels left, 10 pixels down, from top left corner
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:           #if, Player losts, labelling the required message
            lost_label = lost_font.render("You Lost !!", 1, (255,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()   #refresh the display, So that It shows the updated game stats
    #------------------------------->>>>>>>>>>>>>>>>>>

    while run:
        clock.tick(FPS)   #Sets the clock Speed based on FPS on any device
        redraw_window()

        if lives <= 0 or player.health <= 0:  #sufficient lost condition
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:    #if Lostcount > FPS value * no of ship
                run = False
            else:
                continue

        if len(enemies) == 0:  #If, no of enemies on the screen is 0
            level += 1  # level up
            wave_length += 5   # adding more 5 enemies in the next level
            for i in range(wave_length):    #setting enemies to coming in random positions in concurrent times
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)    #appending randomly chosen enemy into enemies list

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  #if we press quit, It will stop the game
                quit()

        keys = pygame.key.get_pressed()   #It returns a dictionary in terms whether they r pressed or not at the current time
        
        #K_anyKey used as a prefix to set the key for movement
        # so, Here K_a -> left, K_d -> right, K_w -> upwards and K_s for downward
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:    #to shoot by player, Press space 
            player.shoot()

        # Now, for each enemeis in the list ->
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*FPS) == 1: # enemy having probability of 50% of shooting, in every 2 second, enemy shoot the bullet so 2*FPS
                enemy.shoot()

            if collide(enemy, player):    #If, Collide between player and enemy
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:   # We lost the lives as enemies hit the check point
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)   #to shoot by player into upward direction(-ve value shows)

#--------------------------------------------------------------------------------------------------------

# Main menu function to start the game

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 35)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Welcome ukroy07, Press any key to begin...", 1, (0,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))    #title should be at the middle of the screen
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:    #If, we press any of the mouse button, go to main method
                main()           
    pygame.quit()

#-------------------------------------------------------------------------------------------------------

#calling the main_menu() function to start the game accordingly

main_menu()