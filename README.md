# dig-ilp-rankings

Formulates the ILP model using Gurobi with variables as the extractions. Finally selects the most possible extractions.

## Running the ILP Rankings

* Load Properties File:

```
properties = json.load(codecs.open('properties_non_cluster.json', 'r', 'utf-8'))
```

* Init ILP Extractions With Dictionaries

```
ilp_formulation = ilp_extractions.ILPFormulation({
    'city-country':properties['city_country'],
    'city-state':properties['city_state'],
    'state-country': properties['state_country'],
    'city_alt': properties['city_alt'],
    'city_all': properties['city_all']
    }
```

* Run ILP over knowledge_graph

```
ilp_formulation.formulate_ILP(knowledge_graph)
```

* The ILP code will modify the knowledge_graph object passed



