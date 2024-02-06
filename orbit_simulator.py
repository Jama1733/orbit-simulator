import pygame
import pygame_menu
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

# set up variables for slowing the progression of time
counter = 0
wait = 1

# speed slider setup
default_speed = 10
max_speed = 10
def speed_slider_change(value):
    global wait
    diff = max_speed - value
    wait = round(diff) + 1
menu.add.range_slider("Speed of time", default_speed, (0, max_speed), 1, speed_slider_change, font_size=slider_font_size, width=slider_width, align=left)

# G slider setup
def G_slider_change(value):
    global G
    global frames_list
    G = value
    frames_list = []
G_min = 0
G_max = 10
G = 1
menu.add.range_slider("Gravitational Constant G", 1, (G_min, G_max), 1, G_slider_change, font_size=slider_font_size, width=slider_width, align=left)

# setup toggle switch for toggling body paths
default_paths = False
def paths_toggle_change(value):
    global paths
    if value == "Off": paths = False
    else: paths = True
menu.add.toggle_switch("Body paths", default_paths, paths_toggle_change, state_values=("Off", "On"), font_size=slider_font_size, align=left)

# body path length slider setup
default_paths_length = 1
max_paths_length = 20
def paths_length_change(value):
    global paths_length
    paths_length = round(value*FPS)
menu.add.range_slider("Path length", default_paths_length, (1/FPS, max_paths_length), 1, paths_length_change, width=slider_width, align=left, font_size=slider_font_size)

# set up variables for path generation
paths = default_paths
paths_length = FPS*default_paths_length
frames = FPS*max_paths_length
frames_list = []

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
bodies.append(b3)

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
            new_object = Body(mouse_pos, 10, Vector(0,0), 10, next(body_color))
            bodies.append(new_object)
            object_created = True
            frames_list=[]
        else:
            create_new_object = False

    # always make sure there is a frames list to be rendered so it doesn't skip
    if frames_list == []:
        frames_list = generate_frames_list(bodies, G, frames)
    # only apply forces and transition frames if the game is not paused and every wait frames
    if pause == False and counter%wait==0:
        # generate frames list if necessary
        # generate next frame from the last element of the list and add it to the end
        next_frame = generate_next_frame(frames_list[-1], G)
        frames_list.append(next_frame)
        # pop off first frame and use it
        current_frame = frames_list.pop(0)
        bodies = current_frame

    # draw bodies and then body paths
    for frame in frames_list[:paths_length]:
        # draw bodies
        for body in frames_list[0]:
            pygame.draw.circle(screen, body.color, (body.x, body.y), body.radius)
        # draw paths only if paths is True
        if paths == False: break
        for body in frame:
                pygame.draw.circle(screen, body.color, (body.x, body.y), 1)

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