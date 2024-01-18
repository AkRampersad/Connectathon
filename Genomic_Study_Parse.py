import common
import sys
import json

script_name = sys.argv[0]
file = sys.argv[1]
api = sys.argv[2]

def complete_parse(file_location, api_link):
    g1 = common.Genomic_Study_Parser(file_location)
    return g1.parse_genomic_study(file_location, api_link)

def create_output_file(dictionary, filename):
    with open(filename, 'w') as file:
        json.dump(dictionary,file, indent=2)
dict_to_output = complete_parse(file,api)


input_name = dict_to_output['resource_id']

output_file = f"{input_name}_parsed_output.json"

create_output_file(dict_to_output,output_file)
