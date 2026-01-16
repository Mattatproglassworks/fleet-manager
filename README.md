# Fleet Management System

A comprehensive web-based application for managing vehicle fleets and maintenance records.

## Features

- **Vehicle Management**: Add, edit, view, and delete vehicles
- **Maintenance Tracking**: Log and track all maintenance activities
- **Dashboard**: Real-time statistics and alerts
- **Search & Filter**: Find vehicles and maintenance records quickly
- **Maintenance Alerts**: Track upcoming maintenance schedules
- **Cost Tracking**: Monitor maintenance expenses

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Templating**: Jinja2

## Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Adding a Vehicle
1. Navigate to "Vehicles" from the main menu
2. Click "Add New Vehicle"
3. Fill in vehicle details (VIN, make, model, year, etc.)
4. Click "Save Vehicle"

### Logging Maintenance
1. Go to a vehicle's detail page
2. Click "Add Maintenance Record"
3. Enter service details, cost, and next service date
4. Click "Save Record"

### Dashboard
The dashboard provides:
- Total vehicle count
- Vehicles currently in maintenance
- Recent maintenance activities
- Upcoming maintenance alerts
- Monthly maintenance costs

## Database Schema

### Vehicle Table
- VIN (unique identifier)
- Make, Model, Year
- License Plate
- Current Mileage
- Status (Active, In Maintenance, Retired)
- Assigned Driver
- Purchase Date

### Maintenance Record Table
- Vehicle reference
- Maintenance Type (Oil Change, Tire Rotation, Inspection, Repair, Other)
- Service Date
- Mileage at Service
- Cost
- Service Provider
- Notes
- Next Service Due Date
- Next Service Mileage

## Project Structure

```
fleet-management/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── vehicles.html
│   ├── vehicle_detail.html
│   ├── vehicle_form.html
│   ├── maintenance.html
│   └── maintenance_form.html
└── static/                # Static files (CSS, JS, images)
    └── style.css
```

## Future Enhancements

- User authentication and authorization
- Email/SMS notifications for maintenance alerts
- Export reports to PDF/Excel
- Vehicle photos and documents
- Fuel consumption tracking
- Driver management module
- Mobile responsive improvements
- API endpoints for mobile apps

## License

MIT License

## Support

For issues or questions, please open an issue on the project repository.
