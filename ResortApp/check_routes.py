"""Quick script to check if recipe routes are registered"""
from app.main import app

print("Checking for recipe routes...")
recipe_routes = []
all_routes = []

for route in app.routes:
    if hasattr(route, 'path'):
        path = route.path
        all_routes.append(path)
        if 'recipe' in path.lower():
            recipe_routes.append(path)

if recipe_routes:
    print(f"\n✅ Found {len(recipe_routes)} recipe route(s):")
    for route in recipe_routes:
        print(f"   {route}")
else:
    print("\n❌ No recipe routes found!")
    print("\nFirst 30 registered routes:")
    for route in all_routes[:30]:
        print(f"   {route}")



