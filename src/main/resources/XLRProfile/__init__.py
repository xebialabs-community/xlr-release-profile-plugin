
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
#from XLRProfile import XLRProfile as XLRProfile
import sys
import re
import collections
import requests

import com.xhaus.jyson.JysonCodec as json
from requests.auth import HTTPBasicAuth
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.reflect.Type as Type



class XLRProfile(collections.MutableMapping):



    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):

         # pull in the xlrelease apis
        self.__releaseApi        = XLReleaseServiceHolder.getReleaseApi()
        self.__repositoryService = XLReleaseServiceHolder.getRepositoryService()
        self.__taskApi           = XLReleaseServiceHolder.getTaskApi()

        self.__variable_start_regex = re.compile('^\$\{', re.IGNORECASE)


        self.store = dict()



        if kwargs.has_key('url'):
            kwargs = self.load_from_url(kwargs['url'])
        elif kwargs.has_key('repoId'):
            kwargs = self.load_profile_from_xlr_repo(kwargs['repoId'])
        elif kwargs.has_key('repoString'):
            kwargs = json.loads(str(kwargs['repoString']))

        self.update(dict(*args, **kwargs))  # use the free update to set keys



    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def variables(self):
        return self.__getitem__('variables')

    def set_variable(selfs, key, value):
        self.store['variables'][key] = value

    def toggles(self):
        return self.__getitem__('toggles')

    def load_from_url(self, url):
        """
        reaches out to a url and loads the profile
        :param url:
        :return: dict: profile
        """
        print 1
        response = requests.get(url, verify=False)
        response.raise_for_status()

        return json.loads(str(response.text))

    def load_profile_from_xlr_repo(self, profileName):
        """
        load the profile from the xlr repository
        :param profileName: name of the profile as it was configured
        :return:
        """
        sp = SearchParameters()
        sp.setType(Type.valueOf('rel.ReleaseProfile'))

        for p in self.__repositoryService.listEntities(sp):
            if str(p.getTitle()) == profile:
                return json.loads(p.getProperty('profileJson'))


    def resolve_variables(self):

        for key, val in self.variables():
            if type(val) == dict:
                solution = self.resolve_variable(val)
                self.set_variable(key, solution)

    def resolve_variable(self, **params):
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
                collector_val = self.handle_json_collector(**params['collector'])
            if params['collector'].has_key('type'):
                collector_val = self.handle_json_collector(**params['collector'])
            else:
                print "collector type is not supported.... yet!!!"
                sys.exit(2)

        if collector_val:
            ret_val = collector_val

        return ret_val

    def handle_json_collector(self, **params):
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

        # if we need authentication then lets set it up
        if params.has_key('username') and params.has_key('password'):
            requests.params['auth'] = HTTPBasicAuth(params['username'], params['password'])

        if params.has_key('url'):
            response = requests.get(params['url'], **requests_params)

            response.raise_for_status()

            inputDictionary = json.loads(str(response.text))
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
                        elif len_field == field_counter:
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


    def persist_variables_to_release(self, releaseId):
        """
        Handles resolving the variables and injecting them into the template
        :return:
        """
        release = self.__releaseApi.getRelease(releaseId)
        newVariables = {}
        for key, value in self.variables().items():
            if re.match(self.__variable_start_regex, key) is None:
                key = "${%s}" % (key)
                if type(value) is dict:
                    value = self.resolve_variable(**value)
                newVariables[key] = value
        release.setVariableValues(newVariables)
        self.__releaseApi.updateRelease(releaseId, release)

    def handle_toggles(self, releaseId):

        release = self.__releaseApi.getRelease(releaseId)
        for t in self.toggles():
            task = self.get_task_by_phase_and_title(str(t["phase"]), str(t["task"]), release)
            if task:
                print "removing task %s " % task
                self.__repositoryService.delete(str(task))

            else:
                print "task not found"



    def get_phase_dict(self, release):
        phases = {}

        for p in release.phases:
            phases[str(p.title)] = p

        return phases

    def get_tasks_by_phase_dict(self, phase, release):
        tasks = {}
        for t in phase.tasks:
            tasks[str(t.title)] = t
        return tasks

    def get_tasks_for_phase_by_title(self, phaseTitle, release):

        phasedict = self.get_phase_dict(release)

        if phasedict.has_key(phaseTitle):
            return  self.get_tasks_by_phase_dict(phasedict[phaseTitle], release)
        else:
            return False



    def get_task_by_phase_and_title(self, phaseTitle, taskTitle, release):
        tasks = self.get_tasks_for_phase_by_title(phaseTitle, release)
        if tasks:
            if tasks.has_key(taskTitle):
                return tasks[taskTitle]

        return False
