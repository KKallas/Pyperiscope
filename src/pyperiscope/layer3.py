from .layer2 import Scope
from elvis_repl import elvis
from databoomer import DataBoomer
from string import Template

class Scope(Scope):
    def save_string(self):
        new_template = Template("# comment: Automated step generated with pyPeriscope V2 $comment\npayload = \'\'\'$payload\'\'\'\n$obj_name = Scope(saved_dict=dill.loads(codecs.decode(payload.encode(), 'base64')))")
        self.DataBoomer = DataBoomer(self.save_dict(), obj_name = "step", template = new_template)
        e = elvis()
        e.leave(self.DataBoomer.payload)