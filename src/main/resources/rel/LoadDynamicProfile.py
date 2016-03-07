#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
#from XLRProfile import XLRProfile as XLRProfile
import sys
import XLRProfile
reload(XLRProfile)


from XLRProfile import XLRProfile as XLRProfile

# reload statement.. remove after development phase

__release = getCurrentRelease()

# init the profile using a url
if profileUrl:
    profile = XLRProfile(url=profileUrl)

#if there is no url search the repository
elif profileFromRepository:
    profile = XLRProfile(repoId=profileFromRepository)

# finally pick up the inline specified profile (this being our least favourite options ..
# why .. just becuz
elif profiles:
    profile = XLRProfile(repoString=profiles.replace('\n','').replace('\t', '').replace('\r', ''))
else:
    print "no input profile found.. exiting"
    sys.exit(2)

print str(profile)

# handle the profile
profile.persist_variables_to_release(__release.id)
profile.handle_toggles(__release.id)