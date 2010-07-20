import sys
import os
from ..core.solver import Solver
from ..core.blackbox import BlackBox

__docformat__ = 'restructuredtext'

class Parameter:
    "Used to specify black-box solver options."

    def __init__(self,name=None,value=None,**kwargs):
        self.name = name
        self.value = value
        pass
    
    def str(self):
        if (self.name is not None) and (self.value is not None):
            return self.name + ' ' + str(self.value)
        return ""

    
class NOMADBlackbox(BlackBox):
    """ 
    NOMADBlackbox is an implementation of BlackBox, it contains
    the description and the method of communication between 
    NOMAD solver and an executable blackbox.
    The descriptions include the executable file name
    The communicating methods are read_input and write_output
    Those are specialized to NOMAD solver
    """

    def __init__(self, solver=None, model=None, fileName='blackbox.py',
                 **kwargs):

        BlackBox.__init__(self, solver=solver, model=model, **kwargs)
        self.file_name = fileName
        self.surrogate = None
        pass
     
    def read_input(self, *args, **kwargs):
        """
        .. warning::

            Document this method!!!
        """
        inputValues = []
        paramValues = []
        #print args
        #print ""
        if len(args) < 1:
            return (inputValues, paramValues)

        # Extract every words from the file and save to a list
        f = open(args[1])
        map(lambda l: inputValues.extend(l.strip('\n').strip(' ').split(' ')),
                                         f.readlines())
        f.close()
        return (inputValues, paramValues)
    
    def write_output(self, objectiveValue, constraintValues):
        """
        .. warning::

            Document this method!!!
        """
        print >> sys.stdout, objectiveValue,
        if len(constraintValues) > 0:
            for i in range(len(constraintValues)):
                print >> sys.stdout, constraintValues[i],
            print ""
        return
   
    def generate_surrogate(self):
        """
        .. warning::

            Document this method!!!
        """
        return

    def generate_executable_file(self):
        """
        Generate Python code to play the role of black box executable.
        """
        
        tab = ' '*4
        bb = open(self.file_name, 'w')
        # To avoid the error compability of python version (local version
        # intalled by user) and global version (system), we don't make black
        # box an executable but call it via `python blackbox.py`
        # --------
        # or predifine config.python to the used python
        # rootPackage = config.__name__.replace('.config','')
        #bb.write(config.python + '\n')
        bb.write('#!/usr/bin/env python\n')
        bb.write('import os\n')
        bb.write('import sys\n')
        bb.write('import string\n')
        bb.write('import shutil\n')
        bb.write('import pickle\n')
        bb.write('from opal.Solvers.NOMAD import NOMADBlackbox\n')

        #bb.write('from ' + rootPackage + '.core import modeldata\n')
        #bb.write('from ' + rootPackage + '.core import blackbox\n')
        #if self.solver is not None:
        #    bb.write('from ' + rootPackage + '.Solvers import ' + \
        #             self.solver.name + '\n')
        #bb.write('from ' + self.modelEvaluator.model.moduleName + \
        #         ' import '+ self.modelEvaluator.model.objFuncName + '\n')
        #for constraint in self.modelEvaluator.model.constraintNames:
        #    bb.write('from ' + self.modelEvaluator.model.moduleName + \
        #             ' import '+ constraint + '\n')

        bb.write('# Load test data.\n')
        bb.write('try:\n')
        bb.write(tab + 'blackboxDataFile = open("' + \
                self.model.data_file + '","r")\n')
        bb.write(tab + 'blackboxModel = pickle.load(blackboxDataFile)\n')
        bb.write(tab+'blackboxDataFile.close()\n')
        bb.write('except TypeError:\n')
        bb.write(tab+'print "Error in loading"\n')
        bb.write('blackbox = NOMADBlackbox(model=blackboxModel)\n')
        #bb.write('blackbox.opt_data.synchronize_measures()\n')
        bb.write('blackbox.run(*sys.argv)\n')
        #bb.write('try:\n')
        #bb.write(tab + 'blackboxDataFile = open("' + self.dataFileName + \
        #         '", "w")\n')
        #bb.write(tab+'pickle.dump(blackbox,blackboxDataFile)\n')
        #bb.write(tab+'blackboxDataFile.close()\n')
        #bb.write('except TypeError:\n')
        #bb.write(tab+'print "Error in loading"\n')
        bb.write('blackboxModel.save()\n')
        #bb.write('blackboxRunLogFile.close()\n')
        bb.close()
        #os.chmod(self.runFileName,0755)
        return
    
class NOMADSolver(Solver):
    """
    An instance of the abstract Solver class. 
    A NOMADSolver object specifies the particulars of the NOMAD direct search
    solver for black-box optimization.
    For more information about the NOMAD, see `http://wwww.gerad.ca/NOMAD`_.
    """

    def __init__(self, **kwargs):

        Solver.__init__(self, name='NOMAD', command='nomad',
                        parameter='nomad-param.txt', **kwargs)
        self.paramFileName = 'nomad-param.txt'
        self.resultFileName = 'nomad-result.txt'
        self.solutionFileName = 'nomad-solution.txt'
        self.blackbox = NOMADBlackbox(solver=self)
        self.parameter_settings = [] # List of line in parameter file
        pass

#   def blackbox_read_input(self,argv):
#        inputValues = [] # blackbox input = algorithm parameter
#        paramValues = [] # blackbox parameter
#        if len(argv) < 1:
#            return (inputValues,paramValues)
#        f = open(argv[1])
#        map(lambda l: inputValues.extend(l.strip('\n').strip(' ').split(' ')), f.readlines()) # Extract every words from the file and save to a list
#        f.close()
#        return (inputValues,paramValues)

#    def blackbox_write_output(self,objectiveValue,constraintValues):
#        print >> sys.stdout, objectiveValue,
#        if len(constraintValues) > 0:
#            for i in range(len(constraintValues)):
#                print >> sys.stdout,constraintValues[i],
#            print ""
#        return
    
    def solve(self, model=None, surrogate=None):
        self.blackbox.model = model
        self.blackbox.generate_executable_file()
        if surrogate is not None:
            surrogate.generate_executable_file()
        #   surrogate.save()
        self.initialize()
        self.run()
        return

    def initialize(self):
        "Write NOMAD config to file based on parameter optimization problem."

        descrFile = open(self.paramFileName, "w")

        if self.blackbox.model is not None:
            model = self.blackbox.model
            descrFile.write('DIMENSION ' + str(model.n_var) + '\n')
            # descrFile.write('DISPLAY_DEGREE 4\n')
            descrFile.write('DISPLAY_STATS EVAL & BBE & SOL & & OBJ \\\\ \n')
            descrFile.write('BB_EXE "$python ' + \
                    self.blackbox.file_name + '"\n')
            bbTypeStr = 'BB_OUTPUT_TYPE OBJ'
            for i in range(model.m_con):
                bbTypeStr = bbTypeStr + ' PB'
            descrFile.write(bbTypeStr + '\n')
            surrogate = self.blackbox.surrogate
            if surrogate is not None:
                descrFile.write('SGTE_EXE "$python ' + \
                        surrogate.file_name + '"\n')
            pointStr = str(model.initial_points)
            descrFile.write('X0 ' +  pointStr.replace(',',' ') + '\n')
            lowerBoundStr = str([bound[0] for bound in model.bounds]).replace('None','-').replace(',',' ')
            upperBoundStr = str([bound[1] for bound in model.bounds]).replace('None','-').replace(',',' ')
            descrFile.write('LOWER_BOUND ' + lowerBoundStr + '\n')
            descrFile.write('UPPER_BOUND ' + upperBoundStr + '\n')

        # Write other settings.
        descrFile.write('SOLUTION_FILE ' + self.solutionFileName + '\n')
        descrFile.write('STATS_FILE ' + self.resultFileName + \
                ' EVAL & BBE & BBO & SOL & & OBJ \\\\ \n')
        for param_setting in self.parameter_settings:
            descrFile.write(param_setting + '\n')
        descrFile.close()
        return

    def set_parameter(self, name=None, value=None):
        param = Parameter(name=name,value=value)
        self.parameter_settings.append(param.str())
        return

    def run(self):
        os.system('nomad ' + self.paramFileName)
        return

NOMAD = NOMADSolver()
