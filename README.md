# EnergyFlowVis
This application was created in the context of the CPSC547 Information Visualization at the University of British Columbia (UBC). It’s intended as a way to visualize data from buildings on UBC campus.

The application allows the user to filter on the building grouping type, then on a specific group and finally on a specific building.
It also enables users to choose 2 different time range to compare.

The application is built using the Dash framework from plotly. We used the different examples published on their website as a source of inspiration. The framework is built on top of the web framework Flask. The packages that are imported were used as is, our team didn't customize any of the packages.

See https://energy-flow-vis.herokuapp.com/ for the latest deployment.

## Files and folders
- Assets -> Contains the thumbnail image the CSS file for default formatting in the application. The file was taken from 'https://codepen.io/chriddyp/pen/bWLwgP.css' and the main font was modified to Segoe UI family
- Metadata -> Contains the building metadata CSV and the sensor metadata CSV
- Procfile -> Adds the gunicorn reference so that the application could be deployed on heroku
- Requirements.txt -> Contains all the necessary python libraries that need to be installed prior to running the application
- app.py -> This file needs to be executed to run the app. It contains the necessary call to generate the flask application. When running the file locally, it will run the application at http://127.0.0.1:8050/. This file will call the other libraries created: generate_graph and utilities to generate the graph and for callbacks to update the component displayed. It's where the frame of the application is coded. All packages mentioned in the requirements.txt are called in that code.
- generate_graph.py -> Library created to define graphical elements for the application. Functions will create the query to the database, others will create the sources, targets and values and finally define the graphical figure. The code uses the packages numpy and plotly.
- Utilities.py -> Library created so that functions could be easily reused in either app.py or generate_graph.py. It uses the pandas package.


## How to run the application
1) Install all python packages from the requirement.txt file
    - From the application's folder: pip install -r requirements.txt
2) Run the app.py file from the folder containing all the other .py files, the metadata folder and the assets folder.
    - Python app.py
3) Reach http://127.0.0.1:8050/ and start using the application

## Authors
Claude Demers-Belanger <br />
Research Assistant / Masters Candidate <br />
ETA Lab @ UBC <br />

Sanyogita Manu <br />
Research Assistant / phd Candidate <br />
ETA Lab @ UBC <br />
