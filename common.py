import ijson
import orjson
import json
import util


class Genomic_Study_Parser:
    def __init__(self, *args, **kwargs):
        self.in_date_comp = False
        self.in_name_comp = False
        self.in_date_comp = False
        self.in_assert_comp = False
        self.in_coding_comp = False
        self.in_id_comp = False
        self.in_ident_comp = False
        self.in_extension = False
        self.sample_name = None 

        self.extension_map_keys = ['url','valueReference','reference']

        self.entries = {}
        self.information_dict = {}
        self.final_dict = {}

    def check_map_key(self, value):
        if value == 'name':
            self.in_name_comp = True
        if value == 'performedDateTime':
            self.in_date_comp = True
        if value == 'subject':
            self.in_name_comp = True
        if value == 'asserter':
            self.in_assert_comp = True
        if value == 'reasonCode':
            self.in_coding_comp = True
        if value == 'id':
            self.in_id_comp = True
        if value == 'identifier':
            self.in_ident_comp = True
        if value == 'resourceType':
            self.resource = True


    def pop_required_elements(self, element_to_pop, dict_to_modify):
        analysis_key = list(dict_to_modify.keys())[0]
        #self.final_dict[analysis_key] = {}
        in_rna = 'RNA' in analysis_key
        embedded_dict = dict_to_modify[analysis_key]
        if element_to_pop == 'build':
            if 'LA26806-2' in embedded_dict:
                self.final_dict['ref_build'] = embedded_dict.pop('LA26806-2', None)
            elif 'LA14029-5' in embedded_dict:
                self.final_dict['ref_build'] = embedded_dict.pop('LA14029-5', None)
        if element_to_pop == 'VCF_file' in dict_to_modify[analysis_key]:
            if 'VCF_file' in embedded_dict:
                self.final_dict['VCF_file'] = embedded_dict.pop('VCF_file', None)
        if element_to_pop == 'BED_files' and not in_rna:
            if 'called_regions' in embedded_dict:
                self.final_dict['BED_called_regions'] = embedded_dict.pop('called_regions', None)
            if 'uncalled_regions' in embedded_dict:
                self.final_dict['BED_uncalled_regions'] = embedded_dict.pop('uncalled_regions', None)
        self.final_dict['extra_references'] = embedded_dict
        self.information_dict[analysis_key] = self.final_dict


    
    def check_parsed_code(self,value):
        if value == "LA26806-2":
            self.information_dict['HumanRefSeqNCBIBuildId'] = GRCh38
        if 'codes' not in self.information_dict.keys():
            self.information_dict['codes'] = [value]
        else:
            self.information_dict['codes'].append(value)
    
 
    def check_prefix(self,prefix, value, desired_event):
        split_prefix = prefix.split('.')
        if split_prefix[-1] == desired_event and desired_event == 'display':
            self.information_dict['codes'][-1] += f": {value}"
            self.in_coding_comp = False
        if split_prefix[0] == 'extension':
            if split_prefix[-1] == desired_event and desired_event == "reference":
                query_type = value.split('/')
                response = util.get_extension_json(query=value,api_url=self.api_link)
                Parse_class = util.Parsers(response)
                parsed = Parse_class.parse_procedure(response)
                self.pop_required_elements('build',parsed)
                self.pop_required_elements('VCF_file', parsed)
                self.pop_required_elements('BED_files', parsed)




    def parse_genomic_study(self, input_path, api_link):
        self.api_link = api_link
        with open(input_path, 'r') as json_file:
            parser = ijson.parse(json_file)
            for prefix, event, value in parser:
                if prefix.split('.')[0] == 'extension':
                    self.in_extension = True
                else:
                    self.in_extension = False
                if event == "map_key":
                    current_key = value
                    self.check_map_key(value)
                elif event == "string" or event == "number":
                    if self.in_extension:
                        self.check_prefix(prefix, value, desired_event="reference")
                    if self.in_date_comp:
                        self.information_dict['test_date'] = value
                        self.in_date_comp = False
                    if self.in_name_comp:
                        self.information_dict['patient_id'] = value
                        self.in_name_comp = False
                    if self.in_id_comp:
                        self.information_dict['resource_id'] = value
                        self.in_id_comp = False
                    if self.in_assert_comp:
                        self.information_dict['asserter'] = value
                        self.in_assert_comp = False
                    if self.in_ident_comp:
                        self.information_dict['identifier'] = value
                        self.in_ident_comp =False
                    if self.in_coding_comp:
                        self.check_prefix(prefix,value,desired_event="reference")
                    if current_key == 'code':
                        self.check_parsed_code(value)
            
        return self.information_dict


