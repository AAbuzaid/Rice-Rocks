# program template for Spaceship
# http://www.codeskulptor.org/#user45_G16dIIeL28okpJ0.py

import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.3)
soundtrack.set_volume(.3)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound.set_volume(.3)
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        canvas.draw_image(ship_image, [ship_info.get_center()[0] + self.thrust * 90, ship_info.get_center()[1]] ,
                          ship_info.get_size(), self.pos, ship_info.get_size(),
                          self.angle)
    def inc_angle(self):
        self.angle_vel = 0.1

    def dec_angle(self):
        self.angle_vel = -0.1

    def fix_angle(self):
        self.angle_vel = 0
        
    def thrusters(self):
        self.thrust = not self.thrust
        if self.thrust:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()
            
    def get_pos(self):
        return self.pos
            

    def update(self):
        self.angle += self.angle_vel
        vel_vec = angle_to_vector(self.angle)
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[0] *= 0.99
        self.vel[1] *= 0.99
        if self.thrust:
            self.vel[0] += 0.25*vel_vec[0]
            self.vel[1] += 0.25*vel_vec[1]
        if (self.pos[0] < 0) or (self.pos[0] > WIDTH):
            self.pos[0] = self.pos[0] % WIDTH
        if (self.pos[1] < 0) or (self.pos[1] > HEIGHT):
            self.pos[1] = self.pos[1] % HEIGHT
            
    def shoot(self):
        global missile_group
        vel_vec = angle_to_vector(self.angle)
        missile_pos = [40*vel_vec[0] + self.pos[0], 40*vel_vec[1] + self.pos[1]]
        missile_vel = [self.vel[0] + vel_vec[0] * 10, self.vel[1] + vel_vec[1] * 10]        
        missile_group.add(Sprite(missile_pos, missile_vel, 0, 0,
                           missile_image, missile_info, missile_sound))
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos,
                          self.image_size, self.angle)
    
    def get_pos(self):
        return self.pos
    
    def update(self):
        self.pos[0] += self.vel[0]    
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        if (self.pos[0] < 0) or (self.pos[0] > WIDTH):
            self.pos[0] = self.pos[0] % WIDTH
        if (self.pos[1] < 0) or (self.pos[1] > HEIGHT):
            self.pos[1] = self.pos[1] % HEIGHT
        self.age += 1
        return (self.age >= self.lifespan)

            
    def collide(self, other_object):
        other_object_pos = other_object.get_pos()
        distance = math.sqrt(math.pow(self.pos[0] - other_object_pos[0], 2)
                                      + math.pow(self.pos[1] - other_object_pos[1], 2))
        if distance < (self.radius + other_object.radius):
            return True
        else:
            return False
           
        
def draw(canvas):
    global time, lives, score, started, rock_group

    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        soundtrack.rewind()
        return None
    
    # update ship and sprites
    my_ship.update()

    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    hits = group_group_collide(rock_group, missile_group)
    score += hits
    if group_collide(rock_group, my_ship):
        lives -= 1
    if lives == 0:
        started = False
        rock_group = set([])
    # draw score and remaining lives
    canvas.draw_text("Lives " + str(lives), [680, 60], 30, "White")
    canvas.draw_text("Score " + str(score), [30, 60], 30, "White")
    


def key_down(key):
    if key == simplegui.KEY_MAP["right"]:
        my_ship.inc_angle()
    elif key == simplegui.KEY_MAP["left"]:
        my_ship.dec_angle()
    if key == simplegui.KEY_MAP["up"]:
        my_ship.thrusters()
    if key == simplegui.KEY_MAP["space"]:
        my_ship.shoot()
        
def key_up(key):
    if key == simplegui.KEY_MAP["right"] or key == simplegui.KEY_MAP["left"]:
        my_ship.fix_angle()
    if key == simplegui.KEY_MAP["up"]:
        my_ship.thrusters()

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score, my_ship, missile_group
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 3, ship_image, ship_info)
        soundtrack.play()
        missile_group = set([])
        
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    asteroid_vel = [random.random() * random.choice([1 , -1]),
                    random.random() * random.choice([1 , -1])]
    asteroid_center =  [random.random() * WIDTH, random.random() * HEIGHT]
    asteroid_ang_vel = random.random() * random.choice([1 , -1]) * 0.3
    new_sprite = Sprite(asteroid_center, asteroid_vel, 0, asteroid_ang_vel,
                        asteroid_image, asteroid_info)
    if (len(rock_group) < 12) and started and not new_sprite.collide(my_ship):
        rock_group.add(new_sprite)

def process_sprite_group(sprite_set, canvas):
    for sprite in list(sprite_set):
        sprite.draw(canvas)
        if sprite.update():
            sprite_set.remove(sprite)
        
    
def group_collide(group, other_object):
    for sprite in list(group):
        if sprite.collide(other_object):
            group.remove(sprite)
            return True
    return False

def group_group_collide(first_group, second_group):
    global score
    hits = 0
    for sprite1 in list(first_group):
        if group_collide(second_group, sprite1):
            hits += 10
            first_group.discard(sprite1)
    return hits
    
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 3, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
a_missile = Sprite([0, 0], [0,0], 0, 0, missile_image, missile_info, missile_sound)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
