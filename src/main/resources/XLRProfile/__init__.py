
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
#from XLRProfile import XLRProfile as XLRProfile
#
import sys
import re
import collections
import requests

import com.xhaus.jyson.JysonCodec as json
from com.xhaus.jyson import JSONDecodeError

from requests.auth import HTTPBasicAuth

import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.reflect.Type as Type

class CollectorError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self,value, msg):
        self.value = value
        self.msg = msg

    def __str__(self):
        return "%s : %s" % (self.msg, self.value)

class Collector():
    """
    base class for all collectors
    takes care of validating that all collector needed parameters are passed in
    """

    attributes = []
    optional_attributes = []

    def __init__(self, **params):
       self.validate(**params)

    def validate(self, **params):
        for a in self.attributes:
            if params.has_key(a) is not True:
                raise CollectorError(a, "unable to satisfy all attributes")

    def resolve(self):
        return None


class JsonCollector(Collector):

    attributes = ["url", "path"]
    optional_attributes = []

    def __init__(self, **params):

        Collector.__init__(self, **params)

        self.requests_params = {}

        if params.has_key('username') and  params.has_key('password'):
            self.requests_params['auth'] = HTTPBasicAuth(params['username'], params['password'])

        self.__collector_params = params


    def resolve(self):
        """
        resolve the collector
        :return: string
        """
        return self.get_path(self.load_json(self.__collector_params['url']), self.__collector_params['path'])


    def load_json(self, url):
        """
        loads json from a url and translates it into a dictionary
        :param url:
        :return:
        """

        #adding in retry to make all this stuff a little more robust
        retries = 10
        nr_tries = 0

        output = None

        while not retries or nr_tries < retries:

            nr_tries += 1
            print "trying to fetch json from url %s , try nr: %i" % (url, nr_tries)

            #fetch the json
            try:
                response = requests.get(url, verify=False, **self.requests_params)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print "unable to retrieve json from url: %s" % url
                print e.request
                output = None

            #try to decode it
            try:
                print "%s responded with:" % url
                print response.text
                output =  json.loads(str(response.text))
                break
            except Exception:
                print "unable to decode information provided by %s" % url
                output =  None
            except JSONDecodeError:
                print "unable to decode output, not json formatted"
                output = None

        return output

    def get_path(self, json, path):
        """
        traverses the dictionary derived from the json to look if it can satisfy the requested path
        :param json:
        :param path:
        :return:
        """

        if (type(path) is str) or (type(path) is unicode):
            path = str(path).split('/')

        field = path.pop(0)

        try:
            if json.has_key(field):
                if type(json[field]) == dict:
                    return self.get_path(json[field], path)

                elif type(json[field]) == list:
                    if len(json[field]) < 2 :
                        print "found %s" % (json[field][0])
                        return str(json[field][0])

                elif len(path) == 0:
                    print "found %s using path %s" % (field, path)
                    return str(json[field])
            else:
                print "the requested path of %s could not be found in the json document. returning None instead"
                return None
        except Exception:
            print "Error encountered during resolution"




class XLRProfile(collections.MutableMapping):



    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        """
        TODO: need to come up with a way to resolve variables used inside the profile
                Best way to do this i think is to pull all available variables form the xlr context and match the
                dictonary's values against them
        :param args:
        :param kwargs:
        :return:
        """

         # pull in the xlrelease apis
        self.__releaseApi        = XLReleaseServiceHolder.getReleaseApi()
        self.__repositoryService = XLReleaseServiceHolder.getRepositoryService()
        self.__taskApi           = XLReleaseServiceHolder.getTaskApi()

        self.__variable_start_regex = re.compile('\$\{', re.IGNORECASE)


        self.store = dict()



        if kwargs.has_key('url'):
            kwargs = self.load_from_url(kwargs['url'])
        elif kwargs.has_key('repoId'):
            kwargs = self.load_profile_from_xlr_repo(kwargs['repoId'])
        elif kwargs.has_key('repoString'):
            kwargs = json.loads(str(kwargs['repoString']))

        self.update(dict(*args, **kwargs))  # use the free update to set keys


    def resolve_xlr_template_variables(self, release_id, var_dict = None):

        #if no var_dict specified get the profiles variables as default action
        if var_dict == None:
            var_dict = self.variables()

        for k, v in var_dict.items():
            if type(v) == dict:
                var_dict[k] = self.resolve_xlr_template_variables(release_id, v)
            if type(v) == str or type(v) == unicode:
                v = str(v)
                if '${' in v:
                    print "found variable in %s" % v
                    for x, y in self.get_release_variables(release_id).items():
                        if x in v :
                           print "replacing variable %s with value %s" % (x, y)
                           v = v.replace(x, y)
                           var_dict[k] = v

        return var_dict





    def get_release_variables(self,release_id):
        release = self.__releaseApi.getRelease(str(release_id))
        return release.getVariableValues()

    def __getitem__(self, key):
        if self.store.has_key(self.__keytransform__(key)):
            return self.store[self.__keytransform__(key)]
        else:
            return None

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

    def set_variable(self, key, value):
        self.store['variables'][key] = value

    def set_variables_from_dict(self, var_dict):
        self.store['variables'] = var_dict

    def toggles(self):
        return self.__getitem__('toggles')

    def load_from_url(self, url):
        """
        reaches out to a url and loads the profile
        :param url:
        :return: dict: profile
        """
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
            if str(p.getTitle()) == profileName:
                return json.loads(p.getProperty('profileJson'))


    def resolve_variables(self):

        for key, val in self.variables():
            if type(val) == dict:
                solution = self.resolve_variable(val)
                if solution == None:
                    print "value for %s could not be found using the specified collector" % key
                    sys.exit(2)
                else:
                    print "retrieved value: %s for %s" % (solution, key)
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
            # if not params['collector'].has_key('type'):
            #     collector_val = self.handle_json_collector(**params['collector'])
            # if params['collector'].has_key('type'):
            #     collector_val = self.handle_json_collector(**params['collector'])
            # else:
            #     print "collector type is not supported.... yet!!!"
            #     sys.exit(2)
            # if there is no type specified just pass it to the json collector, which is our default choice
            if not params['collector'].has_key('type'):
                col_params = params['collector']
                collector_val = JsonCollector(**col_params).resolve()
            if params['collector'].has_key('type'):
                col_params = params['collector']
                collector_val = JsonCollector(**col_params).resolve()
            else:
                print "collector type is not supported.... yet!!!"
                pass


        if collector_val:
            ret_val = collector_val
        return ret_val



    def persist_variables_to_release(self, releaseId):
        """
        Handles resolving the variables and injecting them into the template
        :return:
        """
        release = self.__releaseApi.getRelease(releaseId)

        #handle variables inside the release first
        self.set_variables_from_dict(self.resolve_xlr_template_variables(releaseId))

        print "resolved profile:"
        print self.variables()

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

        if self.toggles:
            try:
                for t in self.toggles:
                    task = self.get_task_by_phase_and_title(str(t["phase"]), str(t["task"]), release)
                    if task:
                        print "removing task %s " % task
                        self.__repositoryService.delete(str(task))

                    else:
                        print "task not found"
            except TypeError:
                print "toggles not valid... moving on"
        else:
            print "no toggles found"



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
