# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import os

#################################################
# Database Setup
#################################################

# Get the absolute path to the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "Resources", "hawaii.sqlite")

engine = create_engine(f"sqlite:///{db_path}")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
latest_date = session.query(Measurement.date).order_by(
    Measurement.date.desc()).first()[0]

one_year_ago = dt.datetime.strptime(
    latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

most_active_station = active_stations[0][0]


# Define the root route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Define the precipitation route


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Perform a query to retrieve the date and precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    prcp_dict = {date: prcp for date, prcp in results}

    return jsonify(prcp_dict)

# Define the stations route


@app.route("/api/v1.0/stations")
def stations():
    # Query all station names
    results = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station for station, in results]

    return jsonify(station_list)

# Define the tobs route


@app.route("/api/v1.0/tobs")
def tobs():
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list
    tobs_list = [tobs for tobs, in tobs_data]

    return jsonify(tobs_list)

# Define the start and start-end routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    if end is None:
        end = latest_date

    # Query the minimum, average, and maximum temperature
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Convert the query results to a dictionary
    temp_stats = {
        'min_temp': results[0][0],
        'avg_temp': results[0][1],
        'max_temp': results[0][2]
    }

    return jsonify(temp_stats)


if __name__ == "__main__":
    app.run(debug=True, port = 8001)
