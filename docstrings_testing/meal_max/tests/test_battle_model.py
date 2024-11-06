import pytest
from unittest.mock import patch
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats

@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal="Sushi", cuisine="Japanese", price=12.5, difficulty="MED")

@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal="Tacos", cuisine="Mexican", price=8.0, difficulty="LOW")

##################################################
# Combatant Preparation Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the list."""
    battle_model.prep_combatant(sample_meal1)
    assert battle_model.get_combatants() == [sample_meal1]

def test_prep_combatant_full(battle_model, sample_meal1, sample_meal2):
    """Test error when adding a combatant to a full list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(sample_meal1)

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    battle_model.clear_combatants()
    assert battle_model.get_combatants() == []

##################################################
# Battle Test Cases
##################################################

@patch("meal_max.models.battle_model.get_random", return_value=0.1)
@patch("meal_max.models.kitchen_model.update_meal_stats")
def test_battle_winner_combatant1(mock_update, mock_random, battle_model, sample_meal1, sample_meal2):
    """Test battle where combatant 1 wins."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    # Simulate a battle
    winner = battle_model.battle()
    assert winner == sample_meal1.meal
    mock_update.assert_any_call(sample_meal1.id, 'win')
    mock_update.assert_any_call(sample_meal2.id, 'loss')
    assert len(battle_model.get_combatants()) == 1

@patch("meal_max.models.battle_model.get_random", return_value=0.9)
@patch("meal_max.models.kitchen_model.update_meal_stats")
def test_battle_winner_combatant2(mock_update, mock_random, battle_model, sample_meal1, sample_meal2):
    """Test battle where combatant 2 wins."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    # Simulate a battle
    winner = battle_model.battle()
    assert winner == sample_meal2.meal
    mock_update.assert_any_call(sample_meal2.id, 'win')
    mock_update.assert_any_call(sample_meal1.id, 'loss')
    assert len(battle_model.get_combatants()) == 1

def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test error when there are not enough combatants for a battle."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

##################################################
# Battle Score Calculation Test Cases
##################################################

def test_get_battle_score_low_difficulty(battle_model, sample_meal2):
    """Test calculating battle score for LOW difficulty meal."""
    score = battle_model.get_battle_score(sample_meal2)
    expected_score = (sample_meal2.price * len(sample_meal2.cuisine)) - 3
    assert score == expected_score

def test_get_battle_score_med_difficulty(battle_model, sample_meal1):
    """Test calculating battle score for MED difficulty meal."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 2
    assert score == expected_score

