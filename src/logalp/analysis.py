"""Demonstration propagation comparison and plotting interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from logalp.config import BenchmarkConfig
from logalp.fields import FieldEnsemble


def _constant_phase_proxy(
    fields: np.ndarray, config: BenchmarkConfig
) -> np.ndarray:
    """Return an illustrative Fourier conversion proxy.

    This deliberately simple phase mapping demonstrates the package workflow;
    it is not yet the validated physical perturbative or numerical backend.
    """
    phase_rates = config.demo_phase_rate_at_10kev * (
        10.0 / config.energy_array_kev
    )
    kernels = np.exp(1j * np.outer(phase_rates, config.z_kpc))
    amplitudes = fields @ kernels.T * config.dz_kpc
    return np.abs(amplitudes) ** 2


@dataclass(frozen=True)
class ComparisonResult:
    """Results and publication-style plots for a demonstration comparison."""

    fields: Mapping[str, FieldEnsemble]
    config: BenchmarkConfig
    raw: Mapping[str, np.ndarray]
    normalized: Mapping[str, np.ndarray]

    def summary(self, tail_threshold: float = 3.0) -> str:
        """Return a compact plain-text summary."""
        lines = [
            "logALP demonstration comparison",
            f"sightlines: {next(iter(self.fields.values())).values.shape[0]}",
            f"grid: {self.config.n_z} samples across {self.config.length_kpc:g} kpc",
            "energy_keV | "
            + " | ".join(f"{name} P(x>{tail_threshold:g})" for name in self.fields),
        ]
        for energy_index, energy in enumerate(self.config.energies_kev):
            tails = [
                np.mean(values[:, energy_index] > tail_threshold)
                for values in self.normalized.values()
            ]
            lines.append(
                f"{energy:>10g} | " + " | ".join(f"{tail:>18.3f}" for tail in tails)
            )
        return "\n".join(lines)

    def plot_sightlines(self, index: int = 0) -> Figure:
        """Plot one representative sightline from every ensemble."""
        figure, axis = plt.subplots(figsize=(9.0, 4.6))
        for name, ensemble in self.fields.items():
            axis.plot(ensemble.z_kpc, ensemble.values[index], lw=1.7, label=name)
        axis.axhline(0.0, color="0.25", lw=0.7)
        axis.set(
            xlabel="Distance along sightline [kpc]",
            ylabel="Selected field component [a.u.]",
            title="Simple magnetic-field configurations",
        )
        axis.legend(frameon=False)
        figure.tight_layout()
        return figure

    def plot_power_spectra(self) -> Figure:
        """Plot ensemble-mean one-dimensional power spectra."""
        figure, axis = plt.subplots(figsize=(8.2, 4.8))
        for name, ensemble in self.fields.items():
            spacing = float(np.mean(np.diff(ensemble.z_kpc)))
            frequency = np.fft.rfftfreq(ensemble.z_kpc.size, d=spacing)
            axis.loglog(frequency[1:], ensemble.mean_power[1:], lw=2.0, label=name)
        axis.set(
            xlabel="1D spatial frequency [kpc$^{-1}$]",
            ylabel="Mean power [a.u.]",
            title="Matching check: one-dimensional power spectra",
        )
        axis.legend(frameon=False)
        figure.tight_layout()
        return figure

    def plot_distributions(self, xmax: float = 6.0) -> Figure:
        """Compare normalized distributions with the unit-mean exponential null."""
        bins = np.linspace(0.0, xmax, 36)
        null_x = np.linspace(0.0, xmax, 400)
        figure, axes = plt.subplots(2, 2, figsize=(11.0, 8.5), sharex=True, sharey=True)

        for energy_index, (axis, energy) in enumerate(
            zip(axes.flat, self.config.energies_kev)
        ):
            for name, values in self.normalized.items():
                axis.hist(
                    values[:, energy_index],
                    bins=bins,
                    density=True,
                    histtype="step",
                    lw=2.0,
                    label=name,
                )
            axis.plot(null_x, np.exp(-null_x), color="0.15", ls=":", lw=2.2, label=r"$e^{-x}$ null")
            axis.set_title(f"{energy:g} keV")
            axis.set_xlim(0.0, xmax)
            axis.set_ylim(0.0, 1.15)

        for axis in axes[:, 0]:
            axis.set_ylabel("Probability density")
        for axis in axes[-1, :]:
            axis.set_xlabel(r"Normalized conversion proxy $x$")
        handles, labels = axes[0, 0].get_legend_handles_labels()
        figure.legend(
            handles,
            labels,
            loc="upper center",
            ncol=3,
            frameon=False,
            bbox_to_anchor=(0.5, 0.945),
        )
        figure.suptitle(
            "Propagation statistics for field ensembles", y=0.995, fontsize=13
        )
        figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.89))
        return figure

    def plot_tail_probabilities(self, threshold: float = 3.0) -> Figure:
        """Plot P(x > threshold) at each configured energy."""
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        names = list(self.normalized)
        positions = np.arange(len(self.config.energies_kev))
        width = 0.72 / len(names)

        figure, axis = plt.subplots(figsize=(8.5, 4.6))
        for name_index, name in enumerate(names):
            offsets = positions - 0.36 + width / 2 + name_index * width
            tails = np.mean(self.normalized[name] > threshold, axis=0)
            axis.bar(offsets, tails, width, label=name)

        axis.axhline(
            np.exp(-threshold),
            color="0.15",
            ls=":",
            lw=2.0,
            label=fr"exponential null: $e^{{-{threshold:g}}}$",
        )
        axis.set_xticks(positions, [f"{energy:g}" for energy in self.config.energies_kev])
        axis.set(
            xlabel="Energy [keV]",
            ylabel=fr"Fraction with $x>{threshold:g}$",
            title="High-conversion tail comparison",
        )
        axis.legend(frameon=False, ncol=min(3, len(names) + 1))
        figure.tight_layout()
        return figure


def compare(
    fields: Mapping[str, FieldEnsemble],
    config: BenchmarkConfig | None = None,
) -> ComparisonResult:
    """Run the pre-alpha demonstration comparison on supplied field ensembles."""
    config = config or BenchmarkConfig.baseline()
    if len(fields) < 2:
        raise ValueError("compare requires at least two field ensembles")

    raw: dict[str, np.ndarray] = {}
    normalized: dict[str, np.ndarray] = {}
    for name, ensemble in fields.items():
        if ensemble.values.shape[1] != config.n_z:
            raise ValueError(f"{name!r} does not match config.n_z")
        if not np.allclose(ensemble.z_kpc, config.z_kpc):
            raise ValueError(f"{name!r} does not match the configured grid")
        values = _constant_phase_proxy(ensemble.values, config)
        means = values.mean(axis=0, keepdims=True)
        if np.any(means <= 0):
            raise ValueError(f"{name!r} produced a zero ensemble mean")
        raw[name] = values
        normalized[name] = values / means

    return ComparisonResult(dict(fields), config, raw, normalized)
