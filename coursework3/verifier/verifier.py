#! /usr/bin/python2.7
import os, sys
from z3 import *

INIT = 0
TEST_FOUND = 1
VARS_FOUND = 2
CODE_START = 3

class ShimpleVerifier(object):
    def __init__(self, filename):
        self.var = {}
        self.code = {}
        self.solver = Solver()
        self.assertion = Bool('A')

        with open(filename, 'r') as f:
            status = INIT
            current_label = "start"
            current_label_code = []
            for l in f.readlines():
                if status == INIT and "testMe" in l:
                    status = TEST_FOUND
                elif status == TEST_FOUND and "int" in l:
                    var = l.lstrip().lstrip("int").strip().rstrip(";").split(", ")
                    for v in var:
                        self.var[v] = Int(v)
                    status = VARS_FOUND
                elif status == VARS_FOUND and "@this" in l:
                        status = CODE_START
                elif status == CODE_START:
                    k = l.strip().rstrip(";")
                    if k == "":
                        pass
                    elif k == "}":
                        self.code[current_label] = current_label_code
                        break
                    elif k.startswith("label"):
                        self.code[current_label] = current_label_code
                        current_label = k.strip(":")
                        current_label_code = []
                    else:
                        current_label_code.append(k)
        # print self.code
        # print self.var

    def solve(self):
        self.solver.add(self._make_exp("start"))
        self.solver.add(self.assertion == False)
        print self.solver.check()
        print self.solver.model()

    def _make_exp(self, label, phi=None):
        conditions = []
        code = self.code[label]
        phi_num = None
        for i in range(len(code)):
            exp = code[i]

            # Phi parsing
            if exp.startswith("("):
                phi_num = int(exp[1:exp.index(")")])
                exp = exp[exp.index(")")+1:].strip()

            if "@parameter" in exp or exp == "nop":
                continue
            if "throw" in exp:
                return (self.assertion == False)
            if "return" in exp:
                return (self.assertion == True)
            if "$assertionsDisabled" in exp:
                assertion_label = code[i+1].rstrip(";").split()[-1]
                res = self._make_exp(assertion_label)
                # TODO: "And" conditions with res. return that And-value.
                return And(self.merge(conditions), res)

            x = exp.split()
            if (x[0] in self.var) and (x[1] == "="):
                conditions.append(self.l_to_e(x))
            if x[0] == "if":
                then_label = x[-1]
                if_condition = x[1:-2]
                else_label = code[i+1].split()[1]
                # print if_condition, then_label, else_label
                conditions.append(Implies(self.l_to_e(if_condition), self._make_exp(then_label)))
                conditions.append(Implies(Not(self.l_to_e(if_condition)), self._make_exp(else_label)))
                return self.merge(conditions)

        print "LOOP ENDED, BUT NOT FIN!"

    def l_to_e(self, l):
        # Make a z3 expression, from a list of strings.
        if len(l) != 3 and len(l) != 5:
            print "Error: Expression's length is stange: {}".format(l)

        left = self.var[l[0]]
        if len(l) == 3:
            right = self.var[l[2]] if l[2] in self.var else int(l[2])
        else:
            right_1 = self.var[l[2]] if l[2] in self.var else int(l[2])
            right_2 = self.var[l[4]] if l[4] in self.var else int(l[4])
            op_index = ["+", "-", "*", "/"].index(l[3])
            right = [right_1+right_2, right_1-right_2, right_1*right_2, right_1/right_2][op_index]
        op_index = 0 if l[1] == "==" else ["=", ">", ">=", "<", "<="].index(l[1])
        return [left==right, left>right, left>=right, left<right, left<=right][op_index]

    def merge(self,l):
        # Merge list of expression with And
        res = None
        for i in l:
            if res == None:
                res = i
            else:
                res = And(i, res)
        return res

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: python verifier.py javafile"
        sys.exit(-1)
    java_filename = sys.argv[1]
    java_classname = java_filename.split(".java")[0]
    if os.system("java -jar soot.jar -src-prec java -f shimple -pp -cp . {}".format(java_classname)) != 0:
        print "Error: Failed to run soot"
        sys.exit(-1)

    try:
        a = ShimpleVerifier("./sootOutput/{}.shimple".format(java_classname))
        a.solve()
    except IOError:
        print "Error: .shimple file not found"
        sys.exit(-1)

    '''
    x = Int('x')
    y = Int('y')
    b = Bool('b')
    s = Solver()
    s.add(x > 2, x < 2)
    print s.model()
    '''
