from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fleet_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# Models
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    current_mileage = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Active')  # Active, In Maintenance, Retired
    assigned_driver = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    maintenance_records = db.relationship('MaintenanceRecord', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Vehicle {self.make} {self.model} - {self.license_plate}>'


class MaintenanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # Oil Change, Tire Rotation, Inspection, Repair, Other
    service_date = db.Column(db.Date, nullable=False)
    mileage_at_service = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, default=0.0)
    service_provider = db.Column(db.String(100))
    notes = db.Column(db.Text)
    next_service_due = db.Column(db.Date)
    next_service_mileage = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaintenanceRecord {self.maintenance_type} - {self.service_date}>'


# Routes
@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    total_vehicles = Vehicle.query.count()
    active_vehicles = Vehicle.query.filter_by(status='Active').count()
    in_maintenance = Vehicle.query.filter_by(status='In Maintenance').count()
    
    # Recent maintenance
    recent_maintenance = MaintenanceRecord.query.order_by(MaintenanceRecord.service_date.desc()).limit(5).all()
    
    # Upcoming maintenance (within next 30 days)
    thirty_days_from_now = datetime.now().date() + timedelta(days=30)
    upcoming_maintenance = MaintenanceRecord.query.filter(
        MaintenanceRecord.next_service_due <= thirty_days_from_now,
        MaintenanceRecord.next_service_due >= datetime.now().date()
    ).order_by(MaintenanceRecord.next_service_due).all()
    
    # Total maintenance cost this month
    first_day_of_month = datetime.now().replace(day=1).date()
    monthly_cost = db.session.query(db.func.sum(MaintenanceRecord.cost)).filter(
        MaintenanceRecord.service_date >= first_day_of_month
    ).scalar() or 0
    
    return render_template('dashboard.html',
                         total_vehicles=total_vehicles,
                         active_vehicles=active_vehicles,
                         in_maintenance=in_maintenance,
                         recent_maintenance=recent_maintenance,
                         upcoming_maintenance=upcoming_maintenance,
                         monthly_cost=monthly_cost)


@app.route('/vehicles')
def vehicles():
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = Vehicle.query
    
    if search_query:
        query = query.filter(
            (Vehicle.make.contains(search_query)) |
            (Vehicle.model.contains(search_query)) |
            (Vehicle.license_plate.contains(search_query)) |
            (Vehicle.vin.contains(search_query))
        )
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    vehicles_list = query.order_by(Vehicle.make, Vehicle.model).all()
    
    return render_template('vehicles.html', vehicles=vehicles_list, search_query=search_query, status_filter=status_filter)


@app.route('/vehicle/add', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        try:
            vehicle = Vehicle(
                vin=request.form['vin'],
                make=request.form['make'],
                model=request.form['model'],
                year=int(request.form['year']),
                license_plate=request.form['license_plate'],
                purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date(),
                current_mileage=int(request.form['current_mileage']),
                status=request.form['status'],
                assigned_driver=request.form.get('assigned_driver', '')
            )
            db.session.add(vehicle)
            db.session.commit()
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('vehicles'))
        except Exception as e:
            flash(f'Error adding vehicle: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('vehicle_form.html', vehicle=None)


@app.route('/vehicle/edit/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            vehicle.vin = request.form['vin']
            vehicle.make = request.form['make']
            vehicle.model = request.form['model']
            vehicle.year = int(request.form['year'])
            vehicle.license_plate = request.form['license_plate']
            vehicle.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()
            vehicle.current_mileage = int(request.form['current_mileage'])
            vehicle.status = request.form['status']
            vehicle.assigned_driver = request.form.get('assigned_driver', '')
            
            db.session.commit()
            flash('Vehicle updated successfully!', 'success')
            return redirect(url_for('vehicle_detail', id=vehicle.id))
        except Exception as e:
            flash(f'Error updating vehicle: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('vehicle_form.html', vehicle=vehicle)


@app.route('/vehicle/<int:id>')
def vehicle_detail(id):
    vehicle = Vehicle.query.get_or_404(id)
    maintenance_records = MaintenanceRecord.query.filter_by(vehicle_id=id).order_by(MaintenanceRecord.service_date.desc()).all()
    
    # Calculate total maintenance cost
    total_cost = sum(record.cost for record in maintenance_records)
    
    # Check for upcoming maintenance
    upcoming = [record for record in maintenance_records if record.next_service_due and record.next_service_due >= datetime.now().date()]
    
    return render_template('vehicle_detail.html', vehicle=vehicle, maintenance_records=maintenance_records, total_cost=total_cost, upcoming=upcoming)


@app.route('/vehicle/delete/<int:id>', methods=['POST'])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    try:
        # Store vehicle data in session for undo
        session['pending_delete'] = {
            'type': 'vehicle',
            'id': id,
            'name': f'{vehicle.year} {vehicle.make} {vehicle.model}'
        }
        session.modified = True
        
        db.session.delete(vehicle)
        db.session.commit()
        flash('Vehicle deleted successfully! Click undo to restore.', 'warning')
    except Exception as e:
        flash(f'Error deleting vehicle: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('vehicles'))


@app.route('/maintenance')
def maintenance():
    search_query = request.args.get('search', '')
    type_filter = request.args.get('type', '')
    
    query = MaintenanceRecord.query.join(Vehicle)
    
    if search_query:
        query = query.filter(
            (Vehicle.make.contains(search_query)) |
            (Vehicle.model.contains(search_query)) |
            (Vehicle.license_plate.contains(search_query))
        )
    
    if type_filter:
        query = query.filter(MaintenanceRecord.maintenance_type == type_filter)
    
    maintenance_records = query.order_by(MaintenanceRecord.service_date.desc()).all()
    
    return render_template('maintenance.html', maintenance_records=maintenance_records, search_query=search_query, type_filter=type_filter)


@app.route('/maintenance/add/<int:vehicle_id>', methods=['GET', 'POST'])
def add_maintenance(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # Get maintenance type - use custom if "Other" is selected
            maintenance_type = request.form['maintenance_type']
            if maintenance_type == 'Other' and request.form.get('custom_maintenance_type'):
                maintenance_type = request.form['custom_maintenance_type']
            
            maintenance = MaintenanceRecord(
                vehicle_id=vehicle_id,
                maintenance_type=maintenance_type,
                service_date=datetime.strptime(request.form['service_date'], '%Y-%m-%d').date(),
                mileage_at_service=int(request.form['mileage_at_service']),
                cost=float(request.form['cost']),
                service_provider=request.form.get('service_provider', ''),
                notes=request.form.get('notes', ''),
                next_service_due=datetime.strptime(request.form['next_service_due'], '%Y-%m-%d').date() if request.form.get('next_service_due') else None,
                next_service_mileage=int(request.form['next_service_mileage']) if request.form.get('next_service_mileage') else None
            )
            
            # Update vehicle mileage if the service mileage is higher
            if maintenance.mileage_at_service > vehicle.current_mileage:
                vehicle.current_mileage = maintenance.mileage_at_service
            
            db.session.add(maintenance)
            db.session.commit()
            flash('Maintenance record added successfully!', 'success')
            return redirect(url_for('vehicle_detail', id=vehicle_id))
        except Exception as e:
            flash(f'Error adding maintenance record: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('maintenance_form.html', vehicle=vehicle, maintenance=None)


@app.route('/maintenance/edit/<int:id>', methods=['GET', 'POST'])
def edit_maintenance(id):
    maintenance = MaintenanceRecord.query.get_or_404(id)
    vehicle = maintenance.vehicle
    
    if request.method == 'POST':
        try:
            # Get maintenance type - use custom if "Other" is selected
            maintenance_type = request.form['maintenance_type']
            if maintenance_type == 'Other' and request.form.get('custom_maintenance_type'):
                maintenance_type = request.form['custom_maintenance_type']
            
            maintenance.maintenance_type = maintenance_type
            maintenance.service_date = datetime.strptime(request.form['service_date'], '%Y-%m-%d').date()
            maintenance.mileage_at_service = int(request.form['mileage_at_service'])
            maintenance.cost = float(request.form['cost'])
            maintenance.service_provider = request.form.get('service_provider', '')
            maintenance.notes = request.form.get('notes', '')
            maintenance.next_service_due = datetime.strptime(request.form['next_service_due'], '%Y-%m-%d').date() if request.form.get('next_service_due') else None
            maintenance.next_service_mileage = int(request.form['next_service_mileage']) if request.form.get('next_service_mileage') else None
            
            db.session.commit()
            flash('Maintenance record updated successfully!', 'success')
            return redirect(url_for('vehicle_detail', id=maintenance.vehicle_id))
        except Exception as e:
            flash(f'Error updating maintenance record: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('maintenance_form.html', vehicle=vehicle, maintenance=maintenance)


@app.route('/maintenance/delete/<int:id>', methods=['POST'])
def delete_maintenance(id):
    maintenance = MaintenanceRecord.query.get_or_404(id)
    vehicle_id = maintenance.vehicle_id
    
    try:
        # Store maintenance data in session for undo
        session['pending_delete'] = {
            'type': 'maintenance',
            'id': id,
            'vehicle_id': vehicle_id,
            'data': {
                'vehicle_id': maintenance.vehicle_id,
                'maintenance_type': maintenance.maintenance_type,
                'service_date': maintenance.service_date.isoformat(),
                'mileage_at_service': maintenance.mileage_at_service,
                'cost': maintenance.cost,
                'service_provider': maintenance.service_provider,
                'notes': maintenance.notes,
                'next_service_due': maintenance.next_service_due.isoformat() if maintenance.next_service_due else None,
                'next_service_mileage': maintenance.next_service_mileage
            }
        }
        session.modified = True
        
        db.session.delete(maintenance)
        db.session.commit()
        flash('Maintenance record deleted! Click undo to restore.', 'warning')
    except Exception as e:
        flash(f'Error deleting maintenance record: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('vehicle_detail', id=vehicle_id))


@app.route('/undo-delete', methods=['POST'])
def undo_delete():
    if 'pending_delete' not in session:
        return jsonify({'success': False, 'message': 'Nothing to undo'})
    
    delete_info = session.pop('pending_delete')
    session.modified = True
    
    try:
        if delete_info['type'] == 'maintenance':
            # Restore maintenance record
            data = delete_info['data']
            maintenance = MaintenanceRecord(
                vehicle_id=data['vehicle_id'],
                maintenance_type=data['maintenance_type'],
                service_date=datetime.fromisoformat(data['service_date']).date(),
                mileage_at_service=data['mileage_at_service'],
                cost=data['cost'],
                service_provider=data['service_provider'],
                notes=data['notes'],
                next_service_due=datetime.fromisoformat(data['next_service_due']).date() if data['next_service_due'] else None,
                next_service_mileage=data['next_service_mileage']
            )
            db.session.add(maintenance)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Maintenance record restored!', 'redirect': url_for('vehicle_detail', id=delete_info['vehicle_id'])})
        
        return jsonify({'success': False, 'message': 'Cannot undo vehicle deletion'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/upload-document', methods=['GET', 'POST'])
def upload_document():
    vehicles = Vehicle.query.all()
    recent_uploads = MaintenanceRecord.query.order_by(MaintenanceRecord.created_at.desc()).limit(5).all()
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'document' not in request.files:
            flash('⚠️ No file uploaded', 'danger')
            return redirect(request.url)
        
        file = request.files['document']
        
        if file.filename == '':
            flash('⚠️ No file selected', 'danger')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('⚠️ Invalid file type. Please upload PDF, JPG, or PNG files only.', 'danger')
            return redirect(request.url)
        
        if file:
            try:
                # Read file content
                filename = secure_filename(file.filename)
                file_content = file.read()
                
                print(f"📄 Processing file: {filename}, Size: {len(file_content)} bytes")
                
                # Get preselected vehicle if any
                preselected_vehicle_id = request.form.get('vehicle_id')
                if preselected_vehicle_id:
                    preselected_vehicle_id = int(preselected_vehicle_id)
                    print(f"🚗 Preselected vehicle ID: {preselected_vehicle_id}")
                
                # Initialize document processor
                from document_processor import DocumentProcessor
                api_key = os.getenv('OPENAI_API_KEY')
                processor = DocumentProcessor(openai_api_key=api_key)
                
                print(f"🤖 Using OpenAI: {'Yes' if api_key else 'No (fallback mode)'}")
                
                # Prepare vehicles list for processor
                vehicles_list = [{
                    'id': v.id,
                    'vin': v.vin,
                    'make': v.make,
                    'model': v.model,
                    'year': v.year,
                    'license_plate': v.license_plate
                } for v in vehicles]
                
                # Process document
                result = processor.process_document(
                    filename, 
                    file_content, 
                    vehicles_list,
                    preselected_vehicle_id
                )
                
                print(f"📊 Processing result: {result.get('success')}")
                
                if not result['success']:
                    error_msg = result['error']
                    print(f"❌ Error: {error_msg}")
                    flash(f'❌ {error_msg}', 'danger')
                    return render_template('upload_document.html', 
                                         vehicles=vehicles, 
                                         recent_uploads=recent_uploads,
                                         error_details=result.get('extracted_data'))
                
                # Create maintenance record from extracted data
                vehicle = Vehicle.query.get(result['vehicle']['id'])
                
                # Parse service date
                service_date = datetime.now().date()
                if result.get('service_date'):
                    try:
                        service_date = datetime.strptime(result['service_date'], '%Y-%m-%d').date()
                    except:
                        pass
                
                # Create maintenance record
                maintenance = MaintenanceRecord(
                    vehicle_id=vehicle.id,
                    maintenance_type=result['maintenance_type'],
                    service_date=service_date,
                    mileage_at_service=result.get('mileage') or vehicle.current_mileage,
                    cost=result.get('cost') or 0.0,
                    service_provider=result.get('provider'),
                    notes=result.get('description'),
                    next_service_mileage=result.get('next_service_mileage')
                )
                
                # Update vehicle mileage if higher
                if result.get('mileage') and result['mileage'] > vehicle.current_mileage:
                    vehicle.current_mileage = result['mileage']
                
                db.session.add(maintenance)
                db.session.commit()
                
                print(f"✅ Successfully created maintenance record for vehicle {vehicle.id}")
                
                flash(f'✅ Document processed successfully! Created {result["maintenance_type"]} record for {vehicle.year} {vehicle.make} {vehicle.model}', 'success')
                return redirect(url_for('vehicle_detail', id=vehicle.id))
                
            except Exception as e:
                error_detail = str(e)
                print(f"❌ Exception during processing: {error_detail}")
                import traceback
                traceback.print_exc()
                flash(f'❌ Error processing document: {error_detail}', 'danger')
                db.session.rollback()
                return redirect(request.url)
    
    return render_template('upload_document.html', 
                         vehicles=vehicles, 
                         recent_uploads=recent_uploads)


# ===== EXCEL IMPORT/EXPORT ROUTES =====

@app.route('/import-data')
def import_data_page():
    """Display the data import page"""
    total_vehicles = Vehicle.query.count()
    total_records = MaintenanceRecord.query.count()
    return render_template('import_data.html', 
                         total_vehicles=total_vehicles,
                         total_records=total_records)


@app.route('/download-template')
def download_template():
    """Download the Excel import template"""
    from excel_handler import create_fleet_template
    from flask import send_file
    
    template = create_fleet_template()
    
    return send_file(
        template,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Fleet_Import_Template.xlsx'
    )


@app.route('/import-data/upload', methods=['POST'])
def upload_import_file():
    """Handle Excel file upload and show preview"""
    from excel_handler import parse_excel_import
    
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('import_data_page'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('import_data_page'))
    
    # Check file extension
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('Please upload an Excel file (.xlsx or .xls)', 'danger')
        return redirect(url_for('import_data_page'))
    
    try:
        # Parse the Excel file
        parsed = parse_excel_import(file)
        
        # Store parsed data in session for confirmation
        session['import_data'] = {
            'vehicles': [
                {
                    'vin': v['vin'],
                    'make': v['make'],
                    'model': v['model'],
                    'year': v['year'],
                    'license_plate': v['license_plate'],
                    'purchase_date': v['purchase_date'].isoformat() if v.get('purchase_date') else None,
                    'current_mileage': v['current_mileage'],
                    'status': v['status'],
                    'assigned_driver': v['assigned_driver']
                }
                for v in parsed['vehicles']
            ],
            'maintenance': [
                {
                    'vehicle_vin': m['vehicle_vin'],
                    'maintenance_type': m['maintenance_type'],
                    'service_date': m['service_date'].isoformat() if m.get('service_date') else None,
                    'mileage_at_service': m['mileage_at_service'],
                    'cost': m['cost'],
                    'service_provider': m['service_provider'],
                    'notes': m['notes'],
                    'next_service_due': m['next_service_due'].isoformat() if m.get('next_service_due') else None,
                    'next_service_mileage': m['next_service_mileage']
                }
                for m in parsed['maintenance']
            ],
            'errors': parsed['errors'],
            'warnings': parsed['warnings']
        }
        
        return render_template('import_preview.html',
                             vehicles=parsed['vehicles'],
                             maintenance=parsed['maintenance'],
                             errors=parsed['errors'],
                             warnings=parsed['warnings'])
        
    except Exception as e:
        flash(f'Error reading Excel file: {str(e)}', 'danger')
        return redirect(url_for('import_data_page'))


@app.route('/import-data/confirm', methods=['POST'])
def confirm_import():
    """Confirm and execute the import"""
    from excel_handler import import_data_to_db
    from datetime import date
    
    if 'import_data' not in session:
        flash('No import data found. Please upload a file first.', 'danger')
        return redirect(url_for('import_data_page'))
    
    import_data = session['import_data']
    clear_existing = request.form.get('clear_existing') == 'yes'
    
    # Convert date strings back to date objects
    for v in import_data['vehicles']:
        if v['purchase_date']:
            v['purchase_date'] = date.fromisoformat(v['purchase_date'])
    
    for m in import_data['maintenance']:
        if m['service_date']:
            m['service_date'] = date.fromisoformat(m['service_date'])
        if m['next_service_due']:
            m['next_service_due'] = date.fromisoformat(m['next_service_due'])
    
    # Execute import
    result = import_data_to_db(
        {'vehicles': import_data['vehicles'], 'maintenance': import_data['maintenance']},
        db, Vehicle, MaintenanceRecord, clear_existing
    )
    
    # Clear session data
    session.pop('import_data', None)
    
    if result['success']:
        message = f"✅ Import completed! Added {result['vehicles_added']} vehicles and {result['maintenance_added']} maintenance records."
        if result.get('vehicles_skipped', 0) > 0:
            message += f" ({result['vehicles_skipped']} vehicles skipped - already exist)"
        flash(message, 'success')
    else:
        flash(f"❌ Import failed: {'; '.join(result['errors'])}", 'danger')
    
    return redirect(url_for('vehicles'))


# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
