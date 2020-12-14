# EnergyFlowVis
This is application was created in the context of the CPSC547 Information Visualization at the University of British Columbia (UBC). The application allow the user to visualize data from buildings on UBC campus.

The application allows the user to filter on the building grouping type, then on a specific group and finally on a specific building.
It also enable user to choose 2 different time range to compare.

See https://energy-flow-vis.herokuapp.com/ for the latest deployment.

## Files and folders
- Assets - Contains the thumbnail image the CSS file for default formatting in the application. The file was taken from 'https://codepen.io/chriddyp/pen/bWLwgP.css' and the main font was modified to Segoe UI family
- Metadata -> Contains the building metadata CSV and the sensor metadata CSV
- Procfile -> Adds the gunicorn reference so that the application could be deployed on heroku
- Requirements.txt -> Contains all the necessary python librairies that need to be installed prior to running the application
- app.py -> This file needs to be executed to run the app. It contains the necessary call to generate the application. When running the file locally, it will run the application at http://127.0.0.1:8050/. This file will call the other librairies created: generate_graph and utilities to generate the graph and for callbacks to update the component displayed. It's where the frame of the application is coded.
- generate_graph.py -> Librairy created to define graphical elements for the application. Functions will create the query to the database, others will create the sources, targets and values and finally define the graphical figure.
- Utilities.py -> Librairy created so that functions could be easily reused in either app.py or generate_graph.py


## How to run the application
1) Install all python packages from the requirement.txt file
2) Run the app.py file.

# Authors
Claude Demers-Belanger
Research Assistant / Masters Candidate
ETA Lab @ UBC

Sanyogita Manu
Research Assistant / phd Candidate
ETA Lab @ UBC
