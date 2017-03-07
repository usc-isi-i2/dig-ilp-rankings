# Formulate the extractions as Integer Linear Problem

from gurobipy import *
import codecs
import json

TITLE_WEIGHT = 1.0
TEXT_WEIGHT = 0.5
NUMBER_OF_EXTRACTIONS_OF_A_TYPE = 1
CITY_COUNTRY_DICTIONARY = 'resources/city_country_dict_15000.json'
CITY_STATE_DICTIONARY = 'resources/city_state_dict.json'
STATE_COUNTRY_DICTIONARY = 'resources/state_country_dict.json'
CITY_ALL_DICTIONARY = 'resources/city_dict_15000.json'
CITY_ALT_DICTIONARY = 'resources/city_dict_alt_15000.json'

tokens_from_text = [
      {
        'type': 'normal',
        'value': 'seattle',
        'semantic_type': [
        {
            'length': 1,
            'type': 'city',
            'probability': 0.3,
            'offset': 0
        }
        ]
      },
      {
        'type': 'break',
        'value': '\n'
      },
      {
        'type': 'normal',
        'value': 'colorado',
        'semantic_type': [
          {
            'length': 1,
            'type': 'city',
            'probability': 0.1,
            'offset': 0
          }
        ]
      },
      {
        'type': 'normal',
        'value': 'charlotte',
        'semantic_type': [
          {
            'length': 1,
            'type': 'city',
            'probability': 0.2,
            'offset': 0
          },
          {
            'length': 1,
            'type': 'name',
            'probability': 0.5,
            'offset': 0
          }
        ]
      },
      {
        'type': 'break',
        'value': '\n'
      },
      {
        'type': 'normal',
        'value': 'colorado',
        'semantic_type': [
          {
            'length': 1,
            'type': 'city',
            'probability': 1.0,
            'offset': 0
          }
        ]
      }
    ]

tokens_from_title = [
{
'type': 'normal',
'value': 'seattle',
'semantic_type': [
{
    'length': 1,
    'type': 'city',
    'probability': 0.1,
    'offset': 0
}
]
},
{
'type': 'break',
'value': '\n'
},
{
'type': 'normal',
'value': 'colorado',
'semantic_type': [
  {
    'length': 1,
    'type': 'city',
    'probability': 1.0,
    'offset': 0
  }
]
},
{
'type': 'break',
'value': '\n'
},
{
'type': 'normal',
'value': 'colorado',
'semantic_type': [
  {
    'length': 1,
    'type': 'city',
    'probability': 1.0,
    'offset': 0
  }
]
},
{
'type':'normal',
'value': 'kansas',
'semantic_type': [
    {
        'length': 2,
        'type':'city',
        'probability': 0.5,
        'offset': 0
    }
]
},
{
'type':'normal',
'value': 'city',
'semantic_type': [
    {
        'type':'city',
        'offset': 1
    }
]
},
{
'type':'normal',
'value': 'new',
'semantic_type': [
    {
        'length': 3,
        'type':'city',
        'probability': 0.8,
        'offset': 0
    }
]
},
{
'type':'normal',
'value': 'york',
'semantic_type': [
    {
        'type':'city',
        'offset': 1
    }
]
},
{
'type':'normal',
'value': 'city',
'semantic_type': [
    {
        'type':'city',
        'offset': 2
    }
]
},
{
'type':'normal',
'value': 'united',
'semantic_type': [
    {
        'type':'country',
        'offset': 0,
        'length': 2
    }
]
},
{
'type':'normal',
'value': 'states',
'semantic_type': [
    {
        'type':'country',
        'offset': 1
    }
]
},
{
'type':'normal',
'value': 'italy',
'semantic_type': [
    {
        'type':'country',
        'offset': 0,
        'length': 1,
    }
]
},
{
'type':'normal',
'value': 'brazil',
'semantic_type': [
    {
        'type':'country',
        'offset': 0,
        'length': 1,
    }
]
}
]

tokens_input = [
{
    "tokens":tokens_from_text,
    "source":"text",
    "weight":TEXT_WEIGHT
}
,
{
    "tokens":tokens_from_title,
    "source":"title",
    "weight":TITLE_WEIGHT
}
]

coupled_constraints = [
{
    "from":"city",
    "to":"country",
    "dictionary_file":'city-country',
    "from_tokens":set(),
    "to_tokens":set()
},
{
    "from":"city",
    "to":"state",
    "dictionary_file":'city-state',
    "from_tokens":set(),
    "to_tokens":set()
},
{
    "from":"state",
    "to":"country",
    "dictionary_file":'state-country',
    "from_tokens":set(),
    "to_tokens":set()
}
]

STATE_PLACEHOLDER = 'STATE_UNKNOWN'
GENERATED_SEMANTIC_SEPARATOR = '__'
COMBINED_DICTIONARY = 'city_alt'
POPULATION_FACTOR = 15000000.0

# formulate_ILP(tokens_input, coupled_constraints) 

class ILPFormulation():

    def __init__(self, dictionary_files):
        self.dictionaries = dict()
        for key, file in dictionary_files.iteritems():
            self.dictionaries[key] = self.get_dict(file)
        self.coupled_constraints = coupled_constraints

    def get_dict(self, filename):
        dictionary = dict()
        print 'Reading the Dictionary... ',
        print filename 
        with codecs.open(filename, 'r', 'utf-8') as f:
            for line in f:
                dictionary = json.loads(line)
        return dictionary

    def add_coupled_constraints_to_dict(self, token_semantictype_weight_dict, token_semantictype_index_dict):
        # Handling the coupled constraints by making new entries for them in the dictionary
        for constraint in self.coupled_constraints:
            constraint['from_tokens'] = set()
            constraint['to_tokens'] = set()

            for (token, semantic_type, extra_info) in token_semantictype_weight_dict:
                if(semantic_type == constraint['from']):
                    constraint['from_tokens'].add(token)
                    to_tokens_for_from_token = None

                    # Checking if it a city and in the combined dictionary
                    if(constraint['from'] == 'city' and token in self.dictionaries[COMBINED_DICTIONARY]):
                        if(constraint['to'] == 'country'):
                            # Doing this once for a city, when the to constrain is country and not state
                            city_objs = self.dictionaries[COMBINED_DICTIONARY][token]
                            to_tokens_for_from_token = dict()
                            for city_obj in city_objs:

                                to_token = city_obj['country']
                                token_semantictype_weight_dict[token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + constraint['to'], to_token] = city_obj['population']/POPULATION_FACTOR # Added weight as population of the city in country
                                token_semantictype_index_dict[token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + constraint['to'], to_token] = token_semantictype_index_dict[token, semantic_type, extra_info]
                                if((to_token, constraint['to'], '') not in token_semantictype_weight_dict):
                                    # This is a new to_token (ex. country) that is introduced because of the from_token (ex. cities)
                                    token_semantictype_weight_dict[to_token, constraint['to'],''] = 0 #Adding weight as 0 so that it does not come in the objective function
                                    token_semantictype_index_dict[to_token, constraint['to'],''] = token_semantictype_index_dict[token, semantic_type, extra_info]
                                    constraint['to_tokens'].add(to_token)

                                to_token = city_obj['state']
                                if(to_token):
                                    # Doing the same for the state coming from the common dictionary
                                    token_semantictype_weight_dict[token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + 'state', to_token] = city_obj['population']/POPULATION_FACTOR # Added weight as population of the city in country
                                    token_semantictype_index_dict[token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + 'state', to_token] = token_semantictype_index_dict[token, semantic_type, extra_info]
                                    if((to_token, 'state', '') not in token_semantictype_weight_dict):
                                        # This is a new to_token (ex. country) that is introduced because of the from_token (ex. cities)
                                        token_semantictype_weight_dict[to_token, 'state',''] = 0 #Adding weight as 0 so that it does not come in the objective function
                                        token_semantictype_index_dict[to_token, 'state',''] = token_semantictype_index_dict[token, semantic_type, extra_info]
                                        self.coupled_constraints[1]['to_tokens'].add(to_token)


                    else:
                        # The case where from is not city or city is not in the combined dictionary(fallback)
                        if(token in constraint['dictionary']):
                            to_tokens_for_from_token = set(constraint['dictionary'][token])
                    
                        if(not to_tokens_for_from_token):
                            if(constraint['to'] == 'state' and constraint['from'] == 'city'):
                                # There is no corresponding state for the city
                                # Adding a placeholder state
                                to_tokens_for_from_token = set([STATE_PLACEHOLDER])
                                # Need to add the country for placeholder state as well
                                if(token in self.coupled_constraints[0]['dictionary']):
                                    # Token is in City Country dictionary
                                    countries_for_the_city = set(self.coupled_constraints[0]['dictionary'][token])
                                    for country in countries_for_the_city:
                                        # print "Added "+STATE_PLACEHOLDER+" "+country
                                        token_semantictype_weight_dict[STATE_PLACEHOLDER, 'state' + GENERATED_SEMANTIC_SEPARATOR + 'country', country] = 0 # Added weight as 0 so that it does not come in the objective function
                                        token_semantictype_index_dict[STATE_PLACEHOLDER, 'state' + GENERATED_SEMANTIC_SEPARATOR + 'country', country] = token_semantictype_index_dict[token, semantic_type, extra_info]


                        if(to_tokens_for_from_token):
                            for to_token in to_tokens_for_from_token:
                                # print "Added "+token+" "+to_token
                                # Adding to_token (ex. country) in the extra_info field
                                token_semantictype_weight_dict[token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + constraint['to'], to_token] = 0 # Added weight as 0 so that it does not come in the objective function
                                token_semantictype_index_dict[token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + constraint['to'], to_token] = token_semantictype_index_dict[token, semantic_type, extra_info]
                                if((to_token, constraint['to'], '') not in token_semantictype_weight_dict):
                                    # This is a new to_token (ex. country) that is introduced because of the from_token (ex. cities)
                                    token_semantictype_weight_dict[to_token, constraint['to'],''] = 0 #Adding weight as 0 so that it does not come in the objective function
                                    token_semantictype_index_dict[to_token, constraint['to'],''] = token_semantictype_index_dict[token, semantic_type, extra_info]
                                    constraint['to_tokens'].add(to_token)

                if(semantic_type == constraint['to']):
                    constraint['to_tokens'].add(token)

    def combine_values(self, old_value, new_value, logic = 'max'):
        #Logic for combining the values
        #TAKING MAX
        if(logic == 'max'):
            return max(old_value, new_value)
        
        #TAKING MIN
        if(logic == 'min'):
            return min(old_value, new_value)
        
        #TAKING SUM
        if(logic == 'sum'):
            return old_value + new_value

    def update_weights_dictionary(self, token_semantictype_source_weight_dict, token_semantictype_source_index_dict, tokens_with_semantic_types, source, input_index, weight_of_extraction = 1.0):
        """
        :param tokens_with_semantic_types: list of tokens having semantic_types extracted with probabilities
        :param weight_of_extraction: variable to capture the relative weight of title, text or other sources for tokens
        """

        print "Called with " + source
        for index, token in enumerate(tokens_with_semantic_types):
            if('semantic_type' in token):
                value = token['value']
                semantic_types = token['semantic_type']
                for semantic_type in semantic_types:
                    semantic_type_name = semantic_type['type']
                    semantic_probability = semantic_type.get('probability')
                    offset = semantic_type.get('offset')
                    index_value = str(input_index)+":"+str(index)
                    if(not semantic_probability):
                        semantic_probability = 1

                    if(not offset):
                        offset = 0

                    if(offset == 0):
                        length = semantic_type['length']
                        if((value, semantic_type_name, source, length) not in token_semantictype_source_weight_dict):
                            #This value of this length with semantic type is occuring for the 1st time
                            token_semantictype_source_weight_dict[(value, semantic_type_name, source, length)] = semantic_probability*weight_of_extraction
                            token_semantictype_source_index_dict[(value, semantic_type_name, source, length)] = index_value
                        else:
                            #This is a duplicate occurence in the same group (ie. title, text)
                            old_value = token_semantictype_source_weight_dict[(value, semantic_type_name, source, length)]
                            token_semantictype_source_weight_dict[(value, semantic_type_name, source, length)] = self.combine_values(old_value, semantic_probability*weight_of_extraction)
                            old_value = token_semantictype_source_index_dict[(value, semantic_type_name, source, length)]
                            token_semantictype_source_index_dict[(value, semantic_type_name, source, length)] = old_value+";"+index_value

                    else:
                        #This is a multiword token and is currently at the offset th token from the 1st token
                        first_token_value = tokens_with_semantic_types[index - offset]['value']
                        first_token_all_semantic_types = tokens_with_semantic_types[index - offset]['semantic_type']
                        while(offset > 1):
                            offset-=1
                            first_token_value += " " + tokens_with_semantic_types[index - offset]['value']


                        possible_lengths = list()
                        for first_token_semantic_types in first_token_all_semantic_types:
                            if(first_token_semantic_types['type'] == semantic_type_name):
                                if 'length' in first_token_semantic_types:
                                    possible_lengths.append(first_token_semantic_types['length'])

                        correct_length = possible_lengths[0]
                        for possible_length in possible_lengths:
                            if((first_token_value, semantic_type_name, source, possible_length) in token_semantictype_source_weight_dict):
                                correct_length = possible_length

                        old_value = token_semantictype_source_weight_dict[(first_token_value, semantic_type_name, source, correct_length)]
                        old_value_index = token_semantictype_source_index_dict[(first_token_value, semantic_type_name, source, correct_length)]
                        # Update Probabilities (Not Required since will have the same probabilities)
                        # token_semantictype_source_index_weight_dict[(first_token_value, semantic_type_name, source)] = combine_values(old_value, semantic_probability*weight_of_extraction)

                        # Update the key (Add the remaining tokens into the same one)
                        del token_semantictype_source_weight_dict[(first_token_value, semantic_type_name, source, correct_length)]
                        del token_semantictype_source_index_dict[(first_token_value, semantic_type_name, source, correct_length)]
                        token_semantictype_source_weight_dict[(first_token_value + " " + value, semantic_type_name, source, correct_length)] = old_value
                        token_semantictype_source_index_dict[(first_token_value + " " + value, semantic_type_name, source, correct_length)] = old_value_index


    def convert_vars_to_ascii(self, token_semantictype_weight_dict, replacements):
        new_dict = tupledict()
        for (token, semantic_type, extra_info), value in token_semantictype_weight_dict.iteritems():
            new_token = token.encode('ascii', 'replace')
            new_extra_info = extra_info.encode('ascii', 'replace')
            replacements[new_token] = token
            replacements[new_extra_info] = extra_info
            new_dict[new_token, semantic_type, new_extra_info] = value

        return new_dict

    def formulate_ILP(self, tokens_input):

        # Read the dictionaries of the coupled constraints
        for constraint in self.coupled_constraints:
            # print constraint['from'] + " " + constraint['to']
            constraint['dictionary'] = self.dictionaries[constraint['dictionary_file']]

        # Read the tokens from all sources and store in the dictionary with weights
        token_semantictype_source_weight_dict = tupledict()
        token_semantictype_source_index_dict = tupledict()
        for index, token_input in enumerate(tokens_input):
            self.update_weights_dictionary(token_semantictype_source_weight_dict, token_semantictype_source_index_dict, token_input['tokens'], token_input['source'], index, token_input['weight'])

        # Combine the token weights from multiple sources
        token_semantictype_weight_dict = tupledict()
        token_semantictype_index_dict = tupledict()
        for (token, semantic_type, source, length) in token_semantictype_source_weight_dict.iterkeys():
            token_semantictype_weight_dict[token, semantic_type, ''] = token_semantictype_source_weight_dict.sum(token, semantic_type).getValue()
            list_of_indexes = token_semantictype_source_index_dict.select(token, semantic_type)
            token_semantictype_index_dict[token, semantic_type, ''] = ';'.join(list_of_indexes)

        original_dict = token_semantictype_weight_dict.copy()

        self.add_coupled_constraints_to_dict(token_semantictype_weight_dict, token_semantictype_index_dict)

        m = Model("extractions")

        m.ModelSense = -1 #Maximize

        # Gurobi cannot handle variable names in unicode. Converting them to ascii (FIX)
        replacements = dict()
        token_semantictype_weight_dict = self.convert_vars_to_ascii(token_semantictype_weight_dict, replacements)

        # print token_semantictype_weight_dict

        # Add variables to extractions model
        extractions = m.addVars(token_semantictype_weight_dict, obj=token_semantictype_weight_dict, vtype=GRB.BINARY, name="extractions")

        tokens_with_multiple_semantictypes = set()
        seen = set()
        for (token, semantic_type, extra_info) in token_semantictype_weight_dict:
            if(token not in seen):
                seen.add(token)
            else:
                tokens_with_multiple_semantictypes.add(token)

        # print tokens_with_multiple_semantictypes

        # Each token is one of the semantic types
        m.addConstrs((extractions.sum(token, '*', '') <= 1 for token in tokens_with_multiple_semantictypes), "each_token_one_semantic_type")

        distinct_semantic_types = set(semantic_type for (token, semantic_type, extra_info) in token_semantictype_weight_dict)

        # print distinct_semantic_types

        # Restricting the number of extractions of each semantic type
        m.addConstrs((extractions.sum('*', semantic_type, '*') <= NUMBER_OF_EXTRACTIONS_OF_A_TYPE for semantic_type in distinct_semantic_types), "extractions_of_a_type")


        # Adding the constraint that the sum of all city_country(i) variables = value of that city
        # Meaning a city can be present in only 1 country out of the possible countries
        for constraint in self.coupled_constraints:
            for from_token in constraint['from_tokens']:
                # if(constraint['from'] != 'state'):
                m.addConstr((extractions.sum(from_token, constraint['from'] + GENERATED_SEMANTIC_SEPARATOR + constraint['to'], '*') - extractions.sum(from_token, constraint['from'], '*') == 0), constraint['from']+"_in_one_"+constraint['to'])    
        
        # Adding the constraint that a city can be chosen only from the country which is chosen
        # For all city_country variables, the value is <= the value of the country variable

        for constraint in self.coupled_constraints:
            for to_token in constraint['to_tokens']:
                m.addConstrs( (from_to_var <= extractions.sum(to_token, constraint['to'], '') for from_to_var in extractions.select('*', constraint['from']+GENERATED_SEMANTIC_SEPARATOR+constraint['to'], to_token)), constraint['from']+"_from_only_the_"+constraint['to']+"_chosen")
                # m.addConstrs((extractions.select()))

        m.optimize()

        results_dict = m.getAttr('x', extractions)
        new_dict = dict()
        for (token, semantic_type, extra_info), value in results_dict.iteritems():
            token = replacements[token]
            extra_info = replacements[extra_info]

            if((token, semantic_type, extra_info) in original_dict):
                new_dict[token+":"+semantic_type] = value
            if(value > 0.5):
                # This token has been selected
                if((token, semantic_type, extra_info) in token_semantictype_index_dict):
                    semantic_type_split = semantic_type.split(GENERATED_SEMANTIC_SEPARATOR)
                    index_value = token_semantictype_index_dict[token, semantic_type, extra_info]
                    indiv_index_values = index_value.split(";")
                    for indiv_index_value in indiv_index_values:
                        token_input_and_index = indiv_index_value.split(":")
                        semantic_type_list = tokens_input[int(token_input_and_index[0])]['tokens'][int(token_input_and_index[1])]['semantic_type']
                        for semantic_type_obj in semantic_type_list:
                            semantic_type_in_obj = semantic_type_obj['type']
                            if(len(semantic_type_split) == 1):
                                # This is an original semantic type
                                if(semantic_type == semantic_type_in_obj):
                                    semantic_type_obj['selected'] = 1
                                    if(semantic_type == 'city'):
                                        semantic_type_obj['city'] = token

                            else:
                                # This is a generated semantic type
                                if(semantic_type_split[0] == semantic_type_in_obj):
                                    # This is a match. Need to add extra information to this token
                                    semantic_type_obj[semantic_type_split[1]] = extra_info

        # Adding the lat long information as well
        for token_input in tokens_input:
            tokens = token_input['tokens']
            for token in tokens:
                if('semantic_type' in token):
                    semantic_type_list = token['semantic_type']
                    for semantic_type in semantic_type_list:
                        if(semantic_type['type'] == 'city' and semantic_type.get('selected') == 1):
                            # print semantic_type
                            # This is a city extraction
                            city = semantic_type['city']
                            state = semantic_type.get('state')
                            country = semantic_type.get('country')
                            found = False
                            if(city in self.dictionaries[COMBINED_DICTIONARY]):
                                city_objs = self.dictionaries[COMBINED_DICTIONARY][city]
                                for city_obj in city_objs:
                                    if(state == city_obj.get('state') and country == city_obj['country']):
                                        # This is the city
                                        semantic_type['latitude'] = city_obj['latitude']
                                        semantic_type['longitude'] = city_obj['longitude']
                                        semantic_type['geoname_id'] = city_obj['geoname_id']
                                        found = True
                                        break

                                if(not found):
                                    for city_obj in city_objs:
                                        if(country == city_obj['country']):
                                            # This is the city
                                            semantic_type['latitude'] = city_obj['latitude']
                                            semantic_type['longitude'] = city_obj['longitude']
                                            semantic_type['geoname_id'] = city_obj['geoname_id']
                                            found = True
                                            break

                                if(not found):
                                    # Even matching country not found
                                    if(len(city_objs) > 0):
                                        city_obj = city_objs[0]
                                        semantic_type['latitude'] = city_obj['latitude']
                                        semantic_type['longitude'] = city_obj['longitude']
                                        semantic_type['geoname_id'] = city_obj['geoname_id']
                                        if(not country):
                                            semantic_type['country'] = city_obj['country']


        return tokens_input

if __name__ == '__main__':
    ilp_formulation = ILPFormulation({
        'city-country':CITY_COUNTRY_DICTIONARY, 
        'city-state':CITY_STATE_DICTIONARY,
        'state-country': STATE_COUNTRY_DICTIONARY,
        'city_alt':CITY_ALT_DICTIONARY,
        'city_all':CITY_ALL_DICTIONARY        
    })
    ilp_formulation.formulate_ILP(tokens_input)