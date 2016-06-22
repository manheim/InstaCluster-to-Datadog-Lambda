# InstaCluster-to-Datadog-Lambda 
---
###A scheduled AWS lambda function to extract stats from the instaclustr monitoring API and upload them to DataDog


####API Docs
* [Instaclustr monitoring API](https://support.instaclustr.com/hc/en-us/articles/209695488-Monitoring-API)
* [Datadog API] (http://docs.datadoghq.com/api/)

####AWS Docs
* [Creating a python package to deploy on lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
* [Setting up a lambda function to run on a schedule](https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html)


## Configuration
#####Python package
Clone this repo locally and follow the instructions above to set up that directory for building a lambda deploy package so that your pip installs are within the root level of the project.  Pip install the datadog library.  The others should get installed when you do that.

#####Configuration file
All the configuration items are in `configuration.json` You'll need your instaclustr login, api key, and cluster id(s) to monitor.  These are all available from the instclustr dashboard.  You'll also need a datadog api key and app key, which can be found/made in the datadog dashboard.

The configuration file is made up of one or more sections, designated by named tags.  The tag `default` is used if you do not specify a tag when you set up the lambda function (see below).

#####Sample file
```json
{
  "monitor1": {
    "cluster_id": "<ic_cluster_id_1>",
    "env": "<environment_tag_1>",
    "metrics_list": "n::cpuutilization,n::cassandraReads,n::cassandraWrites,n::nodeStatus,cf::<keyspace_1>::<columnfamily_1>::readlatency,cf::<keyspace_1>::<columnfamily_1>::writelatency,cf::<keyspace_1>::<columnfamily_2>::readlatency,cf::<keyspace_1>::<columnfamily_2>::writelatency",
    "dd_options": {
      "api_key": "<data_dog_api_key>",
      "app_key": "<data_dog_app_key>"
    },
    "ic_options": {
      "user_name": "<ic_login>",
      "api_key": "<ic_api_key>"
    }
  },
  "default": {
    "cluster_id": "<ic_cluster_id_2",
    "env": "<environment_tag_2>",
    "metrics_list": "n::cpuutilization,n::cassandraReads,n::cassandraWrites,n::nodeStatus,cf::<keyspace_2>::<columnfamily_1>::readlatency,cf::<keyspace_2>::<columnfamily_1>::writelatency,cf::<keyspace_2>::<columnfamily_2>::readlatency,cf::<keyspace_2::columnfamily_2>::writelatency",
    "dd_options": {
      "api_key": "<data_dog_api_key>",
      "app_key": "<data_dog_app_key>"
    },
    "ic_options": {
      "user_name": "<ic_login>",
      "api_key": "<ic_api_key>"
    }
  }
}
```

The values to put in the file should be fairly self explanitory.  Note that you need to name each keyspace + column family that you want metrics for.  This script does not yet parse available keyspaces.  Also note that instaclustr's API limits each API request to 20 metrics.

#####Lambda Setup
Once you've updated the config file and uploaded a deploment package zipfile, you need to set up the schedule.  The docs show setting up the schedule  via CLI expressions.  However the UI also allows setting up the schedule, which is what I used.  To do this, go to the "Event Sources" tab of the lambda function and add a "CloudWatch Events - Schedule" source and specify the name, schedule etc.

After the event has been created, open it and edit the criteria.  This also allows you to specify the data which gets passed into the `event` tag when the lambda is executed.  By setting this json, you can control which section of the configuration json gets used, allowing you to set up multiple executions of the same lamba to monitor different clusters, and/or different keyspaces.

To set up the input data passed to the json, edit the event sources for the lambda, then create a rule.  Expand the "Configure Input" section and enter json with `{"key": "<the section of the config file>"}`


#####Example
![input]
[input]: constant.png

That's it.  You should then be able to see invocations in the monitoring tab of the lambda function as well as cloudwatch logs of the output.

In datadog, all the metrics will appear as `instaclustr.<metricname>` with an optional `type` for column family specific metrics.  Additionally, the host value of the metric is set to the public ip of the instaclustr node.  There are also tags set on each metric for environment, and availability zone; and keyspace and column family, if applicable.  This allows you to graph and alert on a column family or node basis.

#####Sample Datadog Graph
![graph]
[graph]: graph.png
