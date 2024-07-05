import uuid
import json
import requests
import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from functions.fuseki_connection import set_database, determinationActivity, \
    upload_features, get_feature_names, retrieveFeatureUUID, upload_entity_to_feature, uploadUniqueValues

# This variable contains all strings which are shown in the app
import config.strings as STRINGS
# This variable contains all global configuration options
import config.config as CONFIG

#session_state['fueski_dataset_options'] contains a list of all databases of the graphstore
#session_state['fuseki_database'] contains the name of the currently active database

st.set_page_config(
    page_title= STRINGS.MAINTITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

colored_header(
    label = STRINGS.MAINTITLE,
    description="",
    color_name="red-70"
)


def get_dataset_from_fuseki():
    sparql = SPARQLWrapper(CONFIG.DATASETLIST)
    sparql.setReturnFormat(JSON)
    fuseki_datasets = sparql.query().convert()

    # if 'fueski_dataset_options' not in st.session_state:
    st.session_state['fueski_dataset_options'] = ["None"]
    for dataset in fuseki_datasets["datasets"]:
        st.session_state['fueski_dataset_options'].append(dataset["ds.name"])

    if 'fuseki_database' not in st.session_state:
        st.session_state['fuseki_database'] = "None"

# Retrieve all datasets from the graphstore and save them in the session states
get_dataset_from_fuseki()


selected2 = option_menu(None, STRINGS.HOMETABHEADERS,
                        icons=['nothing','cloud-upload'],
                        menu_icon="", default_index=0, orientation="horizontal")
st.write('--------------')



#Create the dialog to add a new dataset(KG) to the graph store.
if selected2 == STRINGS.UPLOADDATASETHEADER:
    st.info(STRINGS.UPLOADDATASETINFO)

    with st.expander("Create new dataset"):
        new_dataset = st.text_input("Insert dataset name")
        if st.button("Create new dataset"):
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Authorization': 'Basic $(echo -n admin:password | base64)'}
            r = requests.post(CONFIG.DATASETLIST, data=f"dbName={new_dataset.replace(' ', '')}&dbType=tdb",
                              headers=headers)

            get_dataset_from_fuseki()
            st.success("New dataset created")




#Add the select box where a user can choose the active dataset.
##Get the index of the currently active dataset.
index = st.session_state['fueski_dataset_options'].index(st.session_state['fuseki_database'])

st.session_state.fuseki_database = st.selectbox('Please select dataset', index=index,options=st.session_state['fueski_dataset_options'],on_change=set_database, key='name_fuseki_database')

#Build the connection strings to the graphstore based on the select database
host = (f"{CONFIG.GRAPHSTORELINK}{st.session_state.fuseki_database}/sparql")
host_upload = SPARQLWrapper(f"{CONFIG.GRAPHSTORELINK}{st.session_state.fuseki_database}/update")

if not any(key.startswith('level_of_measurement_') for key in st.session_state):
    st.session_state["dataframe_feature_names"] = get_feature_names(host)


#If no database is selected, the processing of the page is stopped and the dialog to upload a json metadata file is therefore omitted.
if st.session_state.fuseki_database=="None":
    st.stop()

#Create the dialog to upload a json metadata file.
if selected2 == 'Upload Dataset':
    st.write("---------------------")
    #upload_option = st.radio(label ="Select upload option",options=["JSON", "CSV"])


    #if upload_option == "JSON":

    #Provide an example of the structure of the json string that has to be uploaded.
    with st.expander("File needs to follow this schema"):
        st.json(STRINGS.JSONMETADATAEXAMPLE)


    #Provide a dialog to uplaod the json metadata file
    uploaded_file = st.file_uploader(f"Upload JSON file", accept_multiple_files=False, on_change=set_database)
    #Stop processing, if there is no file uploaded, otherwise process the file.
    if not uploaded_file:
        st.stop()

    #Read the file
    uploaded_file_bytes = uploaded_file.read()
    uploaded_file_JSON = json.loads(uploaded_file_bytes.decode('utf-8'))

    determinationNameUUID = 'DeterminationOfFeature'
    name = 'Feature'
    rprovName = 'Feature'

    #Provide an upload button and if clicked do:
    if st.button(f"Upload dataset to {st.session_state.fuseki_database}", type='primary'):
        # insert the initial statements into the new database.
        initialGraphUpload = open(CONFIG.INITIALGRAPHUPLOAD).read()
        headers = {'Content-Type': 'text/turtle;charset=utf-8'}

        #Put inital graph upload to the database
        requests.put(f"{CONFIG.GRAPHSTORELINK}{st.session_state.fuseki_database}?default", initialGraphUpload, headers=headers)

        determinationName = 'DeterminationOfFeature'
        label = "Determination of Features"
        ##Insert the determination of feature activity into the database.
        uuid_determinationFeature = determinationActivity(host_upload, determinationName, label)

        ##Insert each feature into the database
        for featureName in uploaded_file_JSON.keys():
            upload_features(host_upload, featureName, uuid_determinationFeature)

        determinationName = 'DeterminationOfScaleOfFeature'
        label = "Determination of Scale of Features"
        ##Insert the determination of scale of feature activity into the database.
        uuid_determinationScale = determinationActivity(host_upload, determinationName, label)

        st.info(STRINGS.UPLOADUNIQUEVALUESINFO)
        name = "ScaleOfFeature"
        rprovName = "scale"

        for featureName in uploaded_file_JSON.keys():

            #Get the UUID for the feature to which the scale should be added.
            featureUUID = retrieveFeatureUUID(host, featureName)

            #Uplaod the scale for the feature in featureName into the graph
            upload_entity_to_feature(host_upload,'ScaleOfFeature','scale','rprov:'+uploaded_file_JSON[featureName]["levelOfScale"],f"Scale of feature {featureName}",featureUUID,uuid_determinationScale)

        #### UNIQUE VALUES
        determinationNameUUID = 'DeterminationOfUniqueValuesOfFeature_'
        determinationName = 'DeterminationOfUniqueValuesOfFeature'
        label = "Determine unique values of features."
        try:
            #Insert the determination of unique values of features activity into the database.
            uuid_determinationUniqueValues = determinationActivity(host_upload,determinationName, label)

            for featureName in uploaded_file_JSON.keys():

                # Get the UUID for the feature to which the scale should be added.
                featureUUID = retrieveFeatureUUID(host, featureName)

                #We need to define the uuid here, because more unique values will be added to this uuid.
                uuid_UniqueValues_seq = uuid.uuid4()

                # Uplaod the unique value collection for the feature in featureName into the graph
                upload_entity_to_feature(host_upload,'UniqueValuesOfFeature', 'uniqueValues', f"<urn:uuid:{uuid_UniqueValues_seq}>",f"Unique Values for feature {featureName}", featureUUID, uuid_determinationUniqueValues)

                i = 0
                for values in uploaded_file_JSON[featureName]["uniqueValues"]:
                    #Uplaod unique values
                    if uploaded_file_JSON[featureName]["levelOfScale"] == "Nominal":
                        uploadUniqueValues(host_upload,uuid_UniqueValues_seq, 'Bag', i, values)
                    else:
                        uploadUniqueValues(host_upload,uuid_UniqueValues_seq, 'Seq', i, values)
                    i = i + 1

        except Exception as e:
            st.error(e)

        switch_page("Data Understanding")