import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

soil_moisture = ctrl.Antecedent(np.arange(0, 101, 1), 'soil_moisture')
temperature = ctrl.Antecedent(np.arange(0, 51, 1), 'temperature')
water_amount = ctrl.Consequent(np.arange(0, 101, 1), 'water_amount')

soil_moisture['low'] = fuzz.trimf(soil_moisture.universe, [0, 0, 50])
soil_moisture['medium'] = fuzz.trimf(soil_moisture.universe, [0, 50, 100])
soil_moisture['high'] = fuzz.trimf(soil_moisture.universe, [50, 100, 100])

temperature['low'] = fuzz.trimf(temperature.universe, [0, 0, 25])
temperature['medium'] = fuzz.trimf(temperature.universe, [0, 25, 50])
temperature['high'] = fuzz.trimf(temperature.universe, [25, 50, 50])

water_amount['low'] = fuzz.trimf(water_amount.universe, [0, 0, 50])
water_amount['medium'] = fuzz.trimf(water_amount.universe, [0, 50, 100])
water_amount['high'] = fuzz.trimf(water_amount.universe, [50, 100, 100])

rule1 = ctrl.Rule(soil_moisture['low'] & temperature['low'], water_amount['high'])
rule2 = ctrl.Rule(soil_moisture['low'] & temperature['medium'], water_amount['high'])
rule3 = ctrl.Rule(soil_moisture['low'] & temperature['high'], water_amount['medium'])
rule4 = ctrl.Rule(soil_moisture['medium'] & temperature['low'], water_amount['medium'])
rule5 = ctrl.Rule(soil_moisture['medium'] & temperature['medium'], water_amount['medium'])
rule6 = ctrl.Rule(soil_moisture['medium'] & temperature['high'], water_amount['low'])
rule7 = ctrl.Rule(soil_moisture['high'] & temperature['low'], water_amount['low'])
rule8 = ctrl.Rule(soil_moisture['high'] & temperature['medium'], water_amount['low'])
rule9 = ctrl.Rule(soil_moisture['high'] & temperature['high'], water_amount['low'])

irrigation_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
irrigation = ctrl.ControlSystemSimulation(irrigation_ctrl)

soil_moisture_values = np.linspace(0, 100, 100)
temperature_values = np.linspace(0, 50, 100)
water_amount_values = np.zeros((100, 100))

for i in range(100):
    for j in range(100):
        irrigation.input['soil_moisture'] = soil_moisture_values[i]
        irrigation.input['temperature'] = temperature_values[j]
        irrigation.compute()
        water_amount_values[i, j] = irrigation.output['water_amount']

fig, axs = plt.subplots(3, 1, figsize=(10, 15))

axs[0].plot(soil_moisture_values, soil_moisture_values, label='Soil Moisture')
axs[0].plot(temperature_values, temperature_values, label='Temperature')
axs[0].set_title('Inputs')
axs[0].legend()

axs[1].imshow(water_amount_values, extent=[0, 100, 0, 50], origin='lower', aspect='auto')
axs[1].set_title('Output (Water Amount)')
axs[1].set_xlabel('Soil Moisture')
axs[1].set_ylabel('Temperature')

soil_moisture.view(sim=irrigation)
temperature.view(sim=irrigation)
water_amount.view(sim=irrigation)

plt.tight_layout()
plt.show()