import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt


from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

from Flask import Flask, jsonify
app = Flask(__name__)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

@app.route("/")
def Vaction():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/station"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """List all available api routes."""
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_twelve_months = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    Precipitation_results = session.query(Measurement.date, func.avg(Measurement.prcp)).\
                    filter(Measurement.date >= last_twelve_months).\
                    group_by(Measurement.date).all()
    precip = {date: prcp for date, prcp in Precipitation_results}

    return jsonify(precip)

@app.route("/api/v1.0/station")
def station():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict()) 

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    station_results = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    station_results
    return jsonify(station_results)

@app.route("/api/v1.0/<start>")
def trip1(start):
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_twelve_months = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    station_results = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    best_station = station_results[0][0]
    session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.station == best_station).all()
    return jsonify(best_station)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
        latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
        last_twelve_months = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
        station_results = session.query(Measurement.station, func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
        best_station = station_results[0][0]
        temperature_results = session.query(Measurement.station, Measurement.tobs).\
                filter(Measurement.station == best_station).\
                filter(Measurement.date >= last_twelve_months).all()
        tobs_df = pd.DataFrame(temperature_results)
        tobs_df.set_index('station', inplace=True)
        tobs_df.head()
        return jsonify(tobs_df)

if __name__ == "__main__":
    app.run(debug=True)