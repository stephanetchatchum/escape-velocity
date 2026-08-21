class DimensionError(Exception):
    pass

prefixes = {
    'Q': 10**30, # Quetta (1 nonillion)
    'R': 10**27, # Ronna (1 octillion)
    'Y': 10**24, # Yotta (1 septillion)
    'Z': 10**21, # Zetta (1 sextillion)
    'E': 10**18, # Exa (1 quintillion)
    'P': 10**15, # Peta (1 quadrillion)
    'T': 10**12, # Tera (1 trillion)
    'G': 10**9, # Giga (1 billion)
    'M': 10**6, # Mega (1 million)
    'k': 10**3, # Kilo (1 thousand)
    'h': 10**2, # Hecta (1 hundred)
    'da': 10**1, # Deca (10)
    'd': 10**-1, # Deci (0.1)
    'c': 10**-2, # Centi (0.01)
    'm': 10**-3, # Milli (0.001)
    'μ': 10**-6, # Micro (1 millionth)
    'n': 10**-9, # Nano (1 billionth)
    'p': 10**-12, # Pico (1 trillionth)
    'f': 10**-15, # Femto (1 quadrillionth)
    'a': 10**-18, # Atto (1 quintillionth)
    'z': 10**-21, # Zepto (1 sextillionth)
    'y': 10**-24, # Yocto (1 septillionth)
    'r': 10**-27, # Ronto (1 octillionth)
    'q': 10**-30, # Quecto (1 nonillionth)
}

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

    def __pow__(self, power):
        return Quantity(self.value ** power, tuple(u * power for u in self.base_unit))


BASE_UNITS = {
    'm'  : Quantity(1, (1,0,0,0,0,0,0)), # length (Metres)
    'kg' : Quantity(1, (0,1,0,0,0,0,0)), # mass (Kilograms)
    's'  : Quantity(1, (0,0,1,0,0,0,0)), # time (Seconds)
    'I'  : Quantity(1, (0,0,0,1,0,0,0)), # Electric current (Amperes)
    'K'  : Quantity(1, (0,0,0,0,1,0,0)), # Thermodynamic Temperature (Kelvin)
    'mol': Quantity(1, (0,0,0,0,0,1,0)), # Amount of substance (Mole)
    'cd' : Quantity(1, (0,0,0,0,0,0,1)),  # Luminous intensity (Candela)

    'g'  : Quantity(0.001, (0,1,0,0,0,0,0)) # mass (Grams)
}

COMPOUND_UNITS = {
    'N' : Quantity(1, (1,1,-2,0,0,0,0)),  # Force (Newton)
    'J' : Quantity(1, (2,1,-2,0,0,0,0)),  # Energy (Joule)
    'W' : Quantity(1, (2,1,-3,0,0,0,0)),  # Power (Watt)
    'Pa' : Quantity(1, (-1,1,-2,0,0,0,0)),# Pressure (Pascal)
    'C' : Quantity(1, (0,0,1,1,0,0,0)),   # Electric Charge (Coulomb)
    'V' : Quantity(1, (2,1,-3,-1,0,0,0)), # Electric Potential (Volt)
    'Ω' : Quantity(1, (1,2,-3,-2,0,0,0)), # Electric Resistance (Ohm)
    'T' : Quantity(1, (0,1,-2,-1,0,0,0)), # Magnetic Field (Tesla)
    'Hz' : Quantity(1, (0,0,-1,0,0,0,0)), # Frequency (Hertz)

    'au' : Quantity(1.495978707*(10**11), (1,0,0,0,0,0,0)), # Astronamical Unit
    'ly' : Quantity(9.4607304725808*(10**15), (1,0,0,0,0,0,0)), # Light Year
    'pc' : Quantity(3.08567758149137*(10**16), (1,0,0,0,0,0,0)), # Parsec
}

KNOWN_UNITS = {**BASE_UNITS, **COMPOUND_UNITS}

REVERSE_LOOKUP = {
    (1,0,0,0,0,0,0): 'm',
    (0,1,0,0,0,0,0): 'kg',
    (0,0,1,0,0,0,0): 's',
    (0,0,0,1,0,0,0): 'I',
    (0,0,0,0,1,0,0): 'K',
    (0,0,0,0,0,1,0): 'mol',
    (0,0,0,0,0,0,1): 'cd',
    (1,1,-2,0,0,0,0): 'N',
    (2,1,-2,0,0,0,0): 'J',
    (2,1,-3,0,0,0,0): 'W',
    (-1,1,-2,0,0,0,0): 'Pa',
    (0,0,1,1,0,0,0): 'C',
    (2,1,-3,-1,0,0,0): 'V',
    (2,1,-3,-2,0,0,0): 'Ω',
    (0,1,-2,-1,0,0,0): 'T',
    (0,0,-1,0,0,0,0): 'Hz',
}

def parse_unit(unit_str):
    if unit_str in KNOWN_UNITS:
        return KNOWN_UNITS[unit_str]

    for prefix, scale in prefixes.items():
        if unit_str.startswith(prefix):
            u = unit_str[len(prefix):]
            if u in KNOWN_UNITS:
                return scale * KNOWN_UNITS[u]

    raise ValueError(f"Unknown unit: {unit_str}")
    