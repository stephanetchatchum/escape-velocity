# Phase 0: Programming Foundations — Complete Specification
### escape_velocity · Stage 1 · Months 1–6 · Projects 1–18

## Before you start: what Phase 0 actually is

**What it is, in plain words.** Phase 0 is not one project — it's eighteen small, unglamorous pieces of software that together become your own personal science toolkit, `escape_velocity`. Nothing in it is specific to space. It's a units system, a way of handling time correctly, a way of describing where something is, a way of reading a few common data formats, plus the testing, logging, and configuration habits that professional scientific software runs on. None of it looks like a satellite or a black hole. That's deliberate — it's the plumbing that everything with a satellite or a black hole in it will later run through.

**What it's meant to do.** Every later phase of this curriculum — orbit mechanics, machine learning on real telescope data, Earth observation pipelines — needs to know what time it is, what units a number is in, and where a point in space actually sits. Rather than solving those problems separately, and sloppily, inside every future project, you solve them once here and import the answer for the next three years. Phase 0's job is to disappear into the background of everything that comes after it.

**How useful it actually is.** Very, but only if you get through it properly. A units library that raises an error instead of silently adding metres to seconds is what stops a bug from surviving undetected into your orbit propagator. A time converter that handles leap seconds correctly is what makes every later timestamp trustworthy instead of "probably fine." The tests, the CI, the logging aren't optional busywork — they're the difference between code that ran once and code you can still trust six months from now. Skipping or rushing this phase doesn't cost you now. It costs you in Phase 5, as a bug you can't find because you don't trust your own units.

**Is it portfolio-worthy? Honestly — not yet, and not on its own.** Right now, in week one, "I built a units library" isn't a line for a CV. It's infrastructure, and infrastructure by itself doesn't show much to someone reading your GitHub for thirty seconds. Two things change that, both already later in your own roadmap:

1. **What it gets used for.** A units library becomes evidence the moment your orbit propagator (Phase 5) uses it to catch a real unit-mismatch bug, or your Earth observation pipeline (Phase 9) depends on it not to silently corrupt a physical quantity. Its value shows up in what it enables, not in what it is.
2. **How it's packaged.** Projects 81–85 turn this from a folder of scripts that work for you into a tested, documented, versioned, installable Python package with continuous integration. That, plus a real PyPI release and possibly a JOSS submission — both already sitting later in this curriculum — is what turns "I wrote some code" into "I maintain a published package," which is a genuinely different sentence in an interview.

So build it properly, don't skip the tests, but don't put it on your CV yet either. Its portfolio value is deferred, not absent. Right now it's an investment, not a return.

One naming note before you start: this document uses `escape_velocity` as the package name throughout, since that's what you settled on. If the package you `pip install -e`'d earlier is still named `evkit`, rename the directory (`toolkit/src/evkit` → `toolkit/src/escape_velocity`) and the `name =` line in `pyproject.toml` before continuing — five minutes now, not a problem later.

## How this document works

Each project below is self-contained. You should not need to leave this document, or search the internet, to understand *what* to build and *why* it works the way it does — the video links are for when a concept genuinely needs a second explanation in a different voice, not because this document left something out.

Every project has the same seven sections:

1. **Mental model** — what the thing actually is, in plain language, before any code or math.
2. **Concepts explained** — the ideas behind the requirements, explained in full, not just linked.
3. **Worked example** — a hand-traced calculation or pseudocode walkthrough of the hardest sub-problem, so you see the shape of a solution before writing your own.
4. **Requirements** — what the finished module must do.
5. **Definition of done** — the specific, checkable conditions that mean you're finished.
6. **Edge cases** — the inputs that break a careless implementation.
7. **Video resources** — search terms for when reading isn't landing.

Pseudocode in this document (written as `function name(...)`) is not code to copy. It's a description of an algorithm's shape, in a form that isn't valid Python or C, precisely so you still have to do the actual translation yourself.

**Build order:** projects 1–4 are strictly sequential (each depends on the one before). Projects 5–10 can be done in any order once 1–4 exist. Projects 11–12 should be started early and grown continuously rather than done as a single block. Projects 13–15 are environment work, do them whenever you want a change of pace from the Python. Projects 16–18 are best done just before you need them for real data, which for most people is around the propagator work in Phase 5.

---

## Project 1: Scientific units and dimensions library

### Mental model

Every physical quantity is two things glued together: a number, and a "shape" describing what *kind* of number it is. `5` alone is meaningless. `5 metres` is a length. `5 metres per second` is a speed. The shape — length, or length-per-time, or mass-times-length-per-time-squared (force) — is what you're tracking underneath the number. Your `Quantity` class is a container that always carries the number and its shape together, and refuses to combine two containers whose shapes disagree. That refusal is the entire point. It's what would have caught the Mars Climate Orbiter bug in 1999, where one team's software produced thrust data in pound-seconds and another team's software consumed it as if it were newton-seconds — two different shapes wearing similar-sounding names, and nothing in either codebase was set up to notice.

### Concepts explained

**Dimensional analysis.** Every unit in physics is built from seven independent base dimensions: length, mass, time, electric current, temperature, amount of substance, luminous intensity. A speed is length¹·time⁻¹. A force is mass¹·length¹·time⁻². Represent this as a 7-tuple of exponents, one slot per base dimension — force is `(1, 1, -2, 0, 0, 0, 0)`, in the order (length, mass, time, current, temperature, amount, luminosity). Multiplying two quantities *adds* their exponent tuples element by element. Dividing *subtracts* them. Raising to a power *multiplies* the whole tuple by that power. This is why dimension-checking is just tuple arithmetic once the representation is right — the physics collapses into arithmetic on a fixed-length list of numbers.

**Operator overloading.** Python lets a class define what `+`, `*`, `/`, and so on mean for its own instances, by implementing methods named `__add__`, `__mul__`, `__truediv__`. When you write `a + b` and `a` is your `Quantity`, Python calls `a.__add__(b)` behind the scenes — this is a lookup, not magic. Once you see `+` as sugar for a specific method call, the rest of this project stops feeling mysterious, and so does most of what comes after it.

**Why addition and multiplication behave differently.** Addition only makes sense between two things of the *same* shape — you can add 2 metres and 3 metres, not 2 metres and 3 seconds. So `__add__` must check the dimension tuples are identical and raise an error otherwise. Multiplication always makes sense between any two quantities — 2 metres times 3 seconds is a legitimate thing (6 metre-seconds), it's just not a unit anyone names. So `__mul__` never raises a dimension error; it adds the tuples and produces whatever shape falls out, named or not.

**Rational exponents, and why `Fraction` matters.** Take the square root of an area (dimension `(2,0,0,0,0,0,0)`) and you should get a length (`(1,0,0,0,0,0,0)`) — exponent 2 divided by 2. Store exponents as plain integers and dividing 1 by 2 in Python gives you the float `0.5`, and floats accumulate rounding error across repeated operations, so two mathematically-equal exponents computed two different ways might not compare equal. `fractions.Fraction` stores a ratio exactly, as a numerator and denominator pair, so `Fraction(1,2) * 2 == Fraction(1,1)` exactly, every time. Use `Fraction` for every exponent slot from the start, even though the vast majority of the time they'll just be small integers.

### Worked example: multiplication and addition, traced by hand

Multiply an acceleration by a mass — this is the `F = ma` case:

```
Quantity A: value = 9.81, dims = (1, 0, -2, 0, 0, 0, 0)   [m/s^2]
Quantity B: value = 70,   dims = (0, 1,  0, 0, 0, 0, 0)   [kg]

function multiply(A, B):
    new_value = A.value * B.value            # 9.81 * 70 = 686.7
    new_dims  = tuple(a + b for a, b in zip(A.dims, B.dims))
    #   pair up each slot: (1+0, 0+1, -2+0, 0+0, 0+0, 0+0, 0+0)
    #   = (1, 1, -2, 0, 0, 0, 0)
    return Quantity(new_value, new_dims)
```

Notice `(1, 1, -2, 0, 0, 0, 0)` is exactly the dimension of force. You never told the function "this is a force" — it fell out of the arithmetic. That's the whole design: never hardcode "force = mass times acceleration" as a special case. Let dimension addition produce it, and let a separate unit registry recognize `(1,1,-2,0,0,0,0)` as "newton" purely for display.

Now addition, where the subtlety is real — adding a length in metres to a length in kilometres:

```
Quantity A: value = 500,  dims = (1,0,0,0,0,0,0), unit = 'm'
Quantity B: value = 2,    dims = (1,0,0,0,0,0,0), unit = 'km'

function add(A, B):
    if A.dims != B.dims:
        raise DimensionError(...)
    # dims match (both length), but the UNITS differ, so convert B into A's unit
    # before touching the raw numbers
    B_value_in_A_units = B.value * (B.unit_to_base_factor / A.unit_to_base_factor)
    #   B.unit_to_base_factor = 1000 (1 km = 1000 m)
    #   A.unit_to_base_factor = 1    (1 m = 1 m)
    #   B_value_in_A_units = 2 * (1000 / 1) = 2000
    return Quantity(A.value + B_value_in_A_units, A.dims, unit=A.unit)
    #   500 + 2000 = 2500 m  (correct — NOT 502)
```

Matching *dimensions* is necessary but not sufficient. `1 m + 1 km` has matching dimensions and mismatched units, and skipping the conversion step is the single most common bug in a first version of this class.

### Requirements

- A `Quantity` class holding a float value and a dimension vector over the seven SI base dimensions: length, mass, time, current, temperature, amount, luminous intensity
- Arithmetic through operator overloading: `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__pow__`, `__neg__`
- Addition and subtraction raise a `DimensionError` when dimensions do not match
- Multiplication and division add and subtract dimension vectors correctly
- Powers work with integer and rational exponents, so a square root of an area gives a length
- Conversion between units of the same dimension: metres to kilometres, kilometres per hour to metres per second
- A registry of named units built from the base set: newton, joule, watt, pascal, astronomical unit, light year, parsec
- `__repr__` and `__str__` that print the value with its unit legibly
- Comparison operators that respect dimensions
- No third-party dependencies — standard library only

### Definition of done

- `Quantity(9.81, 'm/s2') * Quantity(70, 'kg')` returns a force in newtons with the right dimensions
- `Quantity(1, 'm') + Quantity(1, 's')` raises `DimensionError` with a clear message
- A test suite covers every operator, every base dimension, and at least six error cases
- The module sits in `toolkit/src/escape_velocity/units.py` and imports cleanly
- Written up in the toolkit README with three usage examples

### Edge cases to handle

- Adding two quantities with the same dimension but different units (metres and kilometres) — convert, don't reject
- Multiplying by a bare number, which should work and leave dimensions unchanged
- Dividing two identical dimensions, which should produce a dimensionless quantity, not an error
- Zero and negative values
- Fractional powers that produce non-integer dimension exponents
- Very large and very small magnitudes, where float precision starts to matter

### Video resources

- Search **"Python dunder methods explained"** — ArjanCodes and mCoding both build these from first principles rather than treating `@`/`__x__` as magic.
- Search **"operator overloading Python"** — Corey Schafer's OOP series covers it cleanly with runnable examples.
- Search **"dimensional analysis physics explained"** for the base-dimension idea if it feels shaky before you code it.
- Search **"Python Fraction class tutorial"** for exact rational arithmetic and why it beats floats here.

---

## Project 2: Physical constants module with uncertainties

### Mental model

Every constant in physics isn't a single number, it's a small cloud around a number: "the speed of light is exactly this, but the gravitational constant is *probably* this, give or take this much." You're building a number type that carries its own cloud of uncertainty and correctly grows or shrinks that cloud through arithmetic. Add two foggy numbers, get a foggier number back, following exact rules for how the fog combines — that's error propagation, and it's the difference between reporting a number and reporting a measurement.

### Concepts explained

**Why uncertainty exists at all.** Constants like `G` are *measured*, not defined — different experiments get slightly different values, and CODATA publishes a best estimate plus a stated uncertainty, meaning "we're confident the true value sits within this range." Contrast `c`, the speed of light, which is *defined* to be exactly 299,792,458 m/s, so its uncertainty is exactly zero — it's the thing the metre is defined in terms of, not something anyone measured.

**First-order error propagation, from scratch.** For `z = f(x, y)` with independent uncertainties `σx` and `σy`, the general rule is:

```
σz^2 = (∂f/∂x)^2 · σx^2  +  (∂f/∂y)^2 · σy^2
```

For each input, take the partial derivative of the output with respect to that input — how sensitive the answer is to a small wiggle there — square it, multiply by that input's variance, and sum. For the four basic operations this collapses to memorable rules, each derivable from the general formula by actually computing the partial derivative:

- **Addition/subtraction** (`z = x ± y`): absolute uncertainties add in quadrature — `σz = sqrt(σx^2 + σy^2)`
- **Multiplication/division** (`z = x·y` or `z = x/y`): *relative* uncertainties add in quadrature — `σz/z = sqrt((σx/x)^2 + (σy/y)^2)`
- **Powers** (`z = x^n`): relative uncertainty scales by the exponent — `σz/z = n · (σx/x)`

Derive each of these by hand on paper once. That derivation is what makes the rule stick, rather than being a thing you memorized without understanding why it's true.

**Why subtracting two close numbers is dangerous.** If `x = 10.0 ± 0.1` and `y = 9.9 ± 0.1`, then `z = x − y = 0.1`, but `σz = sqrt(0.1^2 + 0.1^2) ≈ 0.14`. The uncertainty is now *larger* than the answer — the result is consistent with zero. The arithmetic is correct and the result is scientifically useless. Flag this case explicitly (when `σz > abs(z)`) rather than silently reporting a number that looks precise but isn't.

### Worked example: propagating uncertainty through escape velocity

Escape velocity is `v = sqrt(2·GM / R)`. Take `GM = 398600.4418 ± 0.0008 km³/s²` (Earth's standard gravitational parameter) and `R = 6371.0 ± 1.0 km` (deliberately generous for illustration).

```
step 1 — nominal value:
    v = sqrt(2 * 398600.4418 / 6371.0) = sqrt(125.16) ≈ 11.186 km/s

step 2 — propagate through each operation in the chain:

  a) division (GM / R): relative uncertainty adds in quadrature
       rel = sqrt((0.0008/398600.4418)^2 + (1.0/6371.0)^2)
           ≈ sqrt(0 + 0.0000247) ≈ 0.000157   (about 0.0157%)
       GM/R = 62.58 ± (62.58 * 0.000157) = 62.58 ± 0.0098

  b) multiply by the exact constant 2: relative uncertainty unchanged
       2*(GM/R) = 125.16 ± 0.0196   (still ~0.0157% relative)

  c) square root, i.e. power of 0.5: relative uncertainty scales BY the exponent
       relative uncertainty of v = 0.5 * 0.0157% = 0.00785%
       σv = 11.186 * 0.0000785 ≈ 0.00088 km/s

  result: v = 11.186 ± 0.001 km/s   (rounded to match the uncertainty's precision)
```

Step (c) is where people most often go wrong — forgetting that the exponent multiplies the *relative* uncertainty, not the absolute one. Trace this with your own numbers by hand before trusting whatever your code prints.

### Requirements

- Extend `Quantity` (project 1) into a `Measurement` class with a nominal value and a standard uncertainty
- Implement first-order error propagation for `+`, `-`, `*`, `/`, and powers
- Handle correlated versus independent variables explicitly, and document which you assume
- Load at least twenty CODATA constants — `G`, `c`, `h`, `hbar`, `k_B`, `N_A`, `m_e`, `m_p`, `e`, `epsilon_0`, `mu_0`, `sigma`, `R`, `g_0`, plus the astronomical set `GM_sun`, `GM_earth`, `R_earth`, `AU`, `parsec`, solar luminosity
- Store constants in a data file, not hardcoded in Python
- Format output as `value ± uncertainty`, with the uncertainty rounded to two significant figures and the value matched to it
- Report relative uncertainty on request

### Definition of done

- Computing Earth's escape velocity from `GM_earth` and `R_earth` gives 11.19 km/s with a sensible propagated uncertainty
- Every constant matches its CODATA value to the last quoted digit, verified by a test
- Formatting produces `6.674 30 ± 0.000 15 × 10^-11`, not fifteen unrounded digits
- Tests cover propagation through each operator against hand-computed values

### Edge cases

- A constant with zero uncertainty, such as the exactly-defined speed of light
- Subtracting two nearly-equal quantities, where relative uncertainty explodes — worth a comment in the code when it happens
- Powers with negative exponents
- Division by a quantity whose uncertainty range includes zero

### Video resources

- Search **"error propagation formula derivation"** — look for one that actually derives the partial-derivative formula rather than stating it.
- Search **"significant figures rules"** for a quick refresher — this part is mechanical, not conceptual.
- Search **"CODATA physical constants explained"** for what the committee does and why values update periodically.

---

## Project 3: Time systems converter

### Mental model

Picture two clocks sitting side by side since 1972. One, TAI, ticks perfectly and never adjusts. The other, UTC — the one on your phone — occasionally pauses for exactly one second (a leap second) to stay roughly aligned with Earth's slightly irregular rotation. GPS time is a third clock that started in 1980 in sync with TAI at that moment and then never adjusted, so it sits at a permanent fixed 19-second offset from TAI forever. Your job is to build the translator that knows, for any given moment, exactly how far apart these clocks currently are — which means knowing the entire history of leap-second pauses.

### Concepts explained

**Why UTC is the wrong clock to compute with.** UTC is what humans read, but because it occasionally gains a second, the *duration* between two UTC timestamps isn't reliably computed by simple subtraction — a leap second might fall in between. TAI has no pauses, so it's the correct internal representation: convert everything to TAI (or an equivalent continuous count like Julian Date) first, do the math, convert back to UTC only for display.

**Julian Date, explained.** JD is the number of days, and fraction of a day, since noon on 1 January 4713 BC — a fixed reference point chosen precisely so any two dates can be compared by simple subtraction, with no calendar irregularities to worry about. JD for 2000 January 1, 12:00 TT is *exactly* 2451545.0 — this is the J2000 epoch, the reference point most orbital element sets use. If your Julian Date formula doesn't reproduce this exact number, it has a bug — this is the single best sanity check in the whole project.

**Why one float isn't enough precision for a JD.** A `float64` carries about 15–17 significant decimal digits. JD values are around 2,451,545 — seven digits before the decimal point — leaving only 8–10 digits after it, which corresponds to a precision of a few tens of microseconds at best, and it degrades further the larger the JD grows (floating point precision is relative, not absolute). Professional astronomy libraries split the JD into two floats — a large integer-ish part and a small fraction close to zero — specifically to dodge this. Worth doing the same if you want robust microsecond precision.

**Greenwich Mean Sidereal Time, in plain terms.** Earth rotates once relative to the *stars* in about 23h 56m — a sidereal day — not 24 hours, because in the roughly 24h it takes to face the Sun again, Earth has also moved along its orbit and needs a little extra rotation to catch up. GMST measures Earth's orientation relative to the stars (specifically, the vernal equinox direction) rather than relative to the Sun. You need it because converting from an Earth-fixed frame (tied to the ground) to an Earth-centred inertial frame (tied to the stars) is, at its core, just "rotate by GMST" — it's the angle between those two reference directions at a given instant.

### Worked example: UTC to TAI, by hand

Convert `2020-01-01 00:00:00 UTC` to TAI.

```
step 1 — look up the leap second table (IERS Bulletin C), find the cumulative count of
         leap seconds inserted between 1972-01-01 and the target date. A leap second was
         added 2016-12-31, bringing the total to 37. None was added between 2017 and 2020,
         so the count is still 37 at your target date.

step 2 — TAI is always AHEAD of UTC by that cumulative count, since UTC has been "held
         back" by that many seconds' worth of pauses:
             TAI = UTC + 37 seconds

step 3 — so 2020-01-01 00:00:00 UTC = 2020-01-01 00:00:37 TAI.

step 4 — GPS time is TAI minus a FIXED 19 seconds (this never changes, because GPS time
         itself has no leap seconds — it simply drifted from UTC as leap seconds accumulated
         after the GPS epoch in 1980):
             GPS = TAI - 19 = 2020-01-01 00:00:18 (in GPS seconds-of-that-instant)

check yourself: GPS minus UTC should equal (37 - 19) = 18 seconds at this date. GPS
satellites themselves broadcast this UTC offset, which is a good independent check on
your own leap-second table.
```

The part to get right in code: your leap-second lookup needs to be *by date*, returning "how many leap seconds had occurred by this date," not a single fixed number — the offset changes every time a new leap second is announced.

### Requirements

- Represent an instant internally on a continuous scale (TAI or Julian Date), not UTC
- Convert UTC to and from TAI using a leap-second table
- Convert to and from GPS time (TAI minus 19 seconds)
- Convert to and from terrestrial time (TAI plus 32.184 seconds)
- Compute Julian Date and Modified Julian Date from a calendar date and time
- Compute Greenwich Mean Sidereal Time from UT1, using the standard polynomial
- Parse and emit ISO 8601 strings
- Load the leap second table from a data file, with its last-updated date stated
- Maintain sub-second precision across all conversions

### Definition of done

- Every conversion round-trips to within one microsecond
- Your Julian Date for 2000 January 1, 12:00 TT equals 2451545.0 exactly
- A conversion across the 2016 December 31 leap second gives the right answer, with a test for it
- GMST for a known date matches a published value to within a millisecond
- The leap second table is in a data file with its source and date documented

### Edge cases

- Dates before 1972, when UTC was defined differently and leap seconds didn't exist
- The leap second itself, 23:59:60, which `datetime` cannot represent
- Dates far in the future, where the leap second table is unknown — warn, don't silently extrapolate
- Negative Julian Dates for dates before 4713 BC
- Precision loss when storing a Julian Date as a single 64-bit float

### Video resources

- Search **"why do we have leap seconds"** — Veritasium and Tom Scott both cover this accessibly.
- Search **"Julian date explained astronomy"** for a walkthrough of the algorithm itself.
- Search **"sidereal time vs solar time"** — a visual of Earth orbiting while spinning makes GMST click faster than algebra alone.

---

## Project 4: Coordinate frame converter

### Mental model

You're standing on a spinning ball and want to describe "where is that satellite" in a way that's useful both to a physicist, who cares about motion relative to the fixed stars, and to someone with a dish antenna in their backyard, who cares which direction to point relative to the ground under their feet. These are genuinely different descriptions of the same point in space, and converting between them is nothing more than composing rotations — like describing a chess move from White's side of the board versus Black's, except the board itself is also spinning underneath you.

### Concepts explained

**ECI vs ECEF.** Earth-Centred Inertial does *not* rotate with the Earth — its axes point at fixed directions relative to the distant stars. Earth-Centred Earth-Fixed *does* rotate with the Earth — its x-axis always points through the Greenwich meridian. A satellite sitting still in ECI coordinates is actually flying past you if you're standing on the ground, because the ground is rotating under it; a satellite sitting still in ECEF coordinates is geostationary. Converting between them is a single rotation by the GMST angle from project 3 — exactly why project 3 had to come first.

**Rotation matrices, from first principles.** A rotation matrix is a 3×3 grid that, multiplied by a position vector, gives that same point's coordinates in a rotated frame. Rotation by angle θ around the z-axis:

```
        [ cos θ   sin θ   0 ]
Rz(θ) = [-sin θ   cos θ   0 ]
        [   0       0     1 ]
```

To go ECI → ECEF, rotate by `+GMST` around z (ECEF has "caught up" by however much Earth has spun since time zero). ECEF → ECI is the inverse rotation, `-GMST`, which for a rotation matrix is just its transpose — rotation matrices are orthogonal, so you never need to compute a full matrix inverse for this.

**Geodetic vs geocentric latitude.** Earth isn't a perfect sphere; it bulges at the equator by about 21 km (an oblate spheroid). Geocentric latitude is measured from Earth's centre. Geodetic latitude — the one on every map and GPS device — is the angle of the *local vertical*, perpendicular to the ellipsoid surface at that point, not pointing at the centre. These differ by up to about 0.2° depending on latitude and coincide at the equator and poles. Converting ECEF (x, y, z) to geodetic lat/lon/altitude generally has no single closed-form step, because the ellipsoid geometry makes it implicit — most implementations either iterate (guess a latitude, refine, repeat until stable) or use a published closed-form approximation. Know which one you used and why.

**The velocity term everyone forgets.** Rotating a *position* vector from ECI to ECEF is correct on its own. Rotating a *velocity* vector the same way is not, because the ECEF frame itself is rotating — a point stationary in ECEF (like a spot on the ground) has *nonzero* velocity in ECI, since the ground is being carried around by Earth's spin. The correction adds the term `ω × r` — Earth's angular velocity vector crossed with position — when going from ECI velocity to ECEF velocity, or subtracts it the other way. At the equator this term is about 465 m/s. Skipping it doesn't give you a slightly wrong answer; it gives you an answer wrong by half a kilometre per second — loud once you have a test for it, invisible if you don't.

### Worked example: the velocity correction, computed by hand

Position `r = (6524.834, 6862.875, 6448.296)` km in ECEF, with ECEF-frame velocity `v_ecef = (-0.001, 0.002, 0.003)` km/s (essentially a fixed ground point).

```
step 1 — Earth's angular velocity vector, along the rotation axis:
    ω = (0, 0, 7.2921150e-5) rad/s     [standard WGS84 sidereal rotation rate]

step 2 — cross product ω × r:
    (ω × r)_x = ω_y*r_z - ω_z*r_y = 0 - 7.2921150e-5 * 6862.875 = -0.50048
    (ω × r)_y = ω_z*r_x - ω_x*r_z = 7.2921150e-5 * 6524.834 - 0 = 0.47582
    (ω × r)_z = ω_x*r_y - ω_y*r_x = 0 - 0 = 0.0

step 3 — velocity in ECI (before axis rotation) is the ECEF velocity PLUS this term:
    v_before_rotation = v_ecef + (ω × r)
                       = (-0.001 - 0.500, 0.002 + 0.476, 0.003 + 0.0)
                       = (-0.501, 0.478, 0.003)  km/s

step 4 — then rotate the whole vector by -GMST to align the axes into true ECI.
```

Notice the correction term (~0.5 km/s) completely dominates the "real" ground velocity (~0.002 km/s). Forgetting `ω × r` for anything tied to the ground doesn't produce a noisy answer, it produces an answer wrong by two orders of magnitude.

### Requirements

- Rotation matrices about each axis, composed correctly
- ECI to ECEF and back, using GMST from project 3
- ECEF to geodetic latitude, longitude, altitude on WGS84, and back
- ECEF to topocentric south-east-zenith or east-north-up, then to azimuth, elevation, range
- Velocity transformation including the `ω × r` term
- All angles in radians internally, degrees only at the interface
- Public functions use the `Quantity` objects from project 1

### Definition of done

- ECEF to geodetic and back round-trips to within one millimetre
- The geodetic conversion method (iterative or closed-form) is stated and justified
- Azimuth and elevation of a known object from a known ground station match a published value to within 0.01 degrees
- Velocity transformation is tested against a case with a nonzero Earth rotation contribution
- Cross-checked against `pyproj` for at least twenty random points

### Edge cases

- Points at the poles, where longitude is undefined
- Points at the geocentre, where the geodetic conversion is singular
- Altitude below the ellipsoid surface, which is valid and occurs in real terrain
- Azimuth wrapping across 360 degrees
- Elevation below the horizon, which is a valid negative number, not an error

### Video resources

- Search **"essence of linear algebra rotation matrices"** (3Blue1Brown) for real intuition before coding.
- Search **"ECEF vs ECI coordinate frames explained"** for the physical picture specifically.
- Search **"WGS84 geodetic vs geocentric latitude"** for the ellipsoid-bulge explanation.
- Search **"cross product geometric meaning"** for why `ω × r` produces a velocity, not just the formula.

---

## Project 5: TLE parser and catalogue manager

### Mental model

A Two-Line Element set is a telegram from the 1960s that the entire satellite-tracking world still runs on: two lines of exactly 69 characters, packed with fixed-width fields, no delimiters, written for punch-card-era computers and never modernised because too much infrastructure depends on the exact format. Parsing it is less like reading a CSV and more like reading a barcode by hand — field boundaries are pure character position, and you have to know the map rather than split on commas.

### Concepts explained

**Fixed-width vs delimited parsing.** A CSV separates fields with commas, so `split(",")` does the work. A TLE has no separators at all — a field is defined purely by "columns 19 to 20 are the epoch year." This means slicing by index: `line[18:20]` in Python's zero-indexed strings for what the TLE spec calls "column 19" in its 1-indexed documentation. That off-by-one between the spec's column numbers and Python's slice indices is the single most common bug in a first parser.

**The implied decimal point in eccentricity.** A field like `0007976` has no decimal point at all — deliberate space-saving, since orbital eccentricity for a bound orbit is always between 0 and 1, so the leading "0." is implied and never written. Prepend it yourself: `"0." + "0007976"` gives `0.0007976`.

**The exponential drag term.** A field like ` 12345-3` means `0.12345 × 10^-3`. The last two characters are the power of ten; the sign in front of the mantissa (a space means positive) and the sign before the exponent both need separate handling. This compressed notation packs a wide dynamic range into eight characters.

**The checksum.** Each line ends with a single check digit. To compute it: sum every digit (0–9) in the line, treat each minus sign as contributing 1, ignore everything else, take the total mod 10. A mismatch against the printed digit means the line is corrupted or mis-copied — a cheap, useful first line of defence.

### Worked example: eccentricity, drag term, and checksum, traced by hand

```
Illustrative TLE line 1 fragment:
1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994

step 1 — eccentricity field, columns 27-33 (1-indexed) = line[26:33] (0-indexed):
    raw = "0007976"
    eccentricity = float("0." + raw) = 0.0007976

step 2 — drag term (BSTAR), columns 54-61 = line[53:61]:
    raw = " 10270-3"
    mantissa_str = raw[:-2].strip()   # "10270"
    exponent_str = raw[-2:]           # "-3"
    bstar = float("0." + mantissa_str) * (10 ** int(exponent_str))
          = 0.10270 * 10**-3
          = 0.00010270

step 3 — checksum over the whole line except the final digit:
    total = 0
    for char in line[:-1]:
        if char.isdigit():
            total += int(char)
        elif char == '-':
            total += 1
        # letters, spaces, '.', '+' contribute nothing
    computed_checksum = total % 10
    assert computed_checksum == int(line[-1]), "checksum mismatch — line is corrupted"
```

Do this by hand on one real Celestrak TLE, character by character, before trusting your parser's output. It's the fastest way to make the column layout permanent in your memory.

### Requirements

- Parse both lines: catalogue number, classification, international designator, epoch, mean motion and its derivatives, drag term, inclination, RAAN, eccentricity, argument of perigee, mean anomaly, revolution number
- Verify the mod-10 checksum on each line and reject lines that fail
- Convert the epoch into a proper time object from project 3
- A `Catalogue` class that loads a full Celestrak file, indexes by catalogue number and name, and supports queries by inclination band, altitude band, and epoch age
- Round-trip: emit a TLE from a parsed object and get the original string back byte for byte

### Definition of done

- Parses the full Celestrak active-satellite file without an unhandled exception
- Round-trip emission is byte-identical for every TLE in that file
- Checksum verification catches a deliberately corrupted line
- Epoch conversion for a known TLE matches an independent reference
- Loading and indexing the full catalogue takes under two seconds

### Edge cases

- Lines shorter than 69 characters, which occurs in some feeds
- Names longer than 24 characters in the optional title line
- Epoch years in the 1957–1999 range, where the two-digit year rule flips
- Negative values in the drag term
- Eccentricity of exactly zero, and values very close to one
- Duplicate catalogue numbers with different epochs — keep the latest
- Files with Windows line endings

### Video resources

- Search **"how to read a TLE two line element"** for field-by-field walkthroughs.
- Search **"mean elements vs osculating elements satellite"** for why a TLE isn't "the position."
- Search **"checksum algorithms explained"** for the mod-10 concept generally.

---

## Project 6: Ephemeris reader for JPL Horizons output

### Mental model

JPL Horizons is astronomy's closest thing to ground truth — given a body and a time, it tells you exactly where NASA's best models say that body was or will be. This project isn't about computing anything physical; it's about becoming fluent at reading someone else's precisely-formatted answer key, so every simulator you build from here has something authoritative to check against. You're building the answer-key reader, not the exam.

### Concepts explained

**Why ground truth matters at all.** Every propagator you write is an approximation, with some truncation error and some simplified force model. Without an independent, trusted reference, you can't distinguish "my propagator is correct" from "my propagator produces plausible-looking wrong numbers." Horizons, built from decades of tracking data and high-fidelity force models, is that independent reference — treating its output as truth for validation is standard practice, even at JPL itself.

**The SOE/EOE markers.** Horizons wraps its actual data between two literal marker lines, `$$SOE` and `$$EOE`, with a large, variably-formatted header before and a footer after. Robust parsing means: scan the header only for a few specific metadata lines (target body, frame), find `$$SOE`, read every line until `$$EOE`, ignore everything after. Trying to parse the header generically breaks the moment JPL tweaks formatting; anchoring on the markers is far more durable.

**Interpolation, conceptually.** Horizons gives position and velocity at discrete steps, say every hour. For a time between two steps, a cubic spline fits a smooth curve through the known points such that value, slope, and curvature all match up cleanly at the segment boundaries. This works well because orbital motion is smooth — no sudden jumps — so a smooth fit through nearby known points is a good estimate of the true position in between, provided you never extrapolate outside the range you actually have data for.

### Worked example: parsing between SOE and EOE, defensively

```
step 1 — read the file into a list of lines.

step 2 — find the index of the line exactly equal to "$$SOE" and exactly equal to "$$EOE".
    if either is missing, raise a clear error rather than silently parsing garbage.

step 3 — the actual records are lines[soe_index+1 : eoe_index], strictly between the markers.

step 4 — Horizons vector output typically spreads one record across multiple physical
         lines (Julian Date on one line, position on the next, velocity on the one after).
         Group them in chunks of the known line-count-per-record — VERIFY this against a
         real downloaded file rather than assuming, since it depends on what output
         options were requested:

    records = []
    lines_per_record = 3   # confirm against a real file first
    data_lines = lines[soe_index+1 : eoe_index]
    for i in range(0, len(data_lines), lines_per_record):
        chunk = data_lines[i : i+lines_per_record]
        jd = parse_float_from(chunk[0])
        x, y, z = parse_three_floats_from(chunk[1])
        vx, vy, vz = parse_three_floats_from(chunk[2])
        records.append((jd, x, y, z, vx, vy, vz))
```

The defensive habit worth keeping: never assume a fixed number of header lines before `$$SOE` — search for the marker, because the header length varies with the options you requested.

### Requirements

- Parse the Horizons vector-table output between `$$SOE` and `$$EOE`
- Extract Julian Date, position vector, and velocity vector per record
- Parse the header for target, centre body, reference frame, and units
- Return a structured object with time, position, and velocity arrays
- Interpolate between records so a position can be requested at any time in the span
- Cache fetched files to disk so repeated tests don't re-hit the network

### Definition of done

- Fetches and parses a full year of Earth's ephemeris relative to the solar system barycentre
- Interpolated positions agree with directly-requested Horizons values to better than one kilometre
- Header metadata is captured and exposed, so the frame is always known
- A cached file is reused rather than refetched, verified by a test

### Edge cases

- Requests returning an error page instead of data
- Time spans crossing the limits of the underlying ephemeris
- Different units appearing in the header (km vs AU)
- Records with fewer fields than expected
- Interpolation requested outside the fetched span — raise, don't extrapolate silently

### Video resources

- Search **"JPL Horizons system tutorial"** for a look at the web interface before touching the API.
- Search **"Python regular expressions tutorial"** for the header-parsing half.
- Search **"cubic spline interpolation explained"** for the intuition, ahead of formalising it in a later project.

---

## Project 7: Telemetry log analyser

### Mental model

Real sensor data is never a clean signal — it's a signal with gaps where the sensor dropped out, spikes where something glitched, and stretches where a value got stuck because a connection froze. Before saying anything scientific about a dataset, you have to characterise its misbehaviour first. This project builds the instrument that looks at a stream of numbers and honestly reports what's wrong with it before anyone draws conclusions from it.

### Concepts explained

**Welford's algorithm, explained fully.** The naive way to compute variance sums all values, divides by count for the mean, then does a second pass computing `(x - mean)^2` for each point. This needs two passes and, worse, loses precision when values are large and close together, since squaring differences of large numbers amplifies rounding error. Welford's algorithm updates a running mean and variance incrementally, one value at a time:

```
count = count + 1
delta = x - mean
mean = mean + delta / count
delta2 = x - mean          # recomputed with the NEW mean
M2 = M2 + delta * delta2
variance = M2 / count       # or M2/(count-1) for sample variance
```

The trick: it never computes `x^2` directly, only ever works with differences from the current running mean, which stay small even when the raw values are huge. That's why it's standard for streaming data and simply more numerically robust even when you have the whole dataset in memory at once.

**Interquartile range outlier detection.** Sort the data. Q1 is the value below which a quarter falls; Q3 is the value below which three-quarters fall. `IQR = Q3 - Q1` measures the spread of the typical middle half, ignoring extremes. A common rule flags anything below `Q1 - 1.5*IQR` or above `Q3 + 1.5*IQR`. This is more robust than "more than two standard deviations from the mean," because the mean and standard deviation are themselves distorted by the very outliers you're trying to find — percentile-based measures aren't dragged around by a few extreme values the way mean and stdev are.

**Why gap detection needs a tolerance.** If the nominal sample period is 1.000 seconds, real timestamps are never *exactly* 1.000 seconds apart — there's always jitter. Flagging every interval that isn't exactly 1.000s as a gap would flag almost the entire file. Define a tolerance instead (flag if the interval exceeds 1.5× nominal), so normal jitter is ignored and only genuine dropouts get reported.

### Worked example: Welford's algorithm traced on four values

```
values = [10, 12, 23, 21]
initial: count=0, mean=0, M2=0

x=10: count=1, delta=10-0=10, mean=0+10/1=10, delta2=10-10=0, M2=0+10*0=0
x=12: count=2, delta=12-10=2, mean=10+2/2=11, delta2=12-11=1, M2=0+2*1=2
x=23: count=3, delta=23-11=12, mean=11+12/3=15, delta2=23-15=8, M2=2+12*8=98
x=21: count=4, delta=21-15=6, mean=15+6/4=16.5, delta2=21-16.5=4.5, M2=98+6*4.5=125

final: mean = 16.5, population variance = M2/count = 125/4 = 31.25
       sample variance = M2/(count-1) = 125/3 ≈ 41.67
```

Check against the naive formula: mean of [10,12,23,21] is indeed 66/4 = 16.5. Once the two methods agree here, trust Welford on a million-row dataset where the naive version is both slower and less numerically stable.

### Requirements

- Read a CSV or similar log with a timestamp column and multiple numeric channels
- Per channel: count, mean, standard deviation, min, max, and the 5th/50th/95th percentiles, using Welford's algorithm for mean and variance
- Detect gaps: intervals exceeding the nominal sampling period by more than a tolerance
- Detect outliers using the interquartile range method, reported rather than silently removed
- Detect stuck channels — value unchanged for a suspiciously long run
- Compute duty cycle and effective sample rate per channel
- Emit a text or markdown summary report

### Definition of done

- Runs on a real log of at least one hundred thousand rows
- Welford's variance agrees with naive two-pass on well-conditioned data and beats it on a deliberately ill-conditioned case
- Gap detection finds a gap you introduced deliberately
- The report is readable by someone who has never seen the data
- Handles a file too large to comfortably fit in memory by streaming

### Edge cases

- Missing values as empty strings, NaN, or sentinels like -999
- Timestamps out of order or duplicated
- A channel that is entirely missing
- Mixed types within a column
- A file with no data rows at all

### Video resources

- Search **"Welford's algorithm variance explained"** for the derivation.
- Search **"interquartile range outliers explained"** — StatQuest covers this with clear worked examples.
- Search **"catastrophic cancellation floating point"**, which resurfaces in a later numerical methods project.

---

## Project 8: Structured logging and diagnostics module

### Mental model

A print statement is a note you leave for yourself while debugging, then delete. A logging system is a flight recorder that's always running, at a detail level you control from outside the code, writing to a destination you control, in a form a machine could parse later. The difference isn't really `print()` versus `logging.info()` syntactically — it's building something you can trust four hours into an unattended run that crashed while you weren't watching.

### Concepts explained

**The logging hierarchy.** Python's `logging` module organises loggers into a tree, usually one per module (`escape_velocity.units`, `escape_velocity.timescales`). Each logger has a level (DEBUG, INFO, WARNING, ERROR, CRITICAL), and a message is emitted only if its level meets the logger's threshold. A message can be filtered again at the *handler* level — you might configure the console handler to show WARNING and above (so the terminal isn't flooded), while the file handler shows everything from DEBUG up (so nothing is lost from the permanent record). This two-stage filtering — logger level, then handler level — is the part that confuses people first; drawing it as two separate gates a message passes through fixes that.

**Why library code should never call `basicConfig`.** If `escape_velocity` calls `logging.basicConfig(...)` internally, you're unilaterally deciding logging configuration for every program that ever imports it, overriding whatever the importing program wanted. The convention: library code creates loggers and emits to them, but never configures handlers or formats globally. Only the top-level application — your `ev` CLI, or a `__main__` script — should call `basicConfig`.

**Decorators, built conceptually.** A decorator is a function that takes another function as input and returns a new function wrapping it, typically doing something before and after the call. `@log_duration` above a function definition is shorthand for `my_function = log_duration(my_function)`. Inside `log_duration`, an inner function records a start time, calls the original, records an end time, logs the difference, and returns whatever the original returned. The decorator never needs to know what the wrapped function does — it just calls it and passes the result through, which is what makes decorators reusable across arbitrary functions.

### Worked example: the timing decorator, step by step

```
step 1 — a decorator is a function of a function:
    function log_duration(func):
        function wrapper(*args, **kwargs):
            start = current_time()
            result = func(*args, **kwargs)     # call the real function
            elapsed = current_time() - start
            logger.info(f"{func.__name__} finished in {elapsed:.3f}s")
            return result
        return wrapper

step 2 — apply it:
    @log_duration
    def propagate_orbit(state, dt):
        ...
    # equivalent to: propagate_orbit = log_duration(propagate_orbit)

step 3 — calling propagate_orbit(state, 60) actually runs wrapper(state, 60), which
         times the real function, logs it, and returns its result — transparently to
         the caller.
```

The subtlety worth tracing: `*args, **kwargs` in `wrapper`'s signature is what lets one decorator wrap *any* function, regardless of how many arguments it takes.

### Requirements

- Configure the standard library `logging` module rather than a custom logger
- Console handler at INFO with a readable format, file handler at DEBUG with full detail
- Timestamp, level, module name, and line number in the file format
- A structured JSON-lines mode for logs meant to be parsed later
- A context manager or decorator that logs entry, exit, and duration of a function
- A rate-limited progress reporter for long loops — log at a fixed interval, not every iteration
- Log rotation, so a long run doesn't fill the disk
- A single import: `from escape_velocity.logging_setup import get_logger`

### Definition of done

- Every module from project 9 onward uses it, with no print statements anywhere in `escape_velocity`
- A log file from a real run is readable and complete
- The timing decorator's reported durations match a stopwatch
- Setting the console to WARNING silences INFO without touching the file output
- Rotation triggers correctly on a deliberately small size limit

### Edge cases

- Logging from multiple modules, where hierarchy matters
- Logging inside library code a user might configure differently — never call `basicConfig` there
- Unicode in log messages
- Exceptions logged with full tracebacks via `exc_info`
- Very high-frequency logging, which will dominate runtime if unmanaged

### Video resources

- Search **"Python logging tutorial"** — Corey Schafer's series is thorough and standard.
- Search **"Python decorators explained"** and **"context managers Python"** for the timing-wrapper mechanics.

---

## Project 9: Experiment configuration system

### Mental model

Six months from now you'll look at a figure and have no idea what settings produced it — what timestep, what tolerance, what initial condition. This project is insurance against that exact moment. Never let a magic number live only inside your code. Every parameter that could plausibly change between runs lives in one config file, and every output is stamped with exactly which config, and which version of your code, produced it — so a result is never separated from its recipe.

### Concepts explained

**Configuration as data, not code.** If a timestep is set by writing `dt = 0.01` in a script, changing it means editing source code — error-prone, and unrepeatable, since there's no record of what the previous value was. If `dt` instead lives in a file your script reads, you can keep multiple configs for different experiments, diff them to see exactly what changed, and never touch the logic code just to change a number.

**Schema validation.** A schema describes what a valid config must contain — required keys, their types, acceptable ranges. Validating before running anything means a typo like `intergrator: "rk4"` is caught immediately with a clear error, instead of silently falling back to a default and producing a confusing wrong result three hours into a run.

**Why hashing the resolved configuration matters.** "Resolved" means the config after defaults and command-line overrides have been layered in — the complete, actual set of parameters governing the run. Hashing this resolved configuration and naming the output directory after the hash means two runs with identical parameters produce identical hashes (and can share a directory, or you can detect the experiment already ran), while runs differing in even one parameter get different hashes and can never accidentally overwrite each other's results.

### Worked example: a deterministic config hash

```
step 1 — a resolved config as a nested dictionary:
    config = {
        "integrator": "rk4",
        "timestep": 0.01,
        "initial_state": {"x": 1.0, "y": 0.0},
    }

step 2 — dictionaries don't guarantee a stable string form on their own, so convert to
         JSON with keys explicitly SORTED:
    canonical_string = json_dumps(config, sort_keys=True)
    # sort_keys=True is the crucial part: the SAME config always produces the SAME
    # string, regardless of insertion order.

step 3 — hash that canonical string:
    hash_value = sha256(canonical_string.encode("utf-8")).hexdigest()
    short_hash = hash_value[:10]     # first 10 characters, still effectively unique

step 4 — output directory becomes something like:
    runs/rk4_dt0.01_a3f9c21e0b/
    and the full resolved config (step 1's dictionary) is written as a file inside it.
```

The step people skip is `sort_keys=True` — without it, the same logical config can hash differently across runs purely from dictionary insertion order, silently breaking deduplication.

### Requirements

- Load configuration from TOML using the standard library `tomllib`
- Validate against a declared schema: required keys, types, allowed ranges
- Apply documented defaults for anything optional
- Allow command-line overrides of any config value
- Compute a hash of the resolved configuration and use it to name the output directory
- Write the resolved configuration, including defaults and overrides, into the output directory
- Record the git commit hash and whether the working tree was dirty at run time
- Fail loudly on an unknown key

### Definition of done

- A run is fully driven by a config file, with no hardcoded parameters
- Rerunning with the same config produces byte-identical output
- An unknown key produces an error naming the key and listing valid ones
- The output directory contains the resolved config and git state, sufficient to reconstruct the run
- A ten-run parameter sweep works from the command line without editing any file

### Edge cases

- A config file that doesn't exist, or is malformed
- A value of the right type but an invalid range
- Nested configuration sections
- An override for a key that doesn't exist in the schema
- Running outside a git repository
- Two different configs colliding on the same hash — should be impossible, but handle it

### Video resources

- Search **"pydantic tutorial"** for a mature validation-library reference, even if you build yours by hand.
- Search **"reproducible research computational science"** for the motivation behind this project.
- Search **"TOML vs YAML vs JSON"** for why TOML is often preferred for config specifically.

---

## Project 10: Command-line framework for your scientific tools

### Mental model

The difference between a script and a tool is that a tool doesn't require opening the source file to use it. A script you run by editing a hardcoded filename at the bottom is something only you, today, can operate. A tool has a stable interface — flags, subcommands, help text — that works the same regardless of who's calling it or which directory they're standing in, including a future version of you who's forgotten how this code works.

### Concepts explained

**argparse and subparsers.** `argparse` is Python's standard tool for declaring a command-line interface — you describe what arguments and flags exist, and it handles parsing, type conversion, and help-text generation. Subparsers let one program have multiple distinct subcommands, the way `git commit` and `git push` are one program with many subcommands, each with independent arguments. Build one top-level parser, call `.add_subparsers()` on it, then add a separate parser per subcommand.

**Exit codes.** Every program returns a small integer to the operating system when it finishes: `0` conventionally means success, nonzero means failure. Shell scripts and automation check this to decide whether to continue. The convention here: `0` success, `1` a handled expected error, `2` a usage error.

**Why stdout and stderr must stay separate.** `stdout` is for a program's actual output; `stderr` is for diagnostics. Unix pipes connect one program's stdout directly to the next program's stdin. If error messages leak into stdout, the next program in a pipeline receives corrupted input. Keeping them separate means a pipeline composes correctly even when one stage prints a warning.

### Worked example: nested subparsers, traced by hand

```
step 1 — top-level parser with a subparsers object:
    parser = ArgumentParser(prog="ev")
    parser.add_argument("--verbose", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

step 2 — one subcommand, "tle", which itself has sub-subcommands "parse" and "filter",
         needing its OWN nested subparsers:
    tle_parser = subparsers.add_parser("tle")
    tle_subparsers = tle_parser.add_subparsers(dest="tle_command", required=True)

    parse_parser = tle_subparsers.add_parser("parse")
    parse_parser.add_argument("file", type=str)

    filter_parser = tle_subparsers.add_parser("filter")
    filter_parser.add_argument("--inclination", type=str)

step 3 — parse what the user actually typed:
    args = parser.parse_args()
    # if they ran: ev tle filter --inclination 95:100
    # then: args.command == "tle", args.tle_command == "filter",
    #       args.inclination == "95:100"

step 4 — dispatch:
    if args.command == "tle":
        if args.tle_command == "parse":
            run_tle_parse(args.file)
        elif args.tle_command == "filter":
            run_tle_filter(args.inclination)
```

Trace this by hand for a second nested subcommand before writing the real thing — the pattern is identical each time, and doing it twice on paper is what makes it stick.

### Requirements

- A single entry point `ev` with subcommands: `ev tle`, `ev time`, `ev horizons`, `ev telemetry`
- Built on `argparse` subparsers
- Correct exit codes: 0 success, 1 handled error, 2 usage error
- Errors to stderr, results to stdout
- Reads from stdin when no input file is given, where that makes sense
- Registered as a console script in `pyproject.toml` so `ev` works after `pip install`

### Definition of done

- `ev tle parse file.tle | ev tle filter --inclination 95:100` works as a pipeline
- `ev --help` and every subcommand's `--help` are useful without reading the source
- A deliberate misuse returns exit code 2 with a message naming what was wrong
- Installed via `pip install -e` and callable as `ev` from any directory
- A shell script uses it end to end

### Edge cases

- No arguments at all — should print help, not a traceback
- Conflicting options
- Output to a file that already exists
- A broken pipe (piping into `head`), which is a real error to handle
- Ctrl-C, which should exit cleanly rather than dumping a traceback

### Video resources

- Search **"Python argparse tutorial"** — Corey Schafer's is the canonical recommendation.
- Search **"command line interface design principles"** for the philosophy behind good CLI design.
- Search **"unix pipes stdin stdout stderr"** if the pipe model is unfamiliar.

---

## Project 11: Test suite for units and time libraries

### Mental model

A test suite is a second, independent opinion on whether your code is right, one that runs in seconds and never gets tired of checking. Without it, "does this work?" is answered by eyeballing printed numbers and deciding they look plausible. With it, the same question gets a yes-or-no answer from a computer every time you change anything — the only way a codebase stays trustworthy as it outgrows what you can hold in your head.

### Concepts explained

**Fixtures.** A fixture is shared setup — a loaded leap-second table, a sample TLE catalogue — that multiple tests need. Instead of recreating it inside every test (duplicating code, and slow if the setup is expensive), define it once and any test that needs it declares it as a parameter; pytest supplies it automatically. If the setup logic ever changes, you change it in exactly one place.

**Parametrisation.** Testing ten unit-conversion pairs by writing ten nearly-identical functions is repetitive, and adding an eleventh case means another near-duplicate. `@pytest.mark.parametrize` lets you write the test logic once and supply a list of input/expected pairs — pytest runs the same body once per pair, reporting each separately. Adding a case becomes adding a line to a list.

**Why `==` is wrong for floats.** `0.1 + 0.2 == 0.3` is `False` in every language using standard floating point, because none of those three decimal values has an exact binary representation. A test like `assert compute() == 11.186` fails unpredictably from rounding noise even when the code is correct. `pytest.approx(11.186, rel=1e-6)` checks "is this within a small relative tolerance," which is what you actually mean by "match."

**Reference-value tests.** These are tests whose expected answer comes from an external, authoritative source — a textbook example, a published constant, a known epoch. Citing the source in the test's docstring means that if the test fails after some future refactor, you can tell whether the bug is in your code or in how you transcribed the reference value — without the citation, a failing reference test is just a mystery.

### Worked example: one fixture, one parametrized test

```
step 1 — a fixture loading something expensive once, shared across tests:
    @pytest.fixture
    def leap_second_table():
        return load_leap_seconds_from_file("data/leap_seconds.dat")

step 2 — a parametrized test using it, checking several UTC-to-TAI cases at once:
    @pytest.mark.parametrize("utc_str, expected_leap_seconds", [
        ("2015-06-30T23:59:59", 35),   # cite: IERS Bulletin C 49
        ("2017-01-01T00:00:00", 37),   # cite: IERS Bulletin C 53
        ("1999-12-31T23:59:59", 32),   # cite: IERS Bulletin C 17
    ])
    def test_leap_second_count(leap_second_table, utc_str, expected_leap_seconds):
        result = leap_second_table.count_at(parse_iso(utc_str))
        assert result == expected_leap_seconds

step 3 — pytest runs this test THREE times, once per tuple, sharing the SAME
         leap_second_table fixture each time. A failure report tells you exactly
         which of the three cases failed.
```

Write this exact pattern — one shared fixture, one parametrized test with cited values — for your own conversions before moving on. It's the template you'll reuse for the rest of the curriculum.

### Requirements

- At least 80 pytest tests across projects 1–4
- Parametrised tests per operator, unit, and time scale
- Fixtures for shared setup
- `pytest.approx`, never bare float equality
- At least 10 reference-value tests, cited in docstrings
- Round-trip tests, property tests, and error-path tests
- At least 90% coverage on `escape_velocity`, suite runs in under 10 seconds

### Definition of done

- Zero failures, zero warnings
- Coverage at or above 90%, with the uncovered lines explainable
- The suite runs fast enough that you actually run it
- At least one test written to fail first, then made to pass, so you know the tests can fail
- Reference-value tests cite their sources

### Edge cases

- Comparing quantities with different but compatible units
- Tests that need network access — marked and skippable
- Tests that need a data file — fail clearly if it's missing
- Platform-dependent floating point behaviour

### Video resources

- Search **"pytest fixtures tutorial"** and **"pytest parametrize tutorial"** for direct, runnable walkthroughs.
- Search **"floating point comparison testing"**, which connects directly to project 12.

---

## Project 12: Numerical assertion helpers and tolerance utilities

### Mental model

"These two numbers are basically equal" is subtler than it sounds. Equal within a fixed amount, or a fixed percentage? What if one of them is exactly zero? This project builds the vocabulary and tooling to make "basically equal" a precise, defensible claim rather than a hand-wave — which matters enormously once you're validating a simulator against a reference and "close enough" needs an actual number behind it.

### Concepts explained

**Absolute vs relative tolerance.** Absolute tolerance says the difference must be smaller than X — good when you know the rough scale of the numbers ("positions must agree to within 1 metre"). Relative tolerance says the difference, as a fraction of the value, must be smaller than X — good when values span wildly different magnitudes. Serious comparisons check both, passing if *either* is satisfied, which handles the case where the true value is near zero, where relative tolerance alone would demand impossible precision.

**Units in the Last Place (ULP).** Every float is a specific bit pattern. Two floats that are the smallest possible step apart are 1 ULP apart. Checking ULP distance asks "are these as close as floating point can possibly make them" — the right bar for testing that two mathematically-equivalent formulas agree to the maximum precision available, as opposed to absolute or relative tolerance, which are the right bar for physical or engineering agreement.

**Why zero needs special handling.** If the reference value is exactly zero, relative error involves dividing by zero — undefined. A robust comparison needs an explicit branch: if the reference is zero (or very close), fall back to absolute tolerance only.

### Worked example: `assert_close` with proper zero-handling

```
function assert_close(actual, expected, abs_tol=1e-8, rel_tol=1e-6):
    diff = abs(actual - expected)

    if expected == 0:
        if diff > abs_tol:
            raise AssertionError(f"expected ~0, got {actual}, error {diff} exceeds abs_tol")
        return

    relative_error = diff / abs(expected)

    if diff <= abs_tol or relative_error <= rel_tol:
        return

    raise AssertionError(
        f"expected {expected}, got {actual}\n"
        f"  absolute error = {diff} (tolerance {abs_tol})\n"
        f"  relative error = {relative_error} (tolerance {rel_tol})\n"
        f"  neither tolerance was satisfied"
    )
```

Trace three cases by hand: `(1000000.1, 1000000.0)` should pass on relative tolerance even though the absolute error looks large; `(0.0000001, 0.0)` should be checked against `abs_tol` only, since the expected value is zero; `(5.001, 5.0)` should pass easily on both. Running these by hand is what makes the "pass if *either*" logic actually make sense.

### Requirements

- `assert_close` with independent absolute and relative tolerances, and a message reporting both errors achieved
- ULP-based comparison using `math.ulp`
- Array comparison reporting the index and magnitude of the worst disagreement
- Detection and clear reporting of NaN and infinity
- Sensible behaviour when the reference value is zero

### Definition of done

- Used by the test suite from project 11 onward wherever more detail than `pytest.approx` is useful
- A failure message reports achieved absolute error, relative error, and ULP distance
- Handles a reference value of exactly zero without a division error
- Documented with a note on when to use absolute versus relative tolerance

### Edge cases

- Reference value of zero
- Both values NaN
- Positive and negative zero
- Denormal numbers near the underflow limit
- Arrays of different shapes

### Video resources

- Search **"floating point arithmetic explained"** — Computerphile's video is an excellent starting point.
- Search **"machine epsilon explained"** for what `sys.float_info.epsilon` represents.
- Search **"numpy testing assert_allclose"** as a mature design reference.

---

## Project 13: Bash toolkit for scientific workflows

### Mental model

Every cluster, every remote server, every CI system you'll ever touch is ultimately a shell prompt. Building a small toolkit of scripts now is less about the specific scripts and more about becoming fluent in a language you cannot avoid — like learning to read a map matters more than memorising any one route.

### Concepts explained

**`set -euo pipefail`, explained.** By default, bash is dangerously forgiving: a failed command doesn't stop the script, an undefined variable silently expands to empty string, and a failure in the middle of a pipe is invisible if the last command in it succeeds. `set -e` exits immediately on any nonzero exit code. `set -u` makes referencing an undefined variable an error, catching typos. `set -o pipefail` makes a pipeline's exit code reflect the first failing command, not just the last. Together they turn bash from "keeps going no matter what" into "stops loudly the moment something's wrong" — what you want for anything unattended.

**Quoting, and the actual failure mode.** `$variable` without quotes gets word-split on whitespace before use, so a path like `/home/user/my results/` silently becomes two arguments. Always writing `"$variable"` prevents this. This single habit prevents the majority of real-world bash bugs.

**Why `shellcheck` is worth running on everything.** Bash allows a lot of subtly wrong things that look fine at a glance. `shellcheck` is a static analyser catching these specific known-dangerous patterns and explaining, in plain English, why each is a problem — an automated, patient teacher for exactly the mistakes otherwise learned the hard way in production at 2am.

### Worked example: a defensively-written cleanup script, annotated

```
#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: clean_runs.sh <directory> <days>"
    exit 2
}

if [[ $# -ne 2 ]]; then
    usage
fi

target_dir="$1"
days="$2"

if [[ ! -d "$target_dir" ]]; then
    echo "error: '$target_dir' is not a directory" >&2
    exit 1
fi

# find candidates FIRST, show them, confirm, THEN delete —
# never delete based on a single unreviewed command
mapfile -t candidates < <(find "$target_dir" -maxdepth 1 -type d -mtime "+${days}")

if [[ ${#candidates[@]} -eq 0 ]]; then
    echo "nothing to clean"
    exit 0
fi

echo "the following ${#candidates[@]} directories will be removed:"
printf '  %s\n' "${candidates[@]}"
read -r -p "proceed? [y/N] " confirm
if [[ "$confirm" != "y" ]]; then
    echo "aborted"
    exit 0
fi

for dir in "${candidates[@]}"; do
    rm -rf -- "$dir"
    echo "removed: $dir"
done
```

Every variable is quoted, `$#` is checked before use, existence is checked before anything destructive, and candidates are listed and confirmed before deletion, not deleted inline as they're found. Run `shellcheck` on your own version and read every warning — each one teaches a specific failure mode.

### Requirements

- Six scripts: `run_sweep.sh`, `archive_results.sh`, `sync_results.sh`, `env_check.sh`, `clean_runs.sh`, `watch_run.sh`
- Every script starts with `set -euo pipefail` and has a usage function
- Every script handles no-argument invocation with usage and exit code 2
- `shellcheck`-clean

### Definition of done

- Every script passes `shellcheck` with no warnings
- A sweep of ten configurations runs unattended and logs each separately
- The archive script produces something someone else could understand
- Scripts work with paths containing spaces
- All scripts are executable, documented, and used at least once for real

### Edge cases

- Paths containing spaces or unicode
- A command failing midway through a sweep — decide and document whether to continue or abort
- Disk full during archiving
- Running from an unexpected working directory
- macOS vs Linux differences in `sed` and `date`

### Video resources

- Search **"bash strict mode set -euo pipefail explained"** for the specific settings.
- Search **"shellcheck tutorial"** for demonstrations of real bugs it catches.

---

## Project 14: Linux environment built from scratch

### Mental model

Your dotfiles and SSH setup are the environment you'll carry to every machine you ever work on. Building this once, deliberately, and keeping it in version control turns "set up a new machine" into a five-minute solved problem, forever, instead of an hour of half-remembered fixes.

### Concepts explained

**PATH, concretely.** Typing `python` doesn't magically resolve — the shell searches a list of directories, in order, stored in `PATH`, and runs the *first* matching executable found. If `/usr/bin` (system Python) comes before your version manager's directory in `PATH`, typing `python` runs the system one regardless of what you meant — the fix is reordering `PATH`, and `which python` is how you diagnose which one actually won.

**Login vs interactive shells.** A login shell — one started as part of logging in, such as over SSH — reads `.profile` or `.bash_profile`. An interactive shell — one where you're actively typing commands — reads `.bashrc`. A shell can be both, neither, or one of these, and each reads a different subset of startup files. Put a `PATH` change only in `.bashrc` and it works fine in a new terminal but might be missing over SSH, which is exactly the "works on my machine, broken over SSH" bug this project inoculates against.

**SSH key authentication.** Instead of a password, SSH authenticates with a matched key pair: a private key kept secret, and a public key placed on the remote machine. Connecting, the server challenges your client to prove it holds the private key matching a public key on file, using math that never requires the private key to leave your machine. An `ssh-agent` holds your decrypted private key in memory for a session, so you type your passphrase once rather than every connection.

### Worked example: diagnosing a broken PATH

```
step 1 — python3 gives an unexpected version. Ask which one is running:
    $ which python3
    /usr/bin/python3          # system python, not the one you wanted

step 2 — inspect PATH directly:
    $ echo $PATH
    /usr/local/bin:/usr/bin:/bin:/home/you/.pyenv/shims
    # /usr/bin comes BEFORE the version manager's shims, so system python always wins

step 3 — fix by ensuring the version manager's shims directory is prepended LAST,
         so it ends up FIRST in the final value — this typically means its init
         lines belong near the END of .bashrc, after other PATH modifications:
    export PATH="$HOME/.pyenv/shims:$PATH"

step 4 — verify in a NEW shell (existing shells don't see .bashrc changes):
    $ source ~/.bashrc
    $ which python3
    /home/you/.pyenv/shims/python3     # correct now
```

The habit worth keeping: whenever a tool "isn't working" and PATH is suspected, `which <command>` is always the first diagnostic step, before touching any config file.

### Requirements

- A dotfiles repository under git: `.bashrc` or `.zshrc`, `.gitconfig`, editor config, `.ssh/config`
- An install script that symlinks dotfiles into place, safe to re-run
- Ed25519 SSH keys, passphrase-protected, with the agent configured
- Named SSH host entries
- A Python version manager chosen deliberately, with the reasoning written down
- Verified by bootstrapping a fresh container or VM

### Definition of done

- A fresh container reaches a working environment with one command
- You can SSH to a remote host by name with no password and no key errors
- You can explain, unprompted, why `.bashrc` isn't read by a login shell
- Dotfiles are on GitHub and have been restored from at least once
- The decisions note explains the Python version manager choice and what was rejected

### Edge cases

- Key permissions that are too open, which SSH silently refuses
- Login vs non-login vs interactive shells, and their different startup files
- PATH ordering where a system tool shadows the intended one
- Different behaviour between bash and zsh

### Video resources

- Search **"MIT missing semester shell tools"** — the single best resource for this whole project.
- Search **"SSH keys explained"** for the public/private key handshake.
- Search **"bashrc vs bash_profile vs profile"** for the login-shell distinction.

---

## Project 15: Git fluency drill

### Mental model

You already use git the way most people use a car's forward gear — commit, push, repeat. This project is reverse, the handbrake, and the dashboard, because a maintainer reviewing your first open source pull request will expect a clean, rebased history, not a diary of every false start.

### Concepts explained

**Interactive rebase.** `git rebase -i` opens your recent commits in a text editor, each prefixed with a command word. Changing `pick` to `squash` merges a commit into the one above; `reword` edits just the message; `drop` removes a commit; reordering lines reorders commits. This is how "fix typo," "actually fix typo," "oops," "real implementation" becomes one or two commits telling a coherent story. Git replays your commits onto a new base, applying your edits, pausing to ask for help if a replay conflicts with what's already there.

**`git bisect`.** If a bug exists now but not at some earlier commit, checking each commit by hand between them is slow. Marking a known-good and known-bad commit makes git perform a binary search: it checks out the midpoint, you test and report `good` or `bad`, and it halves the remaining range — finding the culprit in roughly log₂(N) steps instead of N. `git bisect run <script>` automates the whole search if you have a script that exits nonzero exactly when the bug is present.

**The reflog.** Every time `HEAD` moves — through commits, checkouts, resets, rebases — git records that movement in the reflog, separate from the commit graph. Even after `reset --hard` seemingly destroys commits, they aren't actually gone until garbage collection eventually runs, which isn't immediate. `git reflog` shows where `HEAD` used to point, and checking out that SHA gets you back. This is the single most valuable recovery tool in git, and knowing it exists removes most of the fear around rebasing.

### Worked example: a bisect session, traced step by step

```
step 1 — tests pass at tag v0.3.0 but fail on main right now.
    $ git bisect start
    $ git bisect bad HEAD
    $ git bisect good v0.3.0

step 2 — git checks out a commit roughly halfway between. Test it:
    $ pytest tests/test_units.py     # suppose it PASSES

step 3 — tell git this midpoint was good, narrowing the search:
    $ git bisect good

step 4 — git checks out a new midpoint. Test again:
    $ pytest tests/test_units.py     # suppose it FAILS

step 5 — tell git this was bad:
    $ git bisect bad

    ... repeat roughly log2(number of commits) times ...

step 6 — git reports the first bad commit and shows its diff.

step 7 — clean up: git bisect reset
```

With a scripted test, steps 2–6 collapse into `git bisect run pytest tests/test_units.py` — worth doing both the manual and automated versions once each, so the automation isn't a black box.

### Requirements

- Interactive rebase: squash, reword, reorder, drop, split a commit
- Resolve a genuine three-way merge conflict by hand
- Use `git bisect`, with an automated bisection script
- Recover a deleted branch and commit via `git reflog`
- Use `git stash`, `cherry-pick`, `revert`, knowing when each applies
- A working `.gitignore` and `.gitattributes`
- Commit messages in the conventional form: imperative subject under 50 characters, blank line, body explaining why
- Signed commits

### Definition of done

- Bisect finds a real bug in your own toolkit history
- A five-commit branch is rebased into two clean commits without looking up syntax
- A deliberately destroyed commit is recovered using only the reflog
- Commit history has messages you wouldn't be embarrassed to have reviewed
- Commits show as verified on GitHub

### Edge cases

- A conflict in a binary file, which cannot be merged by hand
- Rebasing an already-pushed branch, and why that's dangerous for shared branches
- A detached HEAD state, and how to get out of it
- Large files or credentials committed by accident

### Video resources

- **learngitbranching.js.org** — an interactive visual trainer, better than most videos for building the mental model.
- Search **"git rebase interactive tutorial"** and **"git bisect tutorial"** for focused walkthroughs.
- Search **"oh shit git explained"** for a walkthrough of common recovery scenarios.

---

## Project 16: Data downloader with caching, retries, and rate limits

### Mental model

Every public data source you'll touch — Celestrak, Horizons, NOAA — is a shared resource with limits, and sometimes flaky. A naive `requests.get(url)` works great until it fails silently the third time, gets you rate-limited, or re-downloads a two-gigabyte file you already had. This project builds the well-behaved, patient client that treats those failures as expected, not exceptional.

### Concepts explained

**Exponential backoff with jitter.** If a request fails with "server busy," retrying immediately makes it worse — especially with many clients doing the same thing at once. Exponential backoff waits progressively longer between retries. Jitter adds a small random amount to each wait specifically to desynchronise multiple clients that might otherwise retry in lockstep and overwhelm a recovering server together.

**Conditional requests.** When a server sends a file, it can include an `ETag` — a fingerprint of that file's content. Next time, you send that ETag back, asking "has this changed?" If not, the server responds with a cheap 304 Not Modified and no body, saving both sides the cost of retransferring unchanged data.

**Why streaming matters for large files.** Loading the entire response into memory is fine for a small TLE file, catastrophic for a multi-gigabyte scene. Streaming lets you process the response in small chunks as they arrive, writing each straight to disk, so peak memory stays roughly constant regardless of total file size.

### Worked example: backoff with jitter, computed by hand

```
function backoff_delay(attempt_number, base=1.0, max_delay=60.0):
    exponential = base * (2 ** attempt_number)
    capped = min(exponential, max_delay)
    jitter = random_uniform(0, capped * 0.5)
    return capped + jitter

attempt 0: exponential=1.0,  capped=1.0,  jitter in [0,0.5],  delay ~1.0-1.5s
attempt 1: exponential=2.0,  capped=2.0,  jitter in [0,1.0],  delay ~2.0-3.0s
attempt 2: exponential=4.0,  capped=4.0,  jitter in [0,2.0],  delay ~4.0-6.0s
attempt 3: exponential=8.0,  capped=8.0,  jitter in [0,4.0],  delay ~8.0-12.0s
```

The delay roughly doubles each attempt (exponential) while also having a random component (jitter) that spreads out simultaneous retries from multiple clients. The `max_delay` cap prevents the wait from growing to absurd lengths after many failures.

### Requirements

- GET with configurable timeout and a descriptive User-Agent
- Exponential backoff with jitter on 429, 500, 502, 503, 504, respecting `Retry-After`
- On-disk cache keyed by URL hash with a configurable TTL
- Conditional requests using ETag and If-Modified-Since
- Rate limiting: a minimum interval between requests to the same host
- Checksum verification where the source publishes one
- Streaming download for large files
- Resume interrupted downloads using range requests
- Wrappers for Celestrak, Horizons, NOAA SWPC

### Definition of done

- Fetches and caches the full Celestrak catalogue; a second call within the TTL makes no network request
- A simulated 429 triggers backoff with the right delays, tested against a mocked server
- A large file downloads by streaming with flat process memory
- An interrupted download resumes rather than restarting
- The full test suite runs offline against the cache
- Rate limiting is verifiably respected

### Edge cases

- No network at all
- DNS failure vs connection refused vs timeout — different problems
- A server returning HTML error pages with status 200
- Redirects, including redirect loops
- Cache corruption — a partial file must not be treated as valid
- Sources requiring authentication, with credentials from the environment, never source code

### Video resources

- Search **"exponential backoff and jitter explained"** for the AWS-style reasoning behind the technique.
- Search **"Python requests tutorial"** for the library basics.
- Search **"HTTP caching ETags explained"** for conditional requests.

---

## Project 17: HDF5 and NetCDF reader and writer

### Mental model

A CSV file is a flat grid. Real simulation output is rarely flat — it's a multi-dimensional array, often too big for memory, with metadata that needs to travel *with* the data rather than live in a README that gets lost. HDF5 is a self-describing container built exactly for this: a filesystem-within-a-file, with folders (groups), files (datasets), and sticky notes (attributes) bundled into one portable file.

### Concepts explained

**Groups, datasets, attributes.** Groups are folders; datasets are the actual multi-dimensional arrays; attributes are small metadata attached to a group or dataset — units, a description, the git commit that produced the file.

**Chunking, and its real consequence.** By default you might imagine a dataset as one contiguous disk block. HDF5 instead stores it in chunks, each compressed and addressed independently. If you plan to read one full timestep at a time, chunking along the time axis means reading one timestep touches exactly one chunk. If chunks instead span all time for a handful of particles, reading one timestep would touch many small pieces of nearly every chunk — dramatically slower. The right shape depends entirely on the intended access pattern, which is why you're asked to measure, not just assume.

**Why NetCDF sits on top of HDF5.** NetCDF-4 is, underneath, an HDF5 file with an added layer of conventions — standardised names for coordinate variables (time, latitude, longitude) and metadata conventions (the CF conventions) that let tools like `xarray` automatically understand your data. Reach for raw HDF5 for full control over your own simulation output; reach for NetCDF when the data has a natural time/lat/lon grid and needs to interoperate with the Earth-science tooling ecosystem you'll lean on in Phase 9.

### Worked example: reasoning through a chunk shape choice

```
Scenario: N-body output, shape (10000 timesteps, 500 particles, 3 dims).
Primary use: read ONE FULL TIMESTEP at a time (rendering an animation frame by frame).

option A — chunk shape (1, 500, 3):
    each chunk = one timestep, all particles, all dims.
    reading one timestep touches EXACTLY one chunk — fast for this pattern.
    downside: reading one particle's FULL trajectory across all time touches
    10000 separate chunks — slow for THAT pattern.

option B — chunk shape (100, 500, 3):
    each chunk = 100 consecutive timesteps.
    reading one timestep still touches only one chunk.
    slightly more overhead per read if access is truly random-access single
    timesteps, since decompressing a larger chunk for one small slice costs more.

decision: since access is primarily sequential single-timestep reads, option B with
a modest size (50-100 timesteps) balances efficient sequential decompression against
wasteful over-decompression for isolated lookups. Document the reasoning, then MEASURE
actual read patterns and let the numbers, not the theory alone, settle it.
```

There is no universally correct chunk shape — the right answer depends on access pattern, and you're expected to measure rather than assume.

### Requirements

- Write simulation output as HDF5: datasets, groups, attributes for metadata
- Store the config hash and git commit from project 9 as file-level attributes
- Chunking chosen deliberately for the expected access pattern, with reasoning documented
- Compression with gzip or lzf, with size/speed trade-off measured
- Append to an existing file incrementally
- Read back partially: one variable, or a slice, without touching the rest
- The equivalent for NetCDF, noting CF-convention differences

### Definition of done

- Produces a file someone else can understand without your code, verified with `h5dump` or HDFView
- A slice read from a gigabyte file is fast and doesn't load the whole file, timed and reported
- Chunk shape choice is documented with a measurement showing it beats the default for your pattern
- Round-trip preserves every value bit for bit

### Edge cases

- Very large datasets exceeding memory
- Variable-length strings, which HDF5 handles awkwardly
- A file left open by a crashed process
- Chunk shapes that don't divide the dataset shape evenly
- NaN and infinity values, which survive HDF5 but may confuse downstream tools

### Video resources

- Search **"HDF5 tutorial python h5py"** for groups, datasets, and attributes with runnable examples.
- Search **"HDF5 chunking explained"** for the performance implications specifically.
- Search **"xarray netcdf tutorial"**, useful groundwork for Phase 9.

---

## Project 18: FITS file reader and header explorer

### Mental model

FITS has been astronomy's standard format since 1981 — older than most software you use daily — and it's still universal because it solved a real problem well: a self-describing, human-readable-header format for scientific images and tables that any telescope or archive can read without ambiguity. Learning to read one by hand, not only through `astropy.io.fits`, means that when an unfamiliar survey's data looks wrong, you know how to investigate rather than just trusting a library.

### Concepts explained

**The header.** A FITS header is a sequence of fixed-width 80-character cards, typically `KEYWORD = value / comment`. Every file must start with mandatory keywords: `SIMPLE` (is this valid FITS), `BITPIX` (the integer or float type used), `NAXIS` (how many dimensions), and one `NAXISn` per dimension giving its size. These handful of keywords alone tell you how to interpret the raw bytes that follow.

**`BSCALE`/`BZERO`.** FITS commonly stores image data as integers, even though the underlying physical quantity is naturally real-valued, because integers take less space. `BSCALE` and `BZERO` give the linear conversion: `physical_value = raw_integer * BSCALE + BZERO`. This lets a file store compact integers while still representing negative values or a wide dynamic range — the header carries what's needed to convert back, so the compression trick is fully reversible.

Note the specific convention: FITS defines `BITPIX = 8` as *already unsigned* (0–255), so it needs no offset trick. It's `BITPIX = 16` (and 32, 64), which FITS defines as *signed*, where representing an effectively-unsigned range requires the classic `BZERO = 32768` offset — shifting a signed 16-bit range up to cover 0–65535. Getting this pairing right (`BZERO = 32768` goes with `BITPIX = 16`, not `BITPIX = 8`) is worth being precise about, since it's an easy mix-up.

**Binary table extensions.** Beyond images, a FITS file can hold tables — a spreadsheet embedded in the file, with named, typed columns (`TIME`, `FLUX`, `FLUX_ERR` for a light curve). Each column's type and unit are declared via header keywords specific to that extension. A single file often contains multiple extensions — a primary header with no data, an image extension, a table extension — which is why you enumerate and handle multiple HDUs rather than assuming exactly one.

### Worked example: computing a physical value from a raw integer

```
Header:
    BITPIX = 16          (16-bit signed integers)
    BSCALE = 0.01
    BZERO  = 0.0
    BUNIT  = 'ADU'

Raw stored pixel value: 4523

    physical_value = raw_integer * BSCALE + BZERO
                    = 4523 * 0.01 + 0.0
                    = 45.23   ADU

A second example, showing the effectively-unsigned trick correctly paired with BITPIX=16:

    BITPIX = 16
    BSCALE = 1.0
    BZERO  = 32768        # shifts signed 16-bit range up to cover 0-65535

    raw_integer = -1000    (as actually stored, signed)
    physical_value = -1000 * 1.0 + 32768 = 31768
```

Never assume a raw integer read from a FITS array is already the physical value — always check `BSCALE`/`BZERO` first. They default to 1.0/0.0 (no scaling) if absent, but check, don't assume.

### Requirements

- Open a FITS file and enumerate its header-data units
- Parse header cards into a structured mapping, preserving comments and order
- Handle mandatory keywords: `SIMPLE`, `BITPIX`, `NAXIS`, and extension keywords
- Read image data with the correct dtype from `BITPIX`, applying `BSCALE` and `BZERO`
- Read binary table extensions, including column names, formats, units
- Summarise the world coordinate system keywords
- Handle multi-extension files
- A pretty-printed header dump wired into the `ev` CLI

### Definition of done

- Opens a real Kepler or TESS light curve file from MAST and correctly reports every extension
- Your parsed header matches `astropy.io.fits` card-for-card on at least five real files
- Image data with nontrivial `BSCALE`/`BZERO` reads back to correct physical values
- A binary table extension reads with correct column types and units
- The header dump is genuinely useful for inspecting an unfamiliar file

### Edge cases

- Files with nonstandard or missing mandatory keywords
- `HIERARCH` cards for keywords longer than eight characters
- `CONTINUE` cards for long string values
- Compressed image extensions
- Very large images that should be memory-mapped rather than loaded

### Video resources

- Search **"FITS file format explained astronomy"** for a structural overview.
- Search **"astropy.io.fits tutorial"** for a reference implementation to compare against.
- Search **"World Coordinate System astronomy WCS explained"** for the projection piece.

---

## When Phase 0 is finished

Not eighteen checkboxes — this combination:

- `escape_velocity` installs with `pip install -e` and imports cleanly on a fresh machine
- `pytest` passes with at least 90% coverage and runs in under 10 seconds
- The `ev` CLI works from any directory, with genuinely useful help text
- You can fetch a live TLE from Celestrak, parse it, convert its epoch across four time scales, and report position in three coordinate frames, using only your own code
- You can fetch an Earth ephemeris from JPL Horizons and interpolate a position at an arbitrary instant
- Every module has a docstring you wouldn't be embarrassed to have reviewed
- The build log has an entry for every week, including the bad ones

One last thing worth saying plainly. The goal of this document isn't that you never search anything again — professional engineers look things up constantly. The goal is that when you do search, you already have the vocabulary and the mental model to recognise whether what you found is actually correct. That's what the concept explanations and worked examples above are for. That skill is what the rest of the curriculum runs on.
