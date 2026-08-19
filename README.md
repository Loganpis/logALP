# logALP

**A reproducible benchmark suite for comparing weak-mixing photon-ALP propagation across controlled and simulation-derived magnetic-field sightlines**

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-pytest-informational.svg)](tests/)
[![Reproducibility](https://img.shields.io/badge/results-reproducible-success.svg)](reproduce.sh)

> **Pre-alpha specification release:** the repository structure and installable package scaffold are available, but the scientific benchmark commands described below are planned rather than implemented. Numerical values and conventions labelled **manuscript check** must be verified against the final paper before the first scientific release.

## Overview

`logALP` is the open-source companion benchmark suite for *Photon-Axion-like Particle Interconversion in 100 Magnetohydrodynamically Simulated Galaxy Clusters*. It isolates one question:

> When field strength and two-point statistics are controlled, does the distribution of weak-mixing photon-ALP conversion retain information about magnetic-field morphology?

The suite compares two propagation routes on identical one-dimensional sightlines:

1. a weak-mixing perturbative Fourier calculation; and
2. an independent ALPro-style numerical transfer-matrix calculation.

It tests both against the analytic unit-mean exponential null, applies the same analysis to matched one-dimensional Gaussian-random-field (GRF) sightlines, and defines a stable input interface for IllustrisTNG-derived sightlines. The core benchmark deliberately retains the controlled setup of the study: a single photon polarization, a constant phase gradient, four monochromatic energies, and the normalized statistic

\[
x \equiv \frac{X}{\langle X\rangle}.
\]

The baseline is a morphology diagnostic, not an observational exclusion pipeline. Plasma-dependent phase evolution, instrumental response, source spectra, absorption, polarization averaging, and likelihood construction are optional extensions and must not be mixed into the acceptance tests for the controlled benchmark.

## Repository goals

- Reproduce the paper's controlled propagation experiment from a clean environment.
- Establish agreement between perturbative Fourier and numerical propagation in the weak-mixing regime.
- Recover the unit-mean exponential null for the appropriate Gaussian complex-amplitude ensemble.
- Compare simulation-derived and GRF sightlines only after matching the stated one-dimensional controls.
- Make normalization, Fourier, unit, boundary, interpolation, and random-seed conventions explicit.
- Produce publication-quality figures and machine-readable benchmark summaries with one command.
- Permit public use without redistributing restricted IllustrisTNG data.

## Installation

The first public versions should be installed directly from GitHub. After a stable API is released on PyPI, `pip install logALP` can become the recommended route.

### Install the latest tagged GitHub release

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "logALP @ git+https://github.com/Loganpis/logALP.git@vX.Y.Z"
```

Replace `vX.Y.Z` with a published release tag. Tagged releases are recommended for scientific work because the exact source can be cited and reproduced.

### Install a development checkout

```bash
git clone https://github.com/Loganpis/logALP.git
cd logALP
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
```

### Future PyPI installation

```bash
python -m pip install logALP
```

This command should not be advertised as available until the distribution has actually been published. The import package and command-line program are both `logalp`.

## Five-minute demonstration

No IllustrisTNG files are required for the demo. The repository includes a small, synthetic, openly redistributable dataset containing two field ensembles on the baseline \(L=400\,\mathrm{kpc}\), \(N_z=200\) grid:

- a seeded non-Gaussian structured ensemble standing in for an MHD-like input; and
- a GRF ensemble matched to its RMS strength and one-dimensional power spectrum.

The synthetic fixture demonstrates the workflow and software interface; it is not evidence for a physical property of IllustrisTNG clusters.

### Run the complete demo

```bash
logalp demo --output demo-results
```

The command validates the inputs, performs perturbative propagation at 10, 25, 50, and 100 keV, verifies a subset with the numerical backend, normalizes \(X\) within each declared ensemble, compares both ensembles with the exponential null, and writes:

```text
demo-results/
├── README.txt
├── config.resolved.yaml
├── environment.json
├── inputs.manifest.json
├── metrics.json
├── tables/
│   ├── solver_agreement.csv
│   └── distribution_summary.csv
└── figures/
    ├── sightlines_and_spectra.pdf
    ├── solver_parity.pdf
    ├── normalized_distributions.pdf
    └── tail_probabilities.pdf
```

Successful completion prints a compact summary such as:

```text
Input validation                 PASS
GRF matching                     PASS
Weak-mixing solver agreement     PASS
Exponential-null diagnostics     RECORDED
Results                          demo-results/
```

`RECORDED` is intentional: a statistical goodness-of-fit result is scientific output, not a software pass/fail condition.

### Inspect the demo in Python

```python
from logalp import BenchmarkConfig, compare, load_example

fields = load_example("structured-vs-matched-grf")
config = BenchmarkConfig.baseline()

result = compare(
    {
        "structured": fields["structured"],
        "matched_grf": fields["matched_grf"],
    },
    config=config,
    solver="perturbative",
    validate_with="numerical",
)

print(result.summary())
result.save("demo-results-python")
```

The example API is part of the design specification and will be finalized during implementation. The eventual quick start must be executed in continuous integration so that every published command is known to work.

## Using your own magnetic-field sightlines

Users normally provide one-dimensional field ensembles extracted from their MHD, GRF, cell-based, analytic, or other magnetic-field models. Raw three-dimensional simulation volumes are not required by the core package.

1. Convert each ensemble to the documented HDF5 or NPZ interchange format.
2. Validate units, grid conventions, path length, metadata, and finite values.
3. Compare the supplied ensembles directly, or generate matched GRF controls.
4. Run every ensemble with one frozen propagation configuration.
5. Inspect the saved matching report before interpreting propagation differences.

```bash
# Validate without performing propagation
logalp sightlines validate fields/model_a.h5
logalp sightlines validate fields/model_b.h5

# Direct comparison of two supplied field ensembles
logalp compare \
  --field Model-A=fields/model_a.h5 \
  --field Model-B=fields/model_b.h5 \
  --config configs/baseline.yaml \
  --output results/direct-comparison

# Controlled comparison: build GRFs matched to Model A, then propagate both
logalp grf match fields/model_a.h5 \
  --config configs/baseline.yaml \
  --seed 240513 \
  --output fields/model_a_matched_grf.h5

logalp compare \
  --field Model-A=fields/model_a.h5 \
  --field Matched-GRF=fields/model_a_matched_grf.h5 \
  --config configs/baseline.yaml \
  --output results/controlled-comparison
```

The direct comparison asks whether the complete supplied models produce different propagation. The controlled comparison asks whether a difference remains after the declared RMS and one-dimensional power-spectrum controls are matched.

## Scientific scope

### Fixed baseline configuration

| Quantity | Baseline value | Role |
|---|---:|---|
| Photon polarization | one fixed linear polarization | morphology diagnostic |
| Energies | 10, 25, 50, 100 keV | four monochromatic benchmarks |
| ALP mass | \(m_a=10^{-12}\,\mathrm{eV}\) | fixed |
| Coupling | \(g_{a\gamma}=10^{-14}\,\mathrm{GeV}^{-1}\) | weak-mixing regime |
| Path length | \(L=400\,\mathrm{kpc}\) | fixed sightline length |
| Samples/domains | \(N_z=200\) | uniform baseline grid |
| Phase model | constant phase gradient along each sightline | controlled Fourier baseline |
| Statistic | \(x=X/\langle X\rangle\) | dimensionless, unit sample/ensemble mean |

The package configuration file is the authoritative machine-readable record of these values. No baseline command may silently override them.

### Propagation definitions

For the selected photon polarization, the perturbative weak-mixing amplitude is represented schematically as

\[
\mathcal A_{\gamma\rightarrow a}(E)
 = C(g_{a\gamma})\int_0^L \!\mathrm dz\,B_\perp(z)
 \exp\!\left[i\int_0^z \!\mathrm dz'\,\Delta(z',E)\right],
\qquad
X(E)=|\mathcal A_{\gamma\rightarrow a}(E)|^2.
\]

With constant \(\Delta(z,E)=\Delta(E)\), the integral is a sampled Fourier component of the selected transverse field. This identity is the basis of the fast perturbative implementation. The numerical reference evolves the corresponding photon-ALP state through the same piecewise-constant domains, without making the first-order amplitude approximation.

The implementation must define in one place:

- the selected polarization and the sign/orientation of \(B_\perp\);
- the Hamiltonian, phase, natural-unit, and probability conventions;
- whether samples denote cell centers or edges;
- the endpoint and quadrature rule used by the perturbative solver;
- the domain ordering and matrix multiplication convention used by the numerical solver; and
- whether \(X\) is the conversion probability or a proportional conversion statistic.

These are **manuscript checks** because the source PDF was not available while this specification was drafted. They must be locked by regression fixtures before release.

### Analytic null

If the relevant Fourier amplitude is a zero-mean circular complex Gaussian variable, its squared magnitude follows an exponential distribution. After normalization by its ensemble mean,

\[
p(x)=e^{-x},\qquad x\ge 0,
\]

with

\[
\mathbb E[x]=1,\qquad \operatorname{Var}(x)=1,
\qquad F(x)=1-e^{-x}.
\]

The exponential is a controlled null model. Failure to match it can indicate finite-sample effects, Fourier-mode correlations, non-circular amplitudes, windowing, normalization choices, or non-Gaussian field morphology; it is not by itself evidence for any unique physical cause.

### Matched one-dimensional GRFs

Each simulation-derived line of sight is paired with a one-dimensional GRF control. Matching is performed in sightline space, not by comparing unrelated ensembles. At minimum, the generated control must preserve:

- grid length, spacing, and boundary convention;
- the line-of-sight mean treatment;
- RMS field strength (or variance after the documented mean subtraction);
- the target one-dimensional power spectrum or explicitly binned spectral estimate; and
- the same propagation and normalization pipeline.

Phase randomization should preserve Fourier amplitudes while drawing phases under the real-field Hermitian constraint. Zero and Nyquist modes require explicit handling. Optional alternatives—parametric spectral fits, circulant embedding, or covariance sampling—must be named in outputs and may not replace the default matched construction silently.

### IllustrisTNG-derived sightline hooks

The core repository does not require proprietary or bulky simulation products. It consumes a documented interchange format containing, at minimum:

```text
z_kpc                 float[Nz]
B_selected_microG     float[Nz]
cluster_id             string
sightline_id           string
orientation            string or float[3]
source                  string
units                   mapping
provenance              mapping
```

Optional fields include electron density, the second transverse magnetic component, radius, redshift, extraction coordinates, snapshot, subhalo/group identifiers, and quality flags. Readers should support HDF5 and NPZ; a small synthetic example is committed to the repository. TNG extraction code belongs in an adapter module and is tested with mocks. Users provide their own authorized simulation data.

## Baseline versus optional extensions

| Component | Baseline acceptance suite | Optional observational extension |
|---|---|---|
| Polarization | one fixed photon polarization | two-polarization/unpolarized states |
| Phase | constant along each sightline | spatially varying plasma phase |
| Energy | 10/25/50/100 keV monochromatic runs | dense or instrument-specific energy grid |
| Source | no intrinsic spectrum | continuum/line source model |
| Detector | none | response matrix, effective area, binning |
| Medium | magnetic field required | electron density, absorption, redshift evolution |
| Output | \(X\), \(x\), distributions, solver residuals | survival spectrum, counts, likelihood products |
| Claim | controlled morphology sensitivity | observation-specific forecast or inference |

Extension outputs must carry `benchmark_class: extension` and record all additional assumptions. They must never overwrite baseline artifacts.

## Benchmark matrix

Every row runs at all four baseline energies unless stated otherwise.

| ID | Input ensemble | Solver(s) | Primary assertion | Required output |
|---|---|---|---|---|
| B00 | zero field | Fourier + numerical | exactly/noisily zero conversion | scalar and residual table |
| B01 | one constant domain | Fourier + numerical + closed form | amplitude and probability convention | convergence curve |
| B02 | sinusoidal field on grid | Fourier + numerical + discrete reference | Fourier frequency/sign convention | response versus phase wavenumber |
| B03 | fixed seeded synthetic field | Fourier + numerical | weak-mixing solver agreement | per-energy parity plot |
| B04 | resolution sequence around \(N_z=200\) | both | discretization convergence | error versus \(N_z\) |
| B05 | ideal complex-Gaussian amplitude draws | analytic null | normalization and distribution code | PDF/CDF/QQ plot |
| B06 | seeded GRF ensemble | both | approach to exponential null where assumptions hold | moments, KS statistic, tail ratios |
| B07 | matched GRF pairs | both | matching fidelity | RMS and power-spectrum residuals |
| B08 | public synthetic interchange fixture | both | end-to-end I/O reproducibility | manifest and figures |
| B09 | user-supplied TNG-derived sightlines | both | morphology comparison | aggregate statistics and figure set |
| E10 | sightlines with \(n_e(z)\) | numerical; perturbative where valid | varying plasma phase | labelled extension outputs |
| E11 | source spectrum and energy grid | numerical | spectral modulation | labelled extension outputs |

## Validation and acceptance tolerances

Tolerances below are proposed release gates, not inferred measurements from the paper. They should be tightened or revised after the frozen reference dataset is generated.

### Deterministic solver checks

- Zero-field conversion: absolute \(X\le 10^{-30}\), or exact zero where the arithmetic path permits.
- Closed-form one-domain and sinusoid tests: relative error \(\le 10^{-8}\) for the perturbative solver away from analytic zeros; use an absolute tolerance of \(10^{-14}\) near zeros.
- Fourier versus numerical weak-mixing conversion: median relative difference \(\le 10^{-3}\), 99th percentile \(\le 10^{-2}\), with a symmetric scaled absolute error reported near zero.
- Baseline grid convergence: doubling from \(N_z=200\) to 400 changes ensemble means by \(\le 1\%\) and predeclared distribution summaries by \(\le 2\%\). Any scientifically material failure is reported, not hidden by changing defaults.
- Probability bounds and norm conservation in the numerical solver: state-norm drift \(\le 10^{-10}\) per sightline and probabilities within \([-10^{-12},1+10^{-12}]\) before clipping. Clipping is forbidden in validation calculations.

### Ensemble checks

- Normalization: \(|\langle x\rangle-1|\le 10^{-12}\) for the stored normalized sample, subject to floating-point precision.
- Ideal-null moments: mean and variance must lie within a predeclared 95% Monte Carlo acceptance interval computed for the exact sample size.
- Ideal-null distribution: one-sample Kolmogorov-Smirnov p-values are recorded but are not used as a reproducibility checksum. CI uses a fixed-seed reference statistic and a tolerance derived from repeated seeded ensembles.
- GRF matching: relative RMS mismatch \(\le 10^{-3}\); binned power residuals are reported and must meet \(\le 5\%\) median absolute fractional deviation over the declared trusted wavenumber interval.
- Tail summaries: report \(P(x>x_0)\) at predeclared thresholds (default \(x_0=1,2,3,5\)) with binomial or bootstrap confidence intervals. No threshold may be selected after inspecting TNG results.

Statistical tests are diagnostics, not binary discoveries. The repository reports effect sizes and uncertainty alongside p-values and records the ensemble size used for every comparison.

## Expected outputs

A baseline run writes an immutable, timestamp-free results directory keyed by configuration and input hashes:

```text
results/baseline/<run_id>/
├── config.resolved.yaml
├── environment.json
├── inputs.manifest.json
├── metrics.json
├── samples.parquet
├── tables/
│   ├── solver_agreement.csv
│   ├── distribution_summary.csv
│   └── grf_matching.csv
└── figures/
    ├── 01_solver_parity.pdf
    ├── 02_null_pdf_cdf.pdf
    ├── 03_null_qq.pdf
    ├── 04_grf_matching.pdf
    ├── 05_morphology_distributions.pdf
    └── 06_tail_probabilities.pdf
```

The publication figure set should show:

1. Fourier-versus-numerical parity by energy, with residual panels.
2. Analytic exponential PDF/CDF and empirical ideal-null or GRF realizations.
3. A quantile-quantile diagnostic emphasizing both the body and tail.
4. Representative matched sightlines plus their one-dimensional power spectra and residuals.
5. Normalized \(x\) distributions for TNG-derived and matched-GRF ensembles at all four energies.
6. Predeclared tail probabilities or ratios with uncertainty intervals.

Plotting code reads saved tables only; it never recomputes propagation implicitly.

## Proposed package structure

```text
logALP/
├── README.md
├── CITATION.cff
├── LICENSE
├── pyproject.toml
├── environment.lock
├── reproduce.sh
├── configs/
│   ├── baseline.yaml
│   └── extension-plasma.example.yaml
├── src/logalp/
│   ├── __init__.py
│   ├── constants.py          # units and physical constants
│   ├── config.py             # validated, immutable run configuration
│   ├── sightlines.py         # typed sightline model and validation
│   ├── io/
│   │   ├── interchange.py    # HDF5/NPZ readers and writers
│   │   └── tng.py            # optional user-data adapter hooks
│   ├── fields/
│   │   ├── analytic.py       # zero, constant, sinusoidal fixtures
│   │   ├── grf.py            # matched 1D GRF construction
│   │   └── spectra.py        # PSD estimation and matching metrics
│   ├── propagation/
│   │   ├── perturbative.py   # direct quadrature/Fourier solver
│   │   ├── numerical.py      # independent transfer-matrix solver
│   │   └── phase.py          # constant and optional plasma phases
│   ├── statistics/
│   │   ├── normalize.py
│   │   ├── null.py
│   │   ├── diagnostics.py
│   │   └── uncertainty.py
│   ├── plotting.py
│   ├── provenance.py
│   └── cli.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── data/                 # tiny synthetic fixtures only
├── examples/
│   ├── README.md              # five-minute tutorial and expected output
│   └── synthetic/             # small public demonstration fixture
├── scripts/
└── docs/
    ├── conventions.md
    ├── data-format.md
    ├── installation.md
    ├── quickstart.md
    └── validation.md
```

`numerical.py` should implement or wrap an ALPro-style domain propagator behind a small internal protocol. If ALPro is used directly, pin and record its version and keep analytic tests independent of it.

## Command-line interface

Illustrative commands; exact option names become stable at the first tagged release.

```bash
# Show and validate the frozen baseline configuration
logalp config validate configs/baseline.yaml

# Run deterministic analytic and solver-parity benchmarks
logalp benchmark solvers --config configs/baseline.yaml

# Generate a reproducible matched-GRF ensemble
logalp grf match data/example_sightlines.h5 \
  --config configs/baseline.yaml --seed 240513 --output results/grf

# Run the controlled distribution benchmark
logalp benchmark distributions \
  --sightlines data/example_sightlines.h5 \
  --controls results/grf/matched.h5 \
  --config configs/baseline.yaml

# Run on locally prepared, authorized TNG-derived inputs
logalp benchmark morphology \
  --sightlines /path/to/tng_sightlines.h5 \
  --controls /path/to/matched_grf.h5 \
  --config configs/baseline.yaml

# Rebuild figures from existing tables
logalp plot results/baseline/<run_id>

# Optional extension; output is segregated automatically
logalp extension spectrum --config configs/extension-plasma.yaml
```

Commands fail on missing units, inconsistent grids, non-finite values, ambiguous polarization, unrecorded seeds, or a baseline/extension classification mismatch.

## Reproducibility requirements

- Support Python 3.10+ with a locked reference environment and a minimally constrained library environment.
- Store the resolved configuration, package version, Git commit, dependency versions, platform, input hashes, seeds, and numerical backend in every run manifest.
- Use a single explicit random generator passed through APIs; never depend on global random state.
- Fix the baseline seed in `configs/baseline.yaml`. Allow replicated seeds through a documented seed schedule.
- Serialize floating-point arrays and metadata in stable, open formats; do not treat pickles as research data.
- Hash raw inputs and generated controls. Derived products must identify their parent hashes.
- Make CPU reference results authoritative. Accelerated backends are optional and must pass the same tolerance suite.
- Ensure `./reproduce.sh baseline` runs end to end without network access after environment installation and data staging.
- Separate cached intermediates from versioned reference fixtures.
- Generate figures deterministically, including sorting, bin edges, colors, fonts, and metadata settings.

## Testing strategy

### Unit tests

Test units, phase construction, analytic fields, discrete Fourier conventions, GRF Hermitian symmetry, normalization, CDF/PDF functions, configuration validation, and interchange-format round trips.

### Property tests

Check invariants: zero coupling or zero field gives zero conversion; field-sign reversal preserves \(X\); amplitude scales linearly and \(X\) quadratically with \(g_{a\gamma}\) in the perturbative regime; seeded generation is repeatable; and normalized samples have unit mean.

### Integration tests

Run both solvers on the same analytic and seeded fixtures at every baseline energy. Exercise the full CLI from input loading through tables and plots.

### Regression tests

Version a tiny, reviewable fixture and expected scalar metrics. Compare floats with physics-based tolerances rather than byte equality. Image regression may protect layout, but numerical tables remain the scientific reference.

### Statistical tests

Use sample-size-aware confidence intervals and deterministic seed schedules. Avoid flaky assertions on a single p-value. Validate test calibration through repeated null ensembles outside the fast CI job.

### Continuous integration

- Fast job: formatting, linting, type checks, unit tests, and small integration suite.
- Scientific job: deterministic solver matrix and reference metrics.
- Scheduled/release job: larger ensembles, statistical calibration, figure generation, and clean-environment reproduction.

## Interpretation guardrails

- The normalized statistic removes overall amplitude information; this is intentional for the morphology diagnostic.
- A matched one-dimensional power spectrum controls two-point structure along the sampled sightline, not every three-dimensional property of a cluster field.
- Sightlines from the same cluster may not be independent. Cluster-level resampling should be the default uncertainty unit when several sightlines per cluster are present.
- Energy panels can be correlated because they reuse fields. Joint claims require a dependence-aware analysis.
- Deviations from the exponential null should be described as distributional deviations until alternative causes have been tested.
- The fixed weak coupling is a benchmark choice, not a sensitivity forecast.

## Citation

If you use this software, cite both the companion study and the archived software release. The repository will include a `CITATION.cff` file and release DOI before publication.

Suggested software citation placeholder:

> Logan [family name], *logALP: magnetic-field morphology benchmarks for photon-ALP propagation*, version X.Y.Z, Zenodo, YEAR, DOI: TBC.

Suggested BibTeX placeholder:

```bibtex
@software{logalp,
  author  = {Logan, GIVEN-NAME},
  title   = {logALP: Magnetic-field morphology benchmarks for photon-ALP propagation},
  year    = {YEAR},
  version = {X.Y.Z},
  doi     = {TBC},
  url     = {https://github.com/Loganpis/logALP}
}
```

Replace all placeholders and add the paper's final bibliographic record before the first public release. Cite ALPro and IllustrisTNG according to their respective documentation whenever those components or data inform a result.

## License and data notes

**Code.** BSD-3-Clause is proposed to encourage reuse while retaining attribution and warranty disclaimers. Confirm that this is compatible with every copied or linked dependency before adding third-party code. A different OSI-approved license may be selected before the first release.

**Documentation.** Unless stated otherwise, documentation and original figures may be released under CC BY 4.0.

**Data.** Commit only small synthetic fixtures and, if permitted, explicitly redistributable derived examples. Do not commit IllustrisTNG snapshots, restricted extracts, credentials, unpublished collaboration data, or data whose redistribution terms are uncertain. Publish extraction instructions, schemas, hashes, and provenance so authorized users can recreate compatible sightlines. The repository license does not relicense third-party data.

**Attribution.** Preserve notices for ALPro, IllustrisTNG, scientific Python dependencies, and any adapted algorithms. Document whether the numerical solver is an original compatible implementation or a wrapper around ALPro.

## Staged implementation roadmap

### Stage 0 - Freeze conventions and scope

- Transcribe the manuscript's Hamiltonian, amplitude, polarization, units, and phase conventions into `docs/conventions.md`.
- Resolve every **manuscript check** in this document.
- Freeze `configs/baseline.yaml` and define the public sightline schema.
- Select the code license and add paper/software citation metadata.

**Exit criterion:** a reviewer can compute B00-B02 independently from the written conventions.

### Stage 1 - Deterministic propagation core

- Implement typed sightlines, unit handling, analytic fixtures, direct perturbative quadrature, Fourier evaluation, and the numerical transfer-matrix solver.
- Complete B00-B04 and enforce deterministic tolerances in CI.

**Exit criterion:** both solvers agree throughout the declared weak-mixing baseline and convergence at \(N_z=200\) is quantified.

### Stage 2 - Null and GRF controls

- Implement the exponential reference distribution and sample-size-aware diagnostics.
- Implement matched one-dimensional GRF generation, spectral estimators, and matching reports.
- Complete B05-B08 with fixed seeds and a public synthetic fixture.

**Exit criterion:** the suite recovers the analytic null in its domain of validity and documents the fidelity of every matched control.

### Stage 3 - Simulation-derived benchmark

- Add the IllustrisTNG interchange adapter and input validator.
- Run B09 on the study's prepared sightlines without placing restricted data in Git.
- Generate all paper-companion tables and figures with cluster-aware uncertainty estimates.

**Exit criterion:** one clean command recreates the released numerical summaries and figures from staged authorized inputs.

### Stage 4 - Public release

- Run the full clean-environment and release CI jobs.
- Complete documentation, examples, changelog, contributor guidance, and archival metadata.
- Tag `v1.0.0`, archive it on Zenodo, insert the DOI, and link the exact release from the paper.

**Exit criterion:** a third party can install, run the public fixture, understand the scientific boundaries, and reproduce the archived benchmark artifacts.

### Stage 5 - Optional observational extensions

- Add spatially varying plasma phase, two-polarization evolution, source spectra, and detector response as separately configured modules.
- Validate each extension against analytic limits and external references.

**Exit criterion:** extension results remain clearly labelled and cannot alter or weaken the frozen baseline tests.

## Release checklist

- [ ] All manuscript conventions verified against the final PDF.
- [ ] Baseline configuration frozen and versioned.
- [ ] B00-B09 pass with recorded tolerances or documented scientific exceptions.
- [ ] Synthetic public example reproduces expected tables and figures.
- [ ] TNG redistribution and attribution requirements reviewed.
- [ ] Paper citation, repository URL, authorship, license, and DOI finalized.
- [ ] Fresh-machine reproduction completed from the tagged commit.
- [ ] Numerical artifacts and environment manifest archived with the release.

## Contributing

Contributions are welcome when they preserve the distinction between the controlled benchmark and observational extensions. Scientific changes should include a test, a convention note, and a statement of their effect on archived metrics. Changes to baseline defaults require a documented decision and a versioned benchmark update.

## Contact

Open a GitHub issue for reproducibility problems, numerical discrepancies, or data-format questions. For scientific correspondence, use the contact details in the companion paper.
