import numpy as np
import random
import math
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

cities_with_coordinates = [
    {"city_name": "Mexico City", "X": 10, "Y": 190},
    {"city_name": "Guadalajara", "X": 20, "Y": 20},
    {"city_name": "Monterrey", "X": 30, "Y": 250},
    {"city_name": "Puebla", "X": 40, "Y": 59},
    {"city_name": "Tijuana", "X": 57, "Y": 200},
    {"city_name": "León", "X": 61, "Y": 68},
    {"city_name": "Cancún", "X": 76, "Y": 81},
    {"city_name": "Mérida", "X": 80, "Y": 80},
    {"city_name": "Toluca", "X": 99, "Y": 19},
    {"city_name": "Querétaro", "X": 100, "Y": 20},
    {"city_name": "Chihuahua", "X": 106, "Y": 28},
    {"city_name": "Saltillo", "X": 120, "Y": 25},
    {"city_name": "Morelia", "X": 131, "Y": 19},
    {"city_name": "Culiacán", ""
                              "X": 147, "Y": 24},
    {"city_name": "Aguascalientes", "X": 102, "Y": 21},
    {"city_name": "Hermosillo", "X": 110, "Y": 29},
    {"city_name": "Veracruz", "X": 96, "Y": 19},
    {"city_name": "Villahermosa", "X": 92, "Y": 17},
    {"city_name": "Durango", "X": 104, "Y": 24},
    {"city_name": "Torreón", "X": 103, "Y": 25}
]

class TSP:
    def __init__(self):
        self.matrix = self._generate_matrix()
        self.routes = []
        self.parents = []
        self.children = []
        self.best_distances = []
        self.best_route = None

    def _generate_child(self, parent: list[int]):
        reproduction_method = random.choice([self._crossover_reproduction, self._inversion_reproduction])
        return reproduction_method(parent)

    def _generate_best_gen(self):
        opponents = random.sample(range(0, 100), 5)
        best_opponent = opponents[0]
        for opponent in opponents:
            # Check if it is taking the best router child or only the index
            if self.routes[opponent] < self.routes[best_opponent]:
                best_opponent = opponent
        return self.matrix[best_opponent]

    def _calculate_route(self, column: list[int]):
        total_distance = 0
        for idx in range(1, len(column)):
            city1 = cities_with_coordinates[column[idx - 1]]
            city2 = cities_with_coordinates[column[idx]]
            total = self._calculate_distance(city1["X"], city1["Y"], city2["X"], city2["Y"])
            total_distance += total
        return total_distance

    def _generate_shuffled_row(self):
        row = list(range(0, 20))
        random.shuffle(row)
        return row

    def _generate_matrix(self, rows=100):
        return np.array([self._generate_shuffled_row() for _ in range(rows)])

    def _calculate_distance(self, x1, y1, x2, y2):
        distance = math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
        return distance

    def _crossover_reproduction(self, parent: list[int]):
        length = len(parent)
        if length < 2:
            return parent
        max_section_length = length // 2
        section_length = random.randint(1, max_section_length)
        start1 = random.randint(0, length - section_length)
        start2 = random.randint(0, length - section_length)
        max_attempts = 100
        attempts = 0
        while abs(start1 - start2) < section_length and attempts < max_attempts:
            start2 = random.randint(0, length - section_length)
            attempts += 1
        if attempts >= max_attempts:
            start1 = 0
            start2 = length - section_length

        section1 = parent[start1:start1 + section_length]
        section2 = parent[start2:start2 + section_length]
        child = list(parent)
        child[start2:(start2 + section_length)] = section1[:]
        child[start1:(start1 + section_length)] = section2[:]
        return child

    def _inversion_reproduction(self, parent: list[int]):
        length = len(parent)
        if length < 2: return parent
        start = random.randint(0, length - 2)
        end = random.randint(start + 1, length - 1)
        child = parent[:]
        child[start:end + 1] = child[start:end + 1][::-1]
        return child

    def run(self, generations=5):
        #for generation in range(generations):
        self.routes = [self._calculate_route(col) for col in self.matrix]
        self.parents = [self._generate_best_gen() for _ in range(100)]
        self.children = [self._generate_child(parent) for parent in self.parents]
        self.routes = [self._calculate_route(child) for child in self.children]
        best_route_index = self.routes.index(min(self.routes))
        self.best_route = self.children[best_route_index]
        print("Best route", self.best_route)
        self.best_distances.append(self.routes[best_route_index])
        #print("Best distance", self.best_distances)
        self.matrix = np.array(self.children)

# Initialize TSP
tsp = TSP()

# Dash app setup
app = dash.Dash(__name__)

@app.callback(
    [Output('route-graph', 'figure'),
     Output('fitness-graph', 'figure'),
     Output('interval-component', 'disabled')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    if n < 1000:
        tsp.run(1)
        disabled = False
    else:
        disabled = True

    route_fig = go.Figure()
    if tsp.best_route is not None and len(tsp.best_route) > 0:
        x_coords = [cities_with_coordinates[city]["X"] for city in tsp.best_route]
        y_coords = [cities_with_coordinates[city]["Y"] for city in tsp.best_route]
        route_fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='lines+markers'))
        route_fig.update_layout(title='Best Route', xaxis_title='X Coordinate', yaxis_title='Y Coordinate', height=600)

    fitness_fig = go.Figure()
    fitness_fig.add_trace(go.Scatter(x=list(range(1, len(tsp.best_distances) + 1)), y=tsp.best_distances, mode='lines+markers'))
    fitness_fig.update_layout(title='Fitness Over Generations', xaxis_title='Generation', yaxis_title='Distance', height=600)

    if tsp.best_distances:
        current_generation = len(tsp.best_distances)
        shortest_distance = tsp.best_distances[-1]
        fitness_fig.add_annotation(
            x=current_generation,
            y=shortest_distance,
            text=f'Shortest Distance: {shortest_distance:.2f}',
            showarrow=True,
            arrowhead=1
        )

    return route_fig, fitness_fig, disabled

app.layout = html.Div([
    dcc.Graph(id='route-graph'),
    dcc.Graph(id='fitness-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0, disabled=False)
])

if __name__ == '__main__':
    app.run_server(debug=True)