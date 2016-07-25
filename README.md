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
..* variableName: name of the variable to make optional

##### Output properties: **N/A**

####  SetDefaultValue
####  LoadDynamicProfile
####  OverwriteVariable
####  loadTemplateProfile

####  SetReleaseCounter
####  SetReleaseCounterString
####  incrementReleaseCounter
####  getReleaseCounter
####  createCounterStore
####  destroyCounterStore




    <type type="rel.MakeVariableOptional" extends="rel.ProfileTask">
        <property name="variableName" label="Variable to Make Optional" category="output"/>
    </type>

    <type type="rel.SetDefaultValue" extends="rel.ProfileTask">
        <property name="variableName" label="Variable to Make Optional" category="output"/>
        <property name="defaultValue" label="default value to assign" category="input"/>
    </type>

    <type type="rel.ReleaseProfile" extends="xlrelease.Configuration">
        <property name="profileJson" default="{}" size="large"/>
    </type>

    <type type="rel.LoadDynamicProfile" extends="rel.ProfileTask" description="Load release profile">
        <property name="profileUrl" label="profile url" required="false" category="input"/>
        <property name="profiles" label="inline profile to load" required="false" category="input" size="large"/>
        <property name="profileFromRepository" label="Profile stored in xlr repository" category="input"
                  required="false"/>
    </type>

    <type type="rel.OverwriteVariable" extends="rel.ProfileTask">
        <property name="variableName" label="Variable overwrite" category="input"/>
        <property name="overwriteValue" label="value to assign" category="input" default="None"/>
    </type>

    <!-- for backwards compatibility -->
    <type type="rel.LoadProfileFromUrl" extends="rel.LoadDynamicProfile" description="backward compatibility"/>

    <!-- release counter stuff -->


    <type type="rel.releaseCounterTask" extends="rel.ProfileTask" virtual="true">
        <property name="counterStore" default="default" label="name of the counter Store" kind="string" required="true"
                  category="input"/>
        <property name="iconLocation" default="rel/profile.png" hidden="true"/>
        <property name="scriptLocation" default="rel/ReleaseCounter.py" category="input" hidden="true"/>
    </type>

    <type type="rel.SetReleaseCounter" extends="rel.releaseCounterTask"
          description="set a counter tied to this release">
        <property name="counterValue" label="value of the counter to set" kind="integer" required="true"
                  category="input"/>
        <property name="taskAction" label="what to do when we get to the script" kind="string" required="true"
                  default="set" hidden="true" category="input"/>
        <property name="counterName" label="name of the counter" kind="string" required="true" category="input"/>
    </type>

    <type type="rel.SetReleaseCounterString" extends="rel.releaseCounterTask"
          description="set a counter tied to this release but as string">
        <property name="counterValue" label="value of the counter to set" kind="string" required="true"
                  category="input"/>
        <property name="taskAction" label="what to do when we get to the script" kind="string" required="true"
                  default="setString" hidden="true" category="input"/>
        <property name="counterName" label="name of the counter" kind="string" required="true" category="input"/>
    </type>

    <type type="rel.incrementReleaseCounter" extends="rel.releaseCounterTask"
          description="get the release counter and increment it before returning">
        <property name="outputVariable" label="name of the variable" kind="string" required="true" category="output"/>
        <property name="counterName" label="name of the counter" kind="string" required="true" category="input"/>
        <property name="taskAction" label="what to do when we get to the script" kind="string" required="true"
                  default="increment" hidden="true" category="input"/>
    </type>

    <type type="rel.getReleaseCounter" extends="rel.releaseCounterTask"
          description="get the release counter and increment it before returning">
        <property name="outputVariable" label="name of the variable" kind="string" required="true" category="output"/>
        <property name="counterName" label="name of the counter" kind="string" required="true" category="input"/>
        <property name="taskAction" label="what to do when we get to the script" kind="string" required="true"
                  default="get" hidden="true" category="input"/>
    </type>

    <type type="rel.createCounterStore" extends="rel.releaseCounterTask" description="Create a fresh new counter store">
        <property name="taskAction" label="what to do when we get to the script" kind="string" required="true"
                  default="createStore" hidden="true" category="input"/>
    </type>
    <type type="rel.destroyCounterStore" extends="rel.releaseCounterTask" description="Destroy a counter store">
        <property name="taskAction" label="what to do when we get to the script" kind="string" required="true"
                  default="destroyStore" hidden="true" category="input"/>
    </type>

    <type type="rel.ReleaseCounterStore" extends="xlrelease.Configuration">
        <property name="counterStorage" default="{}" kind="string"/>
        <property name="modTime" label="time last modification" kind="string"/>
    </type>

    <!-- self tagging releases -->
    <type type="rel.setReleaseTag" extends="rel.ProfileTask">
        <property name="tag" required="true" label="tag to ad to the release" kind="string" category="input"/>
    </type>
    <type type="rel.loadTemplateProfile" extends="rel.ProfileTask">
        <property name="scriptLocation" default="rel/LoadTemplateProfile.py" category="input" hidden="true"/>
        <property name="profile_url" kind="string" required="false" hidden="false" category="input"/>
        <property name="profile" label="inline profile to load" required="false" category="input" size="large"/>
    </type>


</synthetic>


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
