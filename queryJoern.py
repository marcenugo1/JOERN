
from cpgqls_client import CPGQLSClient, import_code_query
from graphviz import Source
import subprocess
from enum import Enum
import pprint


#STEPS TO RUN SCRIPT 
#1. Open Visual Studio Code 
#2. Go to View -> Terminal 
#3. Run "joern --server" on Terminal 
#4. Note: if you want to run server on different port use "joern --server --server-host localhost --server-port 8081" 
#5. Run script as usual. 
#more info on https://joern.io/integrate/

#Common Issues: JOERN server timeout / on hold
#Run command on terminal  lsof -i :8081 
#Get PID and kill the process

class Graphs(Enum):
 CFG = "dotCfg" #Control Flow Graphs
 AST = "dotAst" #Abstract Syntax Trees
 PDG = "dotPdg" #Program Dependence graphs
 CPG14 = "dotCpg14" #Code Property Graphs
 CDG = "dotCdg" #Control Dependence Graphs
 DDG = "dotDdg" #Data Dependence Graphs


"""
    getAllDotRepr
    :param path: path to the source code
    :param projectName: String project name
    :param root: String function name
    :param repr: enum for graph representation
    :return: String output AST/CFG/... in dot format 
""" 
def getAllDotRepr(path, projectName, root,repr):

    server_endpoint = "localhost:8081"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)
    print(result['stdout'])

    query = 'cpg.method("' + root + '").'+ repr +'.l'
    result  = client.execute(query)
    return pprint.pprint(result['stdout'])

"""
    getGraphVisualization creates the .png image of given graph 

    :param path: path of file
    :param projectName:String project name
    :param root: String name of function
    :param repr: enum for graph representation
    :return: .png image on current folder for selected graph notation. 
""" 

def getGraphVisualization(path, projectName, rootFunc, repr):

    server_endpoint = "localhost:8081"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = 'cpg.method.name("' + rootFunc +'").' + str(repr) +'.p |> "' + rootFunc +'.dot"'
    result = client.execute(query)
    s = subprocess.getstatusoutput("dot -Tpng -o " + rootFunc + ".png " + rootFunc + ".dot")
    if s[0] == 0:
        return 'Succss'+ s[1]
    else:
        return'Error: {}'.format(s[1])

# Get all local variables declared in the code 
# A node with type LOCAL represents the declaration of a local variable.
def getAllLocalNames(path, projectName, rootFunc):
    server_endpoint = "localhost:8080"
    basic_auth_credentials = ("username", "password")
    client = CPGQLSClient(server_endpoint, auth_credentials=basic_auth_credentials) 

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = 'cpg.local.name.l'
    result = client.execute(query)
    return pprint.pprint(result['stdout'])

"""
    getAllMethodsNames "METHOD" nodes represent declarations of methods,
                        functions or procedures in programs, and one of their properties is NAME.
                        All names of all method nodes can thus be determined as follows.
    :param path: path of file
    :param projectName: 
    :param root: String name of function
    :param repr: enum for graph representation
    :param isExternal: Boolean returns all METHOD nodes of the Code Property Graph with IS_EXTERNAL property. Default = False
    :return: returns all names of methods present in a Code Property Graph
""" 
# Get all methods declared in the code. 
# A node with the type METHOD represents a method.
def getAllMethodsNames(path, projectName, rootFunc, isExternal=False):
    external = 'true' if isExternal else 'false'
    server_endpoint = "localhost:8081"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = 'cpg.method.isExternal('+external+').name.l'
    result = client.execute(query)
    return pprint.pprint(result['stdout'])


"""
    getOutgoingMethodCalls "METHOD" nodes represent declarations of methods,
                        functions or procedures in programs, and one of their properties is NAME.
                        All names of all method nodes can thus be determined as follows.
    :param path: path of file
    :param projectName: 
    :param root: String name of function
    :param repr: enum for graph representation
    :return: returns all  outgoing calls in a method 
""" 
# Get all calls to other methods made in the given function. 
# built-in operators are modeled as methods, one decision made to enable language-agnostic analysis.
def getOutgoingMethodCalls(path, projectName, rootFunc):
    server_endpoint = "localhost:8081"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = 'cpg.method.name("'+rootFunc+'").call.name.l'
    result = client.execute(query)
    return pprint.pprint(result['stdout'])

# Get all if statemens conditions in the code. 
def getAllIfConditions(path, projectName, rootFunc):
    server_endpoint = "localhost:8080"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = 'cpg.method("'+rootFunc+'").controlStructure.condition.code.l'
    result = client.execute(query)
    return result['stdout']

# Get all variables delcared inside if statements
def getAllVariablesInIfStatements(path, projectName, rootFunc):
    server_endpoint = "localhost:8081"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = 'cpg.method("'+rootFunc+'").controlStructure.whenTrue.ast.isLocal.name.l'
    result = client.execute(query)
    return pprint.pprint(result['stdout'])

# Avoid `strcat` or `strncat` functions. 
# These can be used insecurely causing non null-termianted strings leading to memory corruption.
# A secure alternative is `strcat_s`.
def getstrcat(path, projectName):
    server_endpoint = "localhost:8080"
    client = CPGQLSClient(server_endpoint)

    query = import_code_query(path, projectName)
    result = client.execute(query)

    query = '({cpg.method("(?i)(strcat|strncat)").callIn}).l'
    result = client.execute(query)
    return pprint.pprint(result['stdout'])

if __name__ == "__main__":
    result = getstrcat("secureExample.c","secure")
    result2 = getstrcat("insecureExample.c","insecure")
    #result = getAllDotRepr("foo.c","foo","foo",Graphs.AST.value)
    #result = getGraphVisualization("foo.c","foo","foo", Graphs.AST.value)
    #result = getAllMethodsNames("foo.c","foo","foo")
    #result = getOutgoingMethodCalls("foo.c","foo","foo")
    #result = getAllIfConditions("foo.c","foo","foo")
    #result = getAllLocalNames("foo.c","foo","foo") #get all local variables 
    #result = getAllVariablesInIfStatements("foo.c","foo","foo") #get all local variables in IF statements 

    print(result)
    print(result2)

