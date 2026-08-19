"""Simple magnetic-field containers and synthetic demonstration fields."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np

from logalp.config import BenchmarkConfig


@dataclass(frozen=True)
class FieldEnsemble:
    """A named ensemble of one-dimensional selected-polarization sightlines."""

    name: str
    values: np.ndarray
    z_kpc: np.ndarray
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        values = np.asarray(self.values, dtype=float)
        z_kpc = np.asarray(self.z_kpc, dtype=float)
        if values.ndim != 2:
            raise ValueError("values must have shape (n_sightlines, n_z)")
        if z_kpc.ndim != 1 or values.shape[1] != z_kpc.size:
            raise ValueError("z_kpc must be one-dimensional and match values.shape[1]")
        if values.shape[0] < 2:
            raise ValueError("an ensemble needs at least two sightlines")
        if not np.all(np.isfinite(values)) or not np.all(np.isfinite(z_kpc)):
            raise ValueError("field values and coordinates must be finite")
        if np.any(np.diff(z_kpc) <= 0):
            raise ValueError("z_kpc must be strictly increasing")
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "z_kpc", z_kpc)

    @property
    def rms(self) -> np.ndarray:
        """RMS strength of every sightline."""
        return np.sqrt(np.mean(self.values**2, axis=1))

    @property
    def mean_power(self) -> np.ndarray:
        """Mean one-dimensional discrete power spectrum."""
        return np.mean(np.abs(np.fft.rfft(self.values, axis=1)) ** 2, axis=0)


def make_demo_fields(
    config: BenchmarkConfig | None = None,
    *,
    rms: float = 1.0,
    phase_jitter: float = 0.12,
) -> dict[str, FieldEnsemble]:
    """Create matched GRF-like and phase-correlated demonstration ensembles.

    Each paired sightline shares its Fourier amplitudes. The ensembles therefore
    match in RMS and discrete one-dimensional power while differing in phase
    organization. These fields are educational fixtures, not MHD simulations.
    """
    config = config or BenchmarkConfig.baseline()
    if rms <= 0:
        raise ValueError("rms must be positive")
    if phase_jitter < 0:
        raise ValueError("phase_jitter must be non-negative")

    rng = np.random.default_rng(config.seed)
    n_modes = config.n_z // 2 + 1
    mode = np.arange(n_modes, dtype=float)
    envelope = (1.0 + (mode / 9.0) ** 2) ** (-5.0 / 6.0)

    grf_rows: list[np.ndarray] = []
    structured_rows: list[np.ndarray] = []

    for _ in range(config.n_sightlines):
        amplitudes = envelope * rng.rayleigh(scale=1.0, size=n_modes)
        amplitudes[0] = 0.0

        grf_phase = rng.uniform(0.0, 2.0 * np.pi, size=n_modes)
        translation = rng.uniform(0.0, 2.0 * np.pi)
        structured_phase = translation * mode + rng.normal(
            0.0, phase_jitter, size=n_modes
        )

        grf_coeff = amplitudes * np.exp(1j * grf_phase)
        structured_coeff = amplitudes * np.exp(1j * structured_phase)
        grf_coeff[0] = structured_coeff[0] = 0.0

        if config.n_z % 2 == 0:
            grf_coeff[-1] = amplitudes[-1] * rng.choice((-1.0, 1.0))
            structured_coeff[-1] = amplitudes[-1] * rng.choice((-1.0, 1.0))

        grf = np.fft.irfft(grf_coeff, n=config.n_z)
        structured = np.fft.irfft(structured_coeff, n=config.n_z)
        scale = rms / np.sqrt(np.mean(grf**2))
        grf_rows.append(grf * scale)
        structured_rows.append(structured * scale)

    metadata = {
        "kind": "synthetic-demo",
        "matched": "paired Fourier amplitudes",
        "seed": config.seed,
    }
    return {
        "GRF-like": FieldEnsemble(
            "GRF-like", np.stack(grf_rows), config.z_kpc, metadata
        ),
        "phase-correlated": FieldEnsemble(
            "phase-correlated",
            np.stack(structured_rows),
            config.z_kpc,
            metadata,
        ),
    }
