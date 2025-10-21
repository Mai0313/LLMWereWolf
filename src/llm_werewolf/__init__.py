from pathlib import Path
from importlib.metadata import version

import logfire

logfire.configure(send_to_logfire=False)

from llm_werewolf.core import GameEngine

package_name = Path(__file__).parent.name
__package__ = package_name
__version__ = version(package_name)

__all__ = ["GameEngine", "__version__"]
