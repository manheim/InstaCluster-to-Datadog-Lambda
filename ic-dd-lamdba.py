from datadog import initialize, api
from datetime import datetime
import requests, json
from requests.auth import HTTPBasicAuth

epoch = datetime(1970, 1, 1)
myformat = "%Y-%m-%dT%H:%M:%S.%fZ"

configFile = "configuration.json"
f = open(configFile)
configuration = json.loads(f.read())
f.close()

cf_specific_metrics = ['readLatency', 'writeLatency', 'sstables', 'tombstones', 'liveCells']

def lambda_handler(event, context):
    print "Gathering stats from cassandra at {0}".format(str(datetime.now()))

    key = 'default'
    try:
        key = event['key']
    except:
        print "No monitoring key set, using: {0}".format(key)

    dd_options = configuration[key]['dd_options']

    initialize(**dd_options)    

    auth_details = HTTPBasicAuth(username=configuration[key]['ic_options']['user_name'], password=configuration[key]['ic_options']['api_key'])
    
    response = requests.get(url="https://api.instaclustr.com/monitoring/v1/clusters/{0}?metrics={1},".format(configuration[key]['cluster_id'], configuration[key]['metrics_list']), auth=auth_details)
    #print "Got Response:  {0}".format(response.content)

    if not response.ok:
        print "Could not fetch metrics from IC: {0} - {1}".format(response.status_code, response.content)
    else: 
        metric_count = 0;
        metrics = json.loads(response.content)
        for node in metrics:
            public_ip = node["publicIp"]
            az = node["rack"]["name"]
            print "{0} : {1}".format(public_ip, az)
            for metric in node["payload"]:
                dd_metric_name = 'instaclustr.{0}'.format(metric["metric"])
                
                mydt = datetime.strptime(metric["values"][0]["time"], myformat)
                time_val= int((mydt - epoch).total_seconds())

                tags=["environment:{0}".format(configuration[key]['env']), "availability_zone:{0}".format(az)]
                
                if metric["metric"] in cf_specific_metrics:
                    dd_metric_name += ".{0}".format(metric["type"])
                    tags.append("keyspace:{0}".format(metric["keyspace"]))
                    tags.append("columnFamily:{0}".format(metric["columnFamily"]))

                if metric["metric"] != "nodeStatus":
                    #print "{0} : {1}".format(dd_metric_name, metric["values"][0]["value"])
                    api.Metric.send(metric=dd_metric_name, points=[(time_val,metric["values"][0]["value"])],host=public_ip, tags=tags)
                    metric_count += 1

        print('{0} cassandra stats uploaded. completed at {1}'.format(metric_count, str(datetime.now())))



