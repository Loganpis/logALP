from logalp import __version__
from logalp.cli import build_parser


def test_version_is_pre_alpha() -> None:
    assert __version__ == "0.0.1"


def test_cli_program_name() -> None:
    assert build_parser().prog == "logalp"
