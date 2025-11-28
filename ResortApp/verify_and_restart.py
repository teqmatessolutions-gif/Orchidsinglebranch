"""
Script to verify recipe router setup and provide restart instructions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("Recipe Router Verification")
print("=" * 70)

all_ok = True

# Check imports
print("\n1. Checking imports...")
try:
    from app.models.recipe import Recipe
    print("   ✓ Models OK")
except Exception as e:
    print(f"   ✗ Models ERROR: {e}")
    all_ok = False

try:
    from app.schemas.recipe import RecipeOut
    print("   ✓ Schemas OK")
except Exception as e:
    print(f"   ✗ Schemas ERROR: {e}")
    all_ok = False

try:
    from app.api import recipe
    print("   ✓ Router import OK")
    print(f"   Router has {len(recipe.router.routes)} routes")
except Exception as e:
    print(f"   ✗ Router import ERROR: {e}")
    import traceback
    traceback.print_exc()
    all_ok = False

# Check app registration
print("\n2. Checking app registration...")
try:
    from app.main import app
    recipe_routes = [r.path for r in app.routes if hasattr(r, 'path') and 'recipe' in r.path.lower()]
    if recipe_routes:
        print(f"   ✓ Router registered with {len(recipe_routes)} route(s)")
        for route in recipe_routes:
            print(f"      {route}")
    else:
        print("   ✗ Router NOT registered in app")
        print("   This means the server needs to be restarted!")
        all_ok = False
except Exception as e:
    print(f"   ✗ Error: {e}")
    all_ok = False

print("\n" + "=" * 70)
if all_ok:
    print("✅ All checks passed!")
    print("\nIf you're still getting 404:")
    print("1. Stop your backend server (Ctrl+C)")
    print("2. Start it again: python main.py")
    print("3. Check the console for '✅ Recipe router registered' message")
else:
    print("❌ Issues found - see errors above")
print("=" * 70)



