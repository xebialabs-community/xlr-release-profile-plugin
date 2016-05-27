
import com.xhaus.jyson.JysonCodec as json

import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.udm.ConfigurationItem as ConfigurationItem
import com.xebialabs.xlrelease.domain.Configuration as Configuration
import com.xebialabs.deployit.plugin.api.reflect.Type as Type
import com.xebialabs.deployit.jcr
import com.xebialabs.deployit.repository
from com.xebialabs.deployit.plugin.api.reflect import DescriptorRegistry
from com.xebialabs.deployit.plugin.api.reflect import Type
import com.xebialabs.deployit.engine.api.dto.ValidatedConfigurationItem

from Base import Base

import datetime

# Globals
__repositoryService = XLReleaseServiceHolder.getRepositoryService()
__ciType = 'rel.ReleaseCounterStore'

StorageTimestamp = " "



def get_ci_object(ciType, id):
    if not DescriptorRegistry.exists(Type.valueOf(ciType)):
        raise ValueError('Unknown CI type %s' % ciType)
    type = Type.valueOf(ciType)
    configurationItem = type.descriptor.newInstance(id)
    return configurationItem

def check_ci_for_validations(ci):
    if isinstance(ci, com.xebialabs.deployit.engine.api.dto.ValidatedConfigurationItem) and not ci.validations.isEmpty():
        raise ValueError('Configuration item contained validation errors: %s' % ci.validations.toString())

def create_ci(storeName):
    '''
    creates a ci in the xl-release repository under /Configuration/Custom of type rel.ReleaseCounterStore
    :param storeName:
    :return:
    '''
    Base.info("creating Counter Store: %s " % storeName)

    ci = get_ci_object(__ciType,  'Configuration/Custom/%s' % storeName)

    ci.setTitle(storeName)

    check_ci_for_validations(ci)

    try:
        __repositoryService.create(ci)
        Base.info("Counter Store: %s created")
    except com.xebialabs.deployit.repository.ItemAlreadyExistsException as e:
        Base.error(e)
        Base.error("Counter Store already exists... moving on")
    except Exception:
        Base.fatal('an error occured while trying to create Counter Store: %s' % storeName)
        sys.exit(2)

def destroy_counter_store(storeName):
    '''
    Destroys a release counter store
    :param storeName:
    :return:
    '''

    if ci_exists(storeName, __ciType):

        ci = load_ci_from_repo(storeName, __ciType )

        __repositoryService.delete(ci.getId())
        Base.info("Counter Store: %s destroyed.... BOOOM" % storeName)

    else:
        Base.error("Counter Store: %s did not exist... Moving on cuz that is how we roll" % storeName)


def time_stamp():
    return str(datetime.datetime.now().isoformat())

def get_counter_storage(counterStoreTitle, updateTimeStamp=True):

    global StorageTimestamp


    counter_store_ci = load_ci_from_repo(counterStoreTitle, __ciType)
    if updateTimeStamp == True:
        StorageTimestamp = counter_store_ci.getProperty('modTime')

    return json.loads(counter_store_ci.getProperty('counterStorage'))

def get_counter_timestamp(counterStoreTitle):

    return load_ci_from_repo(counterStoreTitle, __ciType).getProperty('modTime')

def update_counter_storage(counterStoreTitle, key, value):

    # get a timestamp.
    # because we do not want two proccesses saving to the same store at the same time (data-loss is not a good thing)

    Base.info("attempting to update counterStorage")

    while True:
        data = get_counter_storage(counterStoreTitle)

        if type(data) == dict:
           data[key] = value
        else:
            data = {key : value}

        if update_ci_to_repo(counterStoreTitle, {'counterStorage': data} ) == True:
            Base.info("Counter storage ci: %s saved succesfully" % counterStoreTitle)
            return True

        Base.warning("unable to save counter due to deadlock situation.... retrying")


def update_ci_to_repo(storeName, data):



    Base.info("writing ci: %s to repo" % storeName)

    global StorageTimestamp
    # get the store
    store = load_ci_from_repo(storeName, __ciType)

    # set the properties on the ci to be updated
    for k, v in data.items():

        store.setProperty(k, json.dumps(v))

    store.setProperty('modTime', time_stamp())
    # write back to xlr
    if get_counter_timestamp(storeName) == StorageTimestamp:
        try:
            __repositoryService.update(store)
            return True
        except com.xebialabs.deployit.jcr.RuntimeRepositoryException as e:
            Base.error('Error detected while saving %s' % storeName)
            Base.error('Error: %s' % e)
            return False
        except com.xebialabs.deployit.repository.ItemConflictException as e:
            Base.error('Error detected while saving %s' % storeName)
            Base.error('Error: %s' % e)
            return False
    else:
        Base.error('deadlock collision detected while saving %s' % storeName)
        return False



def load_ci_from_repo(storeName, type):

    sp = SearchParameters()
    sp.setType(Type.valueOf(type))

    for p in __repositoryService.listEntities(sp):
        print p.getId()
        if str(p.getTitle()) == storeName:
            return p

    Base.fatal("unable to find json data repository: %s" % storeName)
    sys.exit(2)

def ci_exists(storeName, type):

    sp = SearchParameters()
    sp.setType(Type.valueOf(type))

    for p in __repositoryService.listEntities(sp):

        if str(p.getTitle()) == storeName:
            return True

    return False


def create_or_update_counter(counterStoreTitle, key, value):

    update_counter_storage(counterStoreTitle, key, value)

def get_counter_value(counterStoreTitle, key):
    try:
      cs = get_counter_storage(counterStoreTitle)
      return cs[key]
    except KeyError:
      return 1

if taskAction == 'set':
    Base.info("setting release counter")
    update_counter_storage(counterStore, counterName, counterValue)
elif taskAction == 'setString':
    Base.info("assigning a string to the release counter")
    update_counter_storage(counterStore, counterName, counterValue)
elif taskAction == 'get':
    Base.info("getting release counter")
    outputVariable = get_counter_value(counterStore, counterName)
elif taskAction == 'increment':
    Base.info("incrementing release counter")
    outputVariable = get_counter_value(counterStore, counterName)
    outputVariable = outputVariable + 1
    update_counter_storage(counterStore, counterName, outputVariable)
elif taskAction == 'createStore':
    Base.info("creating release counterstore: %s" % counterStore )
    create_ci(counterStore)
elif taskAction == 'destroyStore':
    Base.info("Destroying release counterstore: %s" % counterStore )
    destroy_counter_store(counterStore)
else:
    Base.info("nothing to do ")


