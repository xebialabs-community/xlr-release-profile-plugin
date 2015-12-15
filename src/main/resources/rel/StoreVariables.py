#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import sys

import com.xhaus.jyson.JysonCodec as json

def update_variable_store(variable_store_title, variables):
    conn_fac = HttpRequest({'url': 'http://localhost:5516'}, release.scriptUsername, release.scriptUserPassword)
    response = conn_fac.get('/configurations', contentType = 'application/json')
    data = json.loads(response.getResponse())

    variable_store_ci = None
    for i in range(0, len(data)):
        if data[i]['type'] == 'vars.VariableStore' and variable_store_title == data[i]['properties']['title']:
                variable_store_ci = data[i]
                break
    if not variable_store_ci:
        print "ERROR: Unable to find variable store '%s'" % (variable_store_title)
        sys.exit(1)
    variable_store_ci['properties']['variablesJson'] = json.dumps(variables)
    response = conn_fac.put('/configurations/%s' % (variable_store_ci['id']), json.dumps(variable_store_ci), contentType = 'application/json')
    if not response.isSuccessful:
        print "ERROR: Unable to update variable store '%s':" % (variable_store_title)
        response.errorDump()
        sys.exit(1)

update_variable_store(variableStore['title'], getCurrentRelease().getVariableValues())