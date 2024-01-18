import run

api = "https://api.logicahealth.org/genomexstu3/open/"


lung_study = 'Genomic_Studies/Procedure-lungMass.json'
somatic_study = 'Genomic_Studies/Procedure-somaticStudy.json'
trio2_study = 'Genomic_Studies/Procedure-genomicstudy-trio2.json'
ext1 = 'Extensions/Procedure-analysisTumorNormalDNA.json'

print(run.complete_parse(lung_study,api))
print(run.complete_parse(somatic_study,api))
print(run.complete_parse(trio2_study,api))



