import os
import pickle
import io
import streamlit as st
from streamlit_extras.colored_header import colored_header
# This variable contains all strings which are shown in the app
import config.strings as STRINGS

from functions.fuseki_connection import get_dataset

host, host_upload = get_dataset()

st.set_page_config(
    page_title= STRINGS.PREDICTIONMODELPAGETITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

colored_header(
    label = STRINGS.PREDICTIONMODELPAGETITLE,
    description="",
    color_name="red-70"
)

#Choose or upload a new prediction model.
selectedOption = st.radio(label = "",options = [STRINGS.SELECTMODELTEXT, STRINGS.UPLOADMODELTEXT], index = 0)

if( selectedOption == STRINGS.SELECTMODELTEXT ):
    #fetch all models which are saved in the models directory
    models = os.listdir(STRINGS.FILEPATHMODELS)
    loaded_model2 = st.selectbox(label=STRINGS.MODELSELECTBOXLABEL, options=models)
    #st.info(loaded_model2)

elif( selectedOption == STRINGS.UPLOADMODELTEXT ):
    #User wants to upload a new model into the app

    #if "model" in st.session_state:
    #    st.write(st.session_state['model'].feature_names_in_)

    #Generate the upload widget with the providede heading as parameter
    loaded_model2 = st.file_uploader(STRINGS.MODELUPLOADERLABEL)
    #st.markdown(loaded_model2.name)

    #Check if the user selected a database in the graph store
    databaseSelected = st.session_state.fuseki_database
    if databaseSelected != "" and loaded_model2 is not None:
        #Get the name of the model
        modelName = loaded_model2.name
        #Read the file. Be carefull, after .read() is called, the loaded_model2 variable is emtpy and refering to it will make streamlit wait for another input
        uploaded_file_bytes = loaded_model2.read()

        model = pickle.load(io.BytesIO(uploaded_file_bytes))
        #st.info(model)
        pickle.dump(model, open(os.path.join(STRINGS.FILEPATHMODELS, modelName),'wb'))
        st.success(STRINGS.MODELUPLOADSUCCESS)
        loaded_model2 = modelName


if loaded_model2 is not None:
    #st.info(loaded_model2)
    with open(os.path.join(STRINGS.FILEPATHMODELS, loaded_model2), 'rb') as f:
        loaded_model = pickle.load(f)
    #st.info(loaded_model)
    st.session_state.model = loaded_model








