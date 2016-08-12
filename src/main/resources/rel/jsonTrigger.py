#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY Liberty Mutual.
#

###################################################################################
#  Name: release Json  Trigger
#
#  Description: Trigger new release when a call to a json producing rest interface turns up a new result
#
###################################################################################
import sys
import time
from Base import Base

import requests
import com.xhaus.jyson.JysonCodec as json
from com.xhaus.jyson import JSONDecodeError
from requests.auth import HTTPBasicAuth


initialFire = True


def load_json(url, **requests_params):
        """
        loads json from a url and translates it into a dictionary
        :param url:
        :return:
        """

        # adding in retry to make all this stuff a little more robust
        # if all else fails .. we are going to retry 10 times ..
        retries = 3
        nr_tries = 0

        output = None

        while True:
            # increment trie counter
            nr_tries += 1
            Base.info("trying to fetch json from url %s , try nr: %i" % (url, nr_tries))


            # try to fetch a response
            response = requests.get(url, verify=False, **requests_params)

            # if the status code is above 299 (which usually means that we have a problem) retry
            if response.status_code > 299:

                # if the number of retries exceeds 10 fail hard .. cuz that is how we roll
                if nr_tries > retries:
                    Base.fatal('Unable to retrieve json from url after %i retries' % retries)
                    sys.exit(2)

                # warn the user
                Base.warning("unable to retrieve json from url: %s" % url)

                # it is good form to back off a failing remote system a bit .. every retry we are gonna wait 5 seconds longer . Coffee time !!!!
                sleeptime = 5 * int(nr_tries)

                Base.warning("timing out for: %i seconds" % sleeptime)

                # sleep dammit .. i need it ..
                time.sleep(sleeptime)
                output = None
            else:
                # if we do get a proper response code .. break out of the loop
                break

        try:
            Base.info("%s responded with:" % url)
            output = json.loads(str(response.text))

        except Exception:
            Base.warning("unable to decode information provided by %s" % url)
            time.sleep(5)
            output = None
        except JSONDecodeError:
            Base.warning("unable to decode output, not json formatted")
            time.sleep(5)
            output = None

        if output == None:
            Base.fatal("unable extract information from url: %s " % url)

        return output

def get_path(json, path):
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
                return get_path(json[field], path)

            elif type(json[field]) == list:
                if len(json[field]) < 2:
                    Base.info("found %s" % (json[field][0]))
                    return str(json[field][0])

            elif len(path) == 0:
                Base.info("found %s using path" % (field))
                return str(json[field])
        else:
            Base.warning("the requested path of %s could not be found in the json document. returning None instead")
            return None
    except Exception:
        Base.fatal("Error encountered during resolution")


def resolve(url, jsonPath):
    """
    resolve the url with the jsonPath
    :return: string
    """
    return get_path(load_json(url), jsonPath)



#actual script


returnValue = resolve(url, jsonPath)

triggerState = str(returnValue)

Base.info("rel.jsonTrigger found result %s for url:%s" % (returnValue, url))

