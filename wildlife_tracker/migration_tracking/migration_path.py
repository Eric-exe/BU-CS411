from typing import Optional
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:

    def __init__(self,
                species: str,
                start_date: str,
                start_location: Habitat,
                destination: Habitat,
                duration: Optional[int] = None) -> None:
        self.path_id: int
        self.start_date: str = start_date
        self.start_location: Habitat = start_location
        self.destination: Habitat = destination
        self.duration: Optional[int] = duration
