# escape-velocity

**A 300-project route from software engineering to computational science: space systems, Earth observation, and high performance computing.**

![Progress](https://img.shields.io/badge/progress-0%2F300-lightgrey)
![Stage](https://img.shields.io/badge/stage-1%20of%206-blue)
![Started](https://img.shields.io/badge/started-August%202026-blue)

---

Escape velocity is the speed you need to leave a gravity well for good. Below it, you fall back no matter how hard you burn.

I am a software engineering student at African Leadership University in Kigali, from Cameroon, working toward becoming a computational scientist in simulations, astrophysics and space technology. There is a gap between where that starts and where it becomes self-sustaining, and this repository is my route across it, in public, with the evidence attached as it appears.

**Day one is August 2026. Nothing here is built yet.** That is deliberate. A repository that starts empty and visibly fills up is a more honest record than one that arrives finished, and the log below is the point of the whole thing.

---

## Build log

Newest first. One entry per week, whether or not the week went well.

<!--
Format: ### YYYY-MM-DD
Then two or three bullets. Include the weeks where nothing shipped, and say why.
An honest gap is more credible than a silent one.
-->

### Week 0, August 2026
- Repository created. Curriculum rebuilt from a 300-project draft that taught computer science well and computational science badly.
- Starting Stage 1, project 1: scientific units and dimensions library.

## Shipped

Nothing yet. A project appears in this table only when all five rules below are true for it.

| # | Project | Phase | Code | Live | Validation |
|---|---------|-------|------|------|------------|
| | | | | | |

## The five rules

A project is not finished when the code runs. It is finished when all five of these are true.

1. **Real data, never synthetic.** Kepler light curves, Celestrak TLEs, JPL Horizons ephemerides, Sentinel-2 scenes, Gaia catalogues, NOAA feeds.
2. **Validated against a reference.** An error plot against ground truth or a published value, with the tolerance stated.
3. **Tested and continuously integrated.** pytest or ctest, a GitHub Actions workflow, a visible badge.
4. **Documented for a stranger.** Physics, method, assumptions, limitations, and one command that regenerates every figure.
5. **Published where someone can reach it.** Streamlit, PyPI, crates.io, or Zenodo with a DOI. A private repository is not a portfolio.

Twenty projects built to these five rules are worth more than three hundred built without them. The count is not the goal. The count is the map.

## Two orderings, and why

**The phase order** is the reference structure: thirteen coherent bodies of knowledge, numbered 1 to 300. Use it to find where a topic lives.

**The stage order** is the actual route: six stages that cut across phases so that every stage touches foundations, something physical, and something publishable at the same time. Working straight through 1 to 300 would mean eighteen months of toolkit before producing anything showable, and the deadlines that matter do not wait that long. Use it to decide what to do next.

Open [`tracker/index.html`](tracker/index.html) in a browser to switch between the two views and record progress. Progress is stored locally in the browser, so export it regularly.

## The route

| Stage | Window | Draws from | What must exist at the end |
|-------|--------|-----------|----------------------------|
| 1. Instrument yourself | Months 1 to 6 | Toolkit, C fundamentals, numerical core, testing, first orbits | A pip-installable toolkit, first C programs, and a propagator validated against JPL Horizons |
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

Projects 293 and 294, the open source contributions, are not stage bound. They run continuously from month three, because a merged pull request takes calendar time rather than effort time, and it is the only item here that is externally verified.

## Current focus

<!-- Update this every week. It is the first thing a returning visitor reads, and a stale one reads as abandonment. -->

**Stage 1, Phase 0.** Building the scientific toolkit that every later project imports.

- **Now:** project 1, scientific units and dimensions library
- **Next:** project 2, physical constants with uncertainties
- **Compiled track:** not started. First C project is number 19
- **Open source:** choosing a package to follow. Candidates: astropy, lightkurve, skyfield, python-sgp4

## Specifications

Full specifications live in [`docs/specs/`](docs/specs/). Each one states what you are building, what it teaches, where to find the reference material, what the edge cases are, and the definition of done.

Specifications are written one block ahead of where I am working rather than all at once, because a specification written three years before it is needed is written against the wrong understanding of the problem.

- [x] Phase 0, projects 1 to 18
- [ ] Phase 1, projects 19 to 46
- [ ] Phase 2, projects 47 to 78

## Repository structure

```
escape-velocity/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── curriculum.pdf           # the full 300-project specification
│   ├── specs/                   # detailed per-project specs, written a block ahead
│   └── decisions/               # short notes on why the plan changed and when
├── tracker/
│   └── index.html               # interactive progress tracker
├── toolkit/                     # the installable package built across Phase 0
│   ├── pyproject.toml
│   ├── src/evkit/
│   └── tests/
├── phase-01-compiled/           # one directory per project from here on
├── phase-02-numerics/
├── phase-03-software/
├── phase-04-mechanics/
├── phase-05-astrodynamics/
├── phase-06-gnc/
├── phase-07-hpc/
├── phase-08-ml/
├── phase-09-earth-observation/
├── phase-10-physics/
├── phase-11-astronomy/
├── phase-12-capstones/
├── writeups/                    # monthly technical notes
└── scripts/
```

Larger projects graduate into their own repositories once they are worth installing or deploying, and get linked from the shipped table rather than staying nested here. This repository is the index and the log, not a monolith.

## How I work

- One project at a time per track, and never more than three tracks at once.
- No AI-generated code in this repository. Explanation and review are fine, generated solutions are not. The point is the learning, and outsourcing it defeats the exercise.
- Every project starts by writing its definition of done, before any code.
- Weekly entry in the build log, including the weeks where nothing shipped.

## Why this version, and not the first draft

The first draft contained three hundred projects that taught computer science well and computational science badly. Out of three hundred entries, two touched a compiled language, open source contribution sat at project 294, and not a single project required validating a simulation against a reference.

The rebuild kept the count and changed what the projects produce.

- Compiled languages went from 2 projects to 28. ICTP MHPC requires C, C++ or Fortran. Flight software in this sector is C or C++, increasingly Rust.
- High performance computing went from 2 projects to 22, ending in a written performance report rather than a working script.
- Guidance, navigation and control went from roughly 4 projects to 18.
- Ten verification projects were added across numerics and astrodynamics. A simulator without a validation plot is an animation.
- Thirteen social applications were replaced with Earth observation work, because the mission was right and the medium was wrong.

Nothing was cut for being difficult. Things were cut for producing nothing anyone would read.

## License

Code is released under the MIT License. Curriculum text and write-ups are released under CC BY 4.0. Use any of it, and tell me if it helps.

## Contact

Stephane Tchatchum, BSc Software Engineering, African Leadership University, Kigali.

[email] · [LinkedIn] · [portfolio]

---

*Participate in new discoveries, and develop my continent.*