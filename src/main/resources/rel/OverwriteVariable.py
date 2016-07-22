#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import com.xebialabs.xlrelease.api.XLReleaseServiceHolder as XLReleaseServiceHolder

__variable_start_regex = re.compile('^\$\{', re.IGNORECASE)

# grab the current release
__release = getCurrentRelease()

# grab the variable dictionary
variables = __release.getVariableValues()

#check that the variable is properly formatted
if re.match(__variable_start_regex, variableName) is None:
        key = "${%s}" % (variableName)

# set the overwrite
variables[key] = overwriteValue


# update the new variable dict in the release
__release.setVariableValues(variables)


# update the actual running release
releaseApi.updateRelease(release.id, __release)

