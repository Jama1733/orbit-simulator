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
    
    def __repr__(self):
        return f"Vector: x: {self.x}, y: {self.y}"

class Body:
    def __init__(self, pos: tuple, mass: int, velocity: Vector, radius: int, color: str) -> None:
        # body position is x,y
        self.x = pos[0]
        self.y = pos[1]
        self.mass = mass
        self.velocity = velocity
        self.radius = radius
        self.color = color

    # return distance to other body
    def distance_to(self, body2):
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
    
    def __repr__(self):
        return f"Body: x: {self.x}, y: {self.y}, mass: {self.mass}, velocity: {self.velocity}"
