"""Configuration objects for reproducible logALP comparisons."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class BenchmarkConfig:
    """Controlled configuration used by the pre-alpha demonstration workflow."""

    energies_kev: tuple[float, ...] = (10.0, 25.0, 50.0, 100.0)
    alp_mass_ev: float = 1.0e-12
    coupling_gev_inv: float = 1.0e-14
    length_kpc: float = 400.0
    n_z: int = 200
    n_sightlines: int = 600
    seed: int = 240513
    demo_phase_rate_at_10kev: float = 0.18

    def __post_init__(self) -> None:
        if not self.energies_kev or any(energy <= 0 for energy in self.energies_kev):
            raise ValueError("energies_kev must contain positive values")
        if self.length_kpc <= 0:
            raise ValueError("length_kpc must be positive")
        if self.n_z < 4:
            raise ValueError("n_z must be at least 4")
        if self.n_sightlines < 2:
            raise ValueError("n_sightlines must be at least 2")

    @classmethod
    def baseline(cls, **overrides: object) -> "BenchmarkConfig":
        """Return the study-inspired baseline with optional explicit overrides."""
        return replace(cls(), **overrides)

    @property
    def z_kpc(self) -> np.ndarray:
        """Uniform cell-center-like demonstration coordinates."""
        return np.linspace(0.0, self.length_kpc, self.n_z, endpoint=False)

    @property
    def dz_kpc(self) -> float:
        return self.length_kpc / self.n_z

    @property
    def energy_array_kev(self) -> np.ndarray:
        return np.asarray(self.energies_kev, dtype=float)
