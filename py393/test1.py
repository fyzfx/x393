#!/usr/bin/env python
# encoding: utf-8
'''
# Copyright (C) 2015, Elphel.inc.
# test for import_verilog_parameters.py
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

@author:     Andrey Filippov
@copyright:  2015 Elphel, Inc.
@license:    GPLv3.0+
@contact:    andrey@elphel.coml
@deffield    updated: Updated
'''
__author__ = "Andrey Filippov"
__copyright__ = "Copyright 2015, Elphel, Inc."
__license__ = "GPL"
__version__ = "3.0+"
__maintainer__ = "Andrey Filippov"
__email__ = "andrey@elphel.com"
__status__ = "Development"
'''
~/git/x393/py393$ ./test1.py -vv -f/home/andrey/git/x393/system_defines.vh -f /home/andrey/git/x393/includes/x393_parameters.vh  /home/andrey/git/x393/includes/x393_localparams.vh -pNEWPAR=\'h3ff -c write_mem 0x377 25 -c read_mem 0x3ff -i

'''
import sys
import os

from argparse import ArgumentParser
#import argparse
from argparse import RawDescriptionHelpFormatter

from import_verilog_parameters import ImportVerilogParameters
from import_verilog_parameters import VerilogParameters
import x393_mem
import x393_axi_control_status
import x393_pio_sequences
__all__ = []
__version__ = 0.1
__date__ = '2015-03-01'
__updated__ = '2015-03-01'

DEBUG = 1
TESTRUN = 0
PROFILE = 0
callableTasks={}
class CLIError(Exception):
    #Generic exception to raise and log different fatal errors.
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
'''
    for name in x393_mem.X393Mem.__dict__:
        if hasattr((x393_mem.X393Mem.__dict__[name]), '__call__') and not (name[0]=='_'):
            func_args=x393_mem.X393Mem.__dict__[name].func_code.co_varnames[1:x393_mem.X393Mem.__dict__[name].func_code.co_argcount]
#            print (name+": "+str(x393_mem.X393Mem.__dict__[name]))
#            print ("args="+str(func_args))
            print (name+": "+str(func_args))

'''
def extractTasks(obj,inst):
    for name in obj.__dict__:
        if hasattr((obj.__dict__[name]), '__call__') and not (name[0]=='_'):
            func_args=obj.__dict__[name].func_code.co_varnames[1:obj.__dict__[name].func_code.co_argcount]
            callableTasks[name]={'func':obj.__dict__[name],'args':func_args,'inst':inst}
def execTask(commandLine):
    result=None
    cmdList=commandLine #.split()
    try:
        funcName=cmdList[0]
        funcArgs=cmdList[1:]
    except:
        return None
    for i,arg in enumerate(funcArgs):
        try:
            funcArgs[i]=eval(arg) # Try parsing parameters as numbers, if possible
        except:
            pass
#    result = callableTasks[funcName]['func'](callableTasks[funcName]['inst'],*funcArgs)
    try:
        result = callableTasks[funcName]['func'](callableTasks[funcName]['inst'],*funcArgs)
    except Exception as e:
        print ('Error while executing %s %s'%(funcName,str(funcArgs)))
        try:
            funcFArgs= callableTasks[funcName]['args']
        except:
            print ("Unknown task: %s"%(funcName))
            return None
        sFuncArgs=""
        if funcFArgs:
           sFuncArgs+='<'+str(funcFArgs[0])+'>'
        for a in funcFArgs[1:]:
            sFuncArgs+=' <'+str(a)+'>'
        print ("Usage:\n%s %s"%(funcName,sFuncArgs))
        print ("exception message:"+str(e))
    return result
def hx(obj):
    try:
        return "0x%x"%obj
    except:
        return str(obj)
def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by %s on %s.
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

USAGE
''' % (program_shortdesc, __author__,str(__date__))
    preDefines={}
    preParameters={}
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
#        parser.add_argument(                   dest="paths", help="Verilog include files with parameter definitions [default: %(default)s]", metavar="path", nargs='*')
        parser.add_argument("-f", "--icludeFile",  dest="paths", action="append", help="Verilog include files with parameter definitions [default: %(default)s]", metavar="path", nargs='*')
        parser.add_argument("-d", "--define",  dest="defines", action="append", help="Define macro(s)" )
        parser.add_argument("-p", "--parameter",  dest="parameters", action="append", help="Define parameter(s) as name=value" )
        parser.add_argument("-c", "--command",  dest="commands", action="append", help="execute command" , nargs='*')
        parser.add_argument("-i", "--interactive", dest="interactive", action="store_true", help="enter interactive mode [default: %(default)s]")
        
        # Process arguments
        args = parser.parse_args()
#        paths = args.paths
        paths=[]
        for group in args.paths:
            paths+=group
        verbose = args.verbose
        if args.defines:
            for predef in args.defines:
                kv=predef.split("=")
                if len(kv)<2:
                    kv.append("")
                preDefines[kv[0].strip("`")]=kv[1]    
        if verbose > 0:
#            print("Verbose mode on "+hex(verbose))
            args.parameters.append('VERBOSE=%d'%verbose) # add as verilog parameter
        if args.parameters:
            for prePars in args.parameters:
                kv=prePars.split("=")
                if len(kv)>1:
                    preParameters[kv[0]]=(kv[1],"RAW",kv[1]) # todo - need to go through the parser
                    
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
# Take out from the try/except for debugging
    ivp= ImportVerilogParameters(preParameters,preDefines)
    if verbose > 3: print ('paths='+str(paths))   
    if verbose > 3: print ('defines='+str(args.defines))   
    if verbose > 3: print ('parameters='+str(args.parameters)) 
    if verbose > 3: print ('comamnds='+str(args.commands)) 
    for path in paths:
        if verbose > 2: print ('path='+str(path))
        ### do something with inpath ###
        ivp.readParameterPortList(path)
    parameters=ivp.getParameters()
    vpars=VerilogParameters(parameters)
    if verbose > 3:
        defines= ivp.getDefines()
        print ("======= Extracted defines =======")
        for macro in defines:
            print ("`"+macro+": "+defines[macro])        
        print ("======= Parameters =======")
        for par in parameters:
            try:
                print (par+" = "+hex(parameters[par][0])+" (type = "+parameters[par][1]+" raw = "+parameters[par][2]+")")        
            except:
                print (par+" = "+str(parameters[par][0])+" (type = "+parameters[par][1]+" raw = "+parameters[par][2]+")")
        print("vpars.VERBOSE="+str(vpars.VERBOSE))
        print("vpars.VERBOSE__TYPE="+str(vpars.VERBOSE__TYPE))
        print("vpars.VERBOSE__RAW="+str(vpars.VERBOSE__RAW))
    
    if verbose > 3: print (VerilogParameters.__dict__)
    vpars1=VerilogParameters()
    if verbose > 3: print("vpars1.VERBOSE="+str(vpars1.VERBOSE))
    if verbose > 3: print("vpars1.VERBOSE__TYPE="+str(vpars1.VERBOSE__TYPE))
    if verbose > 3: print("vpars1.VERBOSE__RAW="+str(vpars1.VERBOSE__RAW))
    
    x393mem= x393_mem.X393Mem(verbose,True) #add dry run parameter
    x393tasks=x393_axi_control_status.X393AxiControlStatus(verbose,True)
    x393Pio= x393_pio_sequences.X393PIOSequences(verbose,True)
    '''
    print ("----------------------")
    print("x393_mem.__dict__="+str(x393_mem.__dict__))
    print ("----------------------")
    print("x393mem.__dict__="+str(x393mem.__dict__))
    print ("----------------------")
    print("x393_mem.X393Mem.__dict__="+str(x393_mem.X393Mem.__dict__))
    '''
    if verbose > 3: 
        print ("----------------------")
        for name in x393_mem.X393Mem.__dict__:
            if hasattr((x393_mem.X393Mem.__dict__[name]), '__call__') and not (name[0]=='_'):
                func_args=x393_mem.X393Mem.__dict__[name].func_code.co_varnames[1:x393_mem.X393Mem.__dict__[name].func_code.co_argcount]
                print (name+": "+str(func_args))
    extractTasks(x393_mem.X393Mem,x393mem)
    extractTasks(x393_axi_control_status.X393AxiControlStatus,x393tasks)
    extractTasks(x393_pio_sequences.X393PIOSequences,x393Pio)

    if verbose > 3:     
        funcName="read_mem"
        funcArgs=[0x377,123]
        print ('==== testing function : '+funcName+str(funcArgs)+' ====')
#execTask(commandLine)    
        try:
            callableTasks[funcName]['func'](callableTasks[funcName]['inst'],*funcArgs)
        except Exception as e:
            print ('Error while executing %s'%funcName)
            funcFArgs= callableTasks[funcName]['args']
            sFuncArgs=""
            if funcFArgs:
                sFuncArgs+='<'+str(funcFArgs[0])+'>'
                for a in funcFArgs[1:]:
                    sFuncArgs+=' <'+str(a)+'>'
                    print ("Usage:\n%s %s"%(funcName,sFuncArgs))
                    print ("exception message:"+str(e))
     
    for cmdLine in args.commands:
        print ('Running task: '+str(cmdLine))
        rslt= execTask(cmdLine)
        print ('    Result: '+str(rslt))
    '''       
#TODO: use readline
    '''
    if (args.interactive):
        line =""
        while True:
            line=raw_input('x393--> ').strip()
            if not line:
                print ('Use "quit" to exit, "help" - for help')
            elif line == 'quit':
                break
            elif line== 'help' :
                print ("\nAvailable tasks:")
                for name,val in sorted(callableTasks.items()):
#                    funcFArgs=callableTasks[name]['args']
                    funcFArgs=val['args']
                    sFuncArgs=""
                    if funcFArgs:
                        sFuncArgs+='<'+str(funcFArgs[0])+'>'
                        for a in funcFArgs[1:]:
                            sFuncArgs+=' <'+str(a)+'>'
                    print ("Usage: %s %s"%(name,sFuncArgs))
                print ('\n"parameters" and "defines" list known defined parameters and macros')
            elif line == 'parameters':
                parameters=ivp.getParameters()
                for par in parameters:
                    try:
                        print (par+" = "+hex(parameters[par][0])+" (type = "+parameters[par][1]+" raw = "+parameters[par][2]+")")        
                    except:
                        print (par+" = "+str(parameters[par][0])+" (type = "+parameters[par][1]+" raw = "+parameters[par][2]+")")

            elif (line == 'defines') or (line == 'macros'):
                defines= ivp.getDefines()
                for macro in defines:
                    print ("`"+macro+": "+defines[macro])        
            else:
                cmdLine=line.split()
                rslt= execTask(cmdLine)
                print ('    Result: '+hx(rslt))   
#http://stackoverflow.com/questions/11781265/python-using-getattr-to-call-function-with-variable-parameters
#*getattr(foo,bar)(*params)   
    return 0

if __name__ == "__main__":
    if DEBUG:
#        sys.argv.append("-h")
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'test1_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())