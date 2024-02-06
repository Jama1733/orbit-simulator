import pygame
import pygame_menu
from orbit_simulator_classes import Body, Vector

# pygame setup
pygame.init()
screen_width = 1500
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
FPS = 30
black = (0, 0, 0)
background_color = black
running = True

# pygame menu setup
menu_width = 400
menu_height = 100
theme = pygame_menu.themes.Theme(background_color=background_color, border_color=black)
menu = pygame_menu.Menu('Menu', menu_width, menu_height, position=(0,0), surface=screen, theme=theme)

# text setup
font = pygame.font.SysFont("timesnewroman", 25)
text_color = "white"

click_anywhere_text = font.render("Click anywhere to create a new body", True, text_color, background_color)
click_anywhere_text_rect = click_anywhere_text.get_rect()
click_anywhere_text_rect.center = (screen_width//2, screen_height - 10)

body_creation_text = font.render("Scroll to adjust size\nUse + and - to change mass", True, text_color, background_color)
body_creation_text_rect = body_creation_text.get_rect()

# slider setup
slider_font_size=10
left = pygame_menu.locals.ALIGN_LEFT

# G slider setup
def G_slider_change(value):
    global G
    G = value
G_min = 0
G_max = 10
G = 1
menu.add.range_slider("Gravitational Constant G", 1, (G_min, G_max), 1, G_slider_change, font_size=slider_font_size, width=150, align=left)

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

# set up variables for slowing the program
counter = 0
wait = 1

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
            # if the menu is enabled and the mouse is on it do nothing
            # if the menu is disabled or the mouse isn't on it then start body creation
            if menu.is_enabled() and mouse_pos[0]<menu_width and mouse_pos[1]<menu_height:
                pass
            else:
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

    # gravitational constant

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(background_color)

    # render text telling user to click anywhere to create new body
    screen.blit(click_anywhere_text, click_anywhere_text_rect)

    # draw bodies
    for body in bodies:
        pygame.draw.circle(screen, body.color, (body.x, body.y), body.radius)

    # handle body creation
    if create_new_object == True:
        if object_created == False:
            new_object = Body(mouse_pos, 50, Vector(0,0), 10, next(body_color))
            bodies.append(new_object)
            object_created = True
        else:
            create_new_object = False

    # only apply forces if the game is not paused 
    if pause == False and counter%wait==0:
        # set up accelerations set with 0 accelerations on every body to start
        accelerations = {body: Vector(0,0) for body in bodies}
        l = len(bodies)
        # for each body in the system, look at every body past it in the list and apply its gravitational force to the combined acceleration
        # this should cover every pair of interacting bodies
        for i in range(l-1):
            # get values for first body
            body1 = bodies[i]
            mass1 = body1.mass
            # go through the rest in the list
            for j in range(i+1, l):
                # for each first body get values for each one after it
                body2 = bodies[j]
                mass2 = body2.mass
                # find distance between bodies
                distance = body1.distance_to(body2)
                # find magnitudes of force vectors on each body
                acceleration_magnitude1 = G*mass2/(distance)
                acceleration_magnitude2 = G*mass1/(distance)
                # get unit vectors in direction of other body for each one
                unit_vector1 = body1.unit_vector_towards(body2)
                unit_vector2 = body2.unit_vector_towards(body1)
                # create acceleration vectors by scaling unit vectors
                acceleration_vector1 = acceleration_magnitude1 * unit_vector1
                acceleration_vector2 = acceleration_magnitude2 * unit_vector2
                # take current acceleration vector from all other bodies and add calulated acceleration vector to it
                accelerations[body1] = accelerations[body1] + acceleration_vector1
                accelerations[body2] = accelerations[body2] + acceleration_vector2
            #for k,v in accelerations.items(): print(k,'\n', v, '\n')
                

        # apply accelerations to each body
        for body in bodies:
            body.velocity = body.velocity + accelerations[body]
        # apply velocities to each body
        for body in bodies:
            body.x += body.velocity.x
            body.y += body.velocity.y

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

    # menu mainloop
    if menu.is_enabled():
        menu.update(events)
        menu.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.update()
    pygame.display.flip()

    # limits FPS to 60
    clock.tick(FPS)  

    # increment counter to slow the program by wait
    counter+=1

pygame.quit()