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

tokens_from_text = [
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
            'probability': 0.7,
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
},
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
    "dictionary_file":'city-country' 
},
{
    "from":"city",
    "to":"state",
    "dictionary_file":'city-state'
},
{
    "from":"state",
    "to":"country",
    "dictionary_file":'state-country'
}
]

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
                    if(token in constraint['dictionary']):
                        to_tokens_for_from_token = set(constraint['dictionary'][token])
                    if(to_tokens_for_from_token):
                        for to_token in to_tokens_for_from_token:
                            print "Added "+token+" "+to_token
                            # Adding to_token (ex. country) in the extra_info field
                            token_semantictype_weight_dict[token, constraint['from'] + '_' + constraint['to'], to_token] = 0 # Added weight as 0 so that it does not come in the objective function
                            token_semantictype_index_dict[token, constraint['from'] + '_' + constraint['to'], to_token] = token_semantictype_index_dict[token, semantic_type, extra_info]
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
                        if((value, semantic_type_name, source) not in token_semantictype_source_weight_dict):
                            #This value with semantic type is occuring for the 1st time
                            token_semantictype_source_weight_dict[(value, semantic_type_name, source)] = semantic_probability*weight_of_extraction
                            token_semantictype_source_index_dict[(value, semantic_type_name, source)] = index_value
                        else:
                            #This is a duplicate occurence in the same group (ie. title, text)
                            old_value = token_semantictype_source_weight_dict[(value, semantic_type_name, source)]
                            token_semantictype_source_weight_dict[(value, semantic_type_name, source)] = self.combine_values(old_value, semantic_probability*weight_of_extraction)
                            old_value = token_semantictype_source_index_dict[(value, semantic_type_name, source)]
                            token_semantictype_source_index_dict[(value, semantic_type_name, source)] = old_value+";"+index_value

                    else:
                        #This is a multiword token and is currently at the offset th token from the 1st token
                        first_token_value = tokens_with_semantic_types[index - offset]['value']
                        while(offset > 1):
                            offset-=1
                            first_token_value += " " + tokens_with_semantic_types[index - offset]['value']


                        old_value = token_semantictype_source_weight_dict[(first_token_value, semantic_type_name, source)]
                        old_value_index = token_semantictype_source_index_dict[(first_token_value, semantic_type_name, source)]
                        # Update Probabilities (Not Required since will have the same probabilities)
                        # token_semantictype_source_index_weight_dict[(first_token_value, semantic_type_name, source)] = combine_values(old_value, semantic_probability*weight_of_extraction)

                        # Update the key (Add the remaining tokens into the same one)
                        del token_semantictype_source_weight_dict[(first_token_value, semantic_type_name, source)]
                        del token_semantictype_source_index_dict[(first_token_value, semantic_type_name, source)]
                        token_semantictype_source_weight_dict[(first_token_value + " " + value, semantic_type_name, source)] = old_value
                        token_semantictype_source_index_dict[(first_token_value + " " + value, semantic_type_name, source)] = old_value_index

    def formulate_ILP(self, tokens_input):

        # Read the dictionaries of the coupled constraints
        for constraint in self.coupled_constraints:
            print constraint['from'] + " " + constraint['to']
            constraint['dictionary'] = self.dictionaries[constraint['dictionary_file']] 

        # Read the tokens from all sources and store in the dictionary with weights
        token_semantictype_source_weight_dict = tupledict()
        token_semantictype_source_index_dict = tupledict()
        for index, token_input in enumerate(tokens_input):
            self.update_weights_dictionary(token_semantictype_source_weight_dict, token_semantictype_source_index_dict, token_input['tokens'], token_input['source'], index, token_input['weight'])

        # Combine the token weights from multiple sources
        token_semantictype_weight_dict = tupledict()
        token_semantictype_index_dict = tupledict()
        for (token, semantic_type, source) in token_semantictype_source_weight_dict.iterkeys():
            token_semantictype_weight_dict[token, semantic_type, ''] = token_semantictype_source_weight_dict.sum(token, semantic_type).getValue()
            list_of_indexes = token_semantictype_source_index_dict.select(token, semantic_type)
            token_semantictype_index_dict[token, semantic_type, ''] = ';'.join(list_of_indexes)

        self.add_coupled_constraints_to_dict(token_semantictype_weight_dict, token_semantictype_index_dict)

        print token_semantictype_index_dict
        print token_semantictype_weight_dict

        m = Model("extractions")

        m.ModelSense = -1 #Maximize

        # Add variables to extractions model
        extractions = m.addVars(token_semantictype_weight_dict, obj=token_semantictype_weight_dict, vtype=GRB.BINARY, name="extractions")

        tokens_with_multiple_semantictypes = set()
        seen = set()
        for (token, semantic_type, extra_info) in token_semantictype_weight_dict:
            if(token not in seen):
                seen.add(token)
            else:
                tokens_with_multiple_semantictypes.add(token)

        print tokens_with_multiple_semantictypes

        # Each token is one of the semantic types
        m.addConstrs((extractions.sum(token, '*', '') <= 1 for token in tokens_with_multiple_semantictypes), "each_token_one_semantic_type")

        distinct_semantic_types = set(semantic_type for (token, semantic_type, extra_info) in token_semantictype_weight_dict)

        print distinct_semantic_types

        # Restricting the number of extractions of each semantic type
        m.addConstrs((extractions.sum('*', semantic_type, '*') <= NUMBER_OF_EXTRACTIONS_OF_A_TYPE for semantic_type in distinct_semantic_types), "extractions_of_a_type")

        # Making sure each word in the multiword token is either selected or not
        # for multiword_token in multiword_tokens:
        #     print extractions[multiword_token[0],multiword_token[2]]
        #     print extractions[multiword_token[1],multiword_token[2]]
        #     m.addConstr(extractions[multiword_token[0],multiword_token[2]] - extractions[multiword_token[1],multiword_token[2]] == 0)


        # Adding the constraint that the sum of all city_country(i) variables = value of that city
        # Meaning a city can be present in only 1 country out of the possible countries
        for constraint in self.coupled_constraints:
            for from_token in constraint['from_tokens']:
                # if(constraint['from'] != 'state'):
                m.addConstr((extractions.sum(from_token, constraint['from'] + '_' + constraint['to'], '*') - extractions.sum(from_token, constraint['from'], '*') == 0), constraint['from']+"_in_one_"+constraint['to'])    
        
        # Adding the constraint that a city can be chosen only from the country which is chosen
        # For all city_country variables, the value is <= the value of the country variable

        for constraint in self.coupled_constraints:
            for to_token in constraint['to_tokens']:
                m.addConstrs( (from_to_var <= extractions.sum(to_token, constraint['to'], '') for from_to_var in extractions.select('*', constraint['from']+'_'+constraint['to'], to_token)), constraint['from']+"_from_only_the_"+constraint['to']+"_chosen")
                # m.addConstrs((extractions.select()))

        m.optimize()

        print "Constraints:"
        constrs = m.getConstrs()
        for constr in constrs:
            print constr

        results_dict = m.getAttr('x', extractions)
        for (token, semantic_type, extra_info), value in results_dict.iteritems():
            if(value == 1):
                # This token has been selected
                if((token, semantic_type, extra_info) in token_semantictype_index_dict):
                    semantic_type_split = semantic_type.split("_")
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
                            else:
                                # This is a generated semantic type
                                if(semantic_type_split[0] == semantic_type_in_obj):
                                    # This is a match. Need to add extra information to this token
                                    semantic_type_obj[semantic_type_split[1]] = extra_info

        return tokens_input

# TO CHECK EXECUTION UNCOMMENT THE FOLLOWING LINES:

# ilp_formulation = ILPFormulation({
#     'city-country':CITY_COUNTRY_DICTIONARY, 
#     'city-state':CITY_STATE_DICTIONARY,
#     'state-country': STATE_COUNTRY_DICTIONARY
# })
# ilp_formulation.formulate_ILP(tokens_input)