PREFIX = """PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rprov: <http://www.dke.uni-linz.ac.at/rprov#>
            PREFIX prov:  <http://www.w3.org/ns/prov#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX instance:<http://www.semanticweb.org/dke/ontologies#>"""

insertNewActivity = PREFIX + """
                INSERT DATA {{
                    <urn:uuid:{}> rdf:type rprov:{}, owl:NamedIndividual;
                    rdfs:label "{}"@en;
                    prov:endedAtTime '{}'^^xsd:dateTime.
                }}
"""

insertNewFeatureEntity = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:Feature, owl:NamedIndividual;
                    rdfs:label "{}"@en;
                    rprov:wasGeneratedByDUA <urn:uuid:{}>;
                }}
"""

insertNewEntityToFeature = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:{}, owl:NamedIndividual;
                    rprov:{} {};
                    rdfs:label "{}"@en;
                    rprov:toFeature <{}>;
                    rprov:wasGeneratedByDUA  <urn:uuid:{}>;
                    prov:generatedAtTime '{}'^^xsd:dateTime.
                }}
"""

insertNewBinnedValuesToFeature = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:RangeOfBinnedFeature, owl:NamedIndividual;
                    rprov:RangeOfBinnedFeature <urn:uuid:{}>;
                    rdfs:label "{}"@en;
                    rprov:toFeature <{}>;
                    rprov:wasGeneratedByDPA  <urn:uuid:{}>;
                    prov:generatedAtTime '{}'^^xsd:dateTime.
                }}
"""

insertNewMissingValuesEntityToFeature = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:HandlingOfMissingValues, owl:NamedIndividual;
                    rdfs:label "Handling of missing values for {}"@en;
                    rdfs:comment "{}";
                    rprov:toFeature <{}>;
                    rprov:wasGeneratedByDPA  <urn:uuid:{}>;
                    prov:generatedAtTime '{}'^^xsd:dateTime;
                }}
"""

insertUniqueValues = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rdf:{}, owl:NamedIndividual;
                    rdf:_{}  '{}';
                }}
"""

insertPerturbationOption = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:{}, owl:NamedIndividual;
                    rprov:perturbedFeature <{}>;
                    rprov:generationAlgorithm "{}";
                    rprov:assignedPerturbationSettings "{}";
                    rprov:assignedPerturbationLevel "{}";
                    rprov:modelingEntityWasDerivedFrom <{}>;
                    rprov:wasGeneratedByMA  <urn:uuid:{}>;
                    rdfs:label "{}"@en.
                }}
"""

insertClassificationCase = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:ClassificationCase, owl:NamedIndividual;
                    rdfs:label "{}"@en ;
                    rprov:values "{}"@en;
                    rprov:wasAssignedToDeploymentEntity <urn:uuid:{}>;
                    prov:endedAtTime '{}'^^xsd:dateTime.
                }}
"""

insertPerturbationApproach = PREFIX +"""
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:PerturbationApproach, owl:NamedIndividual;
                    rprov:wasGeneratedByBUA <urn:uuid:{}>;
                    prov:generatedAtTime '{}'^^xsd:dateTime.
                }}
"""

insertPerturbationAssessment = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rprov:PerturbationAssessment, owl:NamedIndividual;
                    rdfs:label "{}"@en ;
                    rprov:deploymentEntityWasDerivedFrom <{}>;
                    rprov:perturbedTestCase "Saved as csv with name: {}";
                    rprov:wasGeneratedByDA  <urn:uuid:{}>;
                    rprov:pertModeValue "{}";
                    prov:generatedAtTime '{}'^^xsd:dateTime.
                }}
"""

insertSequenceLine = PREFIX + """
                INSERT DATA {{<urn:uuid:{}> rdf:type rdf:Seq, owl:NamedIndividual; rdf:_{}  '{}';
                }}
"""

getUUIDForFeatureLabel = PREFIX + """
                SELECT ?featureUUID WHERE {{?featureUUID rdf:type rprov:Feature. ?featureUUID rdfs:label "{}"@en}}
"""

getAllLabelsAndUUIDSForFeatures = PREFIX + """
                SELECT ?featureID ?featureName WHERE {{
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label ?featureName.
                }}
"""

getAllUniqueValues = PREFIX + """    
                SELECT ?label ?containerMembershipProperty ?item WHERE {{
                    ?sub rprov:uniqueValues ?container.
                    ?container ?containerMembershipProperty ?item.
                    ?sub rprov:toFeature ?feature.
                    ?feature rdfs:label ?label.
                    FILTER(?containerMembershipProperty!= rdf:type)
                }}
"""

getAllDataRestrictions = PREFIX + """
                SELECT ?sub ?seq ?item ?label ?featureName ?seq ?containerMembershipProperty WHERE {{
                    ?sub rdf:type rprov:DeterminationOfDataRestriction.
                    ?seq rprov:wasGeneratedByDUA ?sub.
                    ?seq rdfs:label ?label.
                    ?seq rprov:toFeature ?feature.
                    ?feature rdfs:label ?featureName.
                    ?seq rprov:restriction ?list.
                    ?list ?containerMembershipProperty ?item.
                    FILTER(?containerMembershipProperty!= rdf:type).
                    FILTER NOT EXISTS{{?seq prov:invalidatedAtTime ?time}}
                }}
"""

getInformationToFeature = PREFIX + """
                SELECT ?featureID ?rprov ?DataUnderstandingEntityID ?label ?DUA WHERE{{
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label "{}"@en.
                    ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    ?DataUnderstandingEntityID rdf:type ?rprov.
                    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA|rprov:wasGeneratedByDPA|rprov:wasGeneratedByBUA ?DUA.   
                    ?DataUnderstandingEntityID rdfs:label ?label.
                    FILTER(?rprov!=owl:NamedIndividual)
                    FILTER(?rprov!=rprov:ScaleOfFeature)  
                    FILTER(?rprov!=rprov:SensorPrecisionOfFeature)  
                    FILTER(?rprov!=rprov:RangeOfBinnedFeature)
                    FILTER(?rprov!=rprov:UniqueValuesOfFeature)
                    FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}

                }}
"""

getLabelForScaleOfFeature = PREFIX + """
                SELECT ?label ?DataUnderstandingEntityID WHERE{{
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label "{}"@en .
                    ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    ?DataUnderstandingEntityID rdf:type rprov:ScaleOfFeature.
                    ?DataUnderstandingEntityID rdfs:label ?label.
                    FILTER NOT EXISTS{{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}}
                }}
"""

getAllPerturbationOptionLabels = PREFIX + """ 
                SELECT ?PerturbationOptionLabel WHERE{{
    					?DataUnderstandingEntityID rdf:type rprov:PerturbationOption.
    					?DataUnderstandingEntityID rdfs:label ?PerturbationOptionLabel.
                }}
"""

getAllFeatureScales = PREFIX + """
                SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?scale ?DUA {
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label ?featureName.
                    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
                    ?DataUnderstandingEntityID rprov:scale ?scale.
                    ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
                    FILTER NOT EXISTS{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}
                }
"""

getAllVolatilityLevels = PREFIX + """
                SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?volatility ?DUA WHERE{
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label ?featureName.
                    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
                    ?DataUnderstandingEntityID rprov:volatilityLevel ?volatility.
                    ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
                    FILTER NOT EXISTS{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}
                }
"""

getAllSensorPrecision = PREFIX + """
                SELECT ?featureID ?featureName ?DataUnderstandingEntityID ?sensorPrecisionLevel ?DUA {
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label ?featureName.
                    ?DataUnderstandingEntityID rdf:type owl:NamedIndividual.
                    ?DataUnderstandingEntityID rprov:sensorPrecisionLevel ?sensorPrecisionLevel.
                    ?DataUnderstandingEntityID rprov:toFeature ?featureID.
                    ?DataUnderstandingEntityID rprov:wasGeneratedByDUA ?DUA.
                    FILTER NOT EXISTS{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}
                }
"""


getAllMissingValues = PREFIX + """
                SELECT ?featureID ?featureName ?DataPreparationEntityID ?MissingValues ?DPA {
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label ?featureName.
                    ?DataPreparationEntityID rdf:type owl:NamedIndividual.
                    ?DataPreparationEntityID rdfs:comment ?MissingValues.
                    ?DataPreparationEntityID rprov:toFeature ?featureID.
                    ?DataPreparationEntityID rprov:wasGeneratedByDPA ?DPA.
                    FILTER NOT EXISTS{?DataPreparationEntityID prov:invalidatedAtTime ?time}
                }
"""

getApproachForGraph = PREFIX + """
                SELECT ?rprov ?DataUnderstandingEntityID ?BUA WHERE{
                    ?DataUnderstandingEntityID rdf:type ?rprov.
                    ?DataUnderstandingEntityID rprov:wasGeneratedByBUA ?BUA.
                    FILTER(?rprov!=owl:NamedIndividual).
                    FILTER(?rprov!=owl:Class).
                    FILTER NOT EXISTS{?DataUnderstandingEntityID prov:invalidatedAtTime ?time}
                }
"""

getAllBinValuesSeq = PREFIX + """
                SELECT ?DPA ?DPE ?feature ?label ?containerMembershipProperty ?item WHERE {
                    ?DPE rprov:RangeOfBinnedFeature ?container.
                    ?DPE rprov:wasGeneratedByDPA ?DPA.
                    ?container ?containerMembershipProperty ?item.
                    ?DPE rprov:toFeature ?feature.
                    ?feature rdfs:label ?label.
                    FILTER(?containerMembershipProperty!= rdf:type).
                    FILTER NOT EXISTS{?DPE prov:invalidatedAtTime ?time}.
                }
"""

getDataRestrictionSeq = PREFIX + """
                SELECT ?DUA ?label ?containerMembershipProperty ?item WHERE {{
                    ?DUA rprov:restriction ?container.
                    ?DUA rprov:wasGeneratedByDUA <{}>.
                    ?container a rdf:Seq .
                    ?container ?containerMembershipProperty ?item.
                    ?DUA rprov:toFeature ?feature.
                    ?feature rdfs:label ?label.
                    FILTER(?containerMembershipProperty!= rdf:type).
                    FILTER NOT EXISTS{{?container prov:invalidatedAtTime ?time}}
                }}
"""

getDataRestrictionSeqDeployment = PREFIX +"""
                SELECT ?dataRestrictionEntity ?feature ?label ?seq ?item WHERE {{
                    <{}> rprov:modelingEntityWasDerivedFrom ?dataRestrictionEntity.
                    ?dataRestrictionEntity rdf:type rprov:DataRestriction.
                    ?dataRestrictionEntity rprov:restriction ?seq.
                    ?seq a rdf:Seq .
                    ?seq ?containerMembershipProperty ?item.
                    ?dataRestrictionEntity rprov:toFeature <{}>.
                    ?dataRestrictionEntity rprov:toFeature ?feature.
                    ?feature rdfs:label ?label.
                    FILTER(?containerMembershipProperty!= rdf:type)
    }}
"""

getAllPerturbationOptions = PREFIX +"""    
                SELECT ?featureID ?featureName ?PerturbationOptionID ?generationAlgo ?settings ?level ?label ?DataRestrictionEntities ?MA {
                    ?featureID rdf:type rprov:Feature .
                    ?featureID rdfs:label ?featureName .
                    ?PerturbationOptionID rdf:type owl:NamedIndividual .
                    ?PerturbationOptionID rprov:perturbedFeature ?featureID .
                    ?PerturbationOptionID rprov:generationAlgorithm ?generationAlgo .
                    ?PerturbationOptionID rprov:assignedPerturbationSettings ?settings .
                    ?PerturbationOptionID rprov:assignedPerturbationLevel ?level .
                    ?PerturbationOptionID rdfs:label ?label .
                    ?PerturbationOptionID rprov:wasGeneratedByMA ?MA
                    OPTIONAL {
                        ?PerturbationOptionID rprov:modelingEntityWasDerivedFrom ?DataRestrictionEntities .
                        ?DataRestrictionEntities rdf:type rprov:DataRestriction .
                    }
                }
"""

getUUIDForLabelAndToFeature = PREFIX + """
                 SELECT ?entitiyUUID WHERE{{
                    ?entitiyUUID rdfs:label "{}"@en .
                    ?entitiyUUID rprov:toFeature <{}> .
                    FILTER NOT EXISTS{{?entitiyUUID prov:invalidatedAtTime ?time}}
                 }}
"""


invalidateWasGeneratedBy = PREFIX +"""    
                INSERT {{?DUE prov:invalidatedAtTime '{}'^^xsd:dateTime;}}
                    WHERE {{?DUE rprov:wasGeneratedBy{} <{}>
                }}
"""
