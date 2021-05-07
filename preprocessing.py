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

# aus datenbank alle möglichen third parties lesen
result_company= client.execute('''query { TiltNodes { edges { node { dataDisclosed { recipients {name} } } } } } ''')
start_indeces = [i for i in range(len(result_company)) if result_company.startswith("null", i)]
for start_idx in start_indeces:
    end_idx=start_idx+4
    result_company=result_company[:start_idx]+ "\'" + result_company[start_idx:end_idx] + "\'" + result_company[end_idx:]
result_dict_company=ast.literal_eval(result_company)
result_dict_company=result_dict_company["data"]["TiltNodes"]["edges"]


# liste enthält alle services aus tilt hub
string_services=""
list_services=[]
for r in result_dict:
    name=r["node"]["meta"]["name"]
    list_services.append(name)
    

# list enthält alle third parties aus tilt hub
for r in result_dict_company:
    name=r["node"]["dataDisclosed"]
    for i in range(len(name)):
        recipient=name[i]["recipients"]
        for j in range(len(recipient)):
            companies=recipient[j]["name"]
            list_services.append(companies)
list_services = list(dict.fromkeys(list_services))
list_services.remove("null")

#combine services and third parties in string
for name in list_services:
    string_services= string_services+ "- [" + str(name) + "](service_company)\n"



# intent mit allen services und companies(third parties) befüllen
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