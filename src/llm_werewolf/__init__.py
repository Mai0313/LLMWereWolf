from importlib.metadata import version
from pathlib import Path

from llm_werewolf.core import GameEngine

package_name = Path(__file__).parent.name
__package__ = package_name
__version__ = version(package_name)

__all__ = [
    # Core classes
    "GameEngine",
    # Package metadata
    "__version__",
]
