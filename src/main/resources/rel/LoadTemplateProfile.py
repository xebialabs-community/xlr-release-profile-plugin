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
reload(XLRProfile)

import urllib3




# reload statement.. remove after development phase

__release = getCurrentRelease()


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

if profile_url:
    for url in profileUrl.split(';'):
        Base.info("trying to add profile from url: %s" % url)
        if validUrl(url):
          p = XLRProfile.XLRProfile(url=url)
          atLeastOne = True
elif profile:
    p = XLRProfile.XLRProfile(repoString=profile.replace('\n','').replace('\t', '').replace('\r', ''))
    p.handle_template_plan(__release.id)
    atLeastOne = True

else:
   Base.fatal("no input profile found.. exiting")
   sys.exit(2)

if atLeastOne == False:
    Base.fatal("no input profile found.. exiting")
    sys.exit(2)


