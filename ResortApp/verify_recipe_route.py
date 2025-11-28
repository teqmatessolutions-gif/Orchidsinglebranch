"""Verify recipe route is registered"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Checking if recipe route is registered...")
print("=" * 60)

try:
    # Import the app
    from app.main import app
    
    # Get all routes
    all_routes = []
    recipe_routes = []
    
    for route in app.routes:
        if hasattr(route, 'path'):
            path = route.path
            all_routes.append(path)
            if 'recipe' in path.lower():
                recipe_routes.append(path)
    
    print(f"\nTotal routes in app: {len(all_routes)}")
    print(f"Recipe routes found: {len(recipe_routes)}")
    
    if recipe_routes:
        print("\n✅ Recipe routes are registered:")
        for route in recipe_routes:
            print(f"   {route}")
    else:
        print("\n❌ No recipe routes found!")
        print("\nFirst 20 routes (to verify app is loaded):")
        for route in all_routes[:20]:
            print(f"   {route}")
        
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING:")
        print("=" * 60)
        print("1. Check your server console for these messages:")
        print("   - '✅ Recipe router imported successfully in app.main'")
        print("   - '✅ Recipe router registered in app.main with X routes'")
        print("\n2. If you see error messages instead, share them.")
        print("\n3. Make sure you restarted the server after adding the recipe router.")
        print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()



