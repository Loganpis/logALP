import matplotlib
import numpy as np

from logalp import BenchmarkConfig, compare, make_demo_fields


matplotlib.use("Agg")


def small_config() -> BenchmarkConfig:
    return BenchmarkConfig.baseline(n_sightlines=40, n_z=64, seed=7)


def test_demo_fields_match_rms_and_power() -> None:
    fields = make_demo_fields(small_config())
    grf = fields["GRF-like"]
    structured = fields["phase-correlated"]

    assert np.allclose(grf.rms, structured.rms, rtol=1e-12, atol=1e-12)
    assert np.allclose(grf.mean_power, structured.mean_power, rtol=1e-12, atol=1e-12)


def test_comparison_normalizes_each_energy() -> None:
    config = small_config()
    result = compare(make_demo_fields(config), config)

    for values in result.normalized.values():
        assert values.shape == (config.n_sightlines, len(config.energies_kev))
        assert np.allclose(values.mean(axis=0), 1.0)


def test_plotting_methods_return_figures() -> None:
    config = small_config()
    result = compare(make_demo_fields(config), config)

    figures = [
        result.plot_sightlines(),
        result.plot_power_spectra(),
        result.plot_distributions(),
        result.plot_tail_probabilities(),
    ]
    assert all(figure.axes for figure in figures)
