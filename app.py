import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",
                        connect_args = {'check_same_thread': False})# the computer wasn't loading up the session correctly hence added an extra conenction.




# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measure_table = Base.classes.measurement
station_table = Base.classes.station
session = Session(engine)
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
        f"<a href = /api/v1.0/precipitation> Precipitation</a><br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperatures<br/>"
        f"/api/v1.0/<start><br/>" 
        f"/api/v1.0/<start>/<end><br/>"
        )
@app.route("/api/v1.0/precipitation")
def precipitation():
    query1 = session.query(measure_table.date, measure_table.prcp).all()
    percep_list = []
    for row in query1:
        each_dict = {}
        each_dict['date'] = row[0]
        each_dict['prcp'] = row[1]
        percep_list.append(each_dict)
    
    return jsonify(percep_list)


@app.route("/api/v1.0/stations")
def stations():
    query2 = session.query(station_table.id, station_table.name).all()
    st_list = []
    for row in query2:
        each_dict = {}
        each_dict['station_id'] = row[0]
        each_dict['station_name'] = row[1]
        st_list.append(each_dict)
    
    return jsonify(st_list)

@app.route("/api/v1.0/tobs")
def tobs():
    query3 = session.query(measure_table.station, func.count(measure_table.id), station_table.name).\
        filter(measure_table.station == station_table.station).\
        group_by(measure_table.station).order_by(func.count(measure_table.id).desc())
    most_tobs_id = query3.first()[0]
    
    
    last_date = session.query(measure_table.date).order_by(measure_table.date.desc()).\
                    filter(measure_table.station == most_tobs_id).first().date
    
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(weeks=52)
    
    
    query4 = session.query(measure_table.date, measure_table.tobs).\
            filter(measure_table.station == most_tobs_id, measure_table.date>last_year).all()
    
   
    tobs_list = []
    for row in query4:
        each_dict = {}
        each_dict['date'] = row[0]
        each_dict['tobs'] = row[1]
        tobs_list.append(each_dict)
    
    return jsonify(tobs_list)



@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_date(start_date=None, end_date = None):
    
    query = [func.min(measure_table.tobs),func.avg(measure_table.tobs), func.max(measure_table.tobs)]
    
    if not end_date:
        query5 = session.query(*query).filter(measure_table.date >=  start_date).all()
        

        temps = list(np.ravel(query5))
          
#     temp_list = []
#     for row in query5:
#         each_dict = {}
#         each_dict['date'] = row[0]
#         each_dict['TMIN'] = row[1]
#         each_dict['TAVG'] = row[2]
#         each_dict['TMAX'] = row[3]
#         temp_list.append(each_dict)
    
        return jsonify(temps)
    
    query5 = session.query(*query).filter(measure_table.date >=  start_date).filter(measure_table.date <=end_date).all()
    temps = list(np.ravel(query5))
    return jsonify(temps)

    
    
    
    
    
   
    

if __name__ == '__main__':
    app.run(debug=True)

    
    
    