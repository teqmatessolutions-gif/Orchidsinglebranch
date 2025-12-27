
filename = "Bookings.jsx"
with open(filename, "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "function Bookings" in line or "const Bookings =" in line:
            print(f"Found at line {i+1}: {line.strip()}")
