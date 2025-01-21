from rdflib import Graph

# Load the RDF file
g = Graph()
g.parse("../Knowledge-Graph-Reasoning-Challenge/DataSet/CompleteData/RDF/add_places.ttl", format="ttl")

# Define the SPARQL query to extract records with :from relationship
query = """
PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
SELECT ?subject ?object
WHERE {
    {
        ?subject :from ?object .
    }
    UNION
    {
        ?subject :to ?object .
    }
    UNION
    {
        ?subject :place ?object .
    }
}
"""

# Execute the query
results = g.query(query)

# Extract the unique room names from the URI
unique_rooms = set()

for row in results:
    # Add the room name to the set
    unique_rooms.add(str(row.object).split('/')[-1].lower())



# Print the unique room names
print(unique_rooms)
# Create a dictionary to store rooms by scene id
rooms_by_scene = {}

# Populate the dictionary
for room in unique_rooms:
    scene_id = int(room.split('_scene')[-1])
    if scene_id not in rooms_by_scene:
        rooms_by_scene[scene_id] = []
    rooms_by_scene[scene_id].append(room)

# Print the dictionary
for scene_id in sorted(rooms_by_scene.keys()):
    print(f"Scene ID: {scene_id}")
    for room in rooms_by_scene[scene_id]:
        print(f"  Room: {room}")