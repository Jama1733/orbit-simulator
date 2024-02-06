import pygame
import pygame_menu
import os, sys
from orbit_simulator_classes import Vector, Body, generate_frames_list, generate_next_frame

# pygame setup
pygame.init()
screen_width = 1500
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
FPS = 60
black = (0, 0, 0)
background_color = black
running = True

# text setup
font = pygame.font.SysFont("timesnewroman", 25)
text_color = "white"

click_anywhere_text = font.render("Click anywhere to create a new body", True, text_color, background_color)
click_anywhere_text_rect = click_anywhere_text.get_rect()
click_anywhere_text_rect.center = (screen_width//2, screen_height - 10)

body_creation_text = font.render("Scroll to adjust size\nUse + and - to change mass", True, text_color, background_color)
body_creation_text_rect = body_creation_text.get_rect()

# pygame menu setup
menu_width = 400
menu_height = 200
theme = pygame_menu.themes.Theme(background_color=background_color, border_color=black)
menu = pygame_menu.Menu('Menu', menu_width, menu_height, position=(0,0), surface=screen, theme=theme)

# slider setup
slider_font_size=15
slider_width=150
left = pygame_menu.locals.ALIGN_LEFT

# set up variables for slowing the program
counter = 0
wait = 1

# speed slider setup
def speed_slider_change(value):
    global wait
    adjusted_value = value-1
    adjusted_value = round(FPS-adjusted_value)
    wait = adjusted_value
menu.add.range_slider("Speed of time", FPS, (0, FPS), 1, speed_slider_change, font_size=slider_font_size, width=slider_width, align=left)

# G slider setup
def G_slider_change(value):
    global G
    G = value
G_min = 0
G_max = 10
G = 1
menu.add.range_slider("Gravitational Constant G", 1, (G_min, G_max), 1, G_slider_change, font_size=slider_font_size, width=slider_width, align=left)

# create generator for body colors
# cycles through the color list
def body_color_generator():
    index = 0
    color_list = ["red", "orange", "yellow", "green", "blue", "purple", "pink"]
    while True:
        yield color_list[index]
        if index < len(color_list)-1:
            index += 1
        else:
            index = 0
body_color = body_color_generator()

# set up booleans for body generation
create_new_object = False
object_created = False
pause = False

# set up frames list
frames = FPS
frames_list = []

# set up bodies for test
bodies = []
v1 = Vector(10,0)
b1 = Body((640, 160), 10, v1, 10, "blue")
v2 = Vector(0,0)
b2 = Body((640, 360), 100, v2, 20, "green")
v3 = Vector(-10,0)
b3 = Body((640, 560), 10, v3, 10, "red")
bodies.append(b1)
bodies.append(b2)
# bodies.append(b3)

while running:
    # poll for events
    events = pygame.event.get()
    for event in events:
    # check for user clicking X on window and end program
        if event.type == pygame.QUIT:
            running = False
        # only start body creation sequence if they click and a new one isn't being created
        if event.type ==  pygame.MOUSEBUTTONDOWN and create_new_object == False:
            mouse_pos = event.pos
            # if the menu is enabled and the mouse is on it then don't start new object creation
            if not(menu.is_enabled() and mouse_pos[0]<menu_width and mouse_pos[1]<menu_height):
                button = event.button
                if button == 1:
                    create_new_object = True
                    object_created = False
                    pause = False
        if event.type == pygame.KEYDOWN:
            # the esc key opens and closes the menu
            key = event.key
            if key == 27:
                if menu.is_enabled():
                    menu.disable()
                else:
                    menu.enable()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(background_color)

    # render text telling user to click anywhere to create new body
    screen.blit(click_anywhere_text, click_anywhere_text_rect)

    # handle body creation
    if create_new_object == True:
        if object_created == False:
            new_object = Body(mouse_pos, 50, Vector(0,0), 10, next(body_color))
            bodies.append(new_object)
            object_created = True
        else:
            create_new_object = False

    # draw bodies and then body paths
    for frame in frames_list:
        if frame == frames_list[0]:
            for body in frame:
                pygame.draw.circle(screen, body.color, (body.x, body.y), body.radius)
        else:
            print('frame')
            for body in frame:
                pygame.draw.circle(screen, body.color, (body.x, body.y), 1)
    
    # draw bodies
    # for body in bodies:
    #     pygame.draw.circle(screen, body.color, (body.x, body.y), body.radius)

    # only apply forces if the game is not paused
    if pause == False and counter%wait==0:
        # generate frames list if necessary
        if frames_list == []:
            frames_list = generate_frames_list(bodies, G, frames)
            # for f in frames_list:
            #     for b in f:
            #         print(b)
            # print()
        # generate next frame from the last element of the list and add it to the end
        next_frame = generate_next_frame(frames_list[-1], G)
        frames_list.append(next_frame)
        # pop off first frame and use it
        current_frame = frames_list.pop(0)
        bodies = current_frame


    # debugging code
    """
    # try to draw velocity vectors on screen for debugging purposes
    scale = 10
    for body in bodies:
        line_v = accelerations[body] * scale
        pygame.draw.line(screen, 'red', (body.x, body.y), (body.x + line_v.x, body.y + line_v.y), width= 3)
    
    # test unit vector creator
    scale = 100
    b3 = Body((350,350),0,Vector(0,0),20,'red')
    b4 = Body(pygame.mouse.get_pos(), 0, Vector(0,0), 20, 'red')
    unit_vector = b3.unit_vector_towards(b4) * scale
    pygame.draw.line(screen, 'red', (b3.x, b3.y), (b3.x+unit_vector.x, b3.y+unit_vector.y))
    """

    # menu updating
    if menu.is_enabled():
        menu.update(events)
        menu.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.update()
    pygame.display.flip()

    # limits FPS to FPS
    clock.tick(FPS)  

    # increment counter to slow the program by wait
    counter+=1

pygame.quit()