from datetime import datetime
from app import app, db, Vehicle, MaintenanceRecord

# Complete vehicle data from the Fleet Info spreadsheet
VEHICLE_DATA = {
    '06': {
        'driver': 'Ryan',
        'miles': 99325,
        'year': 2017,
        'make': 'Ford',
        'model': 'Transit 250',
        'vin': '1FTYR1ZM5HKB10739',
        'license': '8JMJ131'
    },
    '07': {
        'driver': 'Triston',
        'miles': 171222,
        'year': 2016,
        'make': 'Ford',
        'model': 'Transit Connect Cargo',
        'vin': 'NM0LS7E74G1268749',
        'license': '04236W2'
    },
    '08': {
        'driver': 'Extra',
        'miles': 85472,
        'year': 2018,
        'make': 'Ford',
        'model': 'Transit Connect Passenger',
        'vin': 'NM0GS9F74J1365730',
        'license': '8DQR194'
    },
    '09': {
        'driver': 'Alexx',
        'miles': 79000,
        'year': 2017,
        'make': 'Mercedes',
        'model': 'Sprinter 2500',
        'vin': 'WD4PE8CD2HP551309',
        'license': '8USN020'
    },
    '10': {
        'driver': 'Andrew',
        'miles': 89978,
        'year': 2021,
        'make': 'Ford',
        'model': 'Transit Connect Cargo',
        'vin': 'NM0LS7E23M1492076',
        'license': '44695D3'
    },
    '11': {
        'driver': 'Jeremy',
        'miles': 72032,
        'year': 2020,
        'make': 'Toyota',
        'model': 'Prius XLE',
        'vin': 'JTDKARFU9L3125473',
        'license': '8ZER404'
    },
    '12': {
        'driver': 'Mase',
        'miles': 38076,
        'year': 2022,
        'make': 'Mercedes',
        'model': 'Metris',
        'vin': 'W1YV0CEY8N4202764',
        'license': '31451T3'
    },
    '13': {
        'driver': 'Mike',
        'miles': 48674,
        'year': 2022,
        'make': 'Mercedes',
        'model': 'Metris',
        'vin': 'W1YV0CEY9N4184078',
        'license': '3145013'
    },
    '00': {
        'driver': 'Kyle',
        'miles': 71277,
        'year': 2017,
        'make': 'Ford',
        'model': 'F250',
        'vin': '1FT7W2B62JEB29985',
        'license': '16014L2'
    }
}

def import_data():
    print(f"Importing accurate vehicle data from Fleet Info...\n")
    
    with app.app_context():
        print("Clearing existing data...")
        MaintenanceRecord.query.delete()
        Vehicle.query.delete()
        db.session.commit()
        
        print("\n=== Creating Vehicles ===")
        vehicles = {}
        for vehicle_num, data in VEHICLE_DATA.items():
            vehicle = Vehicle(
                vin=data['vin'],
                make=data['make'],
                model=data['model'],
                year=data['year'],
                license_plate=data['license'],
                purchase_date=datetime(data['year'], 1, 1).date(),
                current_mileage=data['miles'],
                status='Active',
                assigned_driver=data['driver']
            )
            db.session.add(vehicle)
            vehicles[vehicle_num] = vehicle
            print(f"  ✓ {data['year']} {data['make']} {data['model']} - {data['driver']} (VIN: {data['vin']}, License: {data['license']})")
        
        db.session.commit()
        print(f"\n✅ Created {len(vehicles)} vehicles")
        print(f"Total vehicles: {Vehicle.query.count()}")

if __name__ == '__main__':
    import_data()
