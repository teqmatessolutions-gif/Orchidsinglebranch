-- Migration: Create Recipe and RecipeIngredient tables
-- This allows linking food menu items to inventory items with quantities

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    food_item_id INTEGER NOT NULL REFERENCES food_items(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    servings INTEGER DEFAULT 1,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recipe_ingredients table
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    inventory_item_id INTEGER NOT NULL REFERENCES inventory_items(id) ON DELETE CASCADE,
    quantity FLOAT NOT NULL,
    unit VARCHAR NOT NULL,
    notes VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_recipes_food_item_id ON recipes(food_item_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_inventory_item_id ON recipe_ingredients(inventory_item_id);

-- Add comments
COMMENT ON TABLE recipes IS 'Recipes linking food menu items to inventory items';
COMMENT ON TABLE recipe_ingredients IS 'Individual ingredients (inventory items) used in recipes';
COMMENT ON COLUMN recipes.servings IS 'Number of servings this recipe makes';
COMMENT ON COLUMN recipe_ingredients.quantity IS 'Quantity of inventory item needed for the recipe';
COMMENT ON COLUMN recipe_ingredients.unit IS 'Unit of measurement (kg, liter, pcs, etc.)';



