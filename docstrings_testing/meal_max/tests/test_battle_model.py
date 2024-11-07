import pytest
from contextlib import contextmanager
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture
def battle_model():
    """Provides a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal='Meal 1', price=20, cuisine='Italian', difficulty='HIGH')

@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal='Meal 2', price=15, cuisine='Mexican', difficulty='LOW')

@pytest.fixture
def sample_meal3():
    return Meal(id=3, meal='Meal 3', price=18, cuisine='Saudi', difficulty='MED')

# Mocking the database connection for tests
@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None
    
    # Mock the get_db_connection function context manager
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_conn, mock_cursor

# Mock update_meal_stats and get_random for controlled testing
@pytest.fixture
def mock_update_meal_stats(mock_db, mocker):
    """Mock update_meal_stats to prevent actual database updates."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")


@pytest.fixture
def mock_requests_get(mocker):
    mock_response = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


# Battle Test Cases


def test_battle_winner_combatant1(mock_requests_get, mock_update_meal_stats, battle_model, sample_meal1, sample_meal2):
    """Test battle where combatant 1 wins."""
    mock_requests_get.text = "0.1"  
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    winner = battle_model.battle()
    assert winner == sample_meal1.meal
    mock_update_meal_stats.assert_any_call(sample_meal1.id, 'win')
    mock_update_meal_stats.assert_any_call(sample_meal2.id, 'loss')
    assert len(battle_model.get_combatants()) == 1
    battle_model.clear_combatants()

def test_battle_winner_combatant2(mock_requests_get, mock_update_meal_stats, battle_model, sample_meal1, sample_meal2):
    """Test battle where combatant 2 wins."""
    mock_requests_get.text = "0.9"  
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    winner = battle_model.battle()
    assert winner == sample_meal2.meal
    mock_update_meal_stats.assert_any_call(sample_meal2.id, 'win')
    mock_update_meal_stats.assert_any_call(sample_meal1.id, 'loss')
    assert len(battle_model.get_combatants()) == 1
    battle_model.clear_combatants()


def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test error when there are not enough combatants"""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

def test_prep_combatant_list_full(battle_model, sample_meal1, sample_meal2):
    """Test that attempting to add more than two combatants raises a ValueError."""
    
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)  




# Battle Score Test Cases


def test_get_battle_score_low_difficulty(battle_model, sample_meal2):
    """Test calculating battle score for LOW difficulty """
    score = battle_model.get_battle_score(sample_meal2)
    expected_score = (sample_meal2.price * len(sample_meal2.cuisine)) - 3
    assert score == expected_score


def test_get_battle_score_high_difficulty(battle_model, sample_meal1):
    """Test calculating battle score for HIGH difficulty"""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 1
    assert score == expected_score

def test_get_battle_score_med_difficulty(battle_model, sample_meal3):
    """Test calculating battle score for MED difficulty"""
    score = battle_model.get_battle_score(sample_meal3)
    expected_score = (sample_meal3.price * len(sample_meal3.cuisine)) - 2
    assert score == expected_score

# Funtionality Test Cases

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test retrieving the current list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert battle_model.get_combatants() == [sample_meal1, sample_meal2]

def test_clear_combatants(battle_model, sample_meal1):
    """Test that clear_combatants properly empties the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.get_combatants()) == 1
    battle_model.clear_combatants()
    assert len(battle_model.get_combatants()) == 0
