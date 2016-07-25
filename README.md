#XL Release variable persistence off plugin

## Preface
This document descripts the functionality provide by the `xlr-release-profile-plugin`, as well as potential future functionality.

## Overview
This module enables users of xl-release to store release lay-outs and variables outside of xlr.
Plus it does all kinds of funky variable management stuff.

## Installation


Copy the plugin JAR file into the `SERVER_HOME/plugins` directory of XL Release.

### Limitations

### Supported Tasks

* LoadProfile **deprecated**
* MakeVariableOptional
* SetDefaultValue
* LoadDynamicProfile
* OverwriteVariable
* LoadProfileFromUrl **deprecated**
* LoadTemplateProfile
* SetReleaseCounter
* SetReleaseCounterString
* IncrementReleaseCounter
* GetReleaseCounter
* CreateCounterStore
* DestroyCounterStore


### configuration items
* ReleaseProfile
* ReleaseCounterStore


### Task documentation

####  MakeVariableOptional
* Description: make a variable optional, this makes a variable that would otherwise be required for a release to start not be required so that we are able to fill it at a later time.
* Input Properties:
  * variableName: name of the variable to make optional
* Output properties: **N/A**

####  SetDefaultValue
* Description: Set a variable to a default value in the template plan.
* Input Properties:
  * variableName: name of the variable to make optional
  * defaultValue: default value to apply to the variable
* Output properties: **N/A**

####  LoadDynamicProfile
* Description: load a variable profile from any location. This function is deprecated and will soon be replaced by loadTemplateProfile.
* Input Properties:
  * profileUrl: http/https url pointing at the profile (json format)
  * profiles: __deprecated__ inline profile (for testing purposes only)
  * profileFromRepository: reads a __ReleaseProfile__ from the internal configuration
* Output properties: **N/A**

####  OverwriteVariable
* Description: Overwrite a variable in the release (hard low-level overwrite)
* Input Properties:
  * variableName: name of the variable overwrite
  * overwriteValue: value to change the variable to. If this field is a string None this task wil not do anything
* Output properties: **N/A**

####  loadTemplateProfile
* Description: Load a release template profile
* Input Properties:
  * profileUrl: url to download the profile from. Multiple profiles can be specified by using a semicolon seperated list of urls (url;url)
  * profile: inline profile to load __Development testing purposes__
* Output properties: **N/A**

####  SetReleaseCounter
* Description: Set a release counter in a counterstore. Counter stores are used to transmit data and variable vaules between seperate releases
* Input Properties:
  * counterStore: name of the **ReleaseCounterStore** store to use
  * counterName: name of the counter to set
  * counterValue: value of the counter to set
* Output properties: **N/A**

####  SetReleaseCounterString
* Description: Set a release counter to a string value in a counterstore. this counter can then no longer be used with incrementCounterstore Counter stores are used to transmit data and variable vaules between seperate releases
* Input Properties:
  * counterStore: name of the **ReleaseCounterStore** store to use
  * counterName: name of the counter to set
  * counterValue: value of the counter to set (string value)
* Output properties: **N/A**


####  incrementReleaseCounter
* Description: increment an integer formatted counter in a counterstore. Counter stores are used to transmit data and variable vaules between seperate releases
* Input Properties:
  * counterStore: name of the **ReleaseCounterStore** store to use
  * counterName: name of the counter to increment
* Output properties:
  * outputVariable: name of the variable to store the incremented counter in

####  getReleaseCounter
* Description: retrieve a value from a counterStore
* Input Properties:
  * counterStore: name of the **ReleaseCounterStore** store to use
  * counterName: name of the counter to retrieve
* Output properties:
  * outputVariable: name of the variable to store the retrieved counter in

####  createCounterStore
* Description: Create a counter store in the XL-Release configuration
* Input Properties:
  * counterStore: name of the **ReleaseCounterStore** store to create
* Output properties: **N/A**

####  destroyCounterStore
* Description:  Destroy a counter store in the XL-Release configuration
* Input Properties:
  * counterStore: name of the **ReleaseCounterStore** store to destroy
* Output properties: **N/A**


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
