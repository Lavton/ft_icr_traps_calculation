from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class TrapVisParams:
    expand_amount: Optional[Callable] = None  # the function that from electrode number return the value the electrode need to be shifted
    view_th: float = 50  # the angle of 3d viewing
    view_phi: float = 25  # the another angle of 3d viewing
    dist: float = 3  # the standard distance of 3d viewing
