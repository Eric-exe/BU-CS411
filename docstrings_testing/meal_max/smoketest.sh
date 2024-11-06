#!/bin/bash

BASE_URL="http://localhost:5000/api"

ECHO_JSON=false

while [ "$#" -gt 0 ]; do
    case $1 in
        --echo-json) ECHO_JSON=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
    done

    check_health() {
    echo "Checking health status..."
    curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
    if [ $? -eq 0 ]; then
        echo "Service is healthy."
    else
        echo "Health check failed."
        exit 1
    fi
}

# Function to check the database connection
check_db() {
    echo "Checking database connection..."
    curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
    if [ $? -eq 0 ]; then
        echo "Database connection is healthy."
    else
        echo "Database check failed."
        exit 1
    fi
}

# Function to check the meal creation
create_meal() {
    meal=$1
    cuisine=$2
    price=$3
    difficulty=$4

    echo "Adding meal ($meal, $cuisine, $price, $difficulty)..."
    curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" -d "{\"meal\": \"$meal\", \"cuisine\": \"$cuisine\", \"price\": $price, \"difficulty\": $difficulty}" | grep -q '"status": "success"'

    if [ $? -eq 0 ]; then
        echo "Meal added successfully."
    else
        echo "Failed to add meal."
        exit 1
    fi
}

# Function to check clear meals
clear_meals() {
    echo "Clearing meals..."
    curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Catalog cleared successfully."
    else
        echo "Failed to clear catalog."
        exit 1
    fi
}

# Function delete meal by id
delete_meal() {
    id=$1
    echo "Deleting meal with id $id..."
    curl -s -X DELETE "$BASE_URL/delete-meal/$id" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Meal deleted successfully."
    else
        echo "Failed to delete meal."
        exit 1
    fi
}

# Function to get meal by id
get_meal_by_id() {
    id=$1
    echo "Getting meal with id $id..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by ($id)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON (ID $id):"
            echo "$response" | jq .
        fi
    fi
    else 
        echo "Failed to retrieve meal by ID ($id)."
        exit 1
    fi
}

# Function to get meal by name
get_meal_by_name() {
    name=$1
    echo "Getting meal with name $name..."
    response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$name")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Meal retrieved successfully by ($name)."
        if [ "$ECHO_JSON" = true ]; then
            echo "Meal JSON (Name $name):"
            echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve meal by name ($name)."
        exit 1
    fi
}

# Function to test battle
test_battle() {
    echo "Testing battle..."
    response=$(curl -s -X GET "$BASE_URL/battle")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Battle tested successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Battle JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to test battle."
        exit 1
    fi
}

# Function to clear combatants
clear_combatants() {
    echo "Clearing combatants..."
    curl -s -X POST "$BASE_URL/clear-combatants" | grep -q '"status": "success"'
    if [ $? -eq 0 ]; then
        echo "Combatants cleared successfully."
    else
        echo "Failed to clear combatants."
        exit 1
    fi
}

# Function to get combatants
get_combatants() {
    echo "Getting combatants..."
    response=$(curl -s -X GET "$BASE_URL/get-combatants")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Combatants retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Combatants JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve combatants."
        exit 1
    fi
}

# Function to prep combatants
prep_combatant() {
    name=$1
    echo "Prepping combatants..."
    response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" -d "{\"meal\": \"$name\"}")

}

# Function to get leaderboard
get_leaderboard() {
    sort_by=$1
    echo "Getting leaderboard..."
    response=$(curl -s -X GET "$BASE_URL/get-leaderboard?sort=$sort_by")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Leaderboard JSON:"
            echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve leaderboard."
        exit 1
    fi
}

# Health checks
check_health
check_db

# Create meals
create_meal "Burger" "American" 10 1
create_meal "Pizza" "Italian" 15 2
create_meal "Sushi" "Japanese" 20 3
create_meal "Taco" "Mexican" 12 2
create_meal "Pasta" "Italian" 18 3

# Get meals by ID
get_meal_by_id 1
get_meal_by_id 2
get_meal_by_id 4

delete_meal_by_id 3
delete_meal_by_id 5

clear_meals

create_meal "Burger" "American" 10 1
create_meal "Pizza" "Italian" 15 2
create_meal "Sushi" "Japanese" 20 3
create_meal "Taco" "Mexican" 12 2

get_meal_by_name "Burger"
get_meal_by_name "Pizza"
get_meal_by_name "Taco"

clear_combatants

prep_combatant "Burger"
prep_combatant "Pizza"
prep_combatant "Sushi"
prep_combatant "Taco"

get_combatants

test_battle
test_battle

get_leaderboard "wins"
get_leaderboard "win_pct"

echo "Smoke test completed successfully."

