"""Quick check to see if recipe router can be imported"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Recipe Router Import Check")
print("=" * 60)

try:
    print("\n1. Testing basic imports...")
    from app.models.recipe import Recipe
    print("   ✓ Recipe model")
    
    from app.schemas.recipe import RecipeOut
    print("   ✓ Recipe schema")
    
    print("\n2. Testing router import...")
    from app.api import recipe
    print("   ✓ Recipe router imported")
    print(f"   Router prefix: {recipe.router.prefix}")
    print(f"   Number of routes: {len(recipe.router.routes)}")
    
    print("\n3. Testing route paths...")
    for route in recipe.router.routes:
        if hasattr(route, 'path'):
            methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
            print(f"   {methods} {route.path}")
    
    print("\n4. Testing app import...")
    from app.main import app
    
    recipe_routes = [r for r in app.routes if hasattr(r, 'path') and 'recipe' in r.path.lower()]
    print(f"   Recipe routes in app: {len(recipe_routes)}")
    
    if recipe_routes:
        print("   ✓ Routes are registered!")
        for route in recipe_routes:
            methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
            print(f"     {methods} {route.path}")
    else:
        print("   ✗ Routes are NOT registered")
        print("\n   This means the router import failed or recipe = None")
        print("   Check your server console for error messages when starting.")
    
    print("\n" + "=" * 60)
    print("Check complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nThis error needs to be fixed before the router can be registered.")



