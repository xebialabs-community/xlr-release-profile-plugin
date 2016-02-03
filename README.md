#XL Release variable persistence off plugin

## Preface
This document descripts the functionality provide by the `xlr-release-profile-plugin`, as well as potential future functionality.

## Overview
This module enables users of xl-release to set up variable profiles

## Installation


Copy the plugin JAR file into the `SERVER_HOME/plugins` directory of XL Release.

### Limitations

## Supported Tasks


## Example Use Case


'''
{"variables":
    {"test1": { "default_value" : "555",
                "collector" : { "type" : "json" ,
                                "url" : "http://192.168.99.100:32768/artifactory/xlrelease/collector_test.json",
                                "path" : "claims/bpm/2012_02/buildNr" }},
     "test2": { "default_value" : "444",
                "collector" : { "type" : "json" ,
                                "url" : "http://192.168.99.100:32768/artifactory/api/storage/xlrelease?properties",
                                "path" : "properties/latest_build" }},
     "test3": "scarecrow" }
     ,"toggles" :
      [{"phase" : "deploy_to_dev", "task" : "shitty", "skip" : "true"},
       {"phase" : "deploy_to_dev", "task" : "shitty1", "skip" : "true"}]
     ,"tasks": {}}
'''
