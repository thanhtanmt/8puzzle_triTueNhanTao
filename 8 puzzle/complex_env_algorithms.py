import random
from collections import deque, defaultdict
from AI import AI

class complex_env_algorithms(AI):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)

    def and_or_search(self, max_steps=1000):
        queue = deque([(self.initial, [], {self.initial}, None)])  # (state, path, and_group, action)
        visited = set()
        explored_states = []
        num_steps = 0

        while queue and num_steps < max_steps:
            state, path, and_group, action = queue.popleft()
            explored_states.append(state)
            num_steps += 1

            # Kiểm tra nhánh AND: Tất cả trạng thái trong and_group phải là mục tiêu
            if all(s == self.goal for s in and_group):
                state_path = [p for p, a in path] + [state]
                return state_path, explored_states

            state_tuple = frozenset(and_group)
            if state_tuple in visited:
                continue
            visited.add(state_tuple)

            # Nhánh OR: Lựa chọn giữa các hành động (lên, xuống, trái, phải)
            neighbors = self.get_neighbors(state)
            for action_idx, neighbor in enumerate(neighbors):
                # Nhánh AND: Tạo tất cả trạng thái có thể xảy ra sau hành động
                and_states = {neighbor}  # Trạng thái bình thường

                # Tạo trạng thái không xác định với xác suất 50%
                if random.random() < 0.7:  # Xác suất 50%
                    i, j = self.find_blank(neighbor)
                    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                    valid_directions = [(di, dj) for di, dj in directions if 0 <= i + di < 3 and 0 <= j + dj < 3]
                    for di, dj in valid_directions:
                        ni, nj = i + di, j + dj
                        state_list = list(map(list, neighbor))
                        state_list[i][j], state_list[ni][nj] = state_list[ni][nj], state_list[i][j]
                        uncertain_state = tuple(map(tuple, state_list))
                        and_states.add(uncertain_state)

                # Thêm nhánh AND vào hàng đợi (không thu hẹp and_states)
                if and_states:
                    action_name = ["up", "down", "right", "left"][action_idx]
                    queue.append((neighbor, path + [(state, action_name)], and_states, action_name))

        return None, explored_states
     
    def belief_propagation(self, max_steps=1000):
        # Tìm các trạng thái ban đầu với số 1 ở (0, 0)
        initial_belief = self.find_states_with_one_at_00(self.initial, max_states=3)

        # Hàng đợi với các trạng thái ban đầu
        belief_queue = deque([(initial_belief, [])])  
        visited = set()
        explored_states = []
        belief_states_path = list(initial_belief)  # Lưu các trạng thái đã đi qua, mỗi trạng thái là tuple

        steps = 0
        while belief_queue and steps < max_steps:
            belief_state, path = belief_queue.popleft()

            # Kiểm tra mục tiêu: Nếu tất cả các trạng thái trong belief_state đều là goal
            if all(state == self.goal for state in belief_state):
                belief_states_path.append(tuple(self.goal))  # Lưu lại path cho mục tiêu
                return belief_states_path, explored_states

            # Nếu trạng thái đã được duyệt, bỏ qua
            belief_state_tuple = frozenset(belief_state)  # Chuyển belief_state thành frozenset để kiểm tra
            if belief_state_tuple in visited:
                continue

            visited.add(belief_state_tuple)
            explored_states.extend(belief_state)  # Thêm các trạng thái đã duyệt

            # Duyệt qua các trạng thái lân cận
            for neighbor in self.get_neighbors(belief_state[0]):  # Lấy trạng thái đầu tiên trong belief_state
                if neighbor not in visited:
                    visited.add(neighbor)
                    belief_queue.append(([neighbor], path + [neighbor]))
                    belief_states_path.append(neighbor)  # Lưu lại trạng thái lân cận

            steps += 1

        return None, explored_states

    def pos_search(self, max_steps=1000):
        initial_belief = self.find_states_with_one_at_00(self.initial, max_states=3)
        
        belief_queue = deque([(tuple(initial_belief), [])]) 
        visited = set() 
        explored_states = set() 
        belief_states_path = [] 
        steps = 0
        while belief_queue and steps < max_steps:
            belief_state, path = belief_queue.popleft()
            if any(state == self.goal for state in belief_state):
                belief_states_path.extend(path + [self.goal])
                return belief_states_path, list(explored_states)

            belief_state_tuple = frozenset(belief_state)
            if belief_state_tuple in visited:
                continue

            visited.add(belief_state_tuple)
            explored_states.update(belief_state) 

            next_belief = set()  # Tập hợp các trạng thái lân cận
            for state in belief_state:
                for neighbor in self.get_neighbors(state):
                    next_belief.add(neighbor)

            # Thêm belief_state mới vào hàng đợi
            next_belief_tuple = frozenset(next_belief)
            if next_belief_tuple not in visited:
                belief_queue.append((list(next_belief), path + [list(next_belief)[0]]))  # Thêm trạng thái đầu tiên vào path
                belief_states_path.append(list(next_belief)[0])  # Lưu trạng thái đại diện

            steps += 1

        return [], list(explored_states)  # Trả về danh sách rỗng nếu không tìm thấy

