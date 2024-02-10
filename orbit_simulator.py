import pygame
import pygame_menu
from numpy import add, subtract
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
menu_height = 500
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

# set up toggle switch for toggling body paths
default_paths = False
def paths_toggle_change(value):
    global paths
    if value == "Off": paths = False
    else: paths = True
menu.add.toggle_switch("Body paths", default_paths, paths_toggle_change, state_values=("Off", "On"), font_size=slider_font_size, align=left)

# set up toggle switch for collisions
collision_strength = 1
default_collisions = True
collisions = default_collisions
def change_collisions(value):
    global collisions
    collisions = not collisions
menu.add.toggle_switch("Collisions", default_collisions, change_collisions, state_values=("Off", "On"), font_size= slider_font_size, align = left)

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

# set up button to center system
# center diff represents the offset of the bodies' true positions from their visual position on the screen
screen_center= (screen_width//2, screen_height//2)
current_center = screen_center
center_diff = (0, 0)
def center_by_position():
    global center
    global center_diff
    global current_center
    average_x = 0
    average_y = 0
    l = len(bodies)
    for body in bodies:
        average_x += body.x
        average_y += body.y
    average_x /= l
    average_y /= l
    center_diff = (average_x - screen_center[0], average_y - screen_center[1])
    current_center = (screen_center[0] + center_diff[0], screen_center[1] + center_diff[1])
menu.add.button("Center system by position", center_by_position, align = left, font_size = slider_font_size)

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

# set up variables for zoom functionality
scale = 1
scale_min = 0
scale_max = 5
scale_decrease_factor = 0.8
scale_increase_factor = 1.2

# set up variables for screen dragging
drag = False
previous_mouse_pos = (0,0)
current_mouse_pos = (0,0)

while running:
    # poll for events
    events = pygame.event.get()
    for event in events:
    # check for user clicking X on window and end program
        if event.type == pygame.QUIT:
            running = False
        # drag the screen if they click and drag
        if event.type ==  pygame.MOUSEBUTTONDOWN and event.button == 1 and not(menu.is_enabled() and event.pos < (menu_width, menu_height)):
            # every time they click this button a new previous must be set at that position
            drag_counter = 0
            drag = True
        if event.type ==  pygame.MOUSEBUTTONUP and event.button == 1:
            drag = False
        # only start body creation sequence if they click and a new one isn't being created
        if event.type ==  pygame.MOUSEBUTTONDOWN and create_new_object == False and event.button == 3:
            # this is for use in determining where it is on the screen
            actual_mouse_pos = event.pos
            # get distances from center of the screen
            x_from_center = actual_mouse_pos[0] - screen_center[0]
            y_from_center = actual_mouse_pos[1] - screen_center[1]
            # scale out the distance from the center of the screen so that if scale is small(zoomed out), then the distance is larger
            # and vice versa when the scale is large and zoomed in, the distance is smaller
            # then translate it to the current center
            mouse_pos = x_from_center/scale + current_center[0], y_from_center/scale + current_center[1]
            # if the menu is enabled and the mouse is on it then don't start new object creation
            if not(menu.is_enabled() and event.pos < (menu_width, menu_height)):
                create_new_object = True
        # zoom funtionality
        if event.type == pygame.MOUSEWHEEL:
            movement = event.y
            # allowing the scale to be adjusted multiplicatively means it can be arbitrarily small or large. really cool for a sense of scale
            if movement > 0 and scale < scale_max:
                scale *= scale_increase_factor
            if movement < 0 and scale > scale_min:
                scale *= scale_decrease_factor
        if event.type == pygame.KEYDOWN:
            # the esc key opens and closes the menu
            key = event.key
            if key == 27:
                if menu.is_enabled():
                    menu.disable()
                else:
                    menu.enable()
            # r restarts the program by resetting bodies
            if key == 114:
                counter = 0
            # press space to pause
            if key == 32:
                pause = not pause

    # do dragging if drag is true
    if drag:       
        if drag_counter == 0:
            previous_mouse_pos = event.pos
        current_mouse_pos = event.pos
        mouse_pos_diff = subtract(previous_mouse_pos, current_mouse_pos)
        mouse_pos_diff = mouse_pos_diff[0]/scale, mouse_pos_diff[1]/scale
        current_center = add(current_center, mouse_pos_diff)
        drag_counter += 1
        previous_mouse_pos = current_mouse_pos
    
    # set up bodies for test only on the first frame
    if counter == 0:
        bodies = []
        frames_list = []
        v1 = Vector(10,0)
        b1 = Body((640, 160), 10, v1, 10, "blue")
        v2 = Vector(0,0)
        b2 = Body((640, 360), 100, v2, 20, "green")
        v3 = Vector(-10,0)
        b3 = Body((640, 560), 10, v3, 10, "red")
        bodies.append(b1)
        bodies.append(b2)
        bodies.append(b3)


    # fill the screen with a color to wipe away anything from last frame
    screen.fill(background_color)

    # render text telling user to click anywhere to create new body
    screen.blit(click_anywhere_text, click_anywhere_text_rect)

    # handle body creation
    if create_new_object == True:
        # if the body hasn't been generated then do it
        if object_created == False:
            new_object = Body(mouse_pos, 10, Vector(0,0), 10, next(body_color))
            bodies.append(new_object)
            object_created = True
            frames_list=[]
        else:
            create_new_object = False

    # check for collisions
    collision_occured = False
    collision_accelerations = {body: Vector(0,0) for body in bodies}
    i = 0
    if collisions and len(bodies) > 1:
        for body1 in bodies[:-1]:
            for body2 in bodies[1+i:]:
                if body1.distance_to(body2) >= body1.radius + body2.radius:
                    continue
                collision_occured = True
                body1_to_body2 = body1.unit_vector_towards(body2)
                body2_to_body1 = body2.unit_vector_towards(body1)
                force_on_body1 = body2.velocity * body2.mass
                force_on_body2 = body1.velocity * body1.mass
                acceleration_on_body1 = force_on_body1/body1.mass
                acceleration_on_body2 = force_on_body2/body2.mass
                collision_accelerations[body1] += collision_strength * acceleration_on_body1
                collision_accelerations[body2] += collision_strength * acceleration_on_body2
            i += 1
    # apply collision velocities and reset frames list
    if collision_occured:
        frames_list = []
        for body in bodies:
            body.velocity += collision_accelerations[body]

    # always make sure there is a frames list to be rendered so it doesn't skip
    # anything that sets the frame list to [] is going to recalculate the body paths
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
            # get the body's distance from the current center 
            # scale that up or down
            # then translate that to the center of the screen
            x = scale * (body.x - current_center[0]) + screen_center[0]
            y = scale * (body.y - current_center[1]) + screen_center[1]
            pygame.draw.circle(screen, body.color, (x, y), body.radius * scale)
        # draw paths only if paths is True
        if paths == False: break
        for body in frame:
                x = scale * (body.x - current_center[0]) + screen_center[0]
                y = scale * (body.y - current_center[1]) + screen_center[1]
                pygame.draw.circle(screen, body.color, (x, y), 1)

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