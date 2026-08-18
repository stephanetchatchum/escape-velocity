# delta-v

**A 300-project route from software engineering to computational science: space systems, Earth observation, and high performance computing.**

![Progress](https://img.shields.io/badge/progress-0%2F300-blue)
![Stage](https://img.shields.io/badge/stage-1%20of%206-blue)
![Focus](https://img.shields.io/badge/current%20focus-orbit%20propagator%20validation-orange)

---

In orbital mechanics, delta-v is the budget of velocity change a spacecraft can afford. It is finite. Every burn you spend on a maneuver that does not take you somewhere is a burn you cannot spend on one that does.

That is the whole idea behind this repository. I am a software engineering student at African Leadership University in Kigali, working toward becoming a computational scientist in simulations, astrophysics and space technology. This is the route I am taking, in public, with the evidence attached.

---

## Completed work

This is the part that matters. Everything below this section is a plan. This section is what actually exists.

| # | Project | Phase | Code | Live | Validation |
|---|---------|-------|------|------|------------|
| 128 | Two-body orbit propagator | Astrodynamics | [repo](#) | [demo](#) | [Horizons error plot](#) |
| 217 | Exoplanet transit classifier | ML for Science | [repo](#) | [demo](#) | [metrics](#) |

<!--
Add a row only when all five rules below are true for that project.
Delete this comment block once the table has real entries.
-->

## The five rules

A project is not finished when the code runs. It is finished when all five of these are true.

1. **Real data, never synthetic.** Kepler light curves, Celestrak TLEs, JPL Horizons ephemerides, Sentinel-2 scenes, Gaia catalogues, NOAA feeds.
2. **Validated against a reference.** An error plot against ground truth or a published value, with the tolerance stated.
3. **Tested and continuously integrated.** pytest or ctest, a GitHub Actions workflow, a visible badge.
4. **Documented for a stranger.** Physics, method, assumptions, limitations, and one command that regenerates every figure.
5. **Published where someone can reach it.** Streamlit, PyPI, crates.io, or Zenodo with a DOI. A private repository is not a portfolio.

Twenty projects built to these five rules are worth more than three hundred built without them.

## How to read this repository

There are two orderings, and they answer different questions.

**The phase order** is the reference structure: thirteen coherent bodies of knowledge, numbered 1 to 300. Use it to find where a topic lives.

**The stage order** is the actual route: six stages that cut across phases so that every stage touches foundations, something physical, and something publishable at the same time. Working straight through 1 to 300 would mean eighteen months of toolkit before reaching anything showable. Use it to decide what to do next.

Open [`tracker/index.html`](tracker/index.html) in a browser to switch between the two views and record progress. Progress is stored locally in the browser, so export it regularly.

## The route

| Stage | Window | Draws from | What must exist at the end |
|-------|--------|-----------|----------------------------|
| 1. Instrument yourself | Months 1 to 6 | Toolkit, C fundamentals, numerical core, testing, first orbits | A pip-installable toolkit, first C programs, and a propagator with a Horizons validation plot |
| 2. Compiled languages and mechanics | Months 7 to 12 | C++, verified integrators, classical mechanics, reproducibility | A C++ N-body that beats the Python one, and a reproducible research repository |
| 3. Astrodynamics and first parallel code | Months 13 to 19 | Rest of astrodynamics, OpenMP and MPI basics, Earth observation fundamentals | A complete mission design toolkit and a first scaling study |
| 4. GNC, flight software and HPC | Months 20 to 26 | Guidance and control, advanced HPC, data engineering | A 6-DOF ADCS loop, embedded C on hardware, an MPI scaling report, a JOSS submission |
| 5. Science applications | Months 27 to 34 | Machine learning, payload engineering, astronomy data | Machine learning on real archives, and a published technical write-up |
| 6. Depth and capstones | Months 35 onward | Advanced computational physics, integration | Three capstones that use everything above |

## The thirteen phases

| Phase | Focus | Projects | Done |
|-------|-------|----------|------|
| 0 | Programming Foundations, Rebuilt | 1 to 18 | 0/18 |
| 1 | Compiled Languages and Systems Programming | 19 to 46 | 0/28 |
| 2 | Mathematical and Numerical Foundations | 47 to 78 | 0/32 |
| 3 | Scientific Software Engineering and Data | 79 to 102 | 0/24 |
| 4 | Classical Mechanics and Dynamics | 103 to 124 | 0/22 |
| 5 | Orbital Mechanics and Astrodynamics | 125 to 154 | 0/30 |
| 6 | Guidance, Navigation, Control and Flight Software | 155 to 172 | 0/18 |
| 7 | High Performance Computing | 173 to 194 | 0/22 |
| 8 | Machine Learning for Science | 195 to 226 | 0/32 |
| 9 | Earth Observation and Remote Sensing | 227 to 250 | 0/24 |
| 10 | Computational Physics and Advanced Methods | 251 to 276 | 0/26 |
| 11 | Astronomy Data and Research Practice | 277 to 292 | 0/16 |
| 12 | Open Source, Publication and Capstones | 293 to 300 | 0/8 |

Projects 293 and 294, the open source contributions, are not stage bound. They run continuously from month three, because a merged pull request takes calendar time rather than effort time and it is the only item here that is externally verified.

## Current focus

<!-- Update this section every week. It is the first thing a returning visitor reads. -->

**Stage 1.** Building the scientific toolkit and closing the compiled-language gap.

- In progress: project 128, two-body orbit propagator
- Next: project 129, validation against JPL Horizons
- Also running: project 19, memory model explorer in C
- Open source: reading open issues in [package name]

## Repository structure

```
delta-v/
├── README.md
├── docs/
│   ├── curriculum.pdf          # the full 300-project specification
│   └── decisions/              # short notes on why the plan changed
├── tracker/
│   └── index.html              # interactive progress tracker
├── toolkit/                    # the reusable library built in Phase 0
│   ├── units/
│   ├── timescales/
│   ├── frames/
│   └── tle/
├── phase-01-compiled/
├── phase-02-numerics/
├── ...
└── writeups/                   # monthly technical notes
```

Larger projects live in their own repositories and are linked from the completed work table rather than nested here. This repository is the index and the log, not a monolith.

## Why this version, and not the first one

The first draft of this curriculum contained three hundred projects that taught computer science well and taught computational science badly. Out of three hundred entries, two touched a compiled language, open source contribution sat at project 294, and not a single project required validating a simulation against a reference.

The rebuild kept the count and changed what the projects produce.

- Compiled languages went from 2 projects to 28. ICTP MHPC requires C, C++ or Fortran. Flight software in the sector is C or C++, increasingly Rust.
- High performance computing went from 2 projects to 22, ending in a written performance report rather than a working script.
- Guidance, navigation and control went from roughly 4 projects to 18.
- Ten verification projects were added across numerics and astrodynamics. A simulator without a validation plot is an animation.
- Thirteen social applications were replaced with Earth observation work, because the mission was right and the medium was wrong.

Nothing was cut for being difficult. Things were cut for producing nothing anyone would read.

## License

Code in this repository is released under the MIT License. The curriculum text and write-ups are released under CC BY 4.0. Use any of it, and tell me if it helps.

## Contact

Stephane Tchatchum, BSc Software Engineering, African Leadership University, Kigali.

[email] · [LinkedIn] · [portfolio]

---

*Participate in new discoveries, and develop my continent.*