from dataclasses import dataclass
from typing import Union


@dataclass
class Links:
    self: Union[str, None] = None
    related: Union[str, None] = None
