import heapq
import time
from AI import AI

class informed_algorithms(AI):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)
    
    def greedy_search(self, timeout=10.0):
        start_time = time.time()
        pq = []
        heapq.heappush(pq, (self.heuristic(self.initial), self.initial, []))
        visited = set()
        explored_states = []

        while pq:
            if time.time() - start_time > timeout:
                print("GBFS timeout after", timeout, "seconds")
                return None, explored_states

            _, state, path = heapq.heappop(pq)
            if state in visited:
                continue

            explored_states.append(state)
            visited.add(state)

            if state == self.goal:
                return path + [state], explored_states

            for neighbor in self.get_neighbors(state):
                if neighbor not in visited:
                    heapq.heappush(pq, (self.heuristic(neighbor), neighbor, path + [state]))

        return None, explored_states
    
    def a_star(self, timeout=10.0):
        start_time = time.time()
        pq = []
        heapq.heappush(pq, (self.heuristic(self.initial), 0, self.initial, []))
        explored_states = []

        while pq:
            if time.time() - start_time > timeout:
                print("A* timeout after", timeout, "seconds")
                return None, explored_states

            f, g, state, path = heapq.heappop(pq)
            explored_states.append(state)

            if state == self.goal:
                return path + [state], explored_states

            for neighbor in self.get_neighbors(state):
                new_g = g + 1
                new_f = new_g + self.heuristic(neighbor)
                heapq.heappush(pq, (new_f, new_g, neighbor, path + [state]))

        return None, explored_states
    
    def ida_star(self, timeout=10.0):
        start_time = time.time()
        threshold = self.heuristic(self.initial)
        explored_states = []
        iteration = 0

        while True:
            if time.time() - start_time > timeout:
                print("IDA* timeout after", timeout, "seconds")
                return None, explored_states

            iteration += 1
            print(f"IDA* iteration {iteration}, threshold = {threshold}")  # Thông báo tiến trình
            result, new_threshold = self.ida_star_recursive(self.initial, [], 0, threshold, explored_states)
            if result:
                return result, explored_states
            if new_threshold == float('inf'):
                return None, explored_states
            threshold = new_threshold

    