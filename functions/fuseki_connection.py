from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import config.config as CONFIG
import config.sparql as SPARQL
# This variable contains all strings which are shown in the app
import config.strings as STRINGS

def set_database():
    keep = ["fuseki_database", "name_fuseki_database", "fueski_dataset_options", "name", "authentication_status", "username"]
    for key in st.session_state.keys():
        if key in keep:
            pass
        else:
            del st.session_state[key]

    st.session_state.fuseki_database = st.session_state.name_fuseki_database

def get_connection_fuseki(host, query):
    sparql = SPARQLWrapper(host)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod(GET)
    return sparql.query().convert()

def get_dataset():
    try:
        host = (f"{CONFIG.GRAPHSTORELINK}{st.session_state.fuseki_database}/sparql")
        host_upload = SPARQLWrapper(f"{CONFIG.GRAPHSTORELINK}{st.session_state.fuseki_database}/update")
        if st.session_state.fuseki_database == "None":
            st.error(STRINGS.SELECTDATASETFIRSTERROR)
            st.stop()
    except:
        st.stop()
    return host, host_upload

#This method returns the current time as xsd:dateTime
def getTimestamp():
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    return timestamp

#This method creates a new determination activitiy in the database
# @param sparqlUpdate The link to the update endpoint of the database.
# @param activityName The rprov name of the new activity.
# @param label The label of the new activtiy.
def determinationActivity(sparqlUpdate, activityName, label):
    uuid_Activity = uuid.uuid4()
    query = SPARQL.insertNewActivity.format(uuid_Activity,activityName,label,getTimestamp())
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return uuid_Activity

#This method inserts a new feature into the database.
# @param sparqlUpdate The link to the update endpoint of the database.
# @param featureLabel The label of the new feature.
# @param activity The uuid of the activity that generated this entity.
def upload_features(sparqlUpdate, featureLabel, activity):
    query = SPARQL.insertNewFeatureEntity.format(uuid.uuid4(),featureLabel,activity)
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method returns the UUID of a feature for a given feature label.
# @param sparqlQuery The link to the query endpoint of the database.
# @param featureLabel The label of the feature for which the UUID should be retrieved.
def retrieveFeatureUUID(sparqlQuery,featureLabel):
    sparql = SPARQLWrapper(sparqlQuery)
    query = SPARQL.getUUIDForFeatureLabel.format(featureLabel)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod(GET)
    result = sparql.query().convert()
    resultJson = pd.json_normalize(result["results"]["bindings"])
    return resultJson["featureUUID.value"][0]

#This method inserts a new entity to a feature in the database.
# @param sparqlUpdate The link to the update endpoint of the database.
# @param entityName The rprov name of the entity.
# @param propertyName The rprov property of the entity.
# @param propertyValue The value of the property.
# @param entityLabel The label of the new entity.
# @param featureUUID The UUID of the feature to which the entity belongs.
# @param activityUUID The UUID of the activity that generated the new entity.
def upload_entity_to_feature(sparqlUpdate, entityName, propertyName, propertyValue, entityLabel, featureUUID, activityUUID):
    query = SPARQL.insertNewEntityToFeature.format(uuid.uuid4(),entityName,propertyName, propertyValue, entityLabel, featureUUID, activityUUID, getTimestamp())
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method inserts a new handling of missing values to a feature in the database.
# @param sparqlUpdate The link to the update endpoint of the database.
# @param featureLabel The label of the feature to which the handling of missing values is assigned.
# @param comment The comment describes what is done when a value is missing.
# @param featureUUID The uuid of the feature to which the handling of missing values is assigned.
# @param activityUUID The uuid of the activity that created this entity.
def uplaod_missing_value_to_feature(sparqlUpdate, featureLabel, comment, featureUUID, activityUUID):
    query = SPARQL.insertNewMissingValuesEntityToFeature.format(uuid.uuid4(), featureLabel, comment, featureUUID, activityUUID, getTimestamp())
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method inserts a new binnned values to a feature in the database.
# @param sparqlUpdate The link to the update endpoint of the database.
# @param seqUUID The uuid the the sequence of the binned values.
# @param featureLabel The label of the feature to which the binned values are assigned.
# @param featureUUID The uuid of the feature to which the handling of missing values is assigned.
# @param activityUUID The uuid of the activity that created this entity.
def uplaod_bin_value_to_feature(sparqlUpdate, seqUUID, featureLabel, featureUUID, activityUUID):
    query = SPARQL.insertNewBinnedValuesToFeature.format(uuid.uuid4(), seqUUID, featureLabel, featureUUID, activityUUID, getTimestamp())
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method inserts unique values for a feature.
# @param sparqlUpdate The link to the update endpoint of the database.
# @param uniqueValueUUID The UUID of the collection of unique values that is assigned to a feature.
# @param type The type of the collection (Bag or Seq)
# @param place The place of the values (necessary for ordinal and cardinal (only min and max are given) values to determine the order).
# @param uniqueValue The actual value.
def uploadUniqueValues(sparqlUpdate, uniqueValueUUID, type, place, uniqueValue):
    query = SPARQL.insertUniqueValues.format(uniqueValueUUID, type, place, uniqueValue)
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method inserts a new perturbation option assigned to feature into the graph.
# @param sparqlUpdate The link to the update endpoint of the database.
# @param poUUID The uuid of the new perturbation option.
# @param perturbedFeature The uuid to the feature that should be perturbed.
# @param perturbationAlgorithm The name of the algorithm that is used.
# @param perturbationSetting Additional parameters for the perturbation.
# @param perturbationLevel The level of the perturbation option.
# @param basedInformation A list of uuids of the entities on which this perturbation option was based on.
# @param generatingActivity The uuid of the activity that generated this perturbation option.
# @param perturbationOptionLabel The label of the perturbation option. The prefix determines the group to which the option is assigned divided by a -.
def uploadPerturbationOption(sparqlUpdate, poUUID, perturbedFeature, perturbationAlgorithm, perturbationSetting, perturbationLevel, basedInformation, generatingActivity, perturbationOptionLabel):
    query = SPARQL.insertPerturbationOption.format(poUUID, "PerturbationOption", perturbedFeature, perturbationAlgorithm, perturbationSetting, perturbationLevel, basedInformation, generatingActivity, perturbationOptionLabel)
    sparqlUpdate.setQuery(query)
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method returns all perturbation options in the graph.
# @param sparqlQuery The link to the query endpoint of the database.
def getPerturbationOptionsFuseki(sparqlQuery):
    query = SPARQL.getAllPerturbationOptions
    results_update = get_connection_fuseki(sparqlQuery, query)
    result = pd.json_normalize(results_update["results"]["bindings"])
    return result

#This method invalidates all entities which were created by an activity.
# @param sparqlupdate The link the SPARQL update endpoint of the database.
# @param activityUUID The uuid of the activity which created the entites that should be invalidated.
# @param stage The phase indicates the stage of the CRISP-DM for the createdBy
def invalidateWasGeneratedBy(sparqlupdate, activityUUID, stage):
    query = SPARQL.invalidateWasGeneratedBy.format(getTimestamp(),stage,activityUUID)
    sparqlupdate.setQuery(query)
    sparqlupdate.setMethod(POST)
    sparqlupdate.query()

#This method returns a list with all feature labels and feature UUIDs.
# @param sparqlQuery The link to the query endpoint of the database.
def get_feature_names(sparqlQuery):
    query = SPARQL.getAllLabelsAndUUIDSForFeatures
    try:
        sparql = SPARQLWrapper(sparqlQuery)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setMethod(GET)
        result_feature_names = sparql.query().convert()
        result_feature_names = pd.json_normalize(result_feature_names["results"]["bindings"])
        return result_feature_names
    except:
        return st.warning("Please select dataset")


#This method returns a dictionary with all unique values of all features.
# @param sparqlQuery The link to the query endpoint of the database.
def getUniqueValuesSeq(sparqlQuery):
    dictionary_uniqueValues = dict()
    query = SPARQL.getAllUniqueValues
    results_feature_uniqueValues = get_connection_fuseki(sparqlQuery, query)
    results_feature_uniqueValues = pd.json_normalize(results_feature_uniqueValues["results"]["bindings"])
    results_feature_uniqueValues= results_feature_uniqueValues.groupby("label.value")["item.value"].apply(list)

    for _index, row in results_feature_uniqueValues.items():
        dictionary_uniqueValues[_index] = row

    return dictionary_uniqueValues

#This method returns information collected about a feature.
# @param sparqlQuery The link to the query endpoint of the database.
# @param featureLabel The label of the feature to which the information should be collected.
def getInformationToFeature(sparqlQuery, featureLabel):
    query = SPARQL.getInformationToFeature.format(featureLabel)
    results_update = get_connection_fuseki(sparqlQuery, query)
    result = pd.json_normalize(results_update["results"]["bindings"])
    return result

#This method returns the label of the scale of a feature.
# @param sparqlQuery The link to the query endpoint of the database.
# @param featureLabel The label of the feature for which the label of the scale should be retrieved.
def getLabelForScaleOfFeature(sparqlQuery, featureLabel):
    query = SPARQL.getLabelForScaleOfFeature.format(featureLabel)
    results_update = get_connection_fuseki(sparqlQuery, query)
    scaleOfFeatureLabel = pd.json_normalize(results_update["results"]["bindings"])
    return scaleOfFeatureLabel

#This method returns the label of the scale of a feature.
# @param sparqlQuery The link to the query endpoint of the database.
# @param label The label of the information that should be returned.
# @param feature The uuid of the feature to which the information is assigned.
def getUUIDForLabelsOfToFeature(sparqlQuery, label, feature):
    query = SPARQL.getUUIDForLabelAndToFeature.format(label, feature)
    results_update = get_connection_fuseki(sparqlQuery, query)
    entityuuid = pd.json_normalize(results_update["results"]["bindings"])
    return entityuuid["entitiyUUID.value"][0]

#This method returns a list of all labels of perturbation options in the graph.
# @param sparqlQuery The link to the query endpoint of the database.
def getAllPerturbationOptionLabels(sparqlQuery):
    query = SPARQL.getAllPerturbationOptionLabels
    results_update = get_connection_fuseki(sparqlQuery, query)
    result = pd.json_normalize(results_update["results"]["bindings"])
    return result

#This method retrieves all scales of all features.
# @param sparqlQuery The link to the query endpoint of the database.
def getFeatureScale(sparqlQuery):
    dictionary_scales = dict()
    results_feature_scale = get_connection_fuseki(sparqlQuery, SPARQL.getAllFeatureScales)
    results_feature_scale = pd.json_normalize(results_feature_scale["results"]["bindings"])
    for _index, row in results_feature_scale.iterrows():
        result_scale = row["scale.value"].partition("#")[2]
        dictionary_scales[row["featureName.value"]] = result_scale
    return dictionary_scales, results_feature_scale

#This method retrieves all volatiliy levels for all features.
# @param sparqlQuery The link to the query endpoint of the database.
def getFeatureVolatility(sparqlQuery):
    dictionary_volatility = dict()
    results_feature_volatility = get_connection_fuseki(sparqlQuery, SPARQL.getAllVolatilityLevels)
    results_feature_volatility = pd.json_normalize(results_feature_volatility["results"]["bindings"])
    for _index, row in results_feature_volatility.iterrows():
        dictionary_volatility[row["featureName.value"]] = row["volatility.value"]

    if dictionary_volatility == {}:
        return Exception
    else:
        return dictionary_volatility, results_feature_volatility

#This method retrieves all sensor precision levels for all features.
# @param sparqlQuery The link to the query endpoint of the database.
def getSensorPrecision(sparqlQuery):
    dictionary_SensorPrecision = dict()
    results_feature_sensor = get_connection_fuseki(sparqlQuery, SPARQL.getAllSensorPrecision)
    results_feature_sensor = pd.json_normalize(results_feature_sensor["results"]["bindings"])

    for _index, row in results_feature_sensor.iterrows():
        dictionary_SensorPrecision[row["featureName.value"]] = float(row["sensorPrecisionLevel.value"])

    results_feature_sensor = results_feature_sensor[["featureID.value", "featureName.value", "DataUnderstandingEntityID.value", "sensorPrecisionLevel.value", "DUA.value"]]
    return dictionary_SensorPrecision, results_feature_sensor

#This method retrieves all missing value inputions for all features.
# @param sparqlQuery The link to the query endpoint of the database.
def getMissingValues(sparqlQuery):
    dictionary_MissingValues = dict()
    results_feature_MissingValues = get_connection_fuseki(sparqlQuery, SPARQL.getAllMissingValues)
    results_feature_MissingValues = pd.json_normalize(results_feature_MissingValues["results"]["bindings"])

    for _index, row in results_feature_MissingValues.iterrows():
        dictionary_MissingValues[row["featureName.value"]] = row["MissingValues.value"]

    return dictionary_MissingValues, results_feature_MissingValues

#This method returns all binned values for all features.
# @param sparqlQuery The link to the query endpoint of the database.
def getBinValuesSeq(sparqlQuery):
    dictionary_BinValues = dict()
    results_feature_BinValues = get_connection_fuseki(sparqlQuery, SPARQL.getAllBinValuesSeq)
    results_feature_BinValues = pd.json_normalize(results_feature_BinValues["results"]["bindings"])
    results_feature_BinValues_grouped= results_feature_BinValues.groupby(["label.value"])["item.value"].apply(list)

    for _index, row in results_feature_BinValues_grouped.items():
        dictionary_BinValues[_index] = row

    return dictionary_BinValues, results_feature_BinValues

#This method uploads a new perturbation assessment for a case into the graph.
# @param uuid_PerturbationAssessment The uuid of the assessment.
# @param label The label of the assessment.
# @param uuid_DefinitionOfPerturbationOption The uuid of the activity that created this assessment.
# @param pertModel The perturbation mode that was used for the assessment.
def uploadPerturbationAssessment(host_upload, uuid_PerturbationAssessment, label,
                                 uuid_DefinitionOfPerturbationOption, perturbationOptions_settings, assessmentPerturbationOptions, pertMode):
    for key in perturbationOptions_settings.keys():
        for perturbationOption in assessmentPerturbationOptions[key]["PerturbationOptionID"]:

            host_upload.setQuery(SPARQL.insertPerturbationAssessment.format(uuid_PerturbationAssessment, label, perturbationOption, f"{label}_{uuid_PerturbationAssessment}", uuid_DefinitionOfPerturbationOption, pertMode, getTimestamp()))
            host_upload.setMethod(POST)
            host_upload.query()

#This method uploads a new entered classification case into the graph.
# @param sparqlUpdate The link the SPARQL update endpoint of the database.
# @param label The name of the Case
# @param uuid_PerturbationAssessment The uuid of the perturbation assessment the case is assigned to.
# @param rows The row of the original new case.
def uploadClassificationCase(sparqlUpdate, label, uuid_PerturbationAssessment, rows):
    sparqlUpdate.setQuery(SPARQL.insertClassificationCase.format(uuid.uuid4(), label, rows, uuid_PerturbationAssessment, getTimestamp()))
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()

#This method uploads a line in a sequence of a data restriction into the graph.
# @param sparqlUpdate The link the SPARQL update endpoint of the database.
# @param uuid_DataRestrictionSeq The uuid of the sequence to which the restriction is added.
# @param number The indexnumber of the restriction.
# @param The value of the restriction.
def uplaodSequence(sparqlUpdate, uuid_DataRestrictionSeq, number, value):
    sparqlUpdate.setQuery(SPARQL.insertSequenceLine.format(uuid_DataRestrictionSeq, number, value))
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()
    return True

#This method returns the data restriction for a given activity.
# @param data_restriction uuid of the activity that created the restriction
# @param sparqlQuery The link to the query endpoint of the database.
def getDataRestrictionSeq(data_restriction, sparqlQuery):
    dictionary_DataRestriction = dict()
    results_feature_DataRestriction = get_connection_fuseki(sparqlQuery, SPARQL.getDataRestrictionSeq.format(data_restriction))
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    results_feature_DataRestriction_grouped= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)

    for _index, row in results_feature_DataRestriction_grouped.items():
        dictionary_DataRestriction[_index] = row

    return dictionary_DataRestriction

#This mehtod returns the data restictions for a specific feature and perturbation options.
# @param data_restriction The uuid of the perturbation option for which a restriction should be searched.
# @param feature The uuid of the feature that is perutrbed by the perturbation option.
# @param sparqlQuery The link to the query endpoint of the database.
def getDataRestrictionSeqDeployment(data_restriction, feature, host):
    dictionary_DataRestriction = dict()
    try:
        results_feature_DataRestriction = get_connection_fuseki(host, SPARQL.getDataRestrictionSeqDeployment.format(data_restriction, feature))
        results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
        results_feature_DataRestriction= results_feature_DataRestriction.groupby("label.value")["item.value"].apply(list)

        for _index, row in results_feature_DataRestriction.items():
            dictionary_DataRestriction[_index] = row

        return dictionary_DataRestriction
    except:
        return

# This method returns all data restrictions that are saved in the database.
# @param host The query link to the database.
def getRestriction(host):
    query = SPARQL.getAllDataRestrictions
    results_feature_DataRestriction = get_connection_fuseki(host, query)
    results_feature_DataRestriction = pd.json_normalize(results_feature_DataRestriction["results"]["bindings"])
    if not results_feature_DataRestriction.empty:
        results_feature_DataRestriction = \
            results_feature_DataRestriction.groupby(["sub.value","seq.value", "label.value", "featureName.value", ], as_index=False)[
                "item.value"].agg(list)
        results_feature_DataRestriction.columns = ['DUA.value', 'DataRestrictionEntity', 'Label', 'Feature', "Value"]

    return results_feature_DataRestriction

#This method returns the uuid of the assessment approach that was chosen for this project.
# @param sparqlQuery The link to the query endpoint of the database.
def getApproach(sparqlQuery):
    results_approach = get_connection_fuseki(sparqlQuery, SPARQL.getApproachForGraph)
    results_approach = pd.json_normalize(results_approach["results"]["bindings"])
    return results_approach["DataUnderstandingEntityID.value"][0]

#This method creates a choice of assessement approach activtiy and the asisgned perturbation appraoch entity.
# @param sparqlUpdate The link the SPARQL update endpoint of the database.
# @param uuid_activity The uuid of the choice of assessment approach activity.
# @param uuid_entity The uuid of the new perturbation assessment entity.
def uploadApproach(sparqlUpdate, uuid_activity, uuid_entity):
    sparqlUpdate.setQuery(SPARQL.insertNewActivity.format(uuid_activity,"ChoiceOfAssessmentApproach", "Choice Of Assessment", getTimestamp()))
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()

    sparqlUpdate.setQuery(SPARQL.insertPerturbationApproach.format(uuid_entity, uuid_activity, getTimestamp()))
    sparqlUpdate.setMethod(POST)
    sparqlUpdate.query()

#This function loads all feature attributes from the database to the session state.
# @param host The query link to the database.
def getAttributes(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value
    except Exception as e:
        pass
        # st.session_state["DF_feature_scale_name"] = pd.DataFrame()
        # st.session_state["level_of_measurement_dic"] = dict()

    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except Exception as e:
        st.warning("No volatility level determined")
        st.session_state["volatility_of_features_dic"] = dict()


    try:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision"] = getSensorPrecision(host)
    except Exception as e:
        st.warning("No sensor precision determined")
        st.session_state["loaded_feature_sensor_precision_dict"] = dict()
        st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()

    try:
        st.session_state["loaded_missingValues_of_features_dic"], st.session_state[
        "DF_feature_missing_values_dic"] = getMissingValues(host)
        if st.session_state["loaded_missingValues_of_features_dic"] == {}:
            st.warning("No missing values determined")
    except:
        pass

    try:
        st.session_state["loaded_bin_dict"], st.session_state["DF_bin_dict"] = getBinValuesSeq(host)
    except Exception as e:
        st.warning("No bins determined")
        st.session_state["loaded_bin_dict"] = dict()

    try:
        uploaded_DataRestriction = getRestriction(host)
        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
            uploaded_DataRestriction["DUA.value"][0], host)

        st.session_state.data_restriction_final.update(st.session_state["data_restrictions_dict"])
    except:
        st.warning("No Data Restrictions determined")


#This function loads all feature attributes from the database to the session state.
# @param host The query link to the database.
def getAttributesDeployment(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value
    except Exception as e:
        pass


    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except Exception as e:
        st.session_state["volatility_of_features_dic"] = dict()


    try:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision"] = getSensorPrecision(host)
    except Exception as e:
        st.session_state["loaded_feature_sensor_precision_dict"] = dict()
        st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()

    try:
        st.session_state["loaded_missingValues_of_features_dic"], st.session_state[
        "DF_feature_missing_values_dic"] = getMissingValues(host)
    except:
        pass

    try:
        st.session_state["loaded_bin_dict"], st.session_state["DF_bin_dict"] = getBinValuesSeq(host)
    except Exception as e:
        st.session_state["loaded_bin_dict"] = dict()

#This function loads all feature attributes from the database to the session state.
# @param host The query link to the database.
def getAttributesDataUnderstanding(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value
    except Exception as e:
        pass

    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["volatility_of_features_dic"], st.session_state[
            "DF_feature_volatility_name"] = getFeatureVolatility(host)
    except Exception as e:
        st.warning("No volatility level determined")
        st.session_state["volatility_of_features_dic"] = dict()


    try:
        st.session_state["loaded_feature_sensor_precision_dict"], st.session_state[
            "DF_feature_sensor_precision"] = getSensorPrecision(host)
    except Exception as e:
        st.warning("No sensor precision determined")
        st.session_state["loaded_feature_sensor_precision_dict"] = dict()
        st.session_state["DF_feature_sensor_precision"] = pd.DataFrame()

    #If there are no data restrictions defined, then take the unique values as restriction.
    if "data_restriction_final" not in st.session_state:
        st.session_state.data_restriction_final = st.session_state.unique_values_dict
    try:
        uploaded_DataRestriction = getRestriction(host)
        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
            uploaded_DataRestriction["DUA.value"][0], host)
    except:
        st.warning("No Data Restrictions determined")

#This function loads all feature attributes from the database to the session state.
# @param host The query link to the database.
def getAttributesDataPreparation(host):

    if not any(key.startswith('level_of_measurement_') for key in st.session_state):
        st.session_state["dataframe_feature_names"] = get_feature_names(host)
    if st.session_state["dataframe_feature_names"].empty:
        st.warning("No features defined. If this is the first time a new dataset is uploaded please define features, a scale for each feature and upload the unique values.")

    try:
        st.session_state["level_of_measurement_dic"], st.session_state["DF_feature_scale_name"] = getFeatureScale(host)
        if st.session_state["level_of_measurement_dic"] == {}:
            st.warning(
                "No feature scales determined. If this is the first time a new dataset is uploaded please define scale for each feature and upload the unique values.")
        else:
            for key, value in st.session_state["level_of_measurement_dic"].items():
                st.session_state[f'level_of_measurement_{key}'] = value

    except Exception as e:
        pass

    try:
        st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)
    except Exception as e:
        st.warning("No Unique Values in database. If this is the first time a new dataset is uploaded please upload the unique values.")
        st.session_state["unique_values_dict"] = {}

    try:
        st.session_state["loaded_missingValues_of_features_dic"], st.session_state[
        "DF_feature_missing_values_dic"] = getMissingValues(host)
        if st.session_state["loaded_missingValues_of_features_dic"] == {}:
            st.warning("No missing values determined")
    except:
        pass

    try:
        st.session_state["loaded_bin_dict"], st.session_state["DF_bin_dict"] = getBinValuesSeq(host)
    except Exception as e:
        st.warning("No bins determined")
        st.session_state["loaded_bin_dict"] = dict()
