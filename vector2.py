class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if other.__class__ != Vector2:
            raise TypeError
        return Vector2(self.x + other.x, self.y + other.y)

    def __rmul__(self, other):
        if other.__class__ != int:
            raise TypeError
        return Vector2(self.x * other, self.y * other)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()