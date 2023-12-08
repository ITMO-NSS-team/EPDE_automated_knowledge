import numpy as np

from epde.operators.utils.template import CompoundOperator
from epde.optimizers.single_criterion.optimizer import Population

class SizeRestriction(CompoundOperator):
    key = 'SizeRestriction'

    def apply(self, objective: Population, arguments: dict):
        self_args, subop_args = self.parse_suboperator_args(arguments = arguments)    
        objective.population = objective.sort()[:objective.length]
        return objective

    def use_default_tags(self):
        self._tags = {'size restriction', 'population level', 'no suboperators', 'standard'}    

class FractionElitism(CompoundOperator):
    key = 'FractionElitism'

    def apply(self, objective: Population, arguments: dict):
        self_args, subop_args = self.parse_suboperator_args(arguments = arguments)    


        for idx, elem in enumerate(objective.population):
            if idx == 0:
                setattr(elem, 'elite', 'immutable')
            else:
                setattr(elem, 'elite', 'non-elite')
                
        return objective
    
    @property
    def operator_tags(self):
        return {'elitism', 'population level', 'auxilary', 'no suboperators', 'standard'}        