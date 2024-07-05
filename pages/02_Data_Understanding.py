import time
import uuid

import pandas as pd
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from functions.functions_DataUnderstanding import update_feature_sensor_precision, defaultValuesCardinal, \
    update_data_restrictions_cardinal, defaultValuesOrdinal, update_data_restrictions_ordinal, defaultValuesNominal, \
    update_data_restrictions_nominal
from functions.functions_Modeling import defaultValuesCardinalRestriction, defaultValuesOrdinalRestriction, \
    defaultValuesNominalRestriction
from functions.functions_Modeling import getDefault
from functions.fuseki_connection import determinationActivity, invalidateWasGeneratedBy, \
    getUniqueValuesSeq, getSensorPrecision, \
    getAttributesDataUnderstanding, get_feature_names, get_dataset, getRestriction, \
    retrieveFeatureUUID, upload_entity_to_feature, uplaodSequence

# This variable contains all strings which are shown in the app
import config.strings as STRINGS
# This variable contains all global configuration options
import config.config as CONFIG

#st.session_state["volatility_of_features_dic"] Contains a list of all volatilty levels per feature


#Retrieve the connection strings for the database
host, host_upload = get_dataset()

#Try to retrieve the feature names from the database
try:
    st.session_state.dataframe_feature_names = get_feature_names(host)
except Exception as e:
    st.error(e)

#When there are no feature names, then the user must upload the feature names first
if st.session_state.dataframe_feature_names.empty:
    try:
        getUniqueValuesSeq(host)

    except Exception as e:
        st.error(STRINGS.ERRORNODATASET)
        if st.button("Home"):
            switch_page("Home")
        #SSif "first_unique_values_dict" not in st.session_state:
        #SS    st.error("No unique values available, please upload dataset again.")
        st.stop()
    st.stop()


optionsDataUnderstanding = option_menu(STRINGS.DATAUNDERSTANDINGHEADING,
                                       STRINGS.DUTABS,
                                       icons=['collection', 'arrow-down-up', 'slash-circle', 'broadcast'],
                                       menu_icon="None", default_index=0, orientation="horizontal")

#This expander shows if information is not determined yet
with st.expander(STRINGS.SHOWINFORMATIONEXANDERHEADER):
    try:
        getAttributesDataUnderstanding(host)
    except Exception as e:
        pass
    try:
        getDefault(host)
    except:
        pass

# First option Scale. A user has the possibility to show the scale of the features in the database.
if optionsDataUnderstanding == STRINGS.DUTAB1:

    determinationName = 'DeterminationOfScaleOfFeature'
    label = '"detScaleOfFeature"@en'
    dicName = 'level_of_measurement_dic'
    name = 'ScaleOfFeature'
    rprovName = 'scale'

    #Check if there are no scales in the database.
    #SSThis can be removed. Uploading the metadata with the json makes sure that the scales are there
    if st.session_state["level_of_measurement_dic"] == {}:
        pass

    else: #Scales are already entered in the database. This is the normal case, when uploading the metadata json file.
        colored_header(
            label=STRINGS.SCALEHEADER,
            description="",
            color_name="red-70",
        )

        st.success(STRINGS.SCALEUPLOAD)
        #Creates an expander that shows the json of the scales
        with st.expander(STRINGS.SCALEEXPANDER):
            st.write(st.session_state.level_of_measurement_dic)

        colored_header(
            label=STRINGS.UNIQUEHEADER,
            description="",
            color_name="red-70",
        )

        #The unique values are uploaded in the metadata json, so they should always be there.
        if st.session_state.unique_values_dict != {}:
            st.success(STRINGS.UNIQUEUPLOAD)
            with st.expander(STRINGS.UNIQUEEXPANDER):
                st.write(st.session_state['unique_values_dict'])

#Feature Volatility
if optionsDataUnderstanding == STRINGS.DUTAB2:

    #Check if there are volatility levels are stored in the session state.
    if st.session_state["volatility_of_features_dic"] == {}:
        st.markdown(STRINGS.VOLATILITYHEADER)

        with st.expander(STRINGS.VOLATILTIYINPUTHEADER):

            #available volatility options:
            options = CONFIG.VOLATILITYOPTIONS
            with st.form(STRINGS.VOLATILTIYCHANGEFORMHEADER):

                #Loop through all the available features
                for index, row in st.session_state.dataframe_feature_names["featureName.value"].items():
                    #For each feature create a selectbox with the volatility levels
                    st.session_state["volatility_of_features_dic"][row] = selectbox(row, options=options, key=f'volatility_of_features_{row}')

                if st.form_submit_button(STRINGS.VOLATILITYSUBMITBUTTON, type="primary"):
                    #Check if the user has inserted a volatility level for each feature
                    if None in st.session_state["volatility_of_features_dic"].values():
                        st.error(STRINGS.ERRORSELECTVOLATILITYLELVELFORALLFEATURES)
                        st.stop()

                    determinationName = 'DeterminationOfVolatilityOfFeature'
                    label = "Determination of feature volatility"
                    name = 'VolatilityOfFeature'
                    rprovName = 'volatilityLevel'

                    #Uplaod the activity to determine the volatiliy levels.
                    uuid_determinationVolatility = determinationActivity(host_upload, determinationName, label)

                    #Uplaod the entities containing the volatility levels.
                    # Show an update bar in the UI while uploading
                    with st.spinner("Uploading..."):
                        # Loop through the dictionary
                        for key, value in st.session_state["volatility_of_features_dic"].items():

                            # Get the UUID for the feature to which the volatility should be added.
                            featureUUID = retrieveFeatureUUID(host, key)

                            # Uplaod the volatility value collection for the feature in featureName into the graph
                            upload_entity_to_feature(host_upload, 'VolatilityOfFeature', 'volatilityLevel', f"'{value}'@en",
                                                     f"Volatility for feature {key}", featureUUID, uuid_determinationVolatility)
                    st.experimental_rerun()

    else:
        st.markdown(STRINGS.VOLATILITYHEADER2)
        with st.expander(STRINGS.VOLATILITYSHOWHEADER):
            st.write(st.session_state["volatility_of_features_dic"])
        if st.button(STRINGS.VOLATILITYDELETEBUTTON, on_click=invalidateWasGeneratedBy,
                     args=(host_upload, st.session_state["DF_feature_volatility_name"]["DUA.value"][0],'DUA'),
                     help=STRINGS.VOLATILITYDELETEBUTTONTOOLTIP):
            pass

#Data Restrictions
if optionsDataUnderstanding == STRINGS.DUTAB3:

    #Load current data restrictions from the database
    uploaded_DataRestriction = getRestriction(host)
    if "data_restrictions_dict" not in st.session_state:
        st.session_state.data_restrictions_dict = dict()
    if st.session_state['data_restrictions_dict'] is None:
        st.session_state['data_restrictions_dict'] = dict()


    if uploaded_DataRestriction.empty:
        st.markdown(STRINGS.DATARESTRICTIONHEADER)
        #Create 3 tabs for the 3 levels of measurement
        tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])

        #Loop through all the features
        for key, values in st.session_state.level_of_measurement_dic.items():

            data_restrictions_dic = dict()
            data = list()
            if values == 'Cardinal':
                with tab1:
                    #Create a new expander for the cardinal feature
                    with st.expander(STRINGS.DEFINERESTRICTIONEXPANDER.format(key)):
                        col1, col2, col3 = st.columns([0.05, 10, 0.5])
                        with col2:

                            #If there is no restriction in the session_state then fetch the upper and lower bound of the feature
                            if f'data_restrictions_{key}_cardinal' not in st.session_state:
                                defaultValuesCardinal(key)

                            try:
                                if key in st.session_state.data_restrictions_dict.keys():
                                    st.session_state[f'data_restrictions_{key}_cardinal'] = [float(s) for s in
                                                                                             st.session_state.data_restrictions_dict[key]]
                            except:
                                pass

                            # TODO the button does not update the value if it was currently entered. You need to change tabs in order to see the change.
                            #Provide a Button to restore the default values providing the maximum valid range.
                            if st.button(STRINGS.DATARESTRICTIONRESTOREDEFAULT.format(key), key=f'defaultValuesCardinal_{key}',type="secondary"):
                                defaultValuesCardinal(key)

                            try:
                                #Create an input filed for the upper and lower bound.
                                lower = round(st.number_input(STRINGS.DATARESTRICTIONLOWER, min_value=float(
                                    st.session_state.unique_values_dict[key][0]), key=f"lower_{key}", value=float(
                                    st.session_state[f'data_restrictions_{key}_cardinal'][0])), 2)
                                upper = round(st.number_input(STRINGS.DATARESTRICTIONUPPER, key=f"upper_{key}", min_value=lower,
                                                              max_value=float(st.session_state.unique_values_dict[key][-1]),
                                                              value=float(st.session_state[f'data_restrictions_{key}_cardinal'][-1])), 2)

                                #Create a button to store the new values to the session states.
                                if st.button(STRINGS.DATARESTRICTIONCHANGEBUTTON, key=f"data_restriction_ok_widget_{key}", type="primary"):
                                    #Check if the lower bound is smaller than the upper bound
                                    if st.session_state[f"lower_{key}"] >= st.session_state[f"upper_{key}"]:
                                        st.error(STRINGS.ERRORDATARESTRICTIONUPPERLOWERBOUND)
                                    else:
                                        #Update the restrictions to the session states
                                        st.session_state[f'data_restrictions_{key}'] = [lower,upper]
                                        st.session_state[f'data_restrictions_{key}_cardinal'] = [lower,upper]
                                        st.session_state['data_restrictions_dict'][key] = [lower,upper]
                                        update_data_restrictions_cardinal(key)
                                        st.success(STRINGS.DATARESTRICTIONCHANGESUCCESS.format(key))
                            except Exception as e:
                                pass

            if values == 'Ordinal':
                with tab2:
                    with st.expander(STRINGS.DEFINERESTRICTIONEXPANDER.format(key)):

                        if f'data_restrictions_{key}_ordinal' not in st.session_state:
                            defaultValuesOrdinal(key)
                        try:
                            if key in st.session_state.data_restrictions_dict.keys():
                                st.session_state[f'data_restrictions_{key}_ordinal'] = [s for s in
                                                                                        st.session_state.data_restrictions_dict[
                                                                                            key]]
                        except:
                            pass

                        if st.button(STRINGS.DATARESTRICTIONRESTOREDEFAULT.format(key), key=f'defaultValuesOrdinal_{key}'):
                            defaultValuesOrdinal(key)
                        st.session_state[f'data_restrictions_{key}_ordinal'] = st.multiselect(
                            STRINGS.DATARESTRICTIONORDINAL.format(key),
                            options=st.session_state.unique_values_dict[key],
                            default=st.session_state[f'data_restrictions_{key}_ordinal'],
                            key=f'data_restrictions_{key}',
                            on_change=update_data_restrictions_ordinal,
                            args=(key,))
                        st.markdown("""---""")

            if values == 'Nominal':
                with tab3:
                    with st.expander(STRINGS.DEFINERESTRICTIONEXPANDER.format(key)):

                        if f'data_restrictions_{key}_nominal' not in st.session_state:
                            defaultValuesNominal(key)
                        if st.button(STRINGS.DATARESTRICTIONRESTOREDEFAULT.format(key), key=f'defaultValuesNominal_{key}'):
                            defaultValuesNominal(key)
                        st.session_state[f'data_restrictions_{key}_nominal'] = st.multiselect(
                            STRINGS.DATARESTRICTIONNOMINAL.format(key),
                            options=st.session_state.unique_values_dict[key],
                            default=st.session_state[f'data_restrictions_{key}_nominal'],
                            key=f'data_restrictions_{key}',
                            on_change=update_data_restrictions_nominal,
                            args=(key,))
                        st.markdown("""---""")

        if st.session_state['data_restrictions_dict'] == {}:
            st.stop()
        else:
            st.write("-------------")
            with st.expander(STRINGS.DATARESTRICTIONDEFINEDEXPANDER):
                st.write(st.session_state['data_restrictions_dict'])
            if st.button(STRINGS.DATARESTRICTIONUPLOADBUTTON, type="primary"):

                #Insert the activity to determine the data restrictions.
                determinationName = 'DeterminationOfDataRestriction'
                label = "detDataRestriction"
                uuid_determinationDataRestriction = determinationActivity(host_upload, determinationName, label)

                #Insert the entities with the data restrictions.
                for key, value in st.session_state['data_restrictions_dict'].items():

                    # Get the UUID for the feature to which the data restriction should be added.
                    featureUUID = retrieveFeatureUUID(host, key)

                    # Upload the sequence with the values first.
                    seqUUID = uuid.uuid4()
                    i = 0
                    for values in value:
                        uplaodSequence(host_upload, seqUUID, i, values)
                        i = i + 1

                    name = 'DataRestriction'
                    rprovName = 'restriction'
                    # Uplaod the data restriction for the feature in key into the graph.
                    upload_entity_to_feature(host_upload, name, rprovName, f"<urn:uuid:{seqUUID}>", f"{rprovName} {key}", featureUUID, uuid_determinationDataRestriction)


                dr_success = st.success(STRINGS.DATARESTRICTIONUPLOADSUCCESS)
                dr_success.empty()
                st.experimental_rerun()
    else: #uploaded_DataRestriction are not empty
        st.markdown(STRINGS.DATARESTRICTIONMARKDOWN)

        for key, value in st.session_state["level_of_measurement_dic"].items():
            if value == "Cardinal":
                defaultValuesCardinalRestriction(key)
            if value == "Ordinal":
                defaultValuesOrdinalRestriction(key)
            if value == "Nominal":
                defaultValuesNominalRestriction(key)


        st.session_state["data_restriction_final"] = st.session_state.unique_values_dict.copy()

        st.session_state.data_restriction_final.update(st.session_state.data_restrictions_dict)

        with st.expander(STRINGS.DATARESTRICTIONSHOWEXPANDER):
            st.write(st.session_state.data_restrictions_dict)

        if st.button(STRINGS.DATARESTRICTIONINVALIDATIONBUTTON):
            invalidateWasGeneratedBy(host_upload, uploaded_DataRestriction["DUA.value"][0], 'DUA')
            del st.session_state["data_restrictions_dict"]
            del st.session_state.data_restriction_final
            st.session_state.data_restriction_final = st.session_state.unique_values_dict.copy()
            uploaded_DataRestriction = pd.DataFrame()
            st.experimental_rerun()


#Sensor precision
if optionsDataUnderstanding == STRINGS.DUTAB4:

    if st.session_state["loaded_feature_sensor_precision_dict"] == {}:
        st.markdown(STRINGS.SENSORPRECISIONMARKDOWN)

        for key, values in st.session_state.level_of_measurement_dic.items():

            if values == 'Cardinal':
                with st.expander(STRINGS.SENSORPRECISONDEFINITIONEXPANDER.format(key)):

                    if "feature_sensor_precision_dict" not in st.session_state:
                        st.session_state[f"feature_sensor_precision_dict"] = dict()

                    if key in st.session_state["feature_sensor_precision_dict"]:
                        st.session_state[f'feature_sensor_precision_{key}'] = \
                            st.session_state["feature_sensor_precision_dict"][key]
                    else:
                        st.session_state[f'feature_sensor_precision_{key}'] = 0

                    st.session_state[f'feature_sensor_precision_{key}'] = round(
                        st.number_input(STRINGS.SENSORPRECISIONINPUTTEXT,
                                        min_value=float(0.00),
                                        max_value=float(100),
                                        value=float(st.session_state[
                                                        f'feature_sensor_precision_{key}']),
                                        key=f'feature_sensor_precision_{key}_widget',
                                        on_change=update_feature_sensor_precision,
                                        args=(key,),
                                        help=STRINGS.SENSORPRECISIONINPUTHELP), 2)
        st.write("----------------------")
        if st.session_state["feature_sensor_precision_dict"] != {}:
            with st.expander(STRINGS.SENSORPRECISIONSHOWEXPANDER):
                st.session_state["feature_sensor_precision_dict"]

            if st.button(STRINGS.SENSORPRECISONUPLOADBUTTON, type="primary"):

                determinationName = 'DeterminationOfSensorPrecisionOfFeature'
                label = "detSensorPrecisionOfFeature"
                uuid_determinationSensorPrecision = determinationActivity(host_upload, determinationName, label)

                # Uplaod the entities containing the sensor precision.
                # Show an update bar in the UI while uploading
                with st.spinner("Uploading..."):
                    # Loop through the dictionary
                    for key, value in st.session_state["feature_sensor_precision_dict"].items():
                        # Get the UUID for the feature to which the sensor precision should be added.
                        featureUUID = retrieveFeatureUUID(host, key)

                        # Uplaod the sensor precision for the feature in key into the graph.
                        upload_entity_to_feature(host_upload, 'SensorPrecisionOfFeature', 'sensorPrecisionLevel', f"'{value}'@en",
                                                 f"Sensor precision for feature {key}", featureUUID,
                                                 uuid_determinationSensorPrecision)
                st.experimental_rerun()

                st.session_state["loaded_feature_sensor_precision_dict"] = st.session_state["feature_sensor_precision_dict"]
                Sensor_success = st.success("Sensor Precision uploaded")
                time.sleep(2)
                Sensor_success.empty()
                st.experimental_rerun()
    else:
        st.markdown(STRINGS.SENSORPRECISIONSHOWMARKDOWN)
        with st.expander(STRINGS.SENSORPRECISIONSHOWEXPANDER):
            st.write(st.session_state["loaded_feature_sensor_precision_dict"])

        if st.button(STRINGS.SENSORPRECISIONINVALIDATIONBUTTON):
            st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
                "DF_feature_sensor_precision"] = getSensorPrecision(host)

            invalidateWasGeneratedBy(host_upload, st.session_state["DF_feature_sensor_precision"]["DUA.value"][0], 'DUA')

            del st.session_state["loaded_feature_sensor_precision_dict"]

            st.experimental_rerun()