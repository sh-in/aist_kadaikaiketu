from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
from pathlib import Path

# eventの数の取得
def do_sparql_query_to_get_events(PROJECT_PATH, activity, scene):
    g = rdflib.Graph()
    g.parse(PROJECT_PATH / Path(f"DataSet/PartiallyMissingData/RDF/222/{activity}_{scene}-222.ttl"))
    knows_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select (count(?event) AS ?count) WHERE {{
        ex:{activity.lower()}_{scene} :hasEvent ?event .
    }}
    """
    qres = g.query(knows_query)
    count = 0
    for row in qres:
        count = str(row["count"])
    return count

# 最初の場所を取得
def do_sparql_query_to_get_first_place(PROJECT_PATH, activity, scene, event_num):
    g = rdflib.Graph()
    g.parse(PROJECT_PATH / Path(f"DataSet/PartiallyMissingData/RDF/222/{activity}_{scene}-222.ttl"))
    knows_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * WHERE {{
        ex:event{event_num}_{activity.lower()}_{scene} (:place|:from) ?room .
        ?room rdfs:label ?name .
    }}
    """
    qres = g.query(knows_query)
    for row in qres:
        place = f"{row.name}"
    try:
        return place
    except:
        return None

# 最後の場所を取得
def do_sparql_query_to_get_last_place(PROJECT_PATH, activity, scene, event_num):
    g = rdflib.Graph()
    g.parse(PROJECT_PATH / Path(f"DataSet/PartiallyMissingData/RDF/222/{activity}_{scene}-222.ttl"))
    knows_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * WHERE {{
        ex:event{event_num}_{activity.lower()}_{scene} (:to|:place) ?room .
        ?room rdfs:label ?name .
    }}
    """
    qres = g.query(knows_query)
    for row in qres:
        place = f"{row.name}"
    try:
        return place
    except:
        return None

# actionの取得
def do_sparql_query_to_get_action(PROJECT_PATH, activity, scene, event_num):
    g = rdflib.Graph()
    g.parse(PROJECT_PATH / Path(f"DataSet/PartiallyMissingData/RDF/222/{activity}_{scene}-222.ttl"))
    knows_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * WHERE {{
        ex:event{event_num}_{activity.lower()}_{scene} :action ?action .
    }}
    """
    qres = g.query(knows_query)
    for row in qres:
        action = f"{row.action}"
    try:
        return action, action.split("/")[-1]
    except:
        return None
    
# 時間の取得
def do_sparql_query_to_get_time(PROJECT_PATH, activity, scene, event_num):
    g = rdflib.Graph()
    g.parse(PROJECT_PATH / Path(f"DataSet/PartiallyMissingData/RDF/222/{activity}_{scene}-222.ttl"))
    knows_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX time: <http://www.w3.org/2006/time#>
    select * WHERE {{
        ex:event{event_num}_{activity.lower()}_{scene} :time ?time .
        ?time time:numericDuration ?duration.
    }}
    """
    qres = g.query(knows_query)
    for row in qres:
        duration = f"{row.duration}"
    try:
        return duration
    except:
        return None