#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
#from XLRProfile import XLRProfile as XLRProfile
import sys
import Base
reload(Base)
from Base import Base
import requests
import XLRProfile

import urllib3
reload(XLRProfile)


from XLRProfile import XLRProfile as XLRProfile

# reload statement.. remove after development phase

__release = getCurrentRelease()

# # init the profile using a url
# if profileUrl:
#     profile = XLRProfile(url=profileUrl)
#
# #if there is no url search the repository
# elif profileFromRepository:
#     profile = XLRProfile(repoId=profileFromRepository)
#
# # finally pick up the inline specified profile (this being our least favourite options ..
# # why .. just becuz
# elif profiles:
#     profile = XLRProfile(repoString=profiles.replace('\n','').replace('\t', '').replace('\r', ''))
# else:
#     Base.fatal("no input profile found.. exiting")
#
# print str(profile)

# handle the profile
# profile.persist_variables_to_release(__release.id)
# profile.handle_toggles(__release.id)
def doHeadRequest(url):
    return requests.head(url, verify=False)


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


profileList = []
atLeastOne = False

if profileUrl:
    for url in profileUrl.split(';'):
        Base.info("trying to add profile from url: %s" % url)
        if validUrl(url):
          p = XLRProfile(url=url)
          p.persist_variables_to_release(__release.id)
          p.handle_toggles(__release.id)
          atLeastOne = True
elif profileFromRepository:
    p = XLRProfile(repoId=profileFromRepository)
    p.persist_variables_to_release(__release.id)
    p.handle_toggles(__release.id)
    atLeastOne = True
elif profiles:
    profile = XLRProfile(repoString=profiles.replace('\n','').replace('\t', '').replace('\r', ''))
    p.persist_variables_to_release(__release.id)
    p.handle_toggles(__release.id)
    atLeastOne = True
else:
   Base.fatal("no input profile found.. exiting")
   sys.exit(2)

if atLeastOne == False:
    Base.fatal("no input profile found.. exiting")
    sys.exit(2)
