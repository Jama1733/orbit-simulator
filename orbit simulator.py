import pygame
from orbit_simulator_classes import Body, Vector
import math
pi = math.pi
sqrt = math.sqrt
sin = math.sin
cos = math.cos
asin = math.asin
acos = math.acos
atan = math.atan

# pygame setup
pygame.init()
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
FPS = 30
background_color = "black"
running = True

# gravitational constant
G = 1

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
    for event in pygame.event.get():
    # check for user clicking X on window and end program
        if event.type == pygame.QUIT:
            running = False


    # fill the screen with a color to wipe away anything from last frame
    screen.fill(background_color)


    # RENDER YOUR GAME HERE
    # draw bodies
    for body in bodies:
        pygame.draw.circle(screen, body.color, (body.x, body.y), body.radius)

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

    # apply accelerations to each body
    for body in bodies:
        body.velocity = body.velocity + accelerations[body]
    # apply velocities to each body
    for body in bodies:
        body.x += body.velocity.x
        body.y += body.velocity.y

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    clock.tick(FPS)  

pygame.quit()