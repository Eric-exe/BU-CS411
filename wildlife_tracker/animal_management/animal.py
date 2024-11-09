from typing import Optional

class Animal:
    def __init__(self, 
                 animal_id: int, 
                 species: str, 
                 age: Optional[int] = None, 
                 health_status: Optional[str] = None) -> None:
        self.animal_id: int = animal_id  
        self.species: str = species 
        self.age: Optional[int] = age  
        self.health_status: Optional[str] = health_status
