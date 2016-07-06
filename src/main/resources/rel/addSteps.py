from Base import Base
import pprint
import random
import math
import com.xhaus.jyson.JysonCodec as json
from com.xebialabs.deployit.plugin.api.reflect import Type
import requests, re
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
from com.xebialabs.deployit.plugin.api.reflect import DescriptorRegistry
from com.xebialabs.deployit.plugin.api.reflect import Type
import com.xebialabs.xlrelease.builder.PhaseBuilder as PhaseBuilder
import com.xebialabs.xlrelease.domain.status.PhaseStatus as PhaseStatus

__release = getCurrentRelease()
__phaseApi  = XLReleaseServiceHolder.getPhaseApi()
__taskApi = XLReleaseServiceHolder.getTaskApi()
__repositoryService = XLReleaseServiceHolder.getRepositoryService()


def find_ci_id(name, type):
    sp = SearchParameters()
    sp.setType(Type.valueOf(str(type)))

    for p in XLReleaseServiceHolder.getRepositoryService().listEntities(sp):
        if str(p.getTitle()) == name:
           return p


def createParallelTaskContainer(phaseId):

    taskType = Type.valueOf('xlrelease.ParallelGroup')

    task = taskType.descriptor.newInstance("nonamerequired")

    return  __taskApi.addTask(str(get_target_phase(phaseId)), task)



def createSimpleTaskInContainer(containerId, taskTypeValue, title, propertyMap):
    parentTask = __taskApi.getTask(str(containerId))
    task = createSimpleTaskObject(taskTypeValue, title, propertyMap)
    task.setContainer(parentTask)
    __taskApi.addTask(str(containerId), task)

def createSimpleTaskInPhase(phaseId, taskTypeValue, title, propertyMap):

    try:
        __taskApi.addTask(str(phaseId),createSimpleTaskObject(taskTypeValue,title,propertyMap))
    except:
        print "unable to create Task: %s in Phase: %s" % (title, phaseId)

def createSimpleTaskObject(taskTypeValue, title, propertyMap={}):
    """
    adds a custom task to a phase in the release
    :param phaseId: id of the phase
    :param taskTypeValue: type of task to add
    :param title: title of the task
    :param propertyMap: properties to add to the task
    :return:
    """
    #print propertyMap

    parenttaskType = Type.valueOf("xlrelease.CustomScriptTask")

    parentTask = parenttaskType.descriptor.newInstance("nonamerequired")
    parentTask.setTitle(title)

    childTaskType = Type.valueOf(taskTypeValue)
    childTask = childTaskType.descriptor.newInstance("nonamerequired")
    for item in propertyMap:
        if childTask.hasProperty(item):
            type = childTask.getType()
            desc = type.getDescriptor()
            pd = desc.getPropertyDescriptor(item)

            if str(pd.getKind()) == "CI":
                childTask.setProperty(item,find_ci_id(str(item),pd.getReferencedType()))
            else:
                childTask.setProperty(item,propertyMap[item])

        else:
            Base.info( "dropped property: %s on %s because: not applicable" % (item, taskTypeValue))
    parentTask.setPythonScript(childTask)

    return parentTask



def createSimpleTask(phaseId, taskTypeValue, title, propertyMap):
    """
    adds a custom task to a phase in the release
    :param phaseId: id of the phase
    :param taskTypeValue: type of task to add
    :param title: title of the task
    :param propertyMap: properties to add to the task
    :return:
    """
    #print propertyMap

    parenttaskType = Type.valueOf("xlrelease.CustomScriptTask")

    parentTask = parenttaskType.descriptor.newInstance("nonamerequired")
    parentTask.setTitle(title)

    childTaskType = Type.valueOf(taskTypeValue)
    childTask = childTaskType.descriptor.newInstance("nonamerequired")
    for item in propertyMap:
        if childTask.hasProperty(item):
            childTask.setProperty(item,propertyMap[item])
        else:
            Base.info( "dropped property: %s on %s because: not applicable" % (item, taskTypeValue))
    parentTask.setPythonScript(childTask)

    __taskApi.addTask(str(phaseId),parentTask)

def phase_exists(targetPhase):
    phaseList = phaseApi.searchPhasesByTitle(targetPhase,release.id)
    if len(phaseList) == 1:
        return True

    return False

def get_target_phase(targetPhase):
    """
    search the release for the targetPhase by string name
    for some stupid reason we can't address it by its name ..

    :param targetPhase:string
    :return:phaseId
    """
    phaseList = phaseApi.searchPhasesByTitle(str(targetPhase),release.id)

    if len(phaseList) == 1:

        return phaseList[0]
    else:

        print "Requested phase: %s not found. Creating it in the template first" % targetPhase
        create_phase(targetPhase, release)
        phaseList = phaseApi.searchPhasesByTitle(str(targetPhase),release.id)
        if len(phaseList) == 1:
            return phaseList[0]
        else:
            Base.fatal("unable to create phase %s.. there is something seriously wrong with your installation" % str(targetPhase))
        #should be replaced by some logic to create the phase


def load_profile(profile):
    """
    returns a dict .. if input is json it will return ad dict .. if dict it will return the dict
    :param profile:
    :return:
    """

    if type(profile) is dict:
        return profile
    else:
       Base.info("loading profile from json")
       return json.loads(profile.replace('\n','').replace('\t', '').replace('\r', ''))




def download_json_profile(url):
    Base.info("downloading json from %s" % url)
    error = 300
    output = requests.get(url, verify=False)



    #adding in retry to make all this stuff a little more robust
    # if all else fails .. we are going to retry 10 times ..
    retries = 10
    nr_tries = 0


    while True:
        # increment trie counter
        nr_tries += 1
        Base.info("trying to fetch json from url %s , try nr: %i" % (url, nr_tries))


        # try to fetch a response
        response = requests.get(url, verify=False)

        # if the status code is above 299 (which usually means that we have a problem) retry
        if response.status_code > 299:

            # if the number of retries exceeds 10 fail hard .. cuz that is how we roll
            if nr_tries > retries:
              Base.fatal('Unable to retrieve json from url after %i retries' % retries )

            # warn the user
            Base.warning("unable to retrieve json from url: %s" % url)

            # it is good form to back off a failing remote system a bit .. every retry we are gonna wait 5 seconds longer . Coffee time !!!!
            sleeptime = 5 * int(nr_tries)

            Base.warning("timing out for: %i seconds" % sleeptime)

            # sleep dammit .. i need it ..
            time.sleep(sleeptime)
        else:
            Base.info("Download from %s : succesfull" % url)
            Base.info( str(response.text))
            return str(response.text)

def handle_profile(profile, targetPhase):
    """
    parse the loaded profile and add a task for each item in it
    :param profile: json or dict
    :param targetPhase: phase to add the steps to
    :return:
    """
    loaded_profile = load_profile(profile)
    phaseId = get_target_phase(targetPhase)
    title_nr = 0

    for type, data in loaded_profile.items():

        if __type_step_dict.has_key(type):
            taskTypeValue = __type_step_dict[type]
        else:
            taskTypeValue = type

        for data_item in data:
            final_data_items = dict(data_item.items() + __default_data_items.items())
            title_nr += 1

            title = get_title("dar_build_task_%s_%i" % (type, title_nr), taskTypeValue, data_item)
            Base.info("creating step: %s" % title)

            createSimpleTaskInPhase(phaseId, taskTypeValue, title, final_data_items )


def get_title(title, citype, data):

    Base.info("GATHERING TITLE for %s" % citype)

    if __type_title_dict.has_key(citype):

        new_title = []
        for x in ['prefix', 'data_fields', 'postfix']:
            try:
                out = __type_title_dict[citype][x]

                if type(out) == list:
                    for e in out:


                        try:

                            new_title.append(str(data[e]))
                        except KeyError:
                            Base.warning( 'unable to retrieve %s from step data' % e)
                else:
                      new_title.append(out)
            except KeyError:
                Base.warning('no data defined for field %s' % x)



        return " ".join(new_title)
    else:
        return title


def create_phase(title, release):
    """
    creates a phase at the end of the release
    :param title: title of the phase
    :param release: the release id of THIS release
    :return: true/false
    """

    #danger close
    # generating a random number for the phaseid prefix
    randIdPost = random.randint(100000,9999999)

    # get the template object from the repository service
    template = __repositoryService.read("/"+release.id)

    # get the phases object
    phases = template.getPhases()

    # get the id for the new phase

    #build the new pahse
    phase = PhaseBuilder.newPhase().withTitle(title)\
        .withId(template.getId()+"/Phase" + str(randIdPost))\
        .withRelease(template)\
        .withStatus(PhaseStatus.PLANNED)\
        .build()

    # get the size of the phases object
    phaseIndex = len(phases)

    # we are always appending phases to the end of the release.. so the index will do
    phases.add(phaseIndex, phase)

    # save the phase
    phaseId = __repositoryService.create(phase)

    # save the release
    __repositoryService.update(template)

    return phaseId

def add_step():
    '''
    adds a build step to the designated phase
    :param kwargs:
    :return:
    '''

    # set defaults for all the variables in the build step
    build_step = {}

    build_step["xlrServer"] = "localhost:4516"
    build_step["userName"] = userName
    build_step["password"] = password
    build_step["description"] = "build step for application"
    build_step["variables"] = ""
    build_step["asynch"] = "false"



    # get variables
    #with default

    if kwargs.has_key("xlrServer"):
        xlrServer = kwargs['xlrServer']
    else:
        xlrServer = "localhost"

    if kwargs.has_key("username"):
        userName = userName



def get_default_val(d):
    return d.getDefaultValue()

def get_task_properties_with_defaults(type, required=True, optional=True, hidden=False):
    output = {}
    mockTask = __taskApi.newTask(type)
    desc = mockTask.getTaskType().getDescriptor()


    for d in desc.getPropertyDescriptors():
        if d.getCategory() == "input":
            if required == True:
                if d.isRequired() == True:
                    output[str(d.getName())] = get_default_val(d)
                    continue
            if optional == True:
                if d.isHidden() == False and d.isRequired() == False:
                    output[str(d.getName())] = get_default_val(d)
                    continue
            if hidden == True:
                if d.isHidden() == True:
                    output[str(d.getName())] = get_default_val(d)
    return output

def parse_application_input(input):

    output = {}

    for line in input.split(";"):
        if '=' in line:
            a, v = line.split("=", 1)

            if v != None:
                output[a] = parse_input_values(v)
        else:

            output[line] = {}

    return output

def parse_input_values(input):
    '''
    parses a string formatted param:val,param:val int a dict where param is the key and val is welll .. huh .. the value
    :param v:
    :return: dict
    '''

    output = {}

    for line in input.split(","):
        k, v = line.split(":", 1)
        output[k] = v

    return output

def initialize_steps_dict(phase, container=None, newTaskType=None, existing_hash=None):
    if newTaskType == None:
        newTaskType = taskType

    if existing_hash == None :
        existing_hash = {}


    if existing_hash.has_key(newTaskType) == False:
        existing_hash[newTaskType] = {}

    if container != None:
        if existing_hash[newTaskType].has_key(phase) == False:
            existing_hash[newTaskType][phase] = {}
            for c in container:
                if existing_hash[newTaskType][phase].has_key(c) == False:
                    existing_hash[newTaskType][phase][c] = []
    else:
        if existing_hash[newTaskType].has_key(phase) == False:
            existing_hash[newTaskType][phase] = []


    return existing_hash

def hash_to_string(hash):
    return ",".join(["=".join([key, str(val)]) for key, val in hash.items()])


def add_steps_from_hash(steps_hash):
    '''
    loop over the steps hash and create phases containers and steps of of it
    :param steps_hash:
    :return:
    '''

    for task, phases in steps_hash.items():
        for phase, objectX in phases.items():
            if type(objectX) == list:
                for t in objectX:
                    createSimpleTaskInPhase(phase, task, t['Title'], t)
            if type(objectX) == dict:
                for c, tasks in objectX.items():
                    containerId =  createParallelTaskContainer(phase)
                    for t in tasks:
                        createSimpleTaskInContainer(containerId, task, t['Title'], t)

def compose_application_settings(type, applications, **kwargs):
    '''
    outcome {app : { setting1: val1, settings2: val2}, app2:{}}
    :param type:
    :param applications:
    :return:
    '''
    output = {}
    # parse the given settings used for every step as a default
    default_values = parse_input_values(generalSettings)

     # parse the input where it comes to application specific settings
    application_settings = parse_application_input(applications)

    # get the task types default values
    app_dict = get_task_properties_with_defaults(type)
    # loop over the applications settings dict
    for app, settings in application_settings.items():
        output[app] = {}
        local = app_dict.copy()

        var_hash = {}

     # set the template name we are going to be using for this run
        local['templateName']         = subTemplate
        local['releaseDescription']   = "%s artifacts for %s. using variables" % (taskAction,app)
        local['releaseTitle']         = "%s: %s" % (taskAction, app)
        local['appName']              = app


        for k, v in default_values.items():
            local[k] = v

        for k, v in settings.items():
            local[k] = v

        for k, v in kwargs.items():
            local[k] = v

        for k, v in local.items():
            # if the app dictionay doesnt have the given key add the setting to the variables .. cuz clearly this should have been a variable
            if app_dict.has_key(k) == False:
                var_hash[k] = v
            # else overwrite the app_dictionary with the more specific setting instead of None or the default
            else:
                output[app][k] = v


        output[app]['Title'] = "%s: %s" % (taskAction, app)

        output[app]['variables'] = hash_to_string(var_hash)


    return output

def handle_build():
    '''
    handles the adding of build steps to a running release
    the application setting represents what needs to be done.
    the passed in settings for the build phases captured in the applications string is formatted
    application=param:val,param:val;
    only application is required really, the other settings are named and are passed through to the step as is
    to make this all work we use the xlr.CreateAndStartSubRelease
    :return:
    '''

    #set the phase name
    phase = "build"

    # get the application settings we need
    application_settings = compose_application_settings("xlr.CreateAndStartSubRelease", applications)

    # initialize the list of containers we need
    container = [0]
    # calculate the number of needed containers in a single phase
    nr_containers = math.ceil(len(application_settings.keys()) / int(parallelGroupSize))
    # if we need more then the default one container add them to the list
    cc = 1
    if parallelGroupSize != 0:
        while (nr_containers + 1)> len(container):
            container.append(cc)
            cc += 1

    # initialize the nested hash we're going to use to propagate all the nice little steps
    steps_hash = initialize_steps_dict("build", container)

    #loop over the applications settings dict and create the step descriptions
    ca = 0
    cc = 0
    for x, settings in application_settings.items():
        if parallelGroupSize != 0:
            if cc >= int(parallelGroupSize):
                cc = 0
                ca += 1

        if type(steps_hash[taskType][phase]) == dict:
            steps_hash[taskType][phase][ca].append(settings)
        else:
            steps_hash[taskType][phase].append(settings)

        cc += 1
    # check which settings are needed for the chosen xlr-task and dump the rest in variables

    add_steps_from_hash(steps_hash)

def handle_deploy():
    '''
    handles the adding of build steps to a running release
    the application setting represents what needs to be done.
    the passed in settings for the build phases captured in the applications string is formatted
    application=param:val,param:val;
    only application is required really, the other settings are named and are passed through to the step as is
    to make this all work we use the xlr.CreateAndStartSubRelease
    :return:
    '''
    steps_hash = {}
    #set the phase name
    phases = environments.split(';')

    for phase in phases:
        print phase

        # get the application settings we need
        application_settings = compose_application_settings("xlr.CreateAndStartSubRelease", applications, environment=phase)

        # initialize the list of containers we need
        container = [0]
        # calculate the number of needed containers in a single phase
        nr_containers = math.ceil(len(application_settings.keys()) / int(parallelGroupSize))
        # if we need more then the default one container add them to the list
        cc = 1
        if parallelGroupSize != 0:
            while (nr_containers + 1)> len(container):
                container.append(cc)
                cc += 1

        # initialize the nested hash we're going to use to propagate all the nice little steps
        steps_hash = initialize_steps_dict(phase, container, newTaskType=taskType)

        #loop over the applications settings dict and create the step descriptions
        ca = 0
        cc = 0
        for x, settings in application_settings.items():
            if parallelGroupSize != 0:
                if cc >= int(parallelGroupSize):
                    cc = 0
                    ca += 1

            if type(steps_hash[taskType][phase]) == dict:
                steps_hash[taskType][phase][ca].append(settings)
            else:
                steps_hash[taskType][phase].append(settings)

            cc += 1
        # check which settings are needed for the chosen xlr-task and dump the rest in variables

        add_steps_from_hash(steps_hash)

def validUrl(url):
    x = int(0)
    while x < int(11):
        x += 1
        try:
            r = doHeadRequest(url)
            r.raise_for_status()
            Base.info('%s might be a valid url' % url)
            return True
        except Exception:
            Base.warning('encountered a minor error going to retry')
    return False



#def handle_steps():


# start of the script
#__release = getCurrentRelease()

if taskAction == 'Build':
    #create_phase("build", __release)
    handle_build()

#Applications/Release1529428/Phase123457/Task632453

if taskAction == "Deploy":
    handle_deploy()



# build_step = {"xlr.CreateAndStartSubRelease" : [{"xlrServer" : serverName,
#                                                  "username": password,
#                                                  "templateName": templateName,
#                                                  "releaseTitle", releaseTitel,
#                                                 "releaseDescription", description,
#                                                 "variables", variables,
#                                                 "asynch": "false"}]}
#


# def tester():
#     print dir(__taskApi)
#     task = __taskApi.newTask('xlr.CreateAndStartSubRelease')
#     print dir(task)
#     type =  task.getTaskType()
#     print dir(type)
#     print type.getTypeSource()
#     desc = type.getDescriptor()
#     print desc.getPropertyDescriptors()
#     for d in desc.getPropertyDescriptors():
#         print dir(d)
#         print d.getName()
#         print d.isHidden()
#         print d.isRequired()
#         print d.defaultValue()