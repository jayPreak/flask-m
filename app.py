# app.py
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database models
class Meter(db.Model):
    __tablename__ = 'meters'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    data = db.relationship('MeterData', backref='meter', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'label': self.label
        }

class MeterData(db.Model):
    __tablename__ = 'meter_data'
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.Integer, db.ForeignKey('meters.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'meter_id': self.meter_id,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value
        }

# Initialize the database and create tables
def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if we already have data
        if Meter.query.count() == 0:
            # Create some meters
            meters = [
                Meter(label="Return by Death Counter"),
                Meter(label="Witch Cult Activity Monitor"),
                Meter(label="Emilia's Mana Level"),
                Meter(label="Roswaal Mansion Energy"),
                Meter(label="Great Rabbit Detection Grid")
            ]
            db.session.add_all(meters)
            db.session.commit()
            
            # Create some meter data
            # For each meter, create data points for the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            for meter in Meter.query.all():
                # Create a reading every hour for 30 days
                current_time = start_date
                meter_data_points = []
                
                while current_time <= end_date:
                    # Generate random value between 0 and 1000
                    value = random.randint(0, 1000)
                    meter_data_points.append(
                        MeterData(
                            meter_id=meter.id,
                            timestamp=current_time,
                            value=value
                        )
                    )
                    current_time += timedelta(hours=1)
                
                db.session.add_all(meter_data_points)
            
            db.session.commit()
            print("Database initialized with sample data")

# Define the routes
@app.route('/meters/', methods=['GET'])
def get_meters():
    meters = Meter.query.all()
    return render_template('meters.html', meters=meters)

@app.route('/meters/<int:meter_id>', methods=['GET'])
def get_meter_data(meter_id):
    # Check if meter exists
    meter = Meter.query.get_or_404(meter_id)
    
    # Get all data for this meter sorted by timestamp
    data = MeterData.query.filter_by(meter_id=meter_id).order_by(MeterData.timestamp).all()
    
    # Convert to JSON
    response = {
        'meter': meter.to_dict(),
        'data': [item.to_dict() for item in data]
    }
    
    return jsonify(response)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    