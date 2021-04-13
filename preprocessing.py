from graphqlclient import GraphQLClient
import ast
import io
import os
import ruamel.yaml

# aus datenbank alle möglichen services lesen
url='http://ec2-18-185-97-19.eu-central-1.compute.amazonaws.com:8082/'
client = GraphQLClient(url)
result = client.execute('''query { TiltNodes { edges { node { meta { name } } } } } ''')
result_dict=ast.literal_eval(result)
result_dict=result_dict["data"]["TiltNodes"]["edges"]

services=[] # liste enthält alle services aus tilt hub
string_services=""
for r in result_dict:
    name=r["node"]["meta"]["name"]
    #services.append("- [" + str(name) + "](service)\n")
    string_services= string_services+ "- [" + str(name) + "](service)\n"


# intent mit allen services befüllen
with open(r'data\nlu.yml', 'r', encoding = "utf-8") as yaml_file:
    code = ruamel.yaml.load(yaml_file, Loader=ruamel.yaml.RoundTripLoader)
    for i in range(len(code["nlu"])):
        for key in code["nlu"][i]:
            if key=="intent":
                if code["nlu"][i][key]=="services":
                    code["nlu"][i]["examples"]=string_services

with open(r'data\nlu.yml', 'w', encoding = "utf-8") as yaml_file:
    dump = ruamel.yaml.dump(code, default_flow_style = False, allow_unicode = True, encoding = None, Dumper=ruamel.yaml.RoundTripDumper)
    yaml_file.write( dump )

# rasa train ausführen
os.system("rasa train")