import math
import random
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

A = 8
B = 25
C = 4
D = 45
E = 10
F = 17
G = 35

WEIGHT = 5

DESIRED_CURVE_CHROMOSOME = [A, B, C, D, E, F, G]

# Manipulation: Gen / Weight

# Function of aptitude (integral of the absolute error between the desired curve and the curve obtained with the parameters)
# 1. Number are divided into WEIGHT (5)
# 2. Inside a loop evaluate fitness function for each chromosome
# 3. The fitness functions formula is

def calculate_y(x, chromosome: list):
    a, b, c, d, e, f, g = chromosome
    c = c if c != 0 else 1
    e = e if e != 0 else 1
    y = a * ((b * math.sin(x / c)) + d * math.cos(x / e)) + f * x - g
    return y


class CurveFitting:
    def __init__(self, mutation_percentage: 0, enable_elitism: False):
        self.mutation_percentage = mutation_percentage
        self.enable_elitism = enable_elitism
        self.matrix: list[list[int]] = [self.get_random_8_bit_number() for _ in range(100)]
        self.parents: list[list[int]] = [self._generate_best_chromosome() for _ in range(100)]
        self.children: list[list[int]] = []
        self.fitness = []
        self.best_fitness = []


    def calculate_fitness(self, chromosome_base: list[int], chromosome: list[int]):
        error = sum(
            (
                abs(
                 calculate_y((j / 10), chromosome_base) -
                 calculate_y((j / 10), [c / WEIGHT for c in chromosome])
                 )
                for j in range(0, 1000)
            )
        )
        return error

    def _generate_best_chromosome(self):
        opponents_idx = random.sample(range(0, 100), 5)
        best_opponent_idx = opponents_idx[0]
        best_opponent_fitness = self.calculate_fitness(DESIRED_CURVE_CHROMOSOME, self.matrix[best_opponent_idx])
        for idx in range(1, len(opponents_idx)):
            opponent_fitness = self.calculate_fitness(DESIRED_CURVE_CHROMOSOME, self.matrix[opponents_idx[idx]])
            if opponent_fitness < best_opponent_fitness:
                best_opponent_idx = opponents_idx[idx]
                best_opponent_fitness = opponent_fitness
        return self.matrix[best_opponent_idx]

    def _reproduce_chromosomes(self, parent1: list[int], parent2: list[int]):
        partition = self.get_random_bites_partition()
        byte_to_mutate_idx = (partition - 1) // 8
        bit_to_mutate = (partition - 1) % 8
        bottom_bitmask = (2 ** bit_to_mutate) - 1
        top_bitmask = 255 - bottom_bitmask
        parent1_partition = parent1[byte_to_mutate_idx]
        parent2_partition = parent2[byte_to_mutate_idx]
        child1_bottom = parent1_partition & bottom_bitmask
        child1_top = parent1_partition & top_bitmask
        child2_bottom = parent2_partition & bottom_bitmask
        child2_top = parent2_partition & top_bitmask
        child1_byte = child1_top | child2_bottom
        child2_byte = child2_top | child1_bottom
        child1 = parent1[:byte_to_mutate_idx] + [child1_byte] + parent2[byte_to_mutate_idx + 1:]
        child2 = parent2[:byte_to_mutate_idx] + [child2_byte] + parent1[byte_to_mutate_idx + 1:]
        return child1, child2

    def _mutate_chromosome(self, chromosome: list[int], mutation_percentage: float):
        bits_to_mutate = int(256 // mutation_percentage)
        for _ in range(bits_to_mutate):
            byte_idx = random.randint(0, 6)
            bit_idx = random.randint(0, 7)
            chromosome[byte_idx] = self.flip_bit(chromosome[byte_idx], bit_idx)
        return chromosome

    def _generate_children(self):
        self.children = []
        for idx in range(0, 100, 2):
            parent1 = self.parents[idx]
            parent2 = self.parents[idx + 1]
            child1, child2 = self._reproduce_chromosomes(parent1, parent2)
            if self.mutation_percentage > 0:
                child1 = self._mutate_chromosome(child1, self.mutation_percentage)
                child2 = self._mutate_chromosome(child2, self.mutation_percentage)
            self.children.append(child1)
            self.children.append(child2)

    def _apply_elitism(self):
        parents_children = self.parents + self.children if self.enable_elitism else self.children
        elite = sorted(
            parents_children,
            key=lambda x: self.calculate_fitness(DESIRED_CURVE_CHROMOSOME, x),
            # reverse=True
        )[:100]
        self.parents = elite

        self.best_fitness.append(self.calculate_fitness(DESIRED_CURVE_CHROMOSOME, elite[0]))



    def run(self):
        self._generate_children()
        self._apply_elitism()


    get_random_8_bit_number = lambda self: [random.randint(0, 255) for _ in range(7)]
    get_random_bites_partition = lambda self: random.randint(1, 55)
    flip_bit = lambda self, number, bit: number ^ (1 << bit)

# Dash app setup
app = dash.Dash(__name__)
curve_fitting = CurveFitting(25, True)

@app.callback(

    [
        Output('curve-graph', 'figure'),
        Output('fitness-graph', 'figure')
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    curve_fitting.run()
    x = [(i / 10) for i in range(0, 1000)]
    y = [calculate_y(xi, DESIRED_CURVE_CHROMOSOME) for xi in x]
    best_chromosome = [calculate_y(xi, [n/WEIGHT for n in curve_fitting.parents[0]]) for xi in x]

    curve_fig = go.Figure()
    curve_fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', line=dict(color='red', dash='dash')))
    curve_fig.add_trace(go.Scatter(x=x, y=best_chromosome, mode='lines+markers', line=dict(color='blue')))
    curve_fig.update_layout(title='Graph of y vs x', xaxis_title='x', yaxis_title='y', height=600)

    fitness_fig = go.Figure()
    fitness_fig.add_trace(go.Scatter(x=[i for i in range(0, n)], y=curve_fitting.best_fitness, mode='lines+markers'))
    fitness_fig.update_layout(title='Fitness vs Iteration', xaxis_title='Iteration', yaxis_title='Fitness', height=600)

    if curve_fitting.best_fitness:
        current_generation = len(curve_fitting.best_fitness)
        shortest_distance = curve_fitting.best_fitness[-1]
        fitness_fig.add_annotation(
            x=current_generation,
            y=shortest_distance + 100,
            text=f'Fitness: {shortest_distance:.2f}',
        )


    return curve_fig, fitness_fig

app.layout = html.Div([
    dcc.Graph(id='curve-graph'),
    dcc.Graph(id='fitness-graph'),
    dcc.Interval(id='interval-component', interval=1*200, n_intervals=0, disabled=False)
])

if __name__ == '__main__':
    app.run_server(debug=True)