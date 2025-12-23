from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass(frozen=True)
class PlayerWeek:
    player_id: str
    season: int
    week: int
    position: str
    points: float

@dataclass #this thing basically automatically creates the __init__ method
class Trade:
    week: int
    give: List[str]   # player_ids you trade away
    get: List[str]    # player_ids you receive