## Hello everyone! 

This repository is intended as documentation of an academic modeling tool for reliability assessment of classification results using a perturbation approach. More information about the general idea can be found here: https://doi.org/10.1007/s42979-024-02892-4.

The code is based on the implementation from Pascal Badzura available at https://github.com/PaBadz/Reliability-Assessment-Thesis.

The tool needs access to a graph store either installed on your computer or available online. 
In our case, we used the Apache Jena Fuseki, which is freely available at https://jena.apache.org/documentation/fuseki2/ and would also recommend this for any tryouts.
Fuseki provides a standalone version including a user interface which can simply be started by double-clicking  on the fuseki-server.bat file.
By default, the UI can be called up via http://localhost:3030/#/. 
This standard path is currently used within the tool and can be changed in the config/config.py file any time. 

In order to start the tool, it is recommended to create a new virtual environment within your python installation.
Within the repository you can find a requirements.txt file including all necessary librarries which can be installed by typing 

pip install -r requirements.txt 

in your terminal, for example the Anaconda prompt.
To start the tool, open your terminal, move to the repository and type 

streamlit run Home.py

which should open the staring page of the tool in your browser. 
Once you see the starting page in browser, you are set to model your first reliability assessment using a perturbation approach! 

#### Link to the demonstration video 
https://youtu.be/Z9SrrTKQzO0




