from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats,
)

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall_return_value = []
    mock_cursor.commit.return_value = None
    
    # Mock the get_db_connection function context manager
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn

    mocker.patch("meal_max.models.kitchen.get_db_connection", mock_get_db_connection)

    return mock_cursor
    
def test_create_meal(mock_cursor):
    """Test creating a new meal."""

    # Create a new meal
    create_meal(meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="LOW")

    # Check if the cursor executed the correct SQL query
    expected_sql_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)
    
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert SQL query is correct
    assert actual_query == expected_sql_query, "The SQL query did not match the expected query."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Spaghetti", "Italian", 10.99, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_with_invalid_price():
    """Test creating a new meal with an invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -10.99. Price must be a positive number.") as e:
        create_meal(meal="Spaghetti", cuisine="Italian", price=-10.99, difficulty="LOW")

    # Attempt with non-numeric price
    with pytest.raises(ValueError, match="Invalid price: NO. Price must be a positive number.") as e:
        create_meal(meal="Spaghetti", cuisine="Italian", price="NO", difficulty="LOW")

def test_create_meal_with_invalid_difficulty():
    """Test creating a new meal with an invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: MEDIUM. Must be 'LOW', 'MED', or 'HIGH'.") as e:
        create_meal(meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="MEDIUM")

    # Attempt with non-string difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: 123. Must be 'LOW', 'MED', or 'HIGH'.") as e:
        create_meal(meal="Spaghetti", cuisine="Italian", price=10.99, difficulty=123)

def test_create_meal_duplicate(mock_cursor):
    """Test creating a new meal with a duplicate name."""

    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    with pytest.raises(ValueError, match="Meal with name Spaghetti already exists") as e:
        create_meal(meal="Spaghetti", cuisine="Italian", price=10.99, difficulty="LOW")
    
def test_delete_meal(mock_cursor):
    """Tests soft deleting a meal."""

    mock_cursor.fetchone.return_value = ([False])

    delete_song(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT SQL query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE SQL query did not match the expected structure."

    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT SQL arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE SQL arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Tests soft deleting a meal with a bad ID."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found") as e:
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Tests soft deleting a meal that has already been deleted."""

    mock_cursor.fetchone.return_value = ([True])

    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted") as e:
        delete_meal(999)

def test_get_meal_by_id(mock_cursor):
    """Tests retrieving a meal by ID."""

    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 10.99, "LOW", False)

    result = get_meal_by_id(1)

    expected_result = Meal(1, "Spaghetti", "Italian", 10.99, "LOW")

    assert result == expected_result, f"Expected {expected_result}, but got {result}."

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    """Tests retrieving a meal by a bad ID."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found") as e:
        get_meal_by_id(999)

def test_get_meal_by_id_deleted(mock_cursor):
    """Tests retrieving a meal that has been deleted."""

    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 10.99, "LOW", True)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted") as e:
        get_meal_by_id(1)

def test_get_meal_by_name(mock_cursor):

    mock_cursor.fetchone.return_value = (1, "Spaghetti", "Italian", 10.99, "LOW", False)

    result = get_meal_by_name("Spaghetti")

    expected_result = Meal(1, "Spaghetti", "Italian", 10.99, "LOW")

    assert result == expected_result, f"Expected {expected_result}, got {result}."

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Spaghetti",)
    assert actual_arguments == expected_arguments, f"The SQL arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_name_bad_name(mock_cursor):
    """Tests retrieving a meal by a bad name."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Ravioli not found") as e:
        get_meal_by_name("Ravioli")

def test_update_meal_stats_win(mock_cursor):
    """Tests updating a meal's stats."""

    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    update_meal_stats(meal_id, "win")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[1][0][1]

    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_loss(mock_cursor):
    """Tests updating a meal's stats."""

    mock_cursor.fetchone.return_value = [False]

    meal_id = 1
    update_meal_stats(meal_id, "loss")

    expected_query = normalize_whitespace("UPDATE meals SET battles = battles + 1 WHERE id = ?")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[1][0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[1][0][1]

    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_deleted_meal(mock_cursor):
    """Tests updating a meal's stats that has been deleted."""

    mock_cursor.fetchone.return_value = [True]

    meal_id = 1
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted") as e:
        update_meal_stats(meal_id, "win")

    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (meal_id,))

def test_update_meal_stats_bad_id(mock_cursor):
    """Tests updating a meal's stats with a bad ID."""

    mock_cursor.fetchone.return_value = None

    meal_id = 999
    with pytest.raises(ValueError, match="Meal with ID 999 not found") as e:
        update_meal_stats(meal_id, "win")

def test_get_leaderboard_win():
    """Test retrieving the leaderboard based on win."""

    mock_cursor.fetchall.return_value = [
        (3, "Sushi", "Japanese", 15.99, "HIGH", 4, 3, (3 * 1.0 / 4)),
        (1, "Spaghetti", "Italian", 10.99, "LOW", 5, 2, (2 * 1.0 / 5)),
        (2, "Ravioli", "Italian", 12.99, "MED", 3, 1, (1 * 1.0 / 3)),
    ]

    mocker.patch("meal_max.models.kitchen.get_db_connection", return_value=mock_cursor)

    result = get_leaderboard("wins")

    expected_result = [
        {"id": 3, "meal": "Sushi", "cuisine": "Japanese", "price": 15.99, "difficulty": "HIGH", "battles": 4, "wins": 3, "win_rate": 0.75},
        {"id": 1, "meal": "Spaghetti", "cuisine": "Italian", "price": 10.99, "difficulty": "LOW", "battles": 5, "wins": 2, "win_rate": 0.4},
        {"id": 2, "meal": "Ravioli", "cuisine": "Italian", "price": 12.99, "difficulty": "MED", "battles": 3, "wins": 1, "win_rate": 0.33},
    ]

    assert result == expected_result, f"Expected {expected_result}, got {result}."

    expected_query = normalize_whitespace(""""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."  

def test_get_leaderboard_win_pct():
    """Test retrieving the leaderboard based on win percentage."""

    mock_cursor.fetchall.return_value = [
        (3, "Sushi", "Japanese", 15.99, "HIGH", 4, 3, (3 * 1.0 / 4)),
        (1, "Spaghetti", "Italian", 10.99, "LOW", 5, 2, (2 * 1.0 / 5)),
        (2, "Ravioli", "Italian", 12.99, "MED", 3, 1, (1 * 1.0 / 3)),
    ]

    mocker.patch("meal_max.models.kitchen.get_db_connection", return_value=mock_cursor)

    result = get_leaderboard("win_pct")

    expected_result = [
        {"id": 3, "meal": "Sushi", "cuisine": "Japanese", "price": 15.99, "difficulty": "HIGH", "battles": 4, "wins": 3, "win_rate": 0.75},
        {"id": 1, "meal": "Spaghetti", "cuisine": "Italian", "price": 10.99, "difficulty": "LOW", "battles": 5, "wins": 2, "win_rate": 0.4},
        {"id": 2, "meal": "Ravioli", "cuisine": "Italian", "price": 12.99, "difficulty": "MED", "battles": 3, "wins": 1, "win_rate": 0.33},
    ]

    assert result == expected_result, f"Expected {expected_result}, got {result}."

    expected_query = normalize_whitespace(""""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_leaderboard_none():
    """Test retrieving the leaderboard with no meals."""

    mock_cursor.fetchall.return_value = []

    mocker.patch("meal_max.models.kitchen.get_db_connection", return_value=mock_cursor)

    result = get_leaderboard("wins")

    expected_result = []

    assert result == expected_result, f"Expected {expected_result}, got {result}."

    expected_query = normalize_whitespace(""""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_clear_meals(mock_cursor):
    """Test clearing the list of meals."""

    mocker.patch.dict(os.environ, {"SQL_CREATE_TABLE_PATH": "/app/sql/create_meal_table.sql"})
    
    # Define the SQL script to recreate the meals table
    create_table_script = """
    DROP TABLE IF EXISTS meals;
    CREATE TABLE meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal TEXT NOT NULL UNIQUE,
        cuisine TEXT NOT NULL,
        price REAL NOT NULL,
        difficulty TEXT CHECK(difficulty IN ('HIGH', 'MED', 'LOW')),
        battles INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        deleted BOOLEAN DEFAULT FALSE
    );
    """
    
    mock_open = mock.mock_open(read_data=create_table_script)
    mocker.patch("builtins.open", mock_open)
    
    clear_meals()
    
    expected_script = normalize_whitespace(create_table_script)
    actual_script = normalize_whitespace(mock_cursor.executescript.call_args[0][0])

    assert actual_script == expected_script, "The executed SQL script did not match the expected script."
    mock_cursor.connection.commit.assert_called_once()

def test_clear_meals_error(mock_cursor):
    """Test clearing the list of meals with an error."""

    mocker.patch.dict(os.environ, {"SQL_CREATE_TABLE_PATH": "/app/sql/create_meal_table.sql"})
    
    create_table_script = """
    DROP TABLE IF EXISTS meals;
    CREATE TABLE meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal TEXT NOT NULL UNIQUE,
        cuisine TEXT NOT NULL,
        price REAL NOT NULL,
        difficulty TEXT CHECK(difficulty IN ('HIGH', 'MED', 'LOW')),
        battles INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        deleted BOOLEAN DEFAULT FALSE
    );
    """
    
    mock_open = mock.mock_open(read_data=create_table_script)
    mocker.patch("builtins.open", mock_open)
    
    mock_cursor.executescript.side_effect = sqlite3.Error("Error executing script")
    
    with pytest.raises(sqlite3.Error, match="Error executing script"):
        clear_meals()
    
    expected_script = normalize_whitespace(create_table_script)
    actual_script = normalize_whitespace(mock_cursor.executescript.call_args[0][0])

    assert actual_script == expected_script, "The executed SQL script did not match the expected script."
    mock_cursor.connection.commit.assert_not_called()