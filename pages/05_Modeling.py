import uuid
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from functions.functions_Modeling import getDefault, changeAlgorithm, \
    update_steps, update_perturbation_level, update_additional_value
from functions.fuseki_connection import getAttributes, getUniqueValuesSeq, \
    determinationActivity, get_dataset, \
    getInformationToFeature, getLabelForScaleOfFeature, getAllPerturbationOptionLabels, uploadPerturbationOption, \
    getUUIDForLabelsOfToFeature, retrieveFeatureUUID
from functions.perturbation_algorithms import percentage_perturbation_settings, sensorPrecision_settings, \
    fixedAmountSteps_settings, perturbRange_settings, perturbBin_settings, perturbInOrder_settings, \
    perturbAllValues_settings
# This variable contains all strings which are shown in the app
import config.strings as STRINGS
# This variable contains all global configuration options
import config.config as CONFIG

# Some init stuff
host, host_upload = get_dataset()

try:
    getUniqueValuesSeq(host)
except Exception as e:
    st.error("Please upload feature values in Data Understanding step")
    if st.button("Data Understanding"):
        switch_page("Data Understanding")
    st.stop()

try:
    getDefault(host)
except:
    st.error("Couldn't load unique values. If already inserted refresh page.")

with st.expander(STRINGS.MODELINGSHOWINFORMATIONEXPANDER):
    try:
        getAttributes(host)
    except Exception as e:
        st.error("Please refresh page or change database.")
        st.stop()

if "selectedEntityLabels" not in st.session_state:
    st.session_state["selectedEntityLabels"] = dict()

if "data_restrictions_dict" not in st.session_state:
    st.session_state["data_restrictions_dict"] = dict()
if st.session_state.dataframe_feature_names.empty:
    st.stop()

if "default" not in st.session_state:
    st.session_state.cardinal_val = {}
    st.session_state.ordinal_val = {}
    st.session_state.nominal_val = {}
    st.session_state.default = {}
    for columns in st.session_state.dataframe_feature_names["featureName.value"]:
        st.session_state.default[columns] = []

# End of init stuff

# horizontal menu
selected2 = option_menu(None, [STRINGS.MODELINGTAB1, STRINGS.MODELINGTAB2],
                        icons=['check2-circle', 'gear'],
                        orientation="horizontal")

# This is the first tab, where a user can define which perturbation options may be used for a given feature.
if selected2 == STRINGS.MODELINGTAB1:

    colored_header(
        label=STRINGS.MODELINGCHOOSEPERTURBATIONOPTIONHEADER,
        description=STRINGS.MODELINGCHOOSEPERTURBATIONOPTIONDESCRIPTION,
        color_name="red-50",
    )

    # We have an extra tab for each of the three level of measurements
    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])

    # Loop through all features.
    for columns, level in st.session_state.level_of_measurement_dic.items():
        if level == "Cardinal":
            with tab1:
                with st.expander(label=STRINGS.MODELINGSHOWPERTURBATIONOPTIONEXPANDER.format(columns)):
                    try:
                        # Check for recommendations
                        # If a feature has a high volatility, then perturbing might be a good idea.
                        if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                            st.warning(STRINGS.MODELINGHIGHVOLATILITYINFO)
                        else:
                            st.info(STRINGS.MODELINGVOLATILITYINFO.format(
                                st.session_state.volatility_of_features_dic[columns]))
                        # TODO one may also check for sensor precision and other infos.
                    except:
                        st.info(STRINGS.MODELINGNOVOLATILITYINFO)

                    try:
                        st.session_state.default[columns] = st.multiselect(f'{columns}',
                                                                           CONFIG.PERTURBATION_OPTIONS_CARDINAL,
                                                                           default=st.session_state.default[
                                                                               columns],
                                                                           key=f"algo_{columns}",
                                                                           on_change=changeAlgorithm,
                                                                           args=(columns,))
                        st.session_state.cardinal_val[columns] = st.session_state.default[columns]

                    except Exception as e:
                        st.error(e)
                        st.info(STRINGS.MODELINGNOCARDINALVALUES, icon="ℹ️")

                    # If sensor precision oder binning was selected as option, check if the necessary information was determined.
                    try:
                        if "Sensor Precision Perturbation" in st.session_state.cardinal_val[columns]:
                            if columns not in st.session_state.loaded_feature_sensor_precision_dict.keys():
                                st.error(STRINGS.MODELINGNOSENSORPRECISION.format(columns))
                            else:
                                st.write(STRINGS.MODELINGSENSORPRECISION,
                                         st.session_state.loaded_feature_sensor_precision_dict[columns])
                    except:
                        pass
                    try:
                        if "Bin Perturbation" in st.session_state.cardinal_val[columns]:
                            if columns not in st.session_state.loaded_bin_dict.keys():
                                st.error(STRINGS.MODELINGNOBINS.format(columns))
                            else:
                                st.write(STRINGS.MODELINGBINS,
                                         [[st.session_state.loaded_bin_dict[columns][i],
                                           st.session_state.loaded_bin_dict[columns][i + 1]] for i in
                                          range(len(st.session_state.loaded_bin_dict[columns]) - 1)])
                    except:
                        pass

        if level == "Ordinal":
            with tab2:
                with st.expander(label=STRINGS.MODELINGSHOWPERTURBATIONOPTIONEXPANDER.format(columns)):
                    try:
                        if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                            st.warning(STRINGS.MODELINGHIGHVOLATILITYINFO)
                        else:
                            st.info(STRINGS.MODELINGVOLATILITYINFO.format(
                                st.session_state.volatility_of_features_dic[columns]))

                    except:
                        st.info(STRINGS.MODELINGNOVOLATILITYINFO)

                    try:
                        st.session_state.default[columns] = st.multiselect(f'{columns}',
                                                                           CONFIG.PERTURBATION_OPTIONS_ORDINAL,
                                                                           default=st.session_state.default[
                                                                               columns],
                                                                           key=f"algo_{columns}",
                                                                           on_change=changeAlgorithm,
                                                                           args=(columns,))
                        st.session_state.ordinal_val[columns] = st.session_state.default[columns]


                    except Exception as e:
                        st.write(e)
                        st.info(STRINGS.MODELINGNOORDINALVALUES, icon="ℹ️")

        if level == "Nominal":
            with tab3:
                with st.expander(label=STRINGS.MODELINGSHOWPERTURBATIONOPTIONEXPANDER.format(columns)):
                    try:
                        if st.session_state.volatility_of_features_dic[columns] == 'High Volatility':
                            st.warning(STRINGS.MODELINGHIGHVOLATILITYINFO)
                        else:
                            st.info(STRINGS.MODELINGVOLATILITYINFO.format(
                                st.session_state.volatility_of_features_dic[columns]))

                    except:
                        st.info(STRINGS.MODELINGNOVOLATILITYINFO)

                    try:
                        st.session_state.default[columns] = st.multiselect(f'{columns}',
                                                                           CONFIG.PERTURBATION_OPTIONS_NOMINAL,
                                                                           default=st.session_state.default[
                                                                               columns],
                                                                           key=f"algo_{columns}",
                                                                           on_change=changeAlgorithm,
                                                                           args=(columns,))
                        st.session_state.nominal_val[columns] = st.session_state.default[columns]
                    except:
                        st.info(STRINGS.MODELINGNONOMINALVALUES, icon="ℹ️")

    colored_header(
        label=STRINGS.MODELINGSHOWCHOSENPERTOPTIONEXPANDERLABEL,
        description=STRINGS.MODELINGSHOWCHOSENPERTOPTIONEXPANDERDESCRIPTION,
        color_name="red-50",
    )
    with st.expander(STRINGS.MODELINGPERTOPTIONS):
        try:
            if st.session_state['cardinal_val'] != {}:
                st.write('**Cardinal**')
                st.json(st.session_state['cardinal_val'])
            if st.session_state['ordinal_val'] != {}:
                st.write('**Ordinal**')
                st.json(st.session_state['ordinal_val'])
            if st.session_state['nominal_val'] != {}:
                st.write('**Nominal**')
                st.json(st.session_state['nominal_val'])
        except:
            st.info(STRINGS.MODELINGNOPERTOPS, icon="ℹ️")

try:
    if selected2 == STRINGS.MODELINGTAB2:

        if "entities" not in st.session_state:
            st.session_state.entities = dict()

        tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])
        settings = dict()
        perturbationLevel = dict()
        options_perturbation_level = ["Red", "Orange", "Green"]

        # Start with cardinal features
        with tab1:
            # check if a perturbation option is chosen for a cardinal feature
            is_empty = True
            for values in st.session_state['cardinal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info(STRINGS.MODELINGNOPOFORSCALE.format("cardinal"))

            # key is the name of the feature
            # values is a list of suitable perturbation options
            for key, values in st.session_state['cardinal_val'].items():

                settingList = dict()
                perturbationLevel_list = dict()

                # Now we create an expander for every feature which got a perturbation option assigned
                with st.expander(STRINGS.MODELINGCUSTOMIZEPOEXPANDER.format(key)):
                    try:
                        if values:
                            pass
                            #try:
                            #    # Retrieve information from the graph in order to select which
                            #    result_2 = getInformationToFeature(host, key)
                            #    entities_selection = result_2["label.value"].tolist()

#
                            #    if len(entities_selection) > 0:
                            #        entities = st.multiselect(
                            #            label=STRINGS.MODELINGSELECTINFORMATIONFORPERTURBATION,
                            #            options=entities_selection, default=entities_selection)

                            #except Exception as e:
                            #    entities = []
                            #    st.info(STRINGS.MODELINGNOINFORMATION)

                            # Add the label of scale of feature as information for the perturbation option
                            #labelForScaleOfFeature = getLabelForScaleOfFeature(host, key)
                            #st.info(entities)
                            #entities.append(labelForScaleOfFeature["label.value"][0])
                            #st.info(entities)

                            #try:

                                #st.session_state["entities"][key] = \
                                #(labelForScaleOfFeature[labelForScaleOfFeature['label.value'].isin(entities)])[
                                #    "DataUnderstandingEntityID.value"].tolist()
                            #    st.session_state["selectedEntityLabels"][key] = entities
#
                            #    # Determine the final data restriction
                            #    flag = False
                            #    for value in entities:
                           #         if value.startswith("restriction"):
                            #            flag = True
                            #    if flag == True:
                            #        st.session_state.data_restriction_final[key] = \
                            #            st.session_state.data_restrictions_dict[key]
                            #    else:
                            #        st.session_state.data_restriction_final[key] = (
                            #            st.session_state.unique_values_dict[key])
                                # st.session_state.data_restriction_final[key]
                            #except Exception as e:
                            #    st.error(e)
                    except Exception as e:
                        st.error(e)

                    # interate(method) through all assigned perturbation options(values)
                    for method in values:
                        # st.write(method)

                        #####################
                        try:
                            # Retrieve information from the graph in order to select which
                            result_2 = getInformationToFeature(host, key)
                            entities_selection = result_2["label.value"].tolist()

                            if len(entities_selection) > 0:
                                entities = st.multiselect(
                                    label=STRINGS.MODELINGSELECTINFORMATIONFORPERTURBATION,
                                    options=entities_selection, default=entities_selection, key=key+method)

                        except Exception as e:
                            entities = []
                            st.info(STRINGS.MODELINGNOINFORMATION)

                        # Add the label of scale of feature as information for the perturbation option
                        labelForScaleOfFeature = getLabelForScaleOfFeature(host, key)
                        # st.info(entities)
                        entities.append(labelForScaleOfFeature["label.value"][0])
                        # st.info(entities)

                        try:

                            # st.session_state["entities"][key] = \
                            # (labelForScaleOfFeature[labelForScaleOfFeature['label.value'].isin(entities)])[
                            #    "DataUnderstandingEntityID.value"].tolist()
                            st.session_state["selectedEntityLabels"][key+method] = entities

                            # Determine the final data restriction
                            flag = False
                            for value in entities:
                                if value.startswith("restriction"):
                                    flag = True
                            if flag == True:
                                st.session_state.data_restriction_final[key] = \
                                    st.session_state.data_restrictions_dict[key]
                            else:
                                st.session_state.data_restriction_final[key] = (
                                    st.session_state.unique_values_dict[key])
                            # st.session_state.data_restriction_final[key]
                        except Exception as e:
                            st.error(e)
                        ########################

                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 1

                        # The default perturbation level is red.
                        if f"assignedPerturbationLevel_{key}_{method}" not in st.session_state:
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = "Red"

                        # First Initialize value which is to perturbate
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = float(
                                st.session_state.data_restriction_final[key][0])

                        # set Data Restriction if selected
                        if st.session_state[f"value_perturbate{key}_{method}"] < float(
                                st.session_state.data_restriction_final[key][0]):
                            st.session_state[f"value_perturbate{key}_{method}"] = float(
                                st.session_state.data_restriction_final[key][0])

                        if f"additional_value_{key}_{method}" not in st.session_state:
                            if 0 < float(st.session_state.data_restriction_final[key][0]):
                                st.session_state[f"additional_value_{key}_{method}"] = \
                                    st.session_state.data_restriction_final[key][0]
                            else:
                                st.session_state[f"additional_value_{key}_{method}"] = 0
                        if "lower_bound" not in st.session_state:
                            st.session_state[f"lower_bound{key}_{method}"] = 0
                        if "upper_bound" not in st.session_state:
                            st.session_state[f"upper_bound{key}_{method}"] = 0


                        # Check which options are selected for the feature.
                        if method == 'Percentage Perturbation':
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))

                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Percentage of steps", min_value=int(1), max_value=int(100),
                                                value=int(st.session_state[f"steps_{key}_{method}"]),
                                                key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL, options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level, args=(key, method))
                            settingList[method] = (
                                percentage_perturbation_settings(st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                        if method == "5% Perturbation":
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL, options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))
                            settingList[method] = (
                                percentage_perturbation_settings(5))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                        if method == "10% Perturbation":
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL, options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                percentage_perturbation_settings(10))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                        elif method == 'Sensor Precision Perturbation':
                            try:
                                if key not in st.session_state.loaded_feature_sensor_precision_dict:
                                    st.warning(STRINGS.MODLEINGNOSENSORPRECISION)
                                    st.session_state.loaded_feature_sensor_precision_dict[key]

                                else:
                                    st.session_state[f"additional_value_{key}_{method}"] = \
                                        st.session_state.loaded_feature_sensor_precision_dict[key]

                                st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))

                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.number_input("Steps", min_value=int(1), step=int(1),
                                                    value=int(st.session_state[f"steps_{key}_{method}"]),
                                                    key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                    args=(key, method)))

                                st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                    STRINGS.MODELINGSELECTPERTLEVEL, options=options_perturbation_level,
                                    index=options_perturbation_level.index(
                                        st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                    help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                    key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                    on_change=update_perturbation_level,
                                    args=(key, method))

                                st.write(
                                    f"Sensor Precision: **{st.session_state.loaded_feature_sensor_precision_dict[key]}**")

                                settingList[method] = (
                                    sensorPrecision_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                             st.session_state[f"steps_{key}_{method}"]))
                                perturbationLevel_list[method] = st.session_state[
                                    f"assignedPerturbationLevel_{key}_{method}"]

                            except Exception as e:
                                st.write(STRINGS.MODELINGSENSORPRECISIONMISSING)
                            st.write("---------------")

                        elif method == 'Fixed Amount Perturbation':
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            st.session_state[f"additional_value_{key}_{method}"] = float(st.number_input("Amount",
                                                                                                         value=float(
                                                                                                             st.session_state[
                                                                                                                 f"additional_value_{key}_{method}"]),
                                                                                                         min_value=float(
                                                                                                             0.00),
                                                                                                         max_value=float(
                                                                                                             st.session_state.data_restriction_final[
                                                                                                                 key][
                                                                                                                 1]),
                                                                                                         key=f"additional_value_widget_{key}_{method}",
                                                                                                         on_change=update_additional_value,
                                                                                                         args=(
                                                                                                         key, method)))

                            st.session_state[f"steps_{key}_{method}"] = int(
                                st.number_input("Steps",
                                                min_value=int(1),
                                                step=int(1),
                                                value=st.session_state[f"steps_{key}_{method}"],
                                                key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL, options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                fixedAmountSteps_settings(st.session_state[f"additional_value_{key}_{method}"],
                                                          st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]

                            st.write("---------------")

                        elif method == 'Range Perturbation':
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))

                            if f"additional_value_{key}_{method}_bound" not in st.session_state:
                                st.session_state[f"additional_value_{key}_{method}_bound"] = [
                                    float(st.session_state.data_restriction_final[key][0]),
                                    float(st.session_state.data_restriction_final[key][-1])]

                            lower_border = round(st.number_input(STRINGS.MODLINGSELECTLOWERBOUND,
                                                                 value=float(
                                                                     st.session_state.data_restriction_final[key][0]),
                                                                 min_value=float(
                                                                     st.session_state.data_restriction_final[key][0]),
                                                                 max_value=float(
                                                                     st.session_state.data_restriction_final[key][-1]),
                                                                 key=f"lower_border_range_perturbation_{key}"), 2)

                            upper_border = round(st.number_input(STRINGS.MODLEINGSELECTUPPERBOUND,
                                                                 value=float(
                                                                     st.session_state.data_restriction_final[key][-1]),
                                                                 min_value=lower_border,
                                                                 max_value=float(
                                                                     st.session_state.data_restriction_final[key][-1]),
                                                                 key=f"upper_border_range_perturbation_{key}"), 2)

                            if st.session_state[f"lower_border_range_perturbation_{key}"] \
                                    >= st.session_state[f"upper_border_range_perturbation_{key}"]:
                                st.error(STRINGS.MODELINGLOWERSMALLERTHANUPPER)
                                st.stop()
                            else:
                                st.session_state[f"additional_value_{key}_{method}_bound"] = \
                                    [float(lower_border), float(upper_border)]

                            if st.session_state[f"steps_{key}_{method}"] == 0:
                                st.session_state[f"steps_{key}_{method}"] = 1

                            st.session_state[f"steps_{key}_{method}"] = int(st.number_input("Steps",
                                                                                            min_value=int(1),
                                                                                            step=int(1),
                                                                                            value=st.session_state[
                                                                                                f"steps_{key}_{method}"],
                                                                                            key=f"steps_widget_{key}_{method}",
                                                                                            on_change=update_steps,
                                                                                            args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL,
                                options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbRange_settings(st.session_state[f"additional_value_{key}_{method}_bound"][0],
                                                      st.session_state[f"additional_value_{key}_{method}_bound"][1],
                                                      st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]

                            st.write("---------------")


                        elif method == 'Bin Perturbation':
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            try:
                                if key not in st.session_state.loaded_bin_dict:
                                    st.warning(STRINGS.MODELINGNOBINDETERMINED)
                                    st.write(st.session_state.loaded_bin_dict[key])
                                else:
                                    st.write([[st.session_state.loaded_bin_dict[key][i],
                                               st.session_state.loaded_bin_dict[key][i + 1]] for i in
                                              range(len(st.session_state.loaded_bin_dict[key]) - 1)])

                                    st.session_state[f"steps_{key}_{method}"] = int(
                                        st.number_input("Steps", min_value=int(1), step=int(1),
                                                        value=st.session_state[f"steps_{key}_{method}"],
                                                        key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                        args=(key, method)))

                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                        STRINGS.MODELINGSELECTPERTLEVEL,
                                        options=options_perturbation_level,
                                        index=options_perturbation_level.index(
                                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                        help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                        key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                        on_change=update_perturbation_level,
                                        args=(key, method))

                                    settingList[method] = (
                                        perturbBin_settings(st.session_state[f"steps_{key}_{method}"]))
                                    perturbationLevel_list[method] = st.session_state[
                                        f"assignedPerturbationLevel_{key}_{method}"]

                                    st.write("---------------")
                            except Exception as e:
                                st.write(STRINGS.MODELINGDETERMINEBINS)

                if settingList:
                    settings[key] = settingList
                if perturbationLevel_list:
                    perturbationLevel[key] = perturbationLevel_list
            st.session_state['settings'] = settings
            st.session_state['perturbationLevel'] = perturbationLevel

        # Ordinal features
        with tab2:
            # Check if POs for oridnal features are assigned
            is_empty = True
            for values in st.session_state['ordinal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info(STRINGS.MODELINGNOPOFORSCALE.format("ordinal"))

            for key, values in st.session_state['ordinal_val'].items():
                # if "settingList" not in st.session_state:
                #     st.session_state.settingList = dict()
                settingList = dict()
                perturbationLevel_list = dict()

                with st.expander(STRINGS.MODELINGCUSTOMIZEPOEXPANDER.format(key)):
                    try:
                        if values:
                            pass
                    except Exception as e:
                        st.error(e)

                    for method in values:

                        ################
                        try:
                            # Retrieve information from the graph in order to select which
                            result_2 = getInformationToFeature(host, key)
                            entities_selection = result_2["label.value"].tolist()

                            if len(entities_selection) > 0:
                                entities = st.multiselect(
                                    label=STRINGS.MODELINGSELECTINFORMATIONFORPERTURBATION,
                                    options=entities_selection, default=entities_selection, key=key+method)

                        except Exception as e:
                            entities = []
                            st.info(STRINGS.MODELINGNOINFORMATION)

                        # Add the label of scale of feature as information for the perturbation option
                        labelForScaleOfFeature = getLabelForScaleOfFeature(host, key)
                        # st.info(entities)
                        entities.append(labelForScaleOfFeature["label.value"][0])
                        # st.info(entities)

                        try:

                            # st.session_state["entities"][key] = \
                            # (labelForScaleOfFeature[labelForScaleOfFeature['label.value'].isin(entities)])[
                            #    "DataUnderstandingEntityID.value"].tolist()
                            st.session_state["selectedEntityLabels"][key+method] = entities

                            # Determine the final data restriction
                            flag = False
                            for value in entities:
                                if value.startswith("restriction"):
                                    flag = True
                            if flag == True:
                                st.session_state.data_restriction_final[key] = \
                                    st.session_state.data_restrictions_dict[key]
                            else:
                                st.session_state.data_restriction_final[key] = (
                                    st.session_state.unique_values_dict[key])
                            # st.session_state.data_restriction_final[key]
                        except Exception as e:
                            st.error(e)

                        #######################

                        if f"assignedPerturbationLevel_{key}_{method}" not in st.session_state:
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = "Red"
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 1
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                        if f"additional_value_{key}_{method}" not in st.session_state:
                            st.session_state[f"additional_value_{key}_{method}"] = 0

                        if method == "Perturb in order":
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            # with st.expander("Show all values:"):
                            #    st.session_state.data_restriction_final[key]

                            if len(st.session_state.data_restriction_final[key]) == 2:
                                st.session_state[f"steps_{key}_{method}"] = 2
                            else:
                                st.session_state[f"steps_{key}_{method}"] = int(
                                    st.number_input("Steps",
                                                    min_value=int(1), step=int(1),
                                                    value=st.session_state[f"steps_{key}_{method}"],
                                                    key=f"steps_widget_{key}_{method}", on_change=update_steps,
                                                    args=(key, method)))

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL,
                                options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbInOrder_settings(st.session_state[f"steps_{key}_{method}"]))
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]

                            st.write("---------------")

                        if method == "Perturb all values":
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            # with st.expander("Show all values:"):
                            #    st.session_state.data_restriction_final[key]

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL,
                                options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (
                                perturbAllValues_settings())  # st.session_state[f"value_perturbate{key}_{method}"],
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                if settingList:
                    settings[key] = settingList
                if perturbationLevel_list:
                    perturbationLevel[key] = perturbationLevel_list
            st.session_state['settings'] = settings
            st.session_state['perturbationLevel'] = perturbationLevel

        # Nominal features
        with tab3:
            # check if algorithm for level of scale is chosen
            is_empty = True
            for values in st.session_state['nominal_val'].values():
                if values:
                    is_empty = False

            if is_empty:
                st.info(STRINGS.MODELINGNOPOFORSCALE.format("nominal"))

            for key, values in st.session_state['nominal_val'].items():
                if "settingList" not in st.session_state:
                    st.session_state.settingList = dict()
                settingList = dict()
                perturbationLevel_list = dict()

                with st.expander(STRINGS.MODELINGCUSTOMIZEPOEXPANDER.format(key)):
                    try:
                        if values:
                            pass
                    except Exception as e:
                        st.error(e)

                    for method in values:

                        ################
                        try:
                            # Retrieve information from the graph in order to select which
                            result_2 = getInformationToFeature(host, key)
                            entities_selection = result_2["label.value"].tolist()

                            if len(entities_selection) > 0:
                                entities = st.multiselect(
                                    label=STRINGS.MODELINGSELECTINFORMATIONFORPERTURBATION,
                                    options=entities_selection, default=entities_selection, key=key + method)

                        except Exception as e:
                            entities = []
                            st.info(STRINGS.MODELINGNOINFORMATION)

                        # Add the label of scale of feature as information for the perturbation option
                        labelForScaleOfFeature = getLabelForScaleOfFeature(host, key)
                        # st.info(entities)
                        entities.append(labelForScaleOfFeature["label.value"][0])
                        # st.info(entities)

                        try:

                            # st.session_state["entities"][key] = \
                            # (labelForScaleOfFeature[labelForScaleOfFeature['label.value'].isin(entities)])[
                            #    "DataUnderstandingEntityID.value"].tolist()
                            st.session_state["selectedEntityLabels"][key + method] = entities

                            # Determine the final data restriction
                            flag = False
                            for value in entities:
                                if value.startswith("restriction"):
                                    flag = True
                            if flag == True:
                                st.session_state.data_restriction_final[key] = \
                                    st.session_state.data_restrictions_dict[key]
                            else:
                                st.session_state.data_restriction_final[key] = (
                                    st.session_state.unique_values_dict[key])
                            # st.session_state.data_restriction_final[key]
                        except Exception as e:
                            st.error(e)

                        #######################


                        if f"assignedPerturbationLevel_{key}_{method}" not in st.session_state:
                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = "Red"
                        if f"steps_{key}_{method}" not in st.session_state:
                            st.session_state[f"steps_{key}_{method}"] = 0
                        if f"value_perturbate{key}_{method}" not in st.session_state:
                            st.session_state[f"value_perturbate{key}_{method}"] = \
                                st.session_state.data_restriction_final[key][0]
                        if f"additional_value_{key}_{method}" not in st.session_state:
                            st.session_state[f"additional_value_{key}_{method}"] = 0

                        if method == "Perturb all values":
                            st.markdown(STRINGS.MODELINGCUSTOMIZEALGO.format(method))
                            # with st.expander("Show all values:"):
                            #    st.session_state.data_restriction_final[key]

                            st.session_state[f"assignedPerturbationLevel_{key}_{method}"] = st.selectbox(
                                STRINGS.MODELINGSELECTPERTLEVEL, options=options_perturbation_level,
                                index=options_perturbation_level.index(
                                    st.session_state[f"assignedPerturbationLevel_{key}_{method}"]),
                                help=STRINGS.MODELINGPERTLEVELEXPLANATION,
                                key=f"assignedPerturbationLevel_widget_{key}_{method}",
                                on_change=update_perturbation_level,
                                args=(key, method))

                            settingList[method] = (perturbAllValues_settings())
                            perturbationLevel_list[method] = st.session_state[
                                f"assignedPerturbationLevel_{key}_{method}"]
                            st.write("---------------")

                if settingList:
                    settings[key] = settingList
                if perturbationLevel_list:
                    perturbationLevel[key] = perturbationLevel_list
            st.session_state['settings'] = settings
            st.session_state['perturbationLevel'] = perturbationLevel

        # If there are options specified, then save them to the graph.
        if st.session_state['settings'] != {}:
            st.write("-------")
            with st.expander(STRINGS.MODELINGSHOWSETTING):
                st.write(st.session_state['settings'])

            with st.form(STRINGS.MODELINGINSERTLABELFORM):
                st.info(STRINGS.MODLEINGLABELINFO)
                labelPerturbation = st.text_input(STRINGS.MODELINGINSERTLABELFORM)

                # Saveing the selected and customized POs to the graph.
                if st.form_submit_button(STRINGS.MODELINGUPLOADBUTTONLABEL, type="primary"):
                    # First, check whether the name of the PO collection is not already used.
                    results = getAllPerturbationOptionLabels(host)

                    # Iterate over the rows of the DataFrame
                    for index, row in results.iterrows():
                        # Get the part of the string before the first '-'
                        value = row["PerturbationOptionLabel.value"].split('-', 1)[0]

                        # If there is already a Collection with this name, then rais an error
                        if value == labelPerturbation:
                            st.warning(STRINGS.MODELINGLABELALREADYEXISTS)
                            st.stop()
                else:
                    st.stop()

                try:
                    # Create and save a modeling activity for the determination of perturbation options
                    determinationName = 'DefinitionOfPerturbationOption'
                    label = "Definition of Perturbation Option"
                    uuid_DefinitionOfPerturbationOption = determinationActivity(host_upload, determinationName, label)




                    # if feature is in perturbation settings
                    # create list with activities and loop in order to insert them as modelingEntityWasDerivedFrom
                    for key in st.session_state['settings']:

                        featureID = retrieveFeatureUUID(host, key)

                        # create another loop in order to get different UUIDs for PerturbationOptions
                        # KG sollen die einzelnen Optionen einzeln oder gesammelt gespeichert werden
                        for method, perturbationOption in st.session_state['settings'][key].items():

                            uuid_PerturbationOption = uuid.uuid4()
                            #liste_entities = st.session_state["entities"][key].copy()
                            liste_entities = st.session_state["selectedEntityLabels"][key+method].copy()
                            #st.info(liste_entities)
                            entityUUIDs = []
                            for entityLabel in liste_entities:
                                entityUUIDs.append(getUUIDForLabelsOfToFeature(host, entityLabel, featureID))

                            #st.info(entityUUIDs)

                            #If the option is bin or sensor then add this information to the entities on which the option is based on.
                            if method == "Bin Perturbation":
                                bin_entity = \
                                    st.session_state.DF_bin_dict[st.session_state.DF_bin_dict["label.value"] == key][
                                        "DPE.value"].reset_index(drop=True)
                                entityUUIDs.append(bin_entity[0])

                            if method == "Sensor Precision Perturbation":
                                sensor_precision = st.session_state.DF_feature_sensor_precision[
                                    st.session_state.DF_feature_sensor_precision["featureName.value"] == key][
                                    "DataUnderstandingEntityID.value"].reset_index(drop=True)
                                entityUUIDs.append(sensor_precision[0])


                            for entitiyUuid in entityUUIDs:
                                perturbationOptionlabel = str(perturbationOption)
                                perturbationOptionlabel = perturbationOptionlabel.replace("'", "").replace("{","").replace("}", "")

                                uploadPerturbationOption(host_upload, uuid_PerturbationOption, featureID, method,
                                                         perturbationOption,
                                                         st.session_state["perturbationLevel"][key][method], entitiyUuid,
                                                         uuid_DefinitionOfPerturbationOption,
                                                         f"{labelPerturbation}-{method}: {perturbationOptionlabel}")
                    st.success(STRINGS.MODELINGPERTOPSSAVED)
                except Exception as e:
                    st.write(e)
                    st.error(STRINGS.MODELINGPERTOPSERROR)

except Exception as e:
    st.warning(e)
