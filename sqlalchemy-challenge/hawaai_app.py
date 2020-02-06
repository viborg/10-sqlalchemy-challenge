import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date/end date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of prcp measurement data"""
    # Query all Measurements
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_prcp_measurements
    all_prcp_measurements = []
    for station, date, prcp in results:
        measurement_dict = {}
        measurement_dict["station"] = station
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_prcp_measurements.append(measurement_dict)

    return jsonify(all_prcp_measurements)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature (tobs) measurement data, ordered by descending date"""
    # Query all Measurements
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        order_by(Measurement.date.desc()).all()
    session.close()

    # Find the date one year before the latest measurement date
    date_latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_latest_str = ''.join(date_latest)         # to convert the tuple to a string
    date_latest_datetime_object = dt.datetime.strptime(date_latest_str, '%Y-%m-%d')
    date_year_ago = date_latest_datetime_object - dt.timedelta(days=365)
    date_year_ago_str = dt.datetime.strftime(date_year_ago, '%Y-%m-%d')
    
    # Create a dictionary from the row data and append to a list of all_tobs_measurements_for_past_year
    all_tobs_measurements_for_past_year = []
    for station, date, tobs in results:
        if date >= date_year_ago_str:
            measurement_dict = {}
            measurement_dict["station"] = station
            measurement_dict["date"] = date
            measurement_dict["tobs"] = tobs
            all_tobs_measurements_for_past_year.append(measurement_dict)

    return jsonify(all_tobs_measurements_for_past_year)


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start=None, end="2020-1clear2-31"):
    stat = calc_temps(start, end)

    return stat


if __name__ == '__main__':
    app.run(debug=True)

