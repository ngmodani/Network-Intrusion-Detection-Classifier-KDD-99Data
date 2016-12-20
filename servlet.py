import pandas as pd
import urllib.request
import json
import time
import random
from flask import Flask, render_template, request
#import urllib.request
#from six.moves import urllib


app = Flask(__name__, static_url_path = '/static')

###################### Home Page #######################
@app.route('/home')
def home():
    return render_template('/home.html')
############### Home Page End #######################    

@app.route('/classify', methods=['GET'])
def run():
    #print("RUN")    
    return render_template('/classify.html')


@app.route('/classify', methods=['POST'])
def start_stream():
    print("in post")
    df = pd.read_csv("kdd_test_data.csv")    
    print("read df")
    start = random.randint(random.randint(0,1000),random.randint(1000,len(df)-15))   
    result = {}    
    print("in while")
    #time.sleep(10) 
    red = 0
    green = 0
    for i in range(0, 20):
        print("Processing")
        result[i] = process(df = df, start= start, end = start + 1)
        #print(result[i])
        if result[i]['result'] == 'attack':
            red = red + 1
        else:
            green = green + 1 
        start += 1    
    return render_template('/classify.html', responses=result, red = red , green = green)    

    

def process(df, start, end):
    print("in process")
    for index,row in df[start:end].iterrows(): 
        logged = row["logged_in"]
        count = row["count"]
        dst_host_count = row["dst_host_count"]
        srv_count = row["srv_count"]
        dst_host_same_src_port_rate = row["dst_host_same_src_port_rate"]
        srv_diff_host_rate = row["srv_diff_host_rate"]
        same_srv_rate = row["same_srv_rate"]
        dst_host_srv_serror_rate = row["dst_host_srv_serror_rate"] 
        serror_rate = row["serror_rate"]
        srv_serror_rate = row["srv_serror_rate"] 
        dst_host_serror_rate = row["dst_host_serror_rate"]
        dst_host_srv_diff_host_rate = row["dst_host_srv_diff_host_rate"]
        dst_host_diff_srv_rate = row["dst_host_diff_srv_rate"] 
        duration = row["duration"]
        dst_host_same_srv_rate = row["dst_host_same_srv_rate"]

        data = {
                "Inputs": {
                        "input1":
                        [
                            {
                                'class-normal': "1",   
                                'logged_in': logged,   
                                'count': count,   
                                'dst_host_count': dst_host_count,   
                                'srv_count': srv_count,   
                                'dst_host_same_src_port_rate': dst_host_same_src_port_rate,   
                                'srv_diff_host_rate': srv_diff_host_rate,   
                                'same_srv_rate': same_srv_rate,   
                                'dst_host_srv_serror_rate': dst_host_srv_serror_rate,   
                                'serror_rate': serror_rate,   
                                'srv_serror_rate': srv_serror_rate,   
                                'dst_host_serror_rate': dst_host_serror_rate,   
                                'dst_host_srv_diff_host_rate': dst_host_srv_diff_host_rate,   
                                'dst_host_diff_srv_rate': dst_host_diff_srv_rate,   
                                'duration': duration,   
                                'dst_host_same_srv_rate': dst_host_same_srv_rate,   
                            }
                        ],
                },
            "GlobalParameters":  {
            }
        }

        body = str.encode(json.dumps(data))

        url = 'https://ussouthcentral.services.azureml.net/workspaces/3e06fa1833c9420c8b0aa701d6ada435/services/c7c270b78a6f450088079b54f70e0fcb/execute?api-version=2.0&format=swagger'
        api_key = 'API key' # Replace this with the API key for the web service
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

        req = urllib.request.Request(url, body, headers)
        try:
            response = urllib.request.urlopen(req)
            result = response.read().decode("utf-8")
            print("got result")
            result = json.loads(result)
            result['service'] = row["service"]
            result['duration'] = row["duration"]
            result['protocol_type'] = row["protocol_type"]
            result['flag'] = row["flag"]
            result['src_bytes'] = row["src_bytes"]
            result['dst_bytes'] = row["dst_bytes"]
            result['logged_in'] = row["logged_in"]
            result['count'] = row["count"]
            result['serror_rate'] = row["serror_rate"]
            if result['Results']['output1'][0]['Scored Labels'] == '0':
                result['result'] = "attack"
            else:
                result['result'] = "normal"
            #print("Response ready")
            return result
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(json.loads(error.read().decode("utf8", 'ignore')))
            return None


def main():
    print("inside main")
    app.run(port=8000)


if __name__ == '__main__':
    main()      
            
