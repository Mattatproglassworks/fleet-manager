from datetime import datetime
from app import app, db, Vehicle

# Restore vehicle 08 - 2018 Ford Transit Connect Passenger
def restore_vehicle_08():
    with app.app_context():
        # Check if vehicle already exists
        existing = Vehicle.query.filter_by(vin='NM0GS9F74J1365730').first()
        if existing:
            print(f"✓ Vehicle already exists: {existing.year} {existing.make} {existing.model}")
            return
        
        vehicle = Vehicle(
            vin='NM0GS9F74J1365730',
            make='Ford',
            model='Transit Connect Passenger',
            year=2018,
            license_plate='8DQR194',
            purchase_date=datetime(2018, 1, 1).date(),
            current_mileage=85472,
            status='Active',
            assigned_driver='Extra'
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        print(f"✅ Restored: {vehicle.year} {vehicle.make} {vehicle.model}")
        print(f"   VIN: {vehicle.vin}")
        print(f"   License: {vehicle.license_plate}")
        print(f"   Driver: {vehicle.assigned_driver}")
        print(f"   Mileage: {vehicle.current_mileage:,}")

if __name__ == '__main__':
    restore_vehicle_08()
