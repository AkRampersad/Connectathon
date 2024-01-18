import orjson
import json
import requests



def api_request(url,query):
    try: 
        request = f"{url}{query}"
        #print("this is the request")
        #print(request)
        response = requests.get(request)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_extension_json(query,api_url):
    response = api_request(api_url, query)
    return response


class Parsers:
    def __init__(self, *args, **awks):
        self.analysis_dict = {}
        self.BED_VCF_dict = {}
        self.code_dict = {"LA26806-2":['ref_build','GRCh38']}
        self.specimen_url = "http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/genomic-study-analysis-specimen"
        Works = False
    
    def parse_values(self,json_dict):
        keys = json_dict.keys()
        if 'valueCodeableConcept' in keys:
            coding = json_dict['valueCodeableConcept']['coding'][0]
            type_of_resource = coding['code']
            if 'display' in coding.keys():
                resource = coding['display']
            self.BED_VCF_dict[type_of_resource] = resource
        if json_dict['url'] == self.specimen_url:
            self.BED_VCF_dict['Specimen'] = json_dict['valueReference']['reference']
            


    def VCF_BED_extract(self,list_of_dicts):
        for resource_dict in list_of_dicts:
            if resource_dict['url'] == 'studied':
                if 'valueReference' in resource_dict.keys():
                    file = resource_dict['valueReference']['reference']
                    self.BED_VCF_dict['called_regions'] = file
            if resource_dict['url'] == 'uncalled':
                file = resource_dict['valueReference']['reference']
                self.BED_VCF_dict['uncalled_regions'] = file
            if resource_dict['url'] == 'file':
                if 'valueReference' in resource_dict.keys():
                    file = resource_dict['valueReference']['reference']
                    self.BED_VCF_dict['VCF_file'] = file
            if resource_dict['url'] == self.specimen_url:
                specimen = resource_dict['valueReference']['reference']
                self.BED_VCF_dict['specimen'] = specimen



    def extension_parse(self,extension_component):
        json_data = extension_component
        parser = orjson.dumps(json_data)
        json_dump = orjson.loads(parser)
        if isinstance(json_dump,list):
            self.VCF_BED_extract(json_dump)
        if isinstance(json_dump,dict):
            if 'valueCodeableConcept' or 'valueReference' in json_dump.keys():
                self.parse_values(json_dump)
            if 'extension' in json_dump.keys():
                imbedded_extention = json_dump['extension']
                self.extension_parse(imbedded_extention)



    def parse_procedure(self, procedure_resource):
        parser = orjson.dumps(procedure_resource)
        json_dump = orjson.loads(parser)
        self.Works = True
        extension_id = json_dump['id']
        for x in json_dump['extension']:
            self.extension_parse(x)
        self.analysis_dict[extension_id] = self.BED_VCF_dict
        self.BED_VCF_dict = {}
        return self.analysis_dict
    


file = 'Extensions/Procedure-analysisTumorNormalDNA.json'

#with open(file, 'r') as procedure_resource:
#    json_object = json.load(procedure_resource)
#    print(type(json_object))
#    p1 = Parsers(json_object)
#    parse1 = p1.parse_procedure(json_object)

