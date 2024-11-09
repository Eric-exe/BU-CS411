from typing import Optional, Any
from wildlife_tracker.animal_management.animal import Animal

class AnimalManager:

    def __init__(self) -> None:
        self.animals: dict[int, Animal] = {}

    def get_animal_by_id(self, animal_id: int) -> Optional[Animal]:
        pass

    def register_animal(Animal) -> None:
        pass

    def remove_animal(animal_id: int) -> None:
        pass

    def update_animal_details(self, animal_id: int, **kwargs: Any) -> None:
        pass

    def get_animal_details(self, animal_id: int) -> dict[str, Any]:
        pass

    def get_animal_by_id(self, animal_id: int) -> Optional[Animal]:
        pass