# Import necessary Libraries
import numpy as np

from flask import(
    Flask,
    render_template,
    jsonify,
    request)

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func

##################################################
# Flask Setup
##################################################
app = Flask(__name__)

# Create engine using the database file
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# Declare a Base using Automap Base
Base = automap_base()

# Reflect the base class to reflect the table
Base.prepare(engine, reflect=True)

# Print all of the base class keys
Base.classes.keys()

# Map the tables to a variable
OTU = Base.classes.otu 
Samples = Base.classes.samples
Samples_MetaData = Base.classes.samples_metadata 

# Create a session
session = Session(engine)

##################################################
# Flask Routes
##################################################

# Home Page --> Render index.html from template
@app.route("/")
def home():
    return(render_template("index.html"))

@app.route("/names")
def names():
    # Get the sample list which is the column names in Samples table 
    samples_column_list = Samples.__table__.columns.keys()
    # First element in the samples_column_list is 'otu_id' so sample list is from 2nd element to the last element
    sample_list = samples_column_list[1:]
    print(sample_list)
    return jsonify(sample_list)

@app.route("/otu")
def otu():
    # Get the otu description from OTU table
    otu_descriptions = session.query(OTU.lowest_taxonomic_unit_found).all()
    otu_list = [i[0] for i in otu_descriptions]
    print(otu_list)
    return jsonify(otu_list)

@app.route("/metadata/<sample>")
def metadata_sample(sample):
    #SAMPLEID in Samples_MetaData table consist of only the digits thererfor trim the sample starting from 4th place
    sampleid = sample[3:]
    metadata_sample_result = session.query(Samples_MetaData).filter(Samples_MetaData.SAMPLEID == sampleid).first()
    # Store the results in a dictionary 
    sample_dict={"AGE":metadata_sample_result.AGE,
                "GENDER": metadata_sample_result.GENDER,
                "ETHNICITY": metadata_sample_result.ETHNICITY,
                "BBTYPE": metadata_sample_result.BBTYPE,
                "LOCATION": metadata_sample_result.LOCATION,
                "SAMPLEID": metadata_sample_result.SAMPLEID}
    print(sample_dict)
    return jsonify(sample_dict)

@app.route("/wfreq/<sample>")
def wfreq(sample):
    sampleid = sample[3:]
    washingfrequency_result = session.query(Samples_MetaData.WFREQ).filter(Samples_MetaData.SAMPLEID == sampleid).first()
    return(jsonify(washingfrequency_result[0]))

@app.route("/samples/<sample>")
def getSamples(sample):
    sample_result = session.query(Samples.otu_id,getattr(Samples,sample)).order_by(getattr(Samples,sample).desc()).all()
    otu_id_list = [i[0] for i in sample_result]
    sample_values_list= [i[1] for i in sample_result]
    sample_dict_result={"otu_ids":otu_id_list, "sample_values": sample_values_list}
    return(jsonify([sample_dict_result]))


##################################################
# Initiate Flask app
##################################################
if __name__=="__main__":
    app.run(debug=True)