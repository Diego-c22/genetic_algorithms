import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


x = ctrl.Antecedent(np.arange(0, 100, 1), 'x')
y = ctrl.Consequent(np.arange(0, 100, 1), 'y')


x['low'] = fuzz.trimf(x.universe, [0, 0, 50])
x['medium'] = fuzz.trimf(x.universe, [0, 50, 100])
x['high'] = fuzz.trimf(x.universe, [50, 100, 100])


y['low'] = fuzz.trimf(y.universe, [0, 0, 50])
y['medium'] = fuzz.trimf(y.universe, [0, 50, 100])
y['high'] = fuzz.trimf(y.universe, [50, 100, 100])


rule1 = ctrl.Rule(x['low'], y['low'])
rule2 = ctrl.Rule(x['medium'], y['medium'])
rule3 = ctrl.Rule(x['high'], y['high'])


tipping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
tipping = ctrl.ControlSystemSimulation(tipping_ctrl)