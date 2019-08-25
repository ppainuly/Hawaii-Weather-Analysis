import numpy as np
from flask import render_template,make_response

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Create a db engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Function to calculate the latest date in the dataset, and the date 366 days before the calculated latest date
# Returns the year-before date
def latest_date():
    year_val = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    datediff = dt.datetime.strptime(year_val.date, "%Y-%m-%d") - dt.timedelta(days=366)
    return datediff
# Flask Setup
app = Flask(__name__)

# Returns a JSON data for Data,Precipitation for last 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():

    datediff = latest_date()
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= datediff).all()
    
    # Convert to a dictionary
    precipitation_dict = dict(results_precipitation)
    return jsonify(precipitation_dict)

# Returns the JSOOn for Station names in the dataset
@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Measurement.station).group_by(Measurement.station).all()

    # Store Station data from Tuples to List
    station_list = [i[0] for i in station_results]
    return jsonify(station_list)

# Returns all the temprature observations by date
@app.route("/api/v1.0/tobs")
def tobs():

    datediff = latest_date()
    tobs_result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= datediff).all()

    # Store Temp Obs data from Tuples to List
    tobs_list = list(tobs_result)

    return jsonify(tobs_list)

# Returns Date, min Temp, Ave Temp, Max Temp for the passed Start Date
@app.route("/api/v1.0/<start>")
def temp(start=None):
    data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()
    data_list=list(data)
    return jsonify(data_list)

# Returns Date, min Temp, Ave Temp, Max Temp between the Start Date and End date passed
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start=None,end=None):
    data = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start,Measurement.date <= end).group_by(Measurement.date).all()
    data_list=list(data)
    return jsonify(data_list)

# Error Response if URL not found
@app.errorhandler(404)
def page_not_found(e):

    return make_response(jsonify({'error': 'URL Not found'}), 404)  

@app.route("/")
def welcome():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5009)







