import random
import math
from AI import AI

class local_search_algorithms(AI):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)

    def simple_hill_climbing(self):
        current = self.initial
        path = [current]
        explored_states = []

        while True:
            explored_states.append(current)
            neighbors = self.get_neighbors(current)
            next_state = None
            current_heuristic = self.heuristic(current)

            for neighbor in neighbors:
                if self.heuristic(neighbor) < current_heuristic:
                    next_state = neighbor
                    break

            if next_state is None:
                break

            current = next_state
            path.append(current)

            if current == self.goal:
                return path, explored_states

        return None, explored_states
    
    def steepest_ascent_hill_climbing(self):
        current = self.initial
        path = [current]
        explored_states = []

        while True:
            explored_states.append(current)
            neighbors = self.get_neighbors(current)
            next_state = None
            best_heuristic = float('inf')

            for neighbor in neighbors:
                neighbor_heuristic = self.heuristic(neighbor)
                if neighbor_heuristic < best_heuristic:
                    best_heuristic = neighbor_heuristic
                    next_state = neighbor

            if next_state is None or best_heuristic >= self.heuristic(current):
                break

            current = next_state
            path.append(current)

            if current == self.goal:
                return path, explored_states

        return None, explored_states
    
    def random_hill_climbing(self):
        current = self.initial
        path = [current]
        explored_states = []

        while True:
            explored_states.append(current)
            neighbors = self.get_neighbors(current)
            next_states = [neighbor for neighbor in neighbors if self.heuristic(neighbor) < self.heuristic(current)]

            if not next_states:
                break

            next_state = random.choice(next_states)
            current = next_state
            path.append(current)

            if current == self.goal:
                return path, explored_states

        return None, explored_states
    
    def simulated_annealing(self):
        current = self.initial
        path = [current]
        explored_states = set()
        current_heuristic = self.heuristic(current)
        best_state = current
        best_heuristic = current_heuristic

        temperature = 1000.0 
        cooling_rate = 0.99
        no_improvement_count = 0
        max_no_improvement = 2000

        while temperature > 0.01 and no_improvement_count < max_no_improvement:
            explored_states.add(current)

            neighbors = self.get_neighbors(current)
            if not neighbors:
                break

            neighbor_heuristic_pairs = [(neighbor, self.heuristic(neighbor)) for neighbor in neighbors]
            neighbor_heuristic_pairs.sort(key=lambda x: x[1])
            next_state, next_heuristic = neighbor_heuristic_pairs[0]

            if next_heuristic >= current_heuristic:
                delta = next_heuristic - current_heuristic
                acceptance_probability = math.exp(-delta / temperature)
                if random.uniform(0, 1) > acceptance_probability:
                    next_state, next_heuristic = random.choice(neighbor_heuristic_pairs)

            if next_heuristic < current_heuristic:
                no_improvement_count = 0
                if next_heuristic < best_heuristic:
                    best_state = next_state
                    best_heuristic = next_heuristic
            else:
                no_improvement_count += 1

            current = next_state
            current_heuristic = next_heuristic
            path.append(current)

            if current == self.goal:
                return path, list(explored_states)

            temperature *= cooling_rate

        if best_state == self.goal:
            return self.reconstruct_path(best_state), list(explored_states)
        return None, list(explored_states)
    
    def beam_search(self, beam_width=5):
        initial_state = self.initial
        if initial_state == self.goal:
            return [initial_state], []

        current_states = [initial_state]
        path = {initial_state: []}

        while current_states:
            next_states = []
            for state in current_states:
                neighbors = self.get_neighbors(state)
                for neighbor in neighbors:
                    if neighbor not in path:
                        path[neighbor] = path[state] + [state]
                        next_states.append(neighbor)

            evaluated = [(self.heuristic(state), state) for state in next_states]
            evaluated.sort(key=lambda x: x[0])

            current_states = [state for (_, state) in evaluated[:beam_width]]

            if self.goal in current_states:
                return path[self.goal] + [self.goal], list(path.keys())

        return None, list(path.keys())
