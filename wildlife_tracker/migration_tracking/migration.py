from typing import Any
from wildlife_tracker.migration_tracking.migration_path import MigrationPath

class Migration:

    def __init__(self) -> None:
        self.migration_id: int
        self.migration_path: MigrationPath
        self.status: str = "Scheduled"
        self.current_date: str
        self.current_location: str

    def schedule_migration(self, migration_path: MigrationPath) -> None:
        pass

    