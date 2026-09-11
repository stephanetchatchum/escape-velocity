"""
evkit.units
-----------
A physical quantity is a number glued to a "shape" (its dimensions).
Two quantities can only be added/compared if their shapes match; they
can always be multiplied/divided, and the resulting shape falls out
of the arithmetic itself — nothing is hardcoded as "this is force."

Dimensions are a 7-tuple of exponents, one per SI base dimension, in
this fixed order:
    (length, mass, time, current, temperature, amount, luminosity)

Exponents are stored as fractions.Fraction so sqrt(area) gives an
*exact* length exponent instead of a float that might drift after
repeated operations.
"""

import re                      # used to parse unit strings like 'm/s2'
from fractions import Fraction # exact rational exponents (see __pow__)


class DimensionError(Exception):
    """Raised when quantities with incompatible dimensions are combined."""
    pass


# --------------------------------------------------------------------------
# SI prefixes: symbol -> multiplicative factor.
# e.g. 'k' means "multiply by 1000" so 'km' = 1000 * (1 metre).
# --------------------------------------------------------------------------
prefixes = {
    'Q': 10**30,   # Quetta
    'R': 10**27,   # Ronna
    'Y': 10**24,   # Yotta
    'Z': 10**21,   # Zetta
    'E': 10**18,   # Exa
    'P': 10**15,   # Peta
    'T': 10**12,   # Tera
    'G': 10**9,    # Giga
    'M': 10**6,    # Mega
    'k': 10**3,    # Kilo
    'h': 10**2,    # Hecto
    'da': 10**1,   # Deca   -- two letters, must be checked before 'd'
    'd': 10**-1,   # Deci
    'c': 10**-2,   # Centi
    'm': 10**-3,   # Milli
    'μ': 10**-6,   # Micro
    'n': 10**-9,   # Nano
    'p': 10**-12,  # Pico
    'f': 10**-15,  # Femto
    'a': 10**-18,  # Atto
    'z': 10**-21,  # Zepto
    'y': 10**-24,  # Yocto
    'r': 10**-27,  # Ronto
    'q': 10**-30,  # Quecto
}

# Sort prefix symbols longest-first. Without this, checking 'd' before
# 'da' would misparse "deca-something" as "deci-a-something".
_PREFIXES_BY_LENGTH = sorted(prefixes.keys(), key=len, reverse=True)

# Human-readable names for each slot of the 7-tuple, in the same order
# the tuple uses. Mostly useful for documentation/debugging.
DIM_NAMES = ('length', 'mass', 'time', 'current', 'temperature', 'amount', 'luminosity')

# The dimension vector for a plain number (no units at all).
ZERO_DIMS = tuple(Fraction(0) for _ in range(7))

# Symbol order used when we fall back to printing raw dimensions,
# e.g. an acceleration with no named unit prints as "m·s^-2".
_BASE_SYMBOLS = ('m', 'kg', 's', 'A', 'K', 'mol', 'cd')


def _to_dims(exponents):
    # Converts a plain tuple of ints/floats into a tuple of Fractions,
    # so every Quantity's base_unit is guaranteed to hold Fractions.
    return tuple(Fraction(e) for e in exponents)


class Quantity:
    # __slots__ fixes the exact set of attributes an instance can have
    # (just value and base_unit) — saves memory and catches typos like
    # self.vlaue = ... at definition time instead of silently creating
    # a stray attribute.
    __slots__ = ('value', 'base_unit')

    def __init__(self, value, unit=ZERO_DIMS):
        """
        `unit` may be either:
          - a unit string such as 'm', 'kg', 'm/s2', 'km/h', 'N', or
          - a 7-tuple of exponents (internal/advanced use — `value` is
            then assumed to already be expressed in coherent SI units).
        """
        if isinstance(unit, str):
            # String path: figure out (a) how to scale the raw number
            # into SI base units, and (b) what dimension tuple results.
            scale, dims = parse_unit_string(unit)
            self.value = float(value) * scale
            self.base_unit = dims
        elif isinstance(unit, tuple):
            # Tuple path: trust the caller, just store it (as Fractions).
            self.value = float(value)
            self.base_unit = _to_dims(unit)
        else:
            raise TypeError(f"unit must be a string or a 7-tuple, got {type(unit).__name__}")

    # -- dimension helpers ----------------------------------------------

    @property
    def is_dimensionless(self):
        # True for things like Quantity(5, 'm') / Quantity(1, 'm')
        return self.base_unit == ZERO_DIMS

    def _unit_label(self):
        # Decide what string to show for this quantity's shape.
        if self.base_unit == ZERO_DIMS:
            return ''  # no unit at all — just print the number
        if self.base_unit in REVERSE_LOOKUP:
            return REVERSE_LOOKUP[self.base_unit]  # named unit, e.g. 'N'
        return _format_dims(self.base_unit)  # fallback, e.g. 'm·s^-2'

    def to(self, unit_str):
        """Return this quantity's numeric value expressed in `unit_str`."""
        scale, dims = parse_unit_string(unit_str)
        if dims != self.base_unit:
            # Can't convert metres into seconds, no matter the scale.
            raise DimensionError(
                f"Cannot convert {self._unit_label() or 'dimensionless'} "
                f"to '{unit_str}': incompatible dimensions"
            )
        # self.value is already in SI base units; dividing by `scale`
        # (how many base units 1 of unit_str equals) undoes that scaling.
        return self.value / scale

    # -- equality / ordering (dimension-aware) ---------------------------

    def __eq__(self, other):
        # NotImplemented (not False!) tells Python to try other.__eq__
        # if `other` isn't a Quantity at all — normal Python protocol.
        if not isinstance(other, Quantity):
            return NotImplemented
        if self.base_unit != other.base_unit:
            # Different shapes are just never equal — this does NOT raise,
            # matching how Python expects == to behave (never throw).
            return False
        return self.value == other.value

    def _require_same_dims(self, other, verb):
        # Shared guard used by add/sub/compare — raises with a message
        # that names both units so the error is actually debuggable.
        if not isinstance(other, Quantity):
            raise TypeError(f"Cannot {verb} a Quantity with {type(other).__name__}")
        if self.base_unit != other.base_unit:
            raise DimensionError(
                f"Cannot {verb} quantities with different dimensions: "
                f"{self._unit_label() or 'dimensionless'} vs "
                f"{other._unit_label() or 'dimensionless'}"
            )

    def __lt__(self, other):
        self._require_same_dims(other, "compare")
        return self.value < other.value

    def __le__(self, other):
        self._require_same_dims(other, "compare")
        return self.value <= other.value

    def __gt__(self, other):
        self._require_same_dims(other, "compare")
        return self.value > other.value

    def __ge__(self, other):
        self._require_same_dims(other, "compare")
        return self.value >= other.value

    # -- arithmetic ---------------------------------------------------------

    def __add__(self, other):
        if isinstance(other, (int, float)):
            # Treat a bare number as a dimensionless Quantity so the
            # dimension check below still applies (and will correctly
            # reject "5 metres + 3" as an error).
            other = Quantity(other)
        if isinstance(other, Quantity):
            self._require_same_dims(other, "add")
            # Both values are already in SI base units, so no unit
            # conversion is needed here — just add the raw numbers.
            return Quantity(self.value + other.value, self.base_unit)
        return NotImplemented

    __radd__ = __add__  # addition is commutative: 5 + Quantity(...) works too

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = Quantity(other)
        if isinstance(other, Quantity):
            self._require_same_dims(other, "subtract")
            return Quantity(self.value - other.value, self.base_unit)
        return NotImplemented

    def __rsub__(self, other):
        # Handles `5 - Quantity(...)` (subtraction isn't commutative,
        # so this can't just alias __sub__ like __radd__ does).
        if isinstance(other, (int, float)):
            return Quantity(other) - self
        return NotImplemented

    def __neg__(self):
        return Quantity(-self.value, self.base_unit)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            # Scaling by a bare number never changes the shape.
            return Quantity(self.value * other, self.base_unit)
        if isinstance(other, Quantity):
            new_value = self.value * other.value
            # This is the whole trick: multiplying quantities ADDS their
            # dimension tuples elementwise. (1,0,-2,..) + (0,1,0,..) = force.
            new_dims = tuple(a + b for a, b in zip(self.base_unit, other.base_unit))
            return Quantity(new_value, new_dims)
        return NotImplemented

    __rmul__ = __mul__  # multiplication is commutative: 3 * Quantity(...) works

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Quantity(self.value / other, self.base_unit)
        if isinstance(other, Quantity):
            new_value = self.value / other.value
            # Dividing SUBTRACTS dimension tuples. Same shape / same
            # shape gives all-zero dims, i.e. dimensionless — not an error.
            new_dims = tuple(a - b for a, b in zip(self.base_unit, other.base_unit))
            return Quantity(new_value, new_dims)
        return NotImplemented

    def __rtruediv__(self, other):
        # Handles `1 / Quantity(4, 's')` -> a frequency, 0.25 Hz
        if isinstance(other, (int, float)):
            return Quantity(other) / self
        return NotImplemented

    def __pow__(self, power):
        # Fraction(power) keeps the exponent exact even for e.g. 0.5,
        # so raising dims by a fractional power doesn't accumulate
        # float rounding error across repeated operations.
        p = power if isinstance(power, Fraction) else Fraction(power)
        new_dims = tuple(d * p for d in self.base_unit)
        # The numeric value itself still uses the ordinary float power.
        return Quantity(self.value ** power, new_dims)

    # -- display -----------------------------------------------------------

    def __repr__(self):
        label = self._unit_label()
        # :g trims trailing zeros and switches to scientific notation
        # automatically for very large/small magnitudes.
        return f"{self.value:g} {label}" if label else f"{self.value:g}"

    __str__ = __repr__  # print() and str() use the same formatting as repr()

    def __hash__(self):
        # Needed because defining __eq__ makes Python drop the default
        # hash — this lets Quantity still be used in sets/dict keys.
        return hash((self.value, self.base_unit))


# --------------------------------------------------------------------------
# Base and named-compound units, defined directly with tuple dims (bypasses
# string parsing entirely, since these ARE the vocabulary the parser uses).
# --------------------------------------------------------------------------
BASE_UNITS = {
    'm':   Quantity(1, (1, 0, 0, 0, 0, 0, 0)),   # length
    'kg':  Quantity(1, (0, 1, 0, 0, 0, 0, 0)),   # mass
    's':   Quantity(1, (0, 0, 1, 0, 0, 0, 0)),   # time
    'A':   Quantity(1, (0, 0, 0, 1, 0, 0, 0)),   # electric current
    'K':   Quantity(1, (0, 0, 0, 0, 1, 0, 0)),   # temperature
    'mol': Quantity(1, (0, 0, 0, 0, 0, 1, 0)),   # amount of substance
    'cd':  Quantity(1, (0, 0, 0, 0, 0, 0, 1)),   # luminous intensity

    # grams: same dimension as kg, but 1 g = 0.001 kg in base-SI value
    'g':   Quantity(0.001, (0, 1, 0, 0, 0, 0, 0)),
}

COMPOUND_UNITS = {
    'N':  Quantity(1, (1, 1, -2, 0, 0, 0, 0)),   # force, Newton
    'J':  Quantity(1, (2, 1, -2, 0, 0, 0, 0)),   # energy, Joule
    'W':  Quantity(1, (2, 1, -3, 0, 0, 0, 0)),   # power, Watt
    'Pa': Quantity(1, (-1, 1, -2, 0, 0, 0, 0)),  # pressure, Pascal
    'C':  Quantity(1, (0, 0, 1, 1, 0, 0, 0)),    # charge, Coulomb
    'V':  Quantity(1, (2, 1, -3, -1, 0, 0, 0)),  # potential, Volt
    'Ω':  Quantity(1, (2, 1, -3, -2, 0, 0, 0)),  # resistance, Ohm
    'T':  Quantity(1, (0, 1, -2, -1, 0, 0, 0)),  # magnetic field, Tesla
    'Hz': Quantity(1, (0, 0, -1, 0, 0, 0, 0)),   # frequency, Hertz

    # non-coherent units: their "1 unit" is NOT 1 in SI base terms
    'au': Quantity(1.495978707e11, (1, 0, 0, 0, 0, 0, 0)),        # Astronomical Unit
    'ly': Quantity(9.4607304725808e15, (1, 0, 0, 0, 0, 0, 0)),    # Light Year
    'pc': Quantity(3.08567758149137e16, (1, 0, 0, 0, 0, 0, 0)),   # Parsec
    'min': Quantity(60, (0, 0, 1, 0, 0, 0, 0)),    # minute = 60 s
    'h':   Quantity(3600, (0, 0, 1, 0, 0, 0, 0)),  # hour = 3600 s
}

# Merge both dicts into one lookup table used everywhere else.
KNOWN_UNITS = {**BASE_UNITS, **COMPOUND_UNITS}

# Build the dims -> symbol map used by _unit_label for pretty-printing.
# Only units whose value == 1 (i.e. "1 unit == 1 in SI base terms") are
# allowed to become the canonical name for their shape. This is what
# stops 'pc' (parsec, value=3e16) from hijacking the display name for
# every plain length just because it happens to share the same dims as 'm'.
REVERSE_LOOKUP = {}
for _symbol, _q in KNOWN_UNITS.items():
    if _q.value == 1 and _q.base_unit not in REVERSE_LOOKUP:
        REVERSE_LOOKUP[_q.base_unit] = _symbol


def _format_dims(dims):
    # Fallback formatter for shapes with no named unit, e.g. acceleration.
    parts = []
    for sym, exp in zip(_BASE_SYMBOLS, dims):
        if exp == 0:
            continue  # skip dimensions this quantity doesn't involve
        if exp == 1:
            parts.append(sym)                       # "m" not "m^1"
        elif exp.denominator == 1:
            parts.append(f"{sym}^{exp.numerator}")   # whole-number exponent
        else:
            parts.append(f"{sym}^({exp.numerator}/{exp.denominator})")  # fractional
    return '·'.join(parts) if parts else 'dimensionless'


# --------------------------------------------------------------------------
# Unit-string parsing: 'm', 'kg m2/s3', 'km/h', 'm/s2', 's^-1', ...
# --------------------------------------------------------------------------

# Matches one token: letters (the unit symbol), then an optional '^',
# then an optional (possibly negative) integer exponent.
# e.g. 's2' -> ('s', '2'); 'm^-1' -> ('m', '-1'); 'kg' -> ('kg', '')
_TOKEN_RE = re.compile(r'^([a-zA-Zμ°Ω]+)\^?(-?\d*)$')


def _lookup_symbol(symbol):
    """Return (scale_to_base_si, dims) for a single unit symbol, honoring prefixes."""
    if symbol in KNOWN_UNITS:
        # Exact match first — this is what lets 'Pa' mean Pascal instead
        # of being misread as prefix 'P' (peta) + unit 'a' (not a unit).
        q = KNOWN_UNITS[symbol]
        return q.value, q.base_unit

    # No exact match — try stripping a prefix off the front.
    for prefix in _PREFIXES_BY_LENGTH:
        if symbol.startswith(prefix):
            remainder = symbol[len(prefix):]
            if remainder in KNOWN_UNITS:
                q = KNOWN_UNITS[remainder]
                return prefixes[prefix] * q.value, q.base_unit

    raise ValueError(f"Unknown unit: {symbol}")


def _parse_token(token):
    """Parse one 'symbol[^]exponent' token, e.g. 's2', 'm^-1', 'kg'."""
    token = token.strip()
    if not token:
        raise ValueError("Empty unit token")

    match = _TOKEN_RE.match(token)
    if not match:
        raise ValueError(f"Invalid unit token: {token!r}")

    symbol, exp_str = match.groups()
    power = int(exp_str) if exp_str else 1  # no digits found -> exponent 1

    base_scale, base_dims = _lookup_symbol(symbol)
    # Raising a unit to a power raises both its scale and its dims,
    # e.g. km^2: scale (1000)^2, dims (1,0,0,..) * 2 = (2,0,0,..).
    scale = base_scale ** power
    dims = tuple(d * power for d in base_dims)
    return scale, dims


def parse_unit_string(unit_str):
    """
    Parse a compound unit string into (scale, dims), where `scale` converts a
    value expressed in `unit_str` into coherent SI base units.
    """
    unit_str = unit_str.strip()
    if not unit_str or unit_str in ('1', 'dimensionless'):
        return 1.0, ZERO_DIMS

    # Everything before the first '/' is the numerator; everything after
    # each subsequent '/' is another denominator (handles 'kg/m/s2').
    parts = unit_str.split('/')
    numerator, denominators = parts[0], parts[1:]

    scale = 1.0
    dims = list(ZERO_DIMS)

    def consume(text, invert):
        nonlocal scale, dims
        # Split a numerator/denominator chunk on whitespace, '.', or '*'
        # so 'kg m2' and 'kg.m2' and 'kg*m2' all mean the same thing.
        for tok in re.split(r'[\s.\*·]+', text.strip()):
            if not tok:
                continue
            tscale, tdims = _parse_token(tok)
            if invert:
                # Denominator: divide scale, subtract dims.
                scale /= tscale
                dims = [d - td for d, td in zip(dims, tdims)]
            else:
                # Numerator: multiply scale, add dims.
                scale *= tscale
                dims = [d + td for d, td in zip(dims, tdims)]

    consume(numerator, invert=False)
    for den in denominators:
        consume(den, invert=True)

    return scale, tuple(dims)


def parse_unit(unit_str):
    """Return a Quantity(1, unit_str) — one unit of `unit_str`, in base SI value."""
    scale, dims = parse_unit_string(unit_str)
    return Quantity(scale, dims)