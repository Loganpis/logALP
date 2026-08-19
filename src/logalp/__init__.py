"""logALP: magnetic-field morphology benchmarks for photon-ALP propagation."""

from logalp.analysis import ComparisonResult, compare
from logalp.config import BenchmarkConfig
from logalp.fields import FieldEnsemble, make_demo_fields

__version__ = "0.1.0"

__all__ = [
    "BenchmarkConfig",
    "ComparisonResult",
    "FieldEnsemble",
    "__version__",
    "compare",
    "make_demo_fields",
]
