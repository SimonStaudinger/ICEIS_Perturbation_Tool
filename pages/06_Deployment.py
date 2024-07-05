import uuid
import pandas as pd
import regex as re
import streamlit as st
import streamlit_ext as ste
#This package is shown as unused, but is needed for the layout!
import streamlit_nested_layout
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu
from streamlit_sortables import sort_items
from streamlit_extras.switch_page_button import switch_page
from functions.functions_Modeling import getDefault, getPerturbationOptions, \
    changePerturbationOption, deleteTable
from functions.functions_Deployment import get_perturbation_level, color_map
from functions.fuseki_connection import getDataRestrictionSeqDeployment, \
    determinationActivity, uploadPerturbationAssessment, uploadClassificationCase, getAttributesDeployment, \
    getUniqueValuesSeq, get_dataset, getRestriction
from functions.perturbation_algorithms import percentage_perturbation, sensorPrecision, fixedAmountSteps, \
    perturbRange, perturbInOrder, perturbAllValues

# This variable contains all strings which are shown in the app
import config.strings as STRINGS

# Set render max elements higher so that all perturbed values can be seen
pd.set_option("styler.render.max_elements", 999_999_999_999)

#Some init stuff
host, host_upload = get_dataset()

try:
    getUniqueValuesSeq(host)

except Exception as e:
    if st.button("Data Understanding"):
        switch_page("Data Understanding")
    st.stop()

try:
    getDefault(host)
except Exception as e:
    st.error(STRINGS.DEPLOYMENTNOUNIQUES)

try:
    getAttributesDeployment(host)
except Exception as e:
    st.stop()

#End of init stuff.

# # horizontal menu
menu_perturbation = option_menu(None, [STRINGS.DEPLOYMENTTAB1, STRINGS.DEPLOYMENTTAB2],
                                icons=['house', 'gear'],
                                orientation="horizontal")

try:
    savedPerturbationOptions = getPerturbationOptions(host)
except Exception as e:
    st.write(e)
    st.info(STRINGS.DEPLOYMENTNOPERTOPTIONS)
    st.stop()

if menu_perturbation == STRINGS.DEPLOYMENTTAB1:
    hide_table_row_index = """
                                            <style>
                                            thead tr th:first-child {display:none}
                                            tbody th {display:none}
                                            </style>
                                            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)


    #try:
    #    recommendations = getPerturbationRecommendations(host)
    #except:
    #    st.info("There are no recommendations at the moment.")

    with st.expander(STRINGS.DEPLOYMENTSHOWALLAVAILABLEPOS):
        st.dataframe(
            savedPerturbationOptions[["FeatureName", "PerturbationOption", "label"]].reset_index(drop=True),
            use_container_width=True)


    def extract_chars(s):
        return s.split('-')[0]


    savedPerturbationOptions['group'] = savedPerturbationOptions['label'].apply(extract_chars)
    options_group=["None"]
    options_group.extend(savedPerturbationOptions["group"].unique().tolist())
    def deletePO():
        del st.session_state.perturbationOptions

    modelingActivityGroupSelection = st.selectbox(STRINGS.DEPLOYMENTSELECTGROUP, options=options_group, index =0, on_change=deletePO)
    modelingActivityIDGroup = savedPerturbationOptions.loc[savedPerturbationOptions["group"]==modelingActivityGroupSelection]["ModelingActivity"].unique()



    if "perturbationOptions" not in st.session_state:

        # save the selected options in a dictionary in order to perform the perturbation
        st.session_state.perturbationOptions_settings = {}

        # save all information for the selected perturbation options in a dictionary
        st.session_state.assessmentPerturbationOptions = {}
        st.session_state.df_test = pd.DataFrame()
        # save default values for each feature
        st.session_state.perturbationOptions = {}
        for columns in st.session_state.dataframe_feature_names["featureName.value"]:
            st.session_state.perturbationOptions[columns] = []
            st.session_state.assessmentPerturbationOptions[columns] = []


    colored_header(
        label=STRINGS.DEPLOYMENTCHOOSEPOSFORPERT,
        description="",
        color_name="red-50",
    )
    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])

    df_test = pd.DataFrame(columns=savedPerturbationOptions.columns)
    # create expander for each feature where the perturbation options can be selected
    for feature_names, level_of_scale in st.session_state.level_of_measurement_dic.items():

        if level_of_scale == "Cardinal":

            with tab1:
                if feature_names not in savedPerturbationOptions["FeatureName"].values:
                    pass
                else:
                    with st.expander(label=STRINGS.DEPLOYMENTPOSFORFEATURE.format(feature_names)):
                        #with st.expander("Show all available Perturbation Options"):
                        #    st.dataframe(
                        #        savedPerturbationOptions.query('FeatureName == "%s"' % feature_names)[
                        #            ["FeatureName", "PerturbationOption", "label", "Settings"]],
                        #        use_container_width=True)

                        settingList = {}
                        settings = {}
                        try:
                            try:
                                if len(st.session_state.perturbationOptions[feature_names])==0:
                                    options = (
                                        savedPerturbationOptions.loc[savedPerturbationOptions['FeatureName'] == feature_names][
                                            "label"])
                                elif len(st.session_state.perturbationOptions[feature_names])>0:
                                    same_entity = (
                                        savedPerturbationOptions.loc[(
                                            savedPerturbationOptions['label'] == st.session_state.perturbationOptions[feature_names][0])&(savedPerturbationOptions['FeatureName'] == feature_names)]["DataRestrictionEntities"]).reset_index(drop=True)
                                    options=savedPerturbationOptions.loc[
                                        (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]

                                if modelingActivityGroupSelection != "None":
                                    try:
                                        st.session_state.perturbationOptions[feature_names] =(
                                            savedPerturbationOptions.loc[(
                                             savedPerturbationOptions['ModelingActivity'] ==modelingActivityIDGroup[0]) & (
                                             savedPerturbationOptions['FeatureName'] == feature_names)][
                                            "label"]).reset_index(drop=True)

                                        same_entity = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions['label'] ==
                                                                                 st.session_state.perturbationOptions[
                                                                                     feature_names][0]) & (
                                                                                     savedPerturbationOptions[
                                                                                         'FeatureName'] == feature_names)][
                                                "DataRestrictionEntities"]).reset_index(drop=True)
                                        options = savedPerturbationOptions.loc[
                                            (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]
                                    except:
                                        options = (
                                            savedPerturbationOptions.loc[
                                                savedPerturbationOptions['FeatureName'] == feature_names][
                                                "label"])
                                else:
                                    pass
                            except:
                                options = (
                                    savedPerturbationOptions.loc[
                                        savedPerturbationOptions['FeatureName'] == feature_names][
                                        "label"])



                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],

                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,)
                                                                                                 )


                            chosen_perturbationOptions_feature = (
                                savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                    st.session_state.perturbationOptions[feature_names])) & (savedPerturbationOptions[
                                                                                                 'FeatureName'] == feature_names)])



                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])


                            if chosen_perturbationOptions_feature.empty:
                                try:
                                    del st.session_state.assessmentPerturbationOptions[
                                    feature_names]
                                except:
                                    pass
                            else:
                                st.session_state.assessmentPerturbationOptions[
                                    feature_names] = chosen_perturbationOptions_feature.to_dict("list")


                            for index, row in chosen_perturbationOptions_feature.iterrows():
                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))
                                # convert values to float except if the key is step
                                for key, value in settings.items():
                                    if key == "steps":
                                        settings[key] = int(value)
                                    elif key == "PerturbationLevel":
                                        pass
                                    else:
                                        settings[key] = float(value)

                                settings["PerturbationLevel"]=chosen_perturbationOptions_feature["PerturbationLevel"][index]

                                if row["PerturbationOption"] in settingList:
                                    st.warning(STRINGS.DEPLOYMENTANOTHERPOCHOSEN.format(row["PerturbationOption"]))
                                else:
                                    settingList[row["PerturbationOption"]] = settings

                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)


                            if len(st.session_state.perturbationOptions_settings[feature_names]) > 1:
                                st.info(STRINGS.DEPLOYMENTDIFFERENTPERTLEVELS)



                            if feature_names in st.session_state.assessmentPerturbationOptions.keys() and \
                                    st.session_state.perturbationOptions[feature_names] != []:
                                st.table(chosen_perturbationOptions_feature[
                                             ["FeatureName", "PerturbationOption", "Settings", "PerturbationLevel", "label"]])

                        except Exception as e:
                            st.write(e)
                            st.info(STRINGS.DEPLOYMENTNOCARDINAL, icon="ℹ️")

        if level_of_scale == "Ordinal":
            with tab2:
                if feature_names not in savedPerturbationOptions["FeatureName"].values:
                    pass
                else:
                    with st.expander(label=STRINGS.DEPLOYMENTPOSFORFEATURE.format(feature_names)):
                        settingList = {}
                        settings = {}

                        try:
                            try:
                                if len(st.session_state.perturbationOptions[feature_names]) == 0:
                                    options = (
                                        savedPerturbationOptions.loc[
                                            savedPerturbationOptions['FeatureName'] == feature_names][
                                            "label"])
                                elif len(st.session_state.perturbationOptions[feature_names]) > 0:
                                    same_entity = (
                                        savedPerturbationOptions.loc[(
                                                                             savedPerturbationOptions['label'] ==
                                                                             st.session_state.perturbationOptions[
                                                                                 feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                            "DataRestrictionEntities"]).reset_index(drop=True)
                                    options = savedPerturbationOptions.loc[
                                        (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                savedPerturbationOptions['FeatureName'] == feature_names)]["label"]

                                if modelingActivityGroupSelection != "None":
                                    try:
                                        st.session_state.perturbationOptions[feature_names] = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions[
                                                                                     'ModelingActivity'] ==
                                                                                 modelingActivityIDGroup[0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "label"]).reset_index(drop=True)

                                        same_entity = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions['label'] ==
                                                                                 st.session_state.perturbationOptions[
                                                                                     feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "DataRestrictionEntities"]).reset_index(drop=True)
                                        options = savedPerturbationOptions.loc[
                                            (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]
                                    except:
                                        options = (
                                            savedPerturbationOptions.loc[
                                                savedPerturbationOptions['FeatureName'] == feature_names][
                                                "label"])
                                else:
                                    pass
                            except:
                                options = (
                                    savedPerturbationOptions.loc[
                                        savedPerturbationOptions['FeatureName'] == feature_names][
                                        "label"])


                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],

                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,)
                                                                                                 )



                            chosen_perturbationOptions_feature = (
                                savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                    st.session_state.perturbationOptions[feature_names])) & (savedPerturbationOptions[
                                                                                                 'FeatureName'] == feature_names)])

                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])
                            st.session_state.assessmentPerturbationOptions[
                                feature_names] = chosen_perturbationOptions_feature.to_dict("list")


                            for index, row in chosen_perturbationOptions_feature.iterrows():
                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))

                                # convert values to float except if the key is step
                                for key, value in settings.items():
                                    if key == "steps":
                                        settings[key] = int(value)
                                    elif key == "PerturbationLevel":
                                        pass

                                settings["PerturbationLevel"] = chosen_perturbationOptions_feature["PerturbationLevel"][index]

                                if row["PerturbationOption"] in settingList:
                                    st.warning(STRINGS.DEPLOYMENTANOTHERPOCHOSEN.format(row["PerturbationOption"]))
                                else:
                                    settingList[row["PerturbationOption"]] = settings

                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)
                            if len(st.session_state.perturbationOptions_settings[feature_names]) > 1:
                                st.info(STRINGS.DEPLOYMENTDIFFERENTPERTLEVELS)

                            if feature_names in st.session_state.assessmentPerturbationOptions.keys() and \
                                    st.session_state.perturbationOptions[feature_names] != []:
                                st.table(chosen_perturbationOptions_feature[
                                             ["FeatureName", "PerturbationOption", "Settings", "PerturbationLevel", "label"]])
                        except Exception as e:
                            st.write(e)
                            st.info(STRINGS.DEPLOYMENTNOORIDINAL, icon="ℹ️")

        if level_of_scale == "Nominal":
            if feature_names not in savedPerturbationOptions["FeatureName"].values:
                pass
            else:
                with tab3:
                    with st.expander(label=STRINGS.DEPLOYMENTPOSFORFEATURE.format(feature_names)):
                        settingList = {}
                        settings = {}
                        try:
                            try:
                                if len(st.session_state.perturbationOptions[feature_names]) == 0:
                                    options = (
                                        savedPerturbationOptions.loc[
                                            savedPerturbationOptions['FeatureName'] == feature_names][
                                            "label"])
                                elif len(st.session_state.perturbationOptions[feature_names]) > 0:
                                    same_entity = (
                                        savedPerturbationOptions.loc[(
                                                                             savedPerturbationOptions['label'] ==
                                                                             st.session_state.perturbationOptions[
                                                                                 feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                            "DataRestrictionEntities"]).reset_index(drop=True)
                                    options = savedPerturbationOptions.loc[
                                        (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                savedPerturbationOptions['FeatureName'] == feature_names)]["label"]

                                if modelingActivityGroupSelection != "None":
                                    try:
                                        st.session_state.perturbationOptions[feature_names] = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions[
                                                                                     'ModelingActivity'] ==
                                                                                 modelingActivityIDGroup[0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "label"]).reset_index(drop=True)

                                        same_entity = (
                                            savedPerturbationOptions.loc[(
                                                                                 savedPerturbationOptions['label'] ==
                                                                                 st.session_state.perturbationOptions[
                                                                                     feature_names][0]) & (
                                                                                 savedPerturbationOptions[
                                                                                     'FeatureName'] == feature_names)][
                                                "DataRestrictionEntities"]).reset_index(drop=True)
                                        options = savedPerturbationOptions.loc[
                                            (savedPerturbationOptions["DataRestrictionEntities"].isin(same_entity)) & (
                                                    savedPerturbationOptions['FeatureName'] == feature_names)]["label"]
                                    except:
                                        options = (
                                            savedPerturbationOptions.loc[
                                                savedPerturbationOptions['FeatureName'] == feature_names][
                                                "label"])
                                else:
                                    pass
                            except:
                                options = (
                                    savedPerturbationOptions.loc[
                                        savedPerturbationOptions['FeatureName'] == feature_names][
                                        "label"])

                            st.session_state.perturbationOptions[feature_names] = st.multiselect(f'{feature_names}',
                                                                                                 options=options,
                                                                                                 default=
                                                                                                 st.session_state.perturbationOptions[
                                                                                                     feature_names],

                                                                                                 key=f"perturbationOption_{feature_names}",
                                                                                                 on_change=changePerturbationOption,
                                                                                                 args=(
                                                                                                     feature_names,)
                                                                                                 )
                            chosen_perturbationOptions_feature = (
                            savedPerturbationOptions.loc[(savedPerturbationOptions['label'].isin(
                                st.session_state.perturbationOptions[feature_names])) & (
                                                                 savedPerturbationOptions[
                                                                     'FeatureName'] == feature_names)])

                            df_test = pd.concat([df_test, chosen_perturbationOptions_feature])

                            st.session_state.assessmentPerturbationOptions[
                                feature_names] = chosen_perturbationOptions_feature.to_dict("list")


                            for index, row in chosen_perturbationOptions_feature.iterrows():

                                keys = re.findall("'(.*?)'", row["Settings"])
                                values = re.findall(': (.*?)(?:,|})', row["Settings"])

                                # create nested dictionary with column name as key and keys as second key and values as values
                                settings = (dict(zip(keys, values)))

                                # convert values to float except if the key is step
                                for key, value in settings.items():
                                    if key == "steps":
                                        settings[key] = int(value)
                                    elif key == "PerturbationLevel":
                                        pass
                                settings["PerturbationLevel"] = chosen_perturbationOptions_feature["PerturbationLevel"][
                                    index]

                                if row["PerturbationOption"] in settingList:
                                    st.warning(STRINGS.DEPLOYMENTANOTHERPOCHOSEN.format(row["PerturbationOption"]))
                                else:
                                    settingList[row["PerturbationOption"]] = settings

                            st.session_state.perturbationOptions_settings[feature_names] = (settingList)
                            if len(st.session_state.perturbationOptions_settings[feature_names]) > 1:
                                st.info(STRINGS.DEPLOYMENTDIFFERENTPERTLEVELS)

                            if feature_names in st.session_state.assessmentPerturbationOptions.keys() and \
                                    st.session_state.perturbationOptions[feature_names] != []:
                                st.table(chosen_perturbationOptions_feature[
                                             ["FeatureName", "PerturbationOption", "Settings", "PerturbationLevel", "label"]])

                        except Exception as e:
                            st.error(e)
                            st.info(STRINGS.DEPLOYMENTNONOMINAL, icon="ℹ️")

    try:
        savedRestrictions = getRestriction(host)

        st.session_state["data_restriction_final_deployment"] = st.session_state.unique_values_dict.copy()

        for feature_name in st.session_state.assessmentPerturbationOptions.keys():
            st.session_state["data_restriction_deployment"] = [(st.session_state.unique_values_dict[feature_names][0]),
                                                             (st.session_state.unique_values_dict[feature_names][-1])]

            try:
                data_restriction_entity = \
                st.session_state.assessmentPerturbationOptions[feature_name]["PerturbationOptionID"][0]

                featureID = st.session_state.assessmentPerturbationOptions[feature_name]["FeatureID"][0]
                st.session_state["data_restriction_deployment"] = getDataRestrictionSeqDeployment(data_restriction_entity,featureID, host)
            except Exception as e:
                pass
            try:
                st.session_state.data_restriction_final_deployment.update(st.session_state.data_restriction_deployment)
            except Exception as e:
                pass

    except Exception as e:
        st.session_state["data_restriction_final_deployment"] = st.session_state.unique_values_dict.copy()


    colored_header(
        label=STRINGS.DEPLOYMENTSHOWCHOSENPOS,
        description=STRINGS.DEPLOYMENTSHOWPOSPREFEATURE,
        color_name="red-50",
    )
    with st.expander(STRINGS.DEPLOYMENTSHOWPOEXPANDERLABEL):


        st.dataframe(df_test[["FeatureName","PerturbationOption","Settings","PerturbationLevel"]].reset_index(drop=True),use_container_width=True)


        try:

            for key in list(st.session_state.assessmentPerturbationOptions.keys()):

                if not st.session_state.assessmentPerturbationOptions[key]:
                    del st.session_state.assessmentPerturbationOptions[key]

            for feature in list(st.session_state.perturbationOptions_settings.keys()):

                if not st.session_state.perturbationOptions_settings[feature]:

                    del st.session_state.perturbationOptions_settings[feature]
        except Exception as e:
            st.error(e)


    with st.expander(STRINGS.DEPLOYMENTSHOWRESTRITIONVALUES):

        st.write(STRINGS.DEPLOYMENTDATARESTRICTIONHEADER, st.session_state.data_restriction_final_deployment)

try:
    if menu_perturbation == STRINGS.DEPLOYMENTTAB2:

        #Set the perturbation mode to Full
        if "pertubation_mode" not in st.session_state:
            st.session_state.pertubation_mode = "Full"

        if "perturb_mode_values" not in st.session_state:
            st.session_state.perturb_mode_values =st.session_state["dataframe_feature_names"]["featureName.value"].values.tolist()

        perturbed_value_list = dict()

        if "perturbed_value_list" not in st.session_state:
            st.session_state.perturbed_value_list = {}
            for columns in st.session_state.dataframe_feature_names["featureName.value"]:
                st.session_state.perturbed_value_list[columns] = []

        #Create two tabs, one to insert new cases and one remove them from the list.
        insert, delete = st.tabs([STRINGS.DEPLOYMENTTABINSERT, STRINGS.DEPLOYMENTTABDELETE])

        #Insert new cases that can be perturbed.
        with insert:
            if "df_aggrid_beginning" not in st.session_state:
                st.session_state.df_aggrid_beginning = pd.DataFrame(
                    columns=st.session_state.dataframe_feature_names["featureName.value"].tolist())


            with st.expander(STRINGS.DEPLOYMENTINSERTNEW, expanded=False):
                with st.form("Add Data"):
                    dic = dict()
                    col_cardinal, col_ordinal, col_nominal = st.columns(3, gap="medium")

                    for feature_name, level_of_scale in st.session_state.level_of_measurement_dic.items():
                        if level_of_scale == "Cardinal":
                            with col_cardinal:
                                dic[feature_name] = st.number_input(STRINGS.DEPLOYMENTSELECTVALUE.format(feature_name),
                                                                    min_value=float(
                                                                        st.session_state.data_restriction_final_deployment[
                                                                            feature_name][0]),
                                                                    max_value=float(
                                                                        st.session_state.data_restriction_final_deployment[
                                                                            feature_name][-1]),
                                                                    key=f"add_data_{feature_name}")

                        if level_of_scale == "Ordinal":
                            with col_ordinal:
                                dic[feature_name] = st.selectbox(STRINGS.DEPLOYMENTSELECTVALUE.format(feature_name),
                                                                 options=st.session_state.data_restriction_final_deployment[
                                                                     feature_name],
                                                                 key=f"add_data_{feature_name}")
                        if level_of_scale == "Nominal":
                            with col_nominal:
                                dic[feature_name] = st.selectbox(STRINGS.DEPLOYMENTSELECTVALUE.format(feature_name),
                                                                 options=st.session_state.data_restriction_final_deployment[
                                                                     feature_name],
                                                                 key=f"add_data_{feature_name}")
                    if st.form_submit_button(STRINGS.DEPLOYMENTSUBMITNEWDATABUTTONLABEL, type='primary'):
                        st.session_state.df_aggrid_beginning = st.session_state.df_aggrid_beginning.append(dic,
                                                                                                           ignore_index=True)
                        st.experimental_rerun()
                        st.success(STRINGS.DEPLOYMENTCASEADDED)


            with st.expander(STRINGS.DEPLOYMENTUPLOADNEW):
                new_cases = st.file_uploader(STRINGS.DEPLOYMENTUPLAODCSV, type="csv")
                if new_cases is not None:
                    file = pd.read_csv(new_cases)
                    for columns in file:
                        if st.session_state.level_of_measurement_dic[columns]=="Cardinal":
                            file[columns] = file[columns].astype(float)
                        else:
                            file[columns] = file[columns].astype(str)

                    st.session_state.df_aggrid_beginning = file




        #Delete inserted cases from the list of available cases
        with delete:
            if st.session_state.df_aggrid_beginning.shape[0] == 0:
                st.write(STRINGS.DEPLOYMENTNOCASES)
            else:

                drop_index = int(st.number_input(STRINGS.DEPLOYMENTSELECTROWTODELETE, (st.session_state.df_aggrid_beginning.index[0] + 1),
                                                 (st.session_state.df_aggrid_beginning.index[-1] + 1)))

                try:
                    if st.button(STRINGS.DEPLOYMENTDELETEROWWITHINDEX.format(drop_index)):
                        st.session_state.df_aggrid_beginning = st.session_state.df_aggrid_beginning.drop(
                            drop_index - 1).reset_index(drop=True)
                        st.experimental_rerun()
                except Exception as e:
                    st.info(e)
            deleteTable("delete_selected_rows_table")
        colored_header(
            label=STRINGS.DEPLOYMENTSELECTROWSOFCASES,
            description=STRINGS.DEPLOYMENTSELECTROWS,
            color_name="red-50",
        )
        if st.session_state.df_aggrid_beginning.shape[0] == 0:
            st.info(STRINGS.DEPLOYMENTNOCASES)
            st.stop()
        # configue aggrid table
        gb = GridOptionsBuilder.from_dataframe(st.session_state.df_aggrid_beginning)
        gb.configure_selection(selection_mode="multiple", use_checkbox=False, rowMultiSelectWithClick=True)
        gb.configure_auto_height(autoHeight=True)

        for feature_name, value in st.session_state.data_restriction_final_deployment.items():
            if st.session_state.level_of_measurement_dic[feature_name] != 'Cardinal':
                gb.configure_column(f"{feature_name}", editable=True, cellEditor="agSelectCellEditor",
                                    cellEditorPopup=True, cellEditorParams={"values": value},
                                    singleClickEdit=False,
                                    sortable=True, filter=True, resizable=True)
            else:
                gb.configure_column(f"{feature_name}", type=['numericColumn', "numberColumnFilter"], editable=True,
                                    sortable=True, filter=True, resizable=True)

        gridOptions = gb.build()

        data = AgGrid(st.session_state.df_aggrid_beginning,
                      gridOptions=gridOptions,
                      enable_enterprise_modules=False,
                      allow_unsafe_jscode=True,
                      editable=True,
                      columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                      data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                      update_mode=GridUpdateMode.SELECTION_CHANGED,
                      allowDragFromColumnsToolPanel=False,
                      alwaysShowVerticalScroll=True,
                      alwaysShowHorizontalScroll=True,
                      theme='streamlit')

        selected_rows = data["selected_rows"]
        selected_rows_DF = pd.DataFrame(selected_rows,
                                        columns=st.session_state.dataframe_feature_names["featureName.value"])
        try:
            for features in selected_rows_DF:
                if st.session_state.level_of_measurement_dic[features] == 'Cardinal':
                    selected_rows_DF[features] = selected_rows_DF[features].astype(float)
        except Exception as e:
            st.error(f"ERROR! Please change! {e}")


        if selected_rows_DF.shape[0] == 0:
            st.info(STRINGS.DEPLOYMENTSELECTCASESTOCONTINUEINFO)
            st.stop()

        with st.expander(STRINGS.DEPLOYMENTSHOWSELECTEDCASES):
            st.dataframe(selected_rows_DF, use_container_width=True)


        with st.expander(STRINGS.DEPLOYMENTSHOWSELECTEDPOS):
            st.write(st.session_state.perturbationOptions_settings)


        label_list = []
        for i in range(0, len(selected_rows)):
            label_case = st.text_input(STRINGS.DEPLOYMENTLABELFORCASE,
                                           help=STRINGS.DEPLOYMENTLABELHELP, key=f"label_{i}")

            if label_case !="":
                label_list.append(label_case)

        if len(label_list) != len(selected_rows):
            st.stop()


        #checkbox_upload = st.checkbox("Upload Perturbation Options to Fuseki", help="This is for testing purposes")

        if st.button(STRINGS.DEPLOYMENTBUTTONSTARTPERTURBING, type="primary"):

            try:
                if "perturbedList" not in st.session_state:
                    st.session_state.perturbedList = dict()

                # divide df based on level of measurement
                nominal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Nominal']
                ordinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Ordinal']
                cardinal = [key for key, value in st.session_state.level_of_measurement_dic.items() if value == 'Cardinal']

                ct = ColumnTransformer(transformers=[
                    ("OneHot", OneHotEncoder(handle_unknown='ignore'), nominal),
                    ("Ordinal", OrdinalEncoder(handle_unknown='error'), ordinal),
                    ("Cardinal", SimpleImputer(strategy='most_frequent'), cardinal)],
                    remainder='drop', verbose_feature_names_out=False)

                df = pd.DataFrame.from_dict(st.session_state.unique_values_dict, orient='index')
                df = df.transpose()
                x = pd.concat([df, selected_rows_DF]).reset_index(drop=True)
                x = x.fillna(method='ffill')

                try:
                    x_trans_df = pd.DataFrame(ct.fit_transform(x).toarray(), columns=ct.get_feature_names_out()).reset_index(drop=True)
                except:
                    x_trans_df = pd.DataFrame(ct.fit_transform(x), columns=ct.get_feature_names_out()).reset_index(drop=True)

                y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))

                result = selected_rows_DF
                # reset index for y_pred in order to be able to insert it to result
                result["prediction"] = y_pred.iloc[len(df):].reset_index(drop=True)

                # change values in selected rows to list in order to extend the list with perturbated values
                # this is done because we need to explode it later
                for row in selected_rows:
                    for feature, value in row.items():
                        if feature != "_selectedRowNodeInfo":
                            if st.session_state.level_of_measurement_dic[feature] != 'Cardinal':
                                row[feature] = [value]
                            else:
                                row[feature] = [round(float(value),3)]

            except Exception as e:
                st.error(f"ERROR! Please change! {e}")

            try:
                result_df = pd.DataFrame(
                    columns=result.columns)  # st.session_state.dataframe_feature_names["featureName.value"].tolist())
                if "result_df" not in st.session_state:
                    st.session_state['result_df'] = result_df

                index_perturb = list()
                # dictionary mit den ausgewählten methoden für jede column
                for i in range(0, len(selected_rows)):
                    try:
                        for column, method in st.session_state['perturbationOptions_settings'].items():

                            perturbedList = dict()

                            for k, v in selected_rows[i].items():

                                try:
                                    if k == column:
                                        for algorithm_keys in method.keys():

                                            if algorithm_keys == 'Percentage Perturbation':

                                                perturbedList[algorithm_keys] = (
                                                    percentage_perturbation(method[algorithm_keys]["steps"],
                                                                            selected_rows[i][k][0],
                                                                            st.session_state.data_restriction_final_deployment[
                                                                                column]))


                                            elif algorithm_keys == '5% Perturbation':
                                                try:
                                                    perturbedList[algorithm_keys] = (
                                                        percentage_perturbation(5, selected_rows[i][k][0],
                                                                                st.session_state.data_restriction_final_deployment[
                                                                                    column]))
                                                except Exception as e:
                                                    st.error(f"ERROR! Please change! {e}")

                                            elif algorithm_keys == '10% Perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    percentage_perturbation(10, selected_rows[i][k][0],
                                                                            st.session_state.data_restriction_final_deployment[
                                                                                column]))

                                            elif algorithm_keys == 'Sensor Precision Perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    sensorPrecision(method[algorithm_keys]["sensorPrecision"],
                                                                    method[algorithm_keys]["steps"],
                                                                    selected_rows[i][k][0],
                                                                    st.session_state.data_restriction_final_deployment[column]))
                                            elif algorithm_keys == 'Fixed Amount Perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    fixedAmountSteps(method[algorithm_keys]["amount"],
                                                                     method[algorithm_keys]["steps"],
                                                                     selected_rows[i][k][0],
                                                                     st.session_state.data_restriction_final_deployment[column]))
                                            elif algorithm_keys == 'Range Perturbation':
                                                perturbedList[algorithm_keys] = (
                                                    perturbRange(method[algorithm_keys]["lowerBound"],
                                                                 method[algorithm_keys]["upperBound"],
                                                                 method[algorithm_keys]["steps"]))

                                            elif algorithm_keys == "Bin Perturbation":
                                                try:
                                                    for j in range(len(st.session_state.loaded_bin_dict[k]) - 1):
                                                        if float(st.session_state.loaded_bin_dict[k][j]) <= float(
                                                                selected_rows[i][k][0]) <= float(
                                                                st.session_state.loaded_bin_dict[k][j + 1]):
                                                            new_list = [float(st.session_state.loaded_bin_dict[k][j]),
                                                                        float(st.session_state.loaded_bin_dict[k][j + 1])]
                                                            break

                                                    perturbedList[algorithm_keys] = (
                                                        perturbRange(new_list[0],
                                                                     new_list[1],
                                                                     method[algorithm_keys]["steps"]))
                                                except:
                                                    st.error(f"Value of **{column}** outside of bin range. Change value or create new bins.")



                                            elif algorithm_keys == 'Perturb in order':
                                                try:

                                                    perturbedList[algorithm_keys] = (
                                                        perturbInOrder(method[algorithm_keys]["steps"],
                                                                       selected_rows[i][k][0],
                                                                       st.session_state.data_restriction_final_deployment[
                                                                           column]))



                                                except Exception as e:
                                                    st.write(e)


                                            elif algorithm_keys == 'Perturb all values':
                                                perturbedList[algorithm_keys] = (
                                                    perturbAllValues(
                                                        selected_rows[i][k][0],
                                                        st.session_state.data_restriction_final_deployment[column]))
                                except Exception as e:
                                    st.error(e)
                                perturbed_value_list[column] = perturbedList

                    except Exception as e:
                        st.write(e)
                    # index perturb contains the different perturbation values for each case
                    index_perturb.append(perturbed_value_list.copy())
                with st.expander(STRINGS.DEPLOYMENTSHOWALLPERTURBEDVALUES):
                    st.write(perturbed_value_list)

                try:
                    for i in range(0, len(selected_rows)):
                        for column, method in index_perturb[i].items():
                            if method:
                                # ausgewählte methoden ist ein dictionary mit der methode als key und perturbated values als value

                                # für jede ausgwählte row in aggrid gebe ein dictionary mit key = column und value = values aus
                                for method_name, perturbed_values in method.items():

                                    for k, v in selected_rows[i].items():
                                        if k == column:
                                            selected_rows[i][k].extend(perturbed_values)

                    result_df = pd.DataFrame(selected_rows,
                                             columns=result.columns)
                except Exception as e:
                    st.empty(e)

                # insert predictions of case into perturbed cases
                result_df["prediction"] = result["prediction"]

                try:
                    # prio and selected
                    for x in st.session_state.perturb_mode_values[::-1]:
                        result_df = result_df.explode(x)

                    # all values in order to have values and not a list
                    for x in st.session_state["dataframe_feature_names"]["featureName.value"].values.tolist():
                        result_df = result_df.explode(x)

                except Exception as e:
                    st.write(e)

                # delete duplicate rows in order to prevent multiple same perturbations

                result_df = result_df.drop_duplicates(keep='first')


                result_df["Case"] = result_df.index

            except Exception as e:
                st.info(e)

            try:


                x = pd.concat([df, result_df.iloc[:, :-1]]).reset_index(drop=True)
                x_filled = x.fillna(method='ffill').copy()


                for columns in x_filled:
                    try:
                        if st.session_state.level_of_measurement_dic[columns] == "Cardinal":
                            x_filled[columns] = x_filled[columns].astype(float)
                        else:
                            x_filled[columns] = x_filled[columns].astype(str)
                    except:
                        pass

                try:
                    x_trans_df = pd.DataFrame(ct.fit_transform(x_filled).toarray(), columns=ct.get_feature_names_out()).reset_index(
                    drop=True)
                except:
                    # st.write(e)
                    x_trans_df = pd.DataFrame(ct.fit_transform(x_filled), columns=ct.get_feature_names_out()).reset_index(
                    drop=True)


                # get predictions for perturbed cases
                y_pred = pd.DataFrame(st.session_state.model.predict(x_trans_df))
                # reset index in order to remove rows which were generated for the onehotencoder
                y_pred = y_pred.iloc[len(df):].reset_index(drop=True)
                # reset index in order to be able to insert y_pred correctly
                result_df = result_df.reset_index(drop=True)
                result_df["prediction"] = y_pred


                try:
                    st.session_state["dfs"] = [value for key, value in result_df.groupby('Case')]
                except Exception as e:
                    st.error(e)

                for i, df in enumerate(st.session_state["dfs"]):

                    determinationNameUUID = 'PerturbationOfClassificationCase'
                    determinationName = 'PerturbationOfClassificationCase'

                    name = 'PerturbationOfClassificationCase'
                    rprovName = 'PerturbationOfClassificationCase'
                    uuid_PerturbationAssessment = uuid.uuid4()

                    #if checkbox_upload:
                    try:
                        uuid_DefinitionOfPerturbationOption = determinationActivity(host_upload, determinationName,label_list[i])
                        uploadPerturbationAssessment(host_upload, uuid_PerturbationAssessment, label_list[i],
                                                         uuid_DefinitionOfPerturbationOption,
                                                         st.session_state.perturbationOptions_settings,
                                                         st.session_state.assessmentPerturbationOptions, st.session_state.pertubation_mode)
                        rows = selected_rows_DF.iloc[i].to_dict()
                        uploadClassificationCase(host_upload, label_list[i], uuid_PerturbationAssessment, rows)
                    except Exception as e:
                        st.error(e)

                    if len(label_list)>1:
                        expand_option_case = False
                    else:
                        expand_option_case = True

                    with st.expander(STRINGS.DEPLOYMENTRETRIEVERESULTS.format(label_list[i]),expanded=expand_option_case):
                        df = df.drop(columns=["Case"])
                        if len(df.index) > 20000:
                            st.info(STRINGS.DEPLOYMENTPERFORMANCEWARINING.format(len(df.index)))
                        try:
                            st.dataframe(df.style.apply(lambda x: ["background-color: {}".format(color_map.get(get_perturbation_level(x.name, v), "")) if v !=
                                                x.iloc[0] else "" for i, v in enumerate(x)], axis=0),use_container_width=True)
                        except Exception as e:
                            st.dataframe(df)
                            st.write(e)

                        different_pred = df.iloc[:1]

                        different_pred2 = df[df['prediction'] != df['prediction'][0]]

                        # shows the first original prediction
                        different_pred3 = pd.concat([different_pred, different_pred2]).reset_index(drop=True)

                        ste.download_button(STRINGS.DEPLOYMENTDOWNLOADCASESBUTTON.format(label_list[i]),
                                            df.to_csv(index=False),
                                            f"{label_list[i]}_{uuid_PerturbationAssessment}.csv")

                        if different_pred2.empty:
                            st.info(STRINGS.DEPLOYMENTNOCHANGEDPREDICTION.format(label_list[i]))
                        else:
                            with st.expander(STRINGS.DEPLOYMENTSHOWCHANGEDCASES):
                                st.dataframe(different_pred3.style.apply(lambda x: ["background-color: {}".format(
                                    color_map.get(get_perturbation_level(x.name, v), "")) if v !=
                                                                                             x.iloc[0] else "" for i, v
                                                                    in enumerate(x)], axis=0),use_container_width=True)

            except Exception as e:
                st.info(e)
except Exception as e:
    st.warning(e)
