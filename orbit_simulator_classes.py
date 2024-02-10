import math

pi = math.pi
sqrt = math.sqrt
sin = math.sin
cos = math.cos
asin = math.asin
acos = math.acos
atan = math.atan

class Vector:
    def __init__(self, x : int, y : int) -> None:
        self.x = x
        self.y = y

    def __add__(self, v):
        v.x += self.x
        v.y += self.y
        return v
    
    def __sub__(self, v):
        v.x -= self.x
        v.y -= self.y
        return v
    
    def __mul__(self, i : int):
        self.x *= i
        self.y *= i
        return self
    
    def __rmul__(self, i : int):
        self.x *= i
        self.y *= i
        return self
    
    def __truediv__(self, i : int):
        self.x = round(self.x/i)
        self.y = round(self.y/i)
        return self
    
    def __repr__(self) -> str:
        return f"Vector: x: {self.x}, y: {self.y}"
    
    def inverse(self):
        return(Vector(self.x*-1, self.y*-1))
    
    def magnitude(self) -> float:
        return sqrt(self.x**2+self.y**2)
    
    def angle(self) -> float:
        v = self.magnitude()
        if self.y >= 0:
            return asin(self.y/v)
        else:
            return asin(self.y/v) + pi

class Body:
    def __init__(self, pos: tuple, mass: int, velocity: Vector, radius: int, color: str) -> None:
        # body position is x,y
        self.x = pos[0]
        self.y = pos[1]
        self.mass = mass
        self.velocity = velocity
        self.radius = radius
        self.color = color

    def __repr__(self):
        return f"Body: x: {self.x}, y: {self.y}, mass: {self.mass}, velocity: {self.velocity}"
    
    # return distance to other body
    def distance_to(self, body2) -> float:
        x2, y2 = body2.x, body2.y
        # x and y distances between objects
        x_diff = self.x - x2
        y_diff = self.y - y2
        # calculate distance using pythagorus
        distance = sqrt(x_diff**2 + y_diff**2)
        return distance

    def unit_vector_towards(self, body) -> Vector:
        a = body.x - self.x
        b = body.y - self.y
        c = sqrt(a**2 + b**2)
        theta = asin(b/c)
        # have to account for when a is negative because asin(b/c) is the same for positive and negative a
        if a < 0:
            a_sign = -1
        else:
            a_sign = 1
        unit_vector = Vector(cos(theta) * a_sign, sin(theta))
        return unit_vector


# get acceleration vectors on each body due to gravity
def acceleration_vectors(body1, body2, G) -> tuple[Vector]:
    # get masses
    mass1 = body1.mass
    mass2 = body2.mass
    # find distance between new_bodies
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

    return acceleration_vector1, acceleration_vector2

# take in a list of bodies and apply all of the appropriate forces to their current velocities and then adjust positions to get next frame of new_bodies
def generate_next_frame(bodies: list, G) -> list[Body]:
    # can't use bodies because it's passed by reference
    # learned that the hard way LMAO couldn't figure out how the simulator was working without the frames list working: bodies was being modified in place!!!
    # can't reassign it because it keeps the references
    # can't use .copy() because it still keeps the refernces to the body objects what a mess

    # go through and reinitialize every body in the frame as a new object with a new refernce because wtf
    new_bodies = []
    for body in bodies:
        new_body = Body((body.x, body.y), body.mass, body.velocity, body.radius, body.color)
        new_bodies.append(new_body)

    # set up accelerations set with 0 accelerations on every body to start
    accelerations = {body: Vector(0,0) for body in new_bodies}
    l = len(new_bodies)
    # for each body in the system, look at every body past it in the list and apply its gravitational force to the combined acceleration
    # this should cover every pair of interacting bodies
    for i in range(l-1):
        # get values for first body
        body1 = new_bodies[i]
        mass1 = body1.mass
        # go through the rest in the list
        for j in range(i+1, l):
            # for each first body get values for each one after it
            body2 = new_bodies[j]
            # get acceleration vectors from function
            acceleration_vector1, acceleration_vector2 = acceleration_vectors(body1, body2, G)
            # take current acceleration vector from all other bodies and add calulated acceleration vector to it
            accelerations[body1] = accelerations[body1] + acceleration_vector1
            accelerations[body2] = accelerations[body2] + acceleration_vector2
            
    # apply accelerations to each body by changing velocity
    for body in new_bodies:
        body.velocity += accelerations[body]
    # apply velocities to each body by changing position
    for body in new_bodies:
        body.x += body.velocity.x
        body.y += body.velocity.y
    return new_bodies

# generate list of n frames into the future
# each list of frames is a list of new_bodies in that frame 
def generate_frames_list(bodies: list, G,  n: int) -> list[list[Body]]:
    # set up frames list and generate first frame to be used for the rest
    frames_list = []
    frames_list.append(generate_next_frame(bodies, G))
    # for as many frames as n, look at the last item of the list and generate the next frame from it and add it to the list
    for i in range(n):
        previous = frames_list[-1]
        frames_list.append(generate_next_frame(previous, G))
    return frames_list