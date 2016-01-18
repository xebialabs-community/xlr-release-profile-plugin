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

from com.xebialabs.xlrelease.domain import Task
from java.text import SimpleDateFormat


import com.xhaus.jyson.JysonCodec as json


__release = getCurrentRelease()

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


def load_profile(profile):
    sp = SearchParameters()
    sp.setType(Type.valueOf('rel.ReleaseProfile'))

    for p in XLReleaseServiceHolder.getRepositoryService().listEntities(sp):
        if str(p.getTitle()) == profile:
            return json.loads(p.getProperty('profileJson'))



def get_variables(profile):
    return load_profile(profile)["variables"]

def get_toggles(profile):
    return load_profile(profile)["toggles"]


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
    variable_start_regex = re.compile('^\$\{', re.IGNORECASE)
    newVariables = {}
    for key, value in get_variables(profile).items():
        if re.match(variable_start_regex, key) is None:
            key = "${%s}" % (key)
            newVariables[key] = value
    __release.setVariableValues(newVariables)
    releaseApi.updateRelease(release.id, __release)

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





update_release_with_variables(Profiles)
handle_toggles(Profiles)
