FILEPATHMODELS = "models"


#fuseki_connection.py

SELECTDATASETFIRSTERROR = "Please select a dataset in Home first!"

#home.py
MAINTITLE = "Reliability Assessment by Perturbation"

JSONMETADATAEXAMPLE = """{
                      "FeatureName1": {"levelOfScale": "Cardinal", 	"uniqueValues": ["minValue", "maxValue"]},
                      "FeatureName2": {"levelOfScale": "Nominal", 	"uniqueValues": ["x", "y","z"]},
                      "FeatureName3": {"levelOfScale": "Ordinal", 	"uniqueValues": ["1", "2", "3"]}
                        }
                    """
SELECTDATASETHEADER = "Select Dataset"
UPLOADDATASETHEADER = "Upload Dataset"
HOMETABHEADERS= [f"{SELECTDATASETHEADER}", f"{UPLOADDATASETHEADER}"]

UPLOADDATASETINFO = "If there is no dataset please open expander below and create dataset."

UPLOADUNIQUEVALUESINFO = "Uploading Unique Values. This process may take a while."

#02_Data_Understanding

DATAUNDERSTANDINGHEADING = "Data Understanding Knowledge"

DUTAB1 = "Input Features"
DUTAB2 = "Feature Volatility"
DUTAB3 = "Data Restrictions"
DUTAB4 = "Feature Sensor Precision"
DUTABS = [DUTAB1, DUTAB2, DUTAB3, DUTAB4]

ERRORNODATASET = "Please upload or choose dataset in Home"
SHOWINFORMATIONEXANDERHEADER = "Show information"

SCALEHEADER = "Scale of Features"
SCALEUPLOAD = "Scale of features uploaded"
SCALEEXPANDER = "Show scale of features"

UNIQUEHEADER = "Unique Feature Values"
UNIQUEUPLOAD = "Unique values uploaded"
UNIQUEEXPANDER = "Show unique values"

VOLATILITYHEADER = """
        **There are no volatility levels stored at the moment!**

        Volatility levels can be defined in the expander below:
        """
VOLATILTIYINPUTHEADER = "Click here to changes volatility of features"
VOLATILTIYCHANGEFORMHEADER = "Change level of volatility for features"
VOLATILITYSUBMITBUTTON = "Submit Volatility Levels"
ERRORSELECTVOLATILITYLELVELFORALLFEATURES = "Please select a volatility level for all features"

VOLATILITYHEADER2 = "**Here you can see the Volatility for each feature**"
VOLATILITYSHOWHEADER = "Show Volatility"
VOLATILITYDELETEBUTTON = "Invalidate current Volatility"
VOLATILITYDELETEBUTTONTOOLTIP = "Old values will be invalidated and new volatility levels can be created"

DATARESTRICTIONHEADER = """
        **Here you can set the Data Restrictions for each feature**
        """

DEFINERESTRICTIONEXPANDER = "Define Data Restrictions for ***{}***"
DATARESTRICTIONRESTOREDEFAULT = "Restore default values providing maximum range for {}"
DATARESTRICTIONLOWER = "Input lower value"
DATARESTRICTIONUPPER = "Input upper value"
DATARESTRICTIONORDINAL = "Select Values for ordinal Value {}"
DATARESTRICTIONNOMINAL = "Select Values for nominal Value {}"
ERRORDATARESTRICTIONUPPERLOWERBOUND = "Lower bound range must be smaller than upper bound."
DATARESTRICTIONCHANGEBUTTON = "Change now"
DATARESTRICTIONCHANGESUCCESS = "Data Restriction for {} saved, please upload when finished."

DATARESTRICTIONDEFINEDEXPANDER = "Defined Data Restriction"
DATARESTRICTIONUPLOADBUTTON = "Upload Data Restrictions"
DATARESTRICTIONUPLOADSUCCESS = "Data Restriction uploaded"

DATARESTRICTIONMARKDOWN = """**Here you can see the Data Restrictions for each feature**"""
DATARESTRICTIONSHOWEXPANDER = "Show current Data Restrictions"
DATARESTRICTIONINVALIDATIONBUTTON = "Invalidate current Data Restrictions"


SENSORPRECISIONMARKDOWN = """**Here you can set the Sensor Precision for each feature**"""
SENSORPRECISONDEFINITIONEXPANDER = "Define sensor precision for {} in percent"
SENSORPRECISIONINPUTTEXT = "Define sensor precision"
SENSORPRECISIONINPUTHELP = "The value was measured with a sensor having the indicated precision."
SENSORPRECISIONSHOWEXPANDER = "Show current Feature Sensor Precision"
SENSORPRECISONUPLOADBUTTON = "Upload Feature Sensor Precision"
SENSORPRECISIONSHOWMARKDOWN = """**Here you can see the current Sensor Precision for each feature:**"""
SENSORPRECISIONINVALIDATIONBUTTON = "Invalidate current Sensor Precision"

#04_Prediction_Model.py

PREDICTIONMODELPAGETITLE = "Prediction Model Selection"

SELECTMODELTEXT = "Select an already uploaded model"
UPLOADMODELTEXT = "Upload a new prediction model"

MODELSELECTBOXLABEL = "Available Models:"

MODELUPLOADERLABEL = "Upload your machine learning model file (saved with pickle)"
MODELUPLOADSUCCESS = "Model uploaded successfully!"


#05_Modeling.py

MODELINGTAB1 = "1. Choose Perturbation Option"
MODELINGTAB2 = "2. Customize and Save Chosen Perturbation Options"

MODELINGSHOWINFORMATIONEXPANDER = "Show information"
MODELINGCHOOSEPERTURBATIONOPTIONHEADER = "Choose suitable Perturbation Option for the features."
MODELINGCHOOSEPERTURBATIONOPTIONDESCRIPTION = "Here you can select which Perturbation Options are suitable for each feature."
MODELINGSHOWPERTURBATIONOPTIONEXPANDER= "Perturbation Options for ***{}***"

MODELINGHIGHVOLATILITYINFO = "Feature has high volatility! Perturbing the feature might be a good idea!"
MODELINGVOLATILITYINFO = "Feature has the volatility level: {}!"
MODELINGNOVOLATILITYINFO = "Currently no volatility level saved! Volatility can indicate features which would pose good candidates for perturbation!"

MODELINGNOCARDINALVALUES = "No Cardinal Values"

MODELINGNOSENSORPRECISION = "No Sensor Precision for {} in Data Understanding step determined. Go to Data Understanding and determine sensor precision for this feature."
MODELINGSENSORPRECISION = "Sensor Precision for this feature: "


MODELINGNOBINS = "No Bin determined for feature {} in Data Preparation step determined. Go to Data Preparation and determine sensor precision for this feature."
MODELINGBINS = "Bins determined for this Perturbation Option: "

MODELINGNOORDINALVALUES = "No Ordinal Values"
MODELINGNONOMINALVALUES = "No Nominal Values"


MODELINGSHOWCHOSENPERTOPTIONEXPANDERLABEL = "Show chosen perturbation options:"
MODELINGSHOWCHOSENPERTOPTIONEXPANDERDESCRIPTION = "Show chosen perturbation options for each feature"
MODELINGPERTOPTIONS = "Perturbation Options:"
MODELINGNOPERTOPS = "If you select perturbation options, they will be shown here"

MODELINGNOINFORMATION = "No Level of Volatility, Data Restrictions, Missing Values, or other information determined"
MODELINGCUSTOMIZEALGO = "#### Customize parameters of {}"

MODELINGPERTLEVELEXPLANATION = "Determines whether the prediction with this perturbation option is allowed to change: Red means thet the prediction for that perturbation option should not change. Orange means that prediction might change. Green means that prediction is expected to change"
MODELINGSELECTPERTLEVEL = "Select Perturbation Level"

MODLEINGNOSENSORPRECISION = "Sensor Precision was not determined in Data Understanding step"
MODELINGSENSORPRECISIONMISSING = "Sensor Precision for this feature should be determined in Data Understanding step."
MODLINGSELECTLOWERBOUND = "Select lower border"
MODLEINGSELECTUPPERBOUND = "Select upper border"
MODELINGLOWERSMALLERTHANUPPER = "Lower border must be smaller than upper border."

MODELINGNOBINDETERMINED = "No information about bins is not determined in Data Understanding Step"
MODELINGDETERMINEBINS = "Binning for this feature should be determined in Data Preparation step."

MODELINGNOPOFORSCALE = "No perturbation options for {} features chosen"

MODELINGSELECTINFORMATIONFORPERTURBATION = "Select the information which was the reason for the perturbation:"
MODELINGCUSTOMIZEPOEXPANDER = "Customize Perturbation Options for Feature {}"


MODELINGSHOWSETTING = "Show all customizations for chosen Perturbation Options"
MODELINGINSERTLABELFORM = "Insert a label for the customized Perturbation Options"
MODLEINGLABELINFO = "This label is used in Deployment to identify this group of perturbation options."
MODELINGUPLOADBUTTONLABEL = "Upload customized Perturbation Options"
MODELINGLABELALREADYEXISTS = "This label already exists! Please choose a different one!"
MODELINGPERTOPSSAVED = "Perturbation Options saved!"
MODELINGPERTOPSERROR = "Error: Could not save Perturbation Options!"

#06_Deployment.py

DEPLOYMENTTAB1 = "1. Select a Group of Predefined Perturbation Options"
DEPLOYMENTTAB2 = "2. Start Perturbing New Cases"

DEPLOYMENTNOUNIQUES = "Couldn't load unique values. If already inserted refresh page."
DEPLOYMENTNOPERTOPTIONS = "There are no perturbation options to select at the moment."
DEPLOYMENTSHOWALLAVAILABLEPOS = "Show all perturbation options saved in the graph"
DEPLOYMENTCHOOSEPOSFORPERT = "Review and refine chosen Perturbation Options"
DEPLOYMENTSELECTGROUP = "Select a group of perturbation options that was predefined in Modeling:"

DEPLOYMENTPOSFORFEATURE = "Perturbation Options for ***{}***"
DEPLOYMENTDIFFERENTPERTLEVELS = "If Perturbation Options differ in Perturbation Level, first one is used for visualization purposes."
DEPLOYMENTANOTHERPOCHOSEN ="Another {} already chosen. First one will be used!"
DEPLOYMENTNOCARDINAL = "No Cardinal Values"
DEPLOYMENTNOORIDINAL = "No Ordinal Values"
DEPLOYMENTNONOMINAL = "No Nominal Values"

DEPLOYMENTSHOWCHOSENPOS = "Show currently chosen Perturbation Option"
DEPLOYMENTSHOWPOSPREFEATURE = "Show chosen Perturbation Option per feature"
DEPLOYMENTSHOWPOEXPANDERLABEL = "Show chosen Perturbation Options"
DEPLOYMENTSHOWRESTRITIONVALUES = "Show current Data Restrictions"
DEPLOYMENTDATARESTRICTIONHEADER = "Data Restrictions:"
DEPLOYMENTTABINSERT = "Insert new perturbation cases"
DEPLOYMENTTABDELETE = "Delete existing perturbation cases"

DEPLOYMENTINSERTNEW = "Insert a new prediction case based on input fields for all features"
DEPLOYMENTUPLOADNEW = "Upload new Data using a csv file"
DEPLOYMENTSELECTVALUE = "Select a Value for {}"
DEPLOYMENTSUBMITNEWDATABUTTONLABEL = "Submit new prediction case!"
DEPLOYMENTCASEADDED = "New case was added"
DEPLOYMENTUPLAODCSV = "Upload a csv file containing new cases."

DEPLOYMENTNOCASES = "No cases available"
DEPLOYMENTSELECTROWTODELETE = "Select a rownumber that should be deleted:"
DEPLOYMENTDELETEROWWITHINDEX = "Delete row with index {}"
DEPLOYMENTDELETETABLEBUTTONLABEL = "Delete whole Table"


DEPLOYMENTSELECTROWSOFCASES = "Available perturbation cases:"
DEPLOYMENTSELECTROWS = "Select one row by clicking on them. Each selected row represents a perturbation case and is perturbed with chosen perturbation options."
DEPLOYMENTSELECTCASESTOCONTINUEINFO = "Select a case to continue"

DEPLOYMENTSHOWSELECTEDCASES = "Show selected cases"
DEPLOYMENTSHOWSELECTEDPOS = "Show chosen Perturbation options"

DEPLOYMENTLABELFORCASE = "Label for the assessment of selected cases"
DEPLOYMENTLABELHELP = "Insert a name for the perturbation Assessment"

DEPLOYMENTBUTTONSTARTPERTURBING = "Start perturbing!"
DEPLOYMENTSHOWALLPERTURBEDVALUES = "Show all perturbed values"

DEPLOYMENTRETRIEVERESULTS = "Get perturbation results for perturbed **case: {}**"
DEPLOYMENTPERFORMANCEWARINING = "There are more than 20.000 perturbed cases, this could lead to performance issues. {} perturbed cases are generated, if performance issues occur. Please select fewer perturbation options."

DEPLOYMENTNOCHANGEDPREDICTION = "No prediction for a perturebd case changed for case {}"
DEPLOYMENTSHOWCHANGEDCASES = "Show only perturebd test cases with changed prediction:"
DEPLOYMENTDOWNLOADCASESBUTTON = "Download CSV file for prediction case: {}"



