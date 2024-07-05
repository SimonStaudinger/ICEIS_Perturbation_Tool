import pandas as pd
import streamlit as st
from functions.fuseki_connection import getUniqueValuesSeq, getPerturbationOptionsFuseki
# This variable contains all strings which are shown in the app
import config.strings as STRINGS

# ------------------------------------------------------------------------------------------------------------------------
def deleteTable(key):
    if st.button(STRINGS.DEPLOYMENTDELETETABLEBUTTONLABEL, type="primary", key=key):
        st.session_state.df_aggrid_beginning = pd.DataFrame(
            columns=st.session_state.dataframe_feature_names["featureName.value"].tolist())

def update_perturbation_level(key, method):
    st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.session_state[
        f"assignedPerturbationLevel_widget_{key}_{method}"]


def update_value_perturbate(key, method):
    st.session_state[f"value_perturbate{key}_{method}"] = st.session_state[
        f"value_perturbation_widget_{key}_{method}"]


def update_additional_value(key, method):
    st.session_state[f"additional_value_{key}_{method}"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]


def upper_lower_bound(key, method):
    st.session_state[f"additional_value_{key}_{method}_bound"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]

def defaultValuesCardinalRestriction(key):
    st.session_state[f'data_restrictions_{key}_cardinal'] = [float(st.session_state.unique_values_dict[key][0]),
                                                             float(st.session_state.unique_values_dict[key][-1])]


def defaultValuesOrdinalRestriction(key):
    st.session_state[f'data_restrictions_{key}_ordinal'] = st.session_state.unique_values_dict[key]


def defaultValuesNominalRestriction(key):
    st.session_state[f'data_restrictions_{key}_nominal'] = st.session_state.unique_values_dict[key]

#@st.cache_data
def getDefault(host):
    st.session_state["unique_values_dict"] = getUniqueValuesSeq(host)

#def getPerturbationRecommendations(host):
#    query = (f"""
#            SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?DUA ?values ?label ?PerturbationAssessment{{
#            ?featureID rdf:type rprov:Feature .
#            ?featureID rdfs:label ?featureName.
#            ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
#	?DataUnderstandingEntityID rprov:perturbedFeature ?featureID.
#    ?DataUnderstandingEntityID rprov:generationAlgorithm ?DUA.
#    ?DataUnderstandingEntityID rprov:values ?values.
#    ?DataUnderstandingEntityID rdfs:label ?label.
#            ?PerturbationAssessment rprov:deploymentEntityWasDerivedFrom ?DataUnderstandingEntityID.
#            }}""")
#
#    results_feature_recommendation = get_connection_fuseki(host, (prefix + query))
#    results_feature_recommendation = pd.json_normalize(results_feature_recommendation["results"]["bindings"])
#    results_feature_recommendation = results_feature_recommendation.groupby(['featureName.value', 'DataUnderstandingEntityID.value','label.value'])['DataUnderstandingEntityID.type'].count().reset_index()
#
#    return results_feature_recommendation

def getPerturbationOptions(host):


    results_feature_PerturbationOption = getPerturbationOptionsFuseki(host)

    try:
        results_feature_PerturbationOption = results_feature_PerturbationOption[["featureID.value","featureName.value","PerturbationOptionID.value","generationAlgo.value", "settings.value", "level.value", "label.value", "DataRestrictionEntities.value", "MA.value"]]
        results_feature_PerturbationOption.columns = ['FeatureID','FeatureName', 'PerturbationOptionID', 'PerturbationOption', "Settings","PerturbationLevel","label" ,"DataRestrictionEntities", "ModelingActivity"]
    except:
        results_feature_PerturbationOption = results_feature_PerturbationOption[
            ["featureID.value", "featureName.value", "PerturbationOptionID.value", "generationAlgo.value",
             "settings.value", "level.value", "label.value", "MA.value"]]
        results_feature_PerturbationOption.columns = ['FeatureID', 'FeatureName', 'PerturbationOptionID',
                                                      'PerturbationOption', "Settings", "PerturbationLevel", "label",
                                                      "ModelingActivity"]

    return results_feature_PerturbationOption

def changeAlgorithm(key):
    st.session_state.default[key] = st.session_state[f"algo_{key}"]

def changePerturbationOption(feature_name):
    st.session_state.perturbationOptions[feature_name] = st.session_state[f"perturbationOption_{feature_name}"]

def update_steps(key, method):
    st.session_state[f"steps_{key}_{method}"] = st.session_state[
        f"steps_widget_{key}_{method}"]

def update_value_perturbate(key, method):
    st.session_state[f"value_perturbate{key}_{method}"] = st.session_state[
        f"value_perturbation_widget_{key}_{method}"]

def update_additional_value(key, method):
    st.session_state[f"additional_value_{key}_{method}"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]

def upper_lower_bound(key, method):
    st.session_state[f"additional_value_{key}_{method}_bound"] = st.session_state[
        f"additional_value_widget_{key}_{method}"]
