#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.reflect.Type as Type
import com.xebialabs.xlrelease.api.v1.forms.Comment as Comment
from com.xebialabs.xlrelease.api.v1 import TaskApi
import sys, string, time
import httplib
from urlparse import urlparse
from requests.auth import HTTPBasicAuth
import requests


from com.xebialabs.xlrelease.domain import Task
from java.text import SimpleDateFormat


import com.xhaus.jyson.JysonCodec as json


__release = getCurrentRelease()

# compile a regex that will sort out if the variables where in the template with the ${} already in the name or not
__variable_start_regex = re.compile('^\$\{', re.IGNORECASE)

# setup the communication object to artifactory


# sp = SearchParameters()
# sp.setType(Type.valueOf('rel.ReleaseProfile'))
# for x in XLReleaseServiceHolder.getRepositoryService().listEntities(sp):
#     print type(x)
#     print x.getTitle()
#     print x.getProperty('variablesJson')
#     print dir(x)
    #print XLReleaseServiceHolder.getRepositoryService().read(str(x))

#EXAMPLE json

# {"variables":
#     {"test1": "batman",
#      "test2": "bane",
#      "test3": "scarecrow" }
#      ,"toggles" :
#       [{"phase" : "deploy_to_dev", "task" : "shitty", "skip" : "true"},
#        {"phase" : "deploy_to_dev", "task" : "shitty1", "skip" : "true"}]
#      ,"tasks": {}}
#
# {"variables":{"test1": "batman","test2": "bane","test3": "scarecrow" },"toggles" :[{"phase" : "deploy_to_dev", "task" : "shitty", "skip" : "true"},{"phase" : "deploy_to_dev", "task" : "shitty1", "skip" : "true"}],"tasks": {}}
# def deleteTaskPatch(taskId):
#     return releaseActorService.deleteTask(taskId)
#
# TaskApi.deleteTask = deleteTaskPatch
#
#
# if servicenowResponse.status == RECORD_CREATED_STATUS:
#     data = json.loads(servicenowResponse.read())
#     sysId = data["result"]["sys_id"]
#     print "Created %s in Service Now." % (sysId)
# else:
#     print "Failed to create record in Service Now"
#     servicenowResponse.errorDump()
#     sys.exit(1)
class ArtifactoryCommunicator(object):

    def __init__(self, **params):
        self.url = params['url']

        self.username = None
        self.password = None
        self.auth = None

        if params.has_key('username'):
            self.username = params['username']
        if params.has_key('password'):
            self.password = params['password']

        if self.username and self.password:
            self.auth=HTTPBasicAuth(self.username, self.password)

    def get_artifact(self,repo, artifact):
            return self.do_get("/artifactory/simple/%s/%s" % (repo, artifact))

    def do_get(self, path):
            return self.do_it("GET", path, "")

    # TODO: remove this once tested
    # def do_it(self, verb, path, doc, parse_response=True):
    #         #print "DO %s %s on %s " % (verb, path, self.endpoint)
    #
    #         parsed_url = urlparse(self.url)
    #         if parsed_url.scheme == "https":
    #             conn = httplib.HTTPSConnection(parsed_url.hostname, parsed_url.port)
    #         else:
    #             conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
    #
    #         try:
    #             auth = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
    #             headers = {"content-type": "application/json", "Authorization": "Basic %s" % auth}
    #             print "blahblah"
    #             conn.request(verb, path, doc, headers)
    #             response = conn.getresponse()
    #             #print response.status, response.reason
    #             if response.status != 200 and response.status != 204 and response.status !=201:
    #                 raise Exception("Error when requesting remote url %s [%s]:%s" % (path,  response.status, response.reason))
    #
    #             if parse_response:
    #                 data = str(response.read())
    #                 decoded = json.loads(data)
    #                 print "blah"
    #                 return decoded
    #             return None
    #         finally:
    #             conn.close()

    def do_it(self,verb, path, data=None, params=None, parse_response=True):
        print "downloading json from %s" % self.url
        error = 300

        url = "%s%s" % (self.url, path)

        if verb == "GET":
            output = requests.get(url)
        elif verb =="POST":
            if params:
                output = requests.post(url,params=params )
            elif data:
                output = requests.post(url, data=data)
            else:
                output = requests.post(url)
        else:
            print "method %s not supported yet " % verb
            return None

        output.raise_for_status()


        print "Download from %s : succesfull" % url

        if parse_response:
            json_data = str(output.text)
            decoded = json.loads(json_data)
            print decoded
            return decoded
        else:
            return output.text

def load_profile(profile):
    sp = SearchParameters()
    sp.setType(Type.valueOf('rel.ReleaseProfile'))

    for p in XLReleaseServiceHolder.getRepositoryService().listEntities(sp):
        if str(p.getTitle()) == profile:
            return json.loads(p.getProperty('profileJson'))



def load_profile_from_url(repository, artifact, server):
    art = ArtifactoryCommunicator(**server)
    print art
    return art.get_artifact(repository, artifact)

def get_variables(profile):
    return profile["variables"]

def get_toggles(profile):
    return profile["toggles"]


def get_phase_dict():
    phases = {}

    for p in __release.phases:
        phases[str(p.title)] = p

    return phases

def get_tasks_by_phase_dict(phase):
    tasks = {}
    for t in phase.tasks:
        tasks[str(t.title)] = t
    return tasks

def get_tasks_for_phase_by_title(phaseTitle):

    phasedict = get_phase_dict()

    if phasedict.has_key(phaseTitle):
        return  get_tasks_by_phase_dict(phasedict[phaseTitle])
    else:
        return False



def get_task_by_phase_and_title(phaseTitle, taskTitle):
    tasks = get_tasks_for_phase_by_title(phaseTitle)
    if tasks:
        if tasks.has_key(taskTitle):
            return tasks[taskTitle]

    return False


def createSimpleTask(phaseId, taskTypeValue, title, propertyMap):
    parenttaskType = Type.valueOf(taskTypeValue)
    parentTask = parenttaskType.descriptor.newInstance("nonamerequired")
    parentTask.setTitle(title)
    sdf = SimpleDateFormat("yyyy-MM-dd hh:mm:ss")
    for item in propertyMap:
        if item.lower().find("date") > -1:
            if propertyMap[item] is not None and len(propertyMap[item]) != 0:
                parentTask.setProperty(item,sdf.parse(propertyMap[item]))
        else:
            parentTask.setProperty(item,propertyMap[item])
    taskApi.addTask(phaseId,parentTask)

def update_release_with_variables(profile):
    """
    Handles resolving the variables and injecting them into the template
    :return:
    """

    newVariables = {}
    for key, value in get_variables(profile).items():
        if re.match(__variable_start_regex, key) is None:
            key = "${%s}" % (key)
            # if the value is a dict with further specification of where to retrieve the variable from resolve it

            if type(value) is dict:
                value = resolve_variable(**value)
            newVariables[key] = value
    __release.setVariableValues(newVariables)
    releaseApi.updateRelease(release.id, __release)

def resolve_variable(**params):
    """
    try to resolve the variable with the information specified
    params can handle:
    :default_value string: the default value to set in case no value could be retrieved
    :collector dict: information used retrieve the value from an additional source
    :param params:
    :return: result for the resolve attempt
    """

    # set our return value to None
    ret_val = None
    collector_val = None

    # start by setting the default value if specified
    if params.has_key('default_value'):
        ret_val = params['default_value']

    # act on the collector parameter
    if params.has_key('collector'):
        # if there is no type specified just pass it to the json collector, which is our default choice
        if not params['collector'].has_key('type'):
            collector_val = handle_json_collector(**params['collector'])
        if params['collector'].has_key('type'):
            collector_val = handle_json_collector(**params['collector'])
        else:
            print "collector type is not supported.... yet!!!"

    if collector_val:
        ret_val = collector_val

    print "ret_val"
    print ret_val
    return ret_val

def handle_json_collector(**params):
    """
    retrieve a template variable by means of json rest call
    :username: username if we need to authenticate (optional)
    :password: password if we need to authenticate (optional)
    :url: url to hit when retrieving the json
    :path: path to the field we want to retrieve in the json file
    :param params:
    :return:
    """
    requests_params = {}

    #if we need authentication then lets set it up
    if params.has_key('username') and params.has_key('password'):
        requests.params['auth']=HTTPBasicAuth(params['username'], params['password'])

    if params.has_key('url'):
        response = requests.get(params['url'], **requests_params)

        response.raise_for_status()
        print response.text

        inputDictionary = json.loads(str(response.text))
        print inputDictionary
        # if the path parameter was given parse it and see if we can retrieve a value . if path was not set return None
        # i could have chosen to return the json in its raw form, but that might lead to unwanted situations and code injection
        if params.has_key('path'):

            # get a list with the fields where looking for
            field_list = params['path'].split('/')
            len_field = len(field_list)
            field_counter = 1

            # loop over the field list and see if we can go down the rabbit hole to retrieve the value where looking for
            for field in field_list:
                if inputDictionary.has_key(field):

                    # if the value of the inputDictionary is another dictionary: input that second dict into inputDictionary
                    # and take it back into the loop
                    if type(inputDictionary[field]) == dict:
                        inputDictionary = inputDictionary[field]

                    # if the value is a loop .. check if it only contains one value .. if so return it as a string. If not return None
                    elif type(inputDictionary[field]) == list:

                        if len(inputDictionary[field]) < 2:
                            print "found %s using path %s" % (inputDictionary[field], params['path'])
                            return str(inputDictionary[field][0])
                        else:
                            print "found mutiple values:%s using path %s" % (inputDictionary[field], params['path'])
                            print "this can lead to unpredictable results so no value will be used"
                            return None

                    # if the field_counter matches the length of the field list we used as input to this loop then we must have found our value
                    # remember we allready tackled lists and dictionaries so no need to worry about those
                    elif len_field == field_counter :
                        print "found %s using path %s" % (inputDictionary[field], params['path'])
                        return str(inputDictionary[field])

                    else:
                        print "the requested path of %s could not be found in the json document. returning None instead"
                        return None

                else:
                    print "the requested path of %s could not be found in the json document. returning None instead"
                    return None

                field_counter += 1

        else:
            print "parameter path should be set when using json collector. This parameter seems to be missing so returning None"
            return None

def get_comment(commentText):

    comment = Comment()
    comment.setComment(commentText)
    return comment

def handle_toggles(profile):
    toggles = get_toggles(profile)

    for t in toggles:
        print str(t)
        task = get_task_by_phase_and_title(str(t["phase"]), str(t["task"]))
        if task:
            print "removing task %s " % task
            _repositoryService.delete(str(task))

        else:
            print "task not found"




profile = load_profile_from_url(repository, artifact, server)
update_release_with_variables(profile)
handle_toggles(profile)
# update_release_with_variables(url)
# handle_toggles(url)
