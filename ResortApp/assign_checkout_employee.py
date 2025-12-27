"""
Quick script to assign an employee to a checkout request
This is a workaround while the UI button is being added
"""
from app.database import SessionLocal
from app.models.checkout import CheckoutRequest
from app.models.employee import Employee


def assign_employee_to_checkout():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("ASSIGN EMPLOYEE TO CHECKOUT REQUEST")
        print("=" * 60)
        print()
        
        # List all pending checkout requests
        pending_checkouts = db.query(CheckoutRequest).filter(
            CheckoutRequest.status == "pending"
        ).all()
        
        if not pending_checkouts:
            print("❌ No pending checkout requests found.")
            return
        
        print(f"📋 Found {len(pending_checkouts)} pending checkout request(s):")
        print()
        for i, checkout in enumerate(pending_checkouts, 1):
            employee_name = "Not assigned"
            if checkout.employee_id:
                emp = db.query(Employee).filter(Employee.id == checkout.employee_id).first()
                if emp:
                    employee_name = emp.name
            
            print(f"  {i}. Room {checkout.room_number} - Guest: {checkout.guest_name}")
            print(f"     Employee: {employee_name}")
            print(f"     Created: {checkout.created_at}")
            print()
        
        # Select checkout request
        if len(pending_checkouts) == 1:
            selected_checkout = pending_checkouts[0]
            print(f"✓ Auto-selected the only checkout request (Room {selected_checkout.room_number})")
        else:
            selection = input(f"Select checkout request (1-{len(pending_checkouts)}): ").strip()
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(pending_checkouts):
                    selected_checkout = pending_checkouts[idx]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid input")
                return
        
        print()
        
        # List all employees
        employees = db.query(Employee).all()
        
        if not employees:
            print("❌ No employees found.")
            return
        
        print(f"👥 Available Employees:")
        print()
        for i, emp in enumerate(employees, 1):
            print(f"  {i}. {emp.name}")
        print()
        
        # Select employee
        emp_selection = input(f"Select employee to assign (1-{len(employees)}): ").strip()
        try:
            emp_idx = int(emp_selection) - 1
            if 0 <= emp_idx < len(employees):
                selected_employee = employees[emp_idx]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Invalid input")
            return
        
        print()
        print("=" * 60)
        print("CONFIRMATION")
        print("=" * 60)
        print(f"  Checkout Request: Room {selected_checkout.room_number}")
        print(f"  Guest: {selected_checkout.guest_name}")
        print(f"  Assign to: {selected_employee.name}")
        print()
        
        confirm = input("Proceed with assignment? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("❌ Assignment cancelled.")
            return
        
        # Assign employee
        selected_checkout.employee_id = selected_employee.id
        db.commit()
        
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"  Employee {selected_employee.name} has been assigned to")
        print(f"  checkout verification for Room {selected_checkout.room_number}")
        print()
        print("Refresh your browser to see the updated assignment.")
        print()
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    assign_employee_to_checkout()
