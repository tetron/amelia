
class _Concat(object):
    def __init__(self, rhs, lhs):
        self.rhs = rhs
        self.lhs = lhs

    def __str__(self):
        return "%s%s" % (to_ref(self.rhs), to_ref(self.lhs))

class _Param(object):
    def __init__(self, n, scope=None):
        self.name = n
        self.scope = scope

    def __getattr__(self, g):
        return self[g]

    def __getitem__(self, g):
        if self.name:
            return _Param(g, scope=self)
        else:
            return _Param(g)

    def __xor__(self, tp):
        self.ptype = tp
        return self

    def __add__(self, val):
        return _Concat(self, val)

    def __str__(self):
        return self.name

def to_ptype(p):
    if p is str:
        return "string"
    else:
        return str(p)

def to_ref(r):
    if isinstance(r, _Param):
        return "$(inputs.%s)" % r
    else:
        return r

class _Command(object):
    def __init__(self, wf, args):
        self.wf = wf
        self.arguments = args
        self.outputs = {}

    def __getattr__(self, g):
        return self[g]

    def __getitem__(self, g):
        if g in self.outputs:
            return self.outputs[g]
        self.outputs[g] = _Param(g, scope=self)
        return self.outputs[g]

    def make_step(self):
        inp = [a for a in self.arguments if isinstance(a, _Param)]
        return {
            "id": self.arguments[0],
            "in": {},
            "out": list(self.outputs.keys()),
            "run": {
                "class": "CommandLineTool",
                "arguments": [to_ref(a) for a in self.arguments],
                "inputs": {i.name: to_ptype(i.ptype) for i in inp},
                "outputs": {i.name: {
                    "type": to_ptype(i.ptype),
                    "outputBinding": {
                        "glob": str(i.glob.glob)
                    }
                } for i in self.outputs.values()},
            }
        }

class _Run(object):
    def __getattr__(self, g):
        return _Param()

    def __getitem__(self, g):
        return _Param()


class Workflow(object):
    def __init__(self):
        self.steps = []

    def Command(self, *args):
        c = _Command(self, args)
        self.steps.append(c)
        return c

    def Run(self, cmd, **kwargs):
        return _Run()

    def make_wf(self):
        return {
            "class": "Workflow",
            "inputs": {},
            "outputs": {},
            "steps": [s.make_step() for s in self.steps]
        }

inputs = _Param(None)

class _Type(object):
    def __init__(self, ptype):
        self.ptype = ptype

    def __str__(self):
        return self.ptype

File = _Type("File")

class Glob(object):
    def __init__(self, g):
        self.glob = g

    def __rshift__(self, val):
        self.param = val
        self.param.glob = self
        return self

    def __xor__(self, tp):
        self.param.ptype = tp
        return self
