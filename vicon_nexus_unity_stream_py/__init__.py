from importlib_metadata import version
from ._utils import _setup_logger

__version__ = version(__package__)


_setup_logger()
