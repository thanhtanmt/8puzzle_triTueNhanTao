import heapq
from collections import deque
from AI import AI

class uniformed_algorithms(AI):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)
    
    def bfs(self):
        queue = deque([(self.initial, [])])
        visited = {self.initial}
        explored_states = []

        while queue:
            state, path = queue.popleft()
            explored_states.append(state)
            if state == self.goal:
                return path + [state], explored_states
            for neighbor in self.get_neighbors(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [state]))
        return None, explored_states

    def dfs(self):
        stack = [(self.initial, [])]
        visited = {self.initial}
        explored_states = []
        while stack:
            state, path = stack.pop()
            explored_states.append(state)
            if state == self.goal:
                return path + [state], explored_states
            for neighbor in self.get_neighbors(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, path + [state]))
        return None, explored_states

    def ucs(self):
        open_list = []
        heapq.heappush(open_list, (0, self.initial, []))
        visited = {}
        explored_states = []

        while open_list:
            cost, state, path = heapq.heappop(open_list)
            explored_states.append(state)
            if state in visited and visited[state] < cost:
                continue
            visited[state] = cost
            if state == self.goal:
                return path + [state], explored_states
            for neighbor in self.get_neighbors(state):
                new_cost = cost + 1
                if neighbor not in visited or new_cost < visited[neighbor]:
                    heapq.heappush(open_list, (new_cost, neighbor, path + [state]))
        return None, explored_states

    def depth_limited_search(self, state, path, depth, visited):
        explored_states = []
        if state == self.goal:
            return path + [state], explored_states
        if depth == 0:
            return None, explored_states
        visited.add(state)
        explored_states.append(state)
        for neighbor in self.get_neighbors(state):
            if neighbor not in visited:
                result, sub_explored = self.depth_limited_search(neighbor, path + [state], depth - 1, visited)
                explored_states.extend(sub_explored)
                if result:
                    return result, explored_states
        return None, explored_states

    def ids(self):
        max_depth = 100
        depth = 0
        while depth <= max_depth:
            visited = set()
            result, explored_states = self.depth_limited_search(self.initial, [], depth, visited)
            if result:
                return result, explored_states
            depth += 1
        return None, []
