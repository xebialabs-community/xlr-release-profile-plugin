#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder
import com.xebialabs.deployit.repository.SearchParameters as SearchParameters
import com.xebialabs.deployit.plugin.api.reflect.Type as Type

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


def get_variables(profile):
    sp = SearchParameters()
    sp.setType(Type.valueOf('rel.ReleaseProfile'))

    for p in XLReleaseServiceHolder.getRepositoryService().listEntities(sp):
        if str(p.getTitle()) == profile:
            return p.getProperty('variablesJson')

variables = json.loads(get_variables(Profiles))

variable_start_regex = re.compile('^\$\{', re.IGNORECASE)
newVariables = {}
for key, value in variables.items():
    if re.match(variable_start_regex, key) is None:
        key = "${%s}" % (key)
    newVariables[key] = value
__release.setVariableValues(newVariables)
releaseApi.updateRelease(release.id, __release)
