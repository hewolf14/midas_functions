import requests
import numpy as np
import pandas as pd
import subprocess
import time

# Create dictionary to convert response codes
#  See https://midas-support.atlassian.net/wiki/spaces/MAW/pages/83787785/Manual+Basic+Information for definition of codes
RespCode = {
    200: 'Success',
    201: 'Created',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not found'
    }

# function for MIDAS Open API
def MidasAPI(method, command, body=None):
    base_url = "https://moa-engineers.midasit.com:443/civil"
    mapi_key = "eyJ1ciI6ImhlbnJ5d29sZiIsInBnIjoiY2l2aWwiLCJjbiI6IklNQkVWTDFHUUEifQ.e6fa541ab5e263b9f4e291c0666aa5ff1ae6a7aeda737b6b7110c021cfaf3d19"

    url = base_url + command
    headers = {
        "Content-Type": "application/json",
        "MAPI-Key": mapi_key
    }

    if method == "POST":
        response = requests.post(url=url, headers=headers, json=body)
    elif method == "PUT":
        response = requests.put(url=url, headers=headers, json=body)
    elif method == "GET":
        response = requests.get(url=url, headers=headers)
    elif method == "DELETE":
        response = requests.delete(url=url, headers=headers)

    print(method, command, response.status_code)
    return response.json()

elems = np.arange(110006, 110020).tolist()

###extract member demands
def member_demands(demand_type, element_numbers, load_cases, filepath, filename, 
                   units={"FORCE": "kips","DIST": "ft"}):
    #demand_type: 'truss', 'beam', 'resultant'
    #element_numbers: list of element demands desired
    #load_case: list of all load cases
    #filepath
    #filename
    if demand_type=='truss':
        df=truss_demands(element_numbers, load_cases, units)
    elif demand_type=='beam':
        df=beam_demands(element_numbers, load_cases, units)
    elif demand_type=='resultant':
        df=resultant_demands(element_numbers, load_cases, units)
    else:
        return "Error: Demand type not available. Must be 'truss', 'beam', or 'resultant'"
    
    df.to_csv(filepath+filename, index=False)
    return 'Written to '+str(filepath)+str(filename)

def truss_demands(element_numbers, load_cases, units={"FORCE": "kips","DIST": "ft"}):
    input_json={
        "Argument": {
            "TABLE_NAME": "TrussForce",
            "TABLE_TYPE": "TRUSSFORCE",
            "EXPORT_PATH": "C:\\MIDAS\\Result\\Output.JSON",
            "UNIT": units,
            "STYLES": {
                "FORMAT": "Fixed",
                "PLACE": 12
            },
            "COMPONENTS": [
                "Elem",
                "Load",
                "Force-I",
                "Force-J"
            ],
            "NODE_ELEMS": {
                "KEYS": element_numbers
            },
            "LOAD_CASE_NAMES": load_cases,
            "PARTS": [
                "Part I",
                "Part J"
                    ]
            }
    }

    file_res = MidasAPI("POST", "/post/table", input_json)
    df=pd.DataFrame(data=file_res['TrussForce']['DATA'], columns=file_res['TrussForce']['HEAD'])
    df=df.drop(columns='Index')
    return df

def beam_demands(element_numbers, load_cases, units={"FORCE": "kips","DIST": "ft"}):
    input_json={
        "Argument": {
            "TABLE_NAME": "BeamForce",
            "TABLE_TYPE": "BEAMFORCE",
            "EXPORT_PATH": "C:\\MIDAS\\Result\\Output.JSON",
            "UNIT": units,
            "STYLES": {
                "FORMAT": "Fixed",
                "PLACE": 12
            },
            "COMPONENTS": [
                "Elem",
                "Load",
                "Part",
                "Axial",
                "Shear-y",
                "Shear-z",
                "Torsion",
                "Moment-y",
                "Moment-z"
            ],
            "NODE_ELEMS": {
                "KEYS": element_numbers
            },
            "LOAD_CASE_NAMES": load_cases,
            "PARTS": [
                "Part I",
                "Part J"
                    ]
            }
    }

    file_res = MidasAPI("POST", "/post/table", input_json)
    df=pd.DataFrame(data=file_res['BeamForce']['DATA'], columns=file_res['BeamForce']['HEAD'])
    df=df.drop(columns='Index')
    return df

def resultant_demands(element_numbers, load_cases, units={"FORCE": "kips","DIST": "ft"}):
    input_json={
        "Argument": {
            "TABLE_NAME": "ResultantForces",
            "TABLE_TYPE": "RESULTANT_FORCES",
            "EXPORT_PATH": "C:\\MIDAS\\Result\\Output.JSON",
            "UNIT": units,
            "STYLES": {
                "FORMAT": "Fixed",
                "PLACE": 12
            },
            "COMPONENTS": [
                "VirtualBeam",
                "Load",
                "Part",
                "Axial",
                "Shear-y",
                "Shear-z",
                "Torsion",
                "Moment-y",
                "Moment-z"
            ],
            "NODE_ELEMS": {
                "KEYS": element_numbers
            },
            "LOAD_CASE_NAMES": load_cases,
            "PARTS": [
                "Part I",
                "Part J"
                    ]
            }
    }

    file_res = MidasAPI("POST", "/post/table", input_json)
    df=pd.DataFrame(data=file_res['ResultantForces']['DATA'], columns=file_res['ResultantForces']['HEAD'])
    df=df.drop(columns='Index')
    return df
###end extract member demands

###begin modify model
def delete_member(element_numbers):
    for element_number in element_numbers:
        MidasAPI("DELETE", "/db/elem/"+str(element_number))
###end modify model

###begin doc projects
def open_midas():

    p = subprocess.Popen([r"C:\Program Files\MIDAS\MIDAS CIVIL NX\MIDAS CIVIL NX\CVLw.exe", "/API"])
    ## wait until civil api process ready
    time.sleep(10)

def open_midas_model(filepath, filename):

    MidasAPI("POST", "/doc/open", {"Argument": filepath+filename})

def saveas_midas_model(filepath, filename):

    MidasAPI("POST", "/doc/saveas", {"Argument": filepath+filename})

def save_midas_model():

    MidasAPI("POST", "/doc/save", {})

def run_midas_model():

    MidasAPI("POST", "/doc/anal", {})
###end doc projects

###1.0 - open midas###
# open_midas()

def exchange_analysis(stay_exchange):
    ##1.1 - open midas model###
    model_file_path=r'C:\Users\Henry.Wolf\OneDrive - Kiewit Corporation\Projects\GA_Talmadge\HEW files\01_modeling\03_full model\01_models\01a_model\04_gen exchange\01_models'
    model_file_name=r'\01a_savannah full.mcb'
    open_midas_model(filepath=model_file_path, filename=model_file_name)

    ##1.2 - save new version of midas model###
    new_model_file_name=f'\\01a_savannah stay {stay_exchange}.mcb'
    saveas_midas_model(filepath=model_file_path, filename=new_model_file_name)

    ##1.3 - delete stay###
    delete_member([920001+stay_exchange*100])

    ##1.4 - save model###
    save_midas_model()

    ##1.5 - run analysis###
    run_midas_model()

def extract_results(stay_exchange, load_cases):

    results_file_path=r'C:\Users\Henry.Wolf\OneDrive - Kiewit Corporation\Projects\GA_Talmadge\HEW files\01_modeling\03_full model\01_models\01a_model\04_gen exchange\02_results'
    #edge girder
    results_file_name=f'\\01_edge girder\\stay {stay_exchange}.csv'
    element_numbers = np.arange(190001, 190223).tolist()
    member_demands('beam', element_numbers, load_cases, results_file_path, results_file_name)
    #resultant section
    results_file_name=f'\\02_half section\\stay {stay_exchange}.csv'
    element_numbers = np.arange(1001, 1223).tolist()
    member_demands('resultant', element_numbers, load_cases, results_file_path, results_file_name)
    #truss
    results_file_name=f'\\03_stays\\stay {stay_exchange}.csv'
    element_numbers = list(range(920101, 927301, 100))
    member_demands('truss', element_numbers, load_cases, results_file_path, results_file_name)

# stays=np.arange(1, 37).tolist()
stays = [16]
load_cases=['pti srv(CB:max)', 'pti str(CB:max)']
for stay in stays:
    #exchange_analysis(stay)
    extract_results(stay, load_cases)
    save_midas_model()