class DimensionError(Exception):
    pass

class Quantity:
    def __init__(self, value, base_unit = (0,0,0,0,0,0,0)):
        self.value = value
        self.base_unit = tuple(base_unit)

    def __eq__(self, other):
        if not isinstance(other, Quantity):
            return False
        return self.value == other.value and self.base_unit == other.base_unit

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Quantity(self.value * other, self.base_unit)

        if isinstance(other, Quantity):
            new_value = self.value * other.value
            new_passport = tuple(u1 + u2 for u1, u2 in zip(self.base_unit, other.base_unit))
            return Quantity(new_value, new_passport)

        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Quantity(self.value / other, self.base_unit)

        if isinstance(other, Quantity):
            new_value = self.value / other.value
            new_passport = tuple(u1 - u2 for u1, u2 in zip(self.base_unit, other.base_unit))
            return Quantity(new_value, new_passport)
            
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            quantity = Quantity(other, (0, 0, 0, 0, 0, 0, 0))
            return quantity / self

        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = Quantity(other)

        if isinstance(other, Quantity):
            if self.base_unit == other.base_unit:
                return Quantity(self.value + other.value, self.base_unit)
            raise DimensionError("Cannot add quantities with different dimensions!")

        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = Quantity(other)

        if isinstance(other, Quantity):
            if self.base_unit == other.base_unit:
                return Quantity(self.value - other.value, self.base_unit)
            raise DimensionError("Cannot subtract quantities with different dimensions!")

        return NotImplemented

    def __neg__(self):
        return Quantity(-self.value, self.base_unit)

    