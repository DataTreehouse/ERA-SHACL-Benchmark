#%%
import os
import csv
import rdflib
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import XSD, RDF, RDFS, OWL
from rdflib import Namespace
from io import BytesIO
import pandas as pd
import rdflib.compare
from pyshacl import validate

def verify_report(test_dir, report_dir):
    g = rdflib.Graph()
    with open(test_dir, "r", encoding="utf-8") as file: # f"../tests/core/property/datatype-era-002.ttl"
            g.parse(data=file.read(), format="ttl")

    h = rdflib.Graph()
    with open(report_dir, "r", encoding="utf-8") as file: # f"../results/jena/reports/core/property/datatype-era-002-report.ttl"
            h.parse(data=file.read(), format="ttl")

    query = """
    CONSTRUCT {
            ?report rdf:type sh:ValidationReport;
                sh:conforms ?conformance;
                sh:result ?result.
            ?result rdf:type sh:ValidationResult;
                    sh:focusNode ?node;
                    sh:resultPath ?path;
                    sh:resultSeverity ?violation;
                    sh:sourceConstraintComponent ?constraintComponent;
                    sh:sourceShape ?sourceShape;
                    sh:value ?value.
    }
    WHERE {
            ?report rdf:type sh:ValidationReport;
                sh:conforms ?conformance;
                sh:result ?result.
            ?result rdf:type sh:ValidationResult;
                    sh:focusNode ?node;
                    sh:resultSeverity ?violation;
                    sh:sourceConstraintComponent ?constraintComponent;
                    sh:sourceShape ?sourceShape.
            OPTIONAL {?result sh:resultMessage ?message}
            OPTIONAL {?result sh:value ?value}
            OPTIONAL {?result sh:resultPath ?path}
    }""" 
    g_c = g.query(query)
    h_c = h.query(query)

    iso1 = rdflib.compare.to_isomorphic(g_c.graph)
    iso2 = rdflib.compare.to_isomorphic(h_c.graph)
    in_both, in_first, in_second = rdflib.compare.graph_diff(iso1, iso2)
    return iso1 == iso2, in_first.serialize(format="turtle"), in_second.serialize(format="turtle")

# verify_report(f"../tests/core/property/maxInclusive-era-001.ttl", f"../results/maplib/reports/core/property/maxInclusive-era-001-report.ttl")
# %%
for engine_name in ['maplib', 'jena', 'topbraid', 'rdf4j', 'rdfunit', 'dotnet_rdf', 'pyshacl', 'corese' ]:

    EARL = Namespace("http://www.w3.org/ns/earl#")
    DOAP = Namespace("http://usefulinc.com/ns/doap#")

    earl = Graph()
    earl.bind("xsd", XSD)
    earl.bind("rdf", RDF)
    earl.bind("rdfs", RDFS)
    earl.bind("owl", OWL)
    earl.bind("earl", EARL)

    engine = URIRef(f"http://{engine_name.lower()}-engine.uri/era/shacl/benchmark/")
    earl.add((engine, RDF.type, EARL.Software))
    earl.add((engine, RDF.type, EARL.TestSubject))
    earl.add((engine, DOAP.name, Literal(engine_name)))

    for root, dirs, files in os.walk(f"../results/{engine_name}"):
        for file in files:
            if "reports" in root and file.endswith("-report.ttl") and "old" not in root:
                report_dir = root + "/" + file
                test_dir = "../tests" + root.split("reports")[1]+"/"+file.replace("-report","")
                try:             
                    verification, in_test, in_report = verify_report(test_dir,report_dir)
                    if verification:
                        outcome = EARL.passed
                    else:
                        outcome = EARL.cantTell            
                except:
                    verification = "Incomplete"
                    in_test = "Unknown"
                    in_report = "Unknown"
                    outcome = EARL.cantTell            

                # with open("./verification.csv", "a", newline="", encoding="utf-8") as csvfile:
                    # writer = csv.writer(csvfile, delimiter="|")
                    # writer.writerow([report_dir, verification ])

                test = URIRef(f"http://github.com/alexisimo/ERA-SHACL-Benchmark/{test_dir.split('../')[1]}")
                test_assertion = BNode()  # a GUID is generated
                test_result = BNode()


                earl.add((test_assertion, RDF.type, EARL.Assertion))
                earl.add((test_assertion, EARL.subject, engine))
                earl.add((test_assertion, EARL.test, test))
                earl.add((test_assertion, EARL.result, test_result))

                earl.add((test_result, RDF.type, EARL.TestResult))
                earl.add((test_result, EARL.mode, EARL.automatic))
                earl.add((test_result, EARL.outcome, outcome))

    earl.serialize(destination=f"../results/{engine_name}/earl.ttl")
