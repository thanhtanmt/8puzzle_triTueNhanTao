import random
from AI import AI
from collections import defaultdict

class reinforcement_algorithms(AI):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)

    q_table = defaultdict(lambda: {a: 0.0 for a in range(4)})
    def q_learning_search(self, max_episodes=1000, max_steps=100):
        if not self.is_solvable(self.initial):
            return None, 0

        alpha = 0.2  
        gamma = 0.9  
        epsilon = 0.3 
        convergence_threshold = 0.1
        states_explored = 0
        path = [self.initial]

        def hamming_distance(state):
            distance = 0
            for i in range(3):
                for j in range(3):
                    if state[i][j] != 0 and state[i][j] != self.goal[i][j]:
                        distance += 1
            return distance

        def get_neighbors(state):
            i, j = None, None
            for r in range(3):
                for c in range(3):
                    if state[r][c] == 0:
                        i, j = r, c
                        break
            neighbors = []
            directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]  
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < 3 and 0 <= nj < 3:
                    new_state = [list(row) for row in state]
                    new_state[i][j], new_state[ni][nj] = new_state[ni][nj], new_state[i][j]
                    neighbors.append(tuple(tuple(row) for row in new_state))
            return neighbors

        for episode in range(max_episodes):
            current_state = self.initial
            max_delta = 0
            episode_states_explored = 0
            epsilon = max(0.05, epsilon * 0.995)

            for step in range(max_steps):
                state_tuple = current_state

                if random.random() < epsilon:
                    action = random.randint(0, 3)
                else:
                    if not self.q_table[state_tuple]:  
                        action = random.randint(0, 3)  
                    else:
                        action = max(self.q_table[state_tuple], key=self.q_table[state_tuple].get)


                dx, dy = self.get_direction_from_action(action)
                i, j = None, None
                for r in range(3):
                    for c in range(3):
                        if current_state[r][c] == 0:
                            i, j = r, c
                            break
                next_i, next_j = i + dy, j + dx
                neighbors = get_neighbors(current_state)

                if not (0 <= next_i < 3 and 0 <= next_j < 3):
                    reward = -10  
                    next_state = current_state
                else:
                    next_state = [list(row) for row in current_state]
                    next_state[i][j], next_state[next_i][next_j] = next_state[next_i][next_j], next_state[i][j]
                    next_state = tuple(tuple(row) for row in next_state)
                    if next_state not in neighbors:
                        reward = -10
                        next_state = current_state
                    else:
                        distance_before = hamming_distance(current_state)
                        distance_after = hamming_distance(next_state)
                        reward = -0.5 + (distance_before - distance_after) * 5
                        if next_state == self.goal:
                            reward = 100

                next_state_tuple = next_state
                old_value = self.q_table[state_tuple][action]
                max_future_q = max(self.q_table[next_state_tuple].values()) if self.q_table[next_state_tuple] else 0.0
                self.q_table[state_tuple][action] = old_value + alpha * (reward + gamma * max_future_q - old_value)
                max_delta = max(max_delta, abs(old_value - self.q_table[state_tuple][action]))

                states_explored += 1
                episode_states_explored += 1
                current_state = next_state

                if current_state == self.goal:
                    break

            if max_delta < convergence_threshold:
                print(f"Q-Learning converged after {episode + 1} episodes")
                break

        path = [self.initial]
        current_state = self.initial
        visited = set([current_state])
        steps = 0
        while current_state != self.goal and steps < max_steps:
            state_tuple = current_state
            if state_tuple not in self.q_table or not self.q_table[state_tuple]:
                break
            action = max(self.q_table[state_tuple], key=self.q_table[state_tuple].get)
            dx, dy = self.get_direction_from_action(action)
            i, j = None, None
            for r in range(3):
                for c in range(3):
                    if current_state[r][c] == 0:
                        i, j = r, c
                        break
            next_i, next_j = i + dy, j + dx
            if not (0 <= next_i < 3 and 0 <= next_j < 3):
                break
            next_state = [list(row) for row in current_state]
            next_state[i][j], next_state[next_i][next_j] = next_state[next_i][next_j], next_state[i][j]
            next_state = tuple(tuple(row) for row in next_state)
            if next_state not in get_neighbors(current_state) or next_state in visited:
                break
            visited.add(next_state)
            path.append(next_state)
            current_state = next_state
            steps += 1

        if current_state == self.goal:
            return path, states_explored
        return None, states_explored
