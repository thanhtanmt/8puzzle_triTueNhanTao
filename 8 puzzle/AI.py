import random
from collections import deque
class AI:
    def __init__(self, initial, goal):
        self.initial = tuple(map(tuple, initial))
        self.goal = tuple(map(tuple, goal))
        self.rows, self.cols = 3, 3
        self.intermediate_states = []

    def find_blank(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        return None

    def get_neighbors(self, state):
        row_col = self.find_blank(state)
        if row_col is None:
            print("Error: No blank space found!")
            return []  # Trả về danh sách trống nếu không tìm thấy ô trống
        row, col = row_col
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        state_list = [list(row) for row in state]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = [row[:] for row in state_list]
                new_state[row][col], new_state[new_row][new_col] = new_state[new_row][new_col], new_state[row][col]
                moves.append(tuple(map(tuple, new_state)))
        return moves

    def state_to_list(self, state):
        return [num for row in state for num in row]

    def list_to_state(self, lst):
        return tuple(tuple(lst[i * 3:(i + 1) * 3]) for i in range(3))
    
    def generate_random_state(self):
        numbers = list(range(9))
        random.shuffle(numbers)
        state = self.list_to_state(numbers)
        while not self.is_solvable(state):
            random.shuffle(numbers)
            state = self.list_to_state(numbers)
        return state

    def fitness(self, state):
        distance = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] and state[i][j] != self.goal[i][j]:
                    value = state[i][j]
                    goal_i, goal_j = divmod(value - 1, 3)
                    distance += abs(i - goal_i) + abs(j - goal_j)
        return -distance

    def crossover(self, parent1, parent2):
        p1_list = self.state_to_list(parent1)
        p2_list = self.state_to_list(parent2)
        crossover_point = random.randint(1, 7)
        child = p1_list[:crossover_point]
        seen = set(child)
        for num in p2_list:
            if num not in seen:
                child.append(num)
                seen.add(num)
        return self.list_to_state(child)
    
    def mutate(self, state, mutation_rate=0.05):
        state_list = self.state_to_list(state)
        if random.random() < mutation_rate:
            i, j = random.sample(range(9), 2)
            state_list[i], state_list[j] = state_list[j], state_list[i]
        return self.list_to_state(state_list)

    def reconstruct_path(self, final_state):
        path = [self.initial]
        current = self.initial
        while current != final_state:
            neighbors = self.get_neighbors(current)
            current = min(neighbors, key=lambda x: self.heuristic(x), default=final_state)
            path.append(current)
            if current == final_state:
                break
        return path

    def genetic_algorithm(self, population_size=50, max_generations=500):
        population = [self.generate_random_state() for _ in range(population_size)]
        explored_states = []
        best_fitness = float('-inf')
        no_improvement_count = 0
        max_no_improvement = 100

        for generation in range(max_generations):
            population = sorted(population, key=self.fitness, reverse=True)
            explored_states.extend(population[:5])
            best_state = population[0]
            current_fitness = self.fitness(best_state)

            if best_state == self.goal:
                path = self.reconstruct_path(best_state)
                return path, explored_states

            if current_fitness > best_fitness:
                best_fitness = current_fitness
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            if no_improvement_count >= max_no_improvement:
                break

            new_population = population[:population_size // 2]
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(new_population, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            population = new_population

        return None, explored_states

    def heuristic(self, state):
        distance = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] and state[i][j] != self.goal[i][j]:
                    value = state[i][j]
                    goal_i, goal_j = divmod(value - 1, 3)
                    distance += abs(i - goal_i) + abs(j - goal_j)
        return distance

    def ida_star_recursive(self, state, path, g, threshold, explored_states):
        f = g + self.heuristic(state)
        explored_states.append(state)

        if f > threshold:
            return None, f
        if state == self.goal:
            return path + [state], threshold

        min_threshold = float('inf')
        for neighbor in self.get_neighbors(state):
            result, new_threshold = self.ida_star_recursive(neighbor, path + [state], g + 1, threshold, explored_states)
            if result:
                return result, threshold
            min_threshold = min(min_threshold, new_threshold)

        return None, min_threshold

    def is_solvable(self, state=None):
        if state is None:
            state = self.initial
        state_list = [num for row in state for num in row if num != 0]
        inversions = 0
        for i in range(len(state_list)):
            for j in range(i + 1, len(state_list)):
                if state_list[i] > state_list[j]:
                    inversions += 1
        return inversions % 2 == 0

    def get_observation(self, state):
        """
        Giả lập quan sát một phần: chỉ quan sát được vị trí của ô số 1.
        Trả về vị trí (row, col) của ô số 1 trong trạng thái.
        """
        for i in range(3):
            for j in range(3):
                if state[i][j] == 1:
                    return (i, j)
        return None

    def find_states_with_one_at_00(self, start_state, max_states=3): 
        """
        Tìm các trạng thái có số 1 ở vị trí (0,0) bằng BFS.
        start_state: Trạng thái ban đầu.
        max_states: Số trạng thái tối đa cần tìm là 3.
        Trả về: Danh sách các trạng thái (dạng tuple) có số 1 ở (0,0).
        """
        queue = deque([(start_state, [])])
        visited = {start_state}
        states_with_one_at_00 = []

        while queue and len(states_with_one_at_00) < max_states:
            state, path = queue.popleft()
            if self.get_observation(state) == (0, 0):
                states_with_one_at_00.append(state)
                if len(states_with_one_at_00) >= max_states:
                    break
            for neighbor in self.get_neighbors(state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [state]))

        while len(states_with_one_at_00) < max_states:
            numbers = list(range(9))
            random.shuffle(numbers)
            numbers[0] = 1
            remaining_numbers = [num for num in numbers[1:] if num != 1]
            if len(remaining_numbers) < 8:
                remaining_numbers.append(0)
            numbers = [1] + remaining_numbers[:8]
            state = self.list_to_state(numbers)
            if self.is_solvable(state) and state not in states_with_one_at_00:
                states_with_one_at_00.append(state)

        return states_with_one_at_00[:max_states]

    def is_valid_assignment(self, state, pos, value):
        """
        Kiểm tra xem việc gán giá trị cho ô pos có thỏa mãn các ràng buộc không.
        state: Ma trận hiện tại (có thể chứa None).
        pos: Vị trí ô (i,j).
        value: Giá trị cần gán (0-8).
        Trả về: True nếu hợp lệ, False nếu không.
        """
        i, j = pos
        # Ràng buộc: Ô (0,0) phải là 1
        if i == 0 and j == 0 and value != 1:
            return False

        # Ràng buộc: Mỗi số chỉ xuất hiện một lần
        for r in range(3):
            for c in range(3):
                if (r, c) != pos and state[r][c] == value:
                    return False

        # Ràng buộc theo hàng: ô(i,j+1) = ô(i,j) + 1 (trừ ô trống)
        if j > 0 and state[i][j - 1] is not None and value != 0 and state[i][j - 1] != value - 1:
            return False
        if j < 2 and value != 0 and state[i][j + 1] is not None and state[i][j + 1] != value + 1:
            return False

        # Ràng buộc theo cột: ô(i+1,j) = ô(i,j) + 3 (trừ ô trống)
        if i > 0 and state[i - 1][j] is not None and value != 0 and state[i - 1][j] != value - 3:
            return False
        if i < 2 and value != 0 and state[i + 1][j] is not None and state[i + 1][j] != value + 3:
            return False

        return True

    def is_solvable(self, state):
        """
        Kiểm tra xem ma trận có solvable không (số nghịch đảo chẵn).
        state: Ma trận 3x3 (có thể chứa None).
        """
        flat = [state[i][j] for i in range(3) for j in range(3) if state[i][j] is not None and state[i][j] != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        return inversions % 2 == 0

    def forward_checking_search(self, depth_limit=9):
        """
        Forward Checking Search cho CSP: Gán giá trị cho các ô từ ma trận rỗng với Forward Checking, MRV, và LCV.
        depth_limit: Số ô tối đa được gán (9 cho ma trận 3x3).
        Trả về: (path, explored_states) hoặc (None, explored_states).
        """
        visited = set()  # Lưu các trạng thái đã thăm
        explored_states = []  # Lưu các trạng thái đã khám phá
        path = []  # Lưu đường đi từ rỗng đến mục tiêu

        def get_domain(state, pos, assigned):
            """
            Lấy tập giá trị hợp lệ cho ô tại pos.
            state: Ma trận hiện tại.
            pos: Vị trí ô (i,j).
            assigned: Tập các giá trị đã gán.
            Trả về: Danh sách các giá trị hợp lệ.
            """
            domain = []
            for value in range(9):
                if value not in assigned and self.is_valid_assignment(state, pos, value):
                    domain.append(value)
            return domain

        def forward_check(state, pos, value, domains, assigned):
            i, j = pos
            new_domains = {k: v[:] for k, v in domains.items()}
            used_values = set(state[r][c] for r in range(3) for c in range(3) if state[r][c] is not None)

            # Chỉ kiểm tra các ô liền kề
            related_positions = []
            if j > 0: related_positions.append((i, j - 1))
            if j < 2: related_positions.append((i, j + 1))
            if i > 0: related_positions.append((i - 1, j))
            if i < 2: related_positions.append((i + 1, j))

            for other_pos in related_positions:
                if other_pos not in assigned:
                    r, c = other_pos
                    new_domain = [val for val in new_domains[other_pos] if val not in used_values]
                    if (i, j) == (0, 0) and value == 1:
                        if other_pos == (0, 1):
                            new_domain = [2]
                        elif other_pos == (1, 0):
                            new_domain = [4]
                    elif value != 0:
                        if c > 0 and state[r][c - 1] is not None and state[r][c - 1] != 0:
                            new_domain = [val for val in new_domain if val == 0 or state[r][c - 1] == val - 1]
                        if c < 2 and state[r][c + 1] is not None and state[r][c + 1] != 0:
                            new_domain = [val for val in new_domain if val == 0 or state[r][c + 1] == val + 1]
                        if r > 0 and state[r - 1][c] is not None and state[r - 1][c] != 0:
                            new_domain = [val for val in new_domain if val == 0 or state[r - 1][c] == val - 3]
                        if r < 2 and state[r + 1][c] is not None and state[r + 1][c] != 0:
                            new_domain = [val for val in new_domain if val == 0 or state[r + 1][c] == val + 3]
                    new_domains[other_pos] = new_domain
                    if not new_domain:
                        return False, domains
            return True, new_domains

        def select_mrv_variable(positions, domains, state):
            """
            Chọn ô có ít giá trị hợp lệ nhất (MRV), đúng lý thuyết.
            positions: Danh sách các ô chưa gán.
            domains: Từ điển chứa tập giá trị hợp lệ.
            state: Ma trận hiện tại.
            Trả về: Vị trí ô được chọn.
            """
            min_domain_size = float('inf')
            selected_pos = None
            for pos in positions:
                domain_size = len(domains[pos])
                if domain_size < min_domain_size:
                    min_domain_size = domain_size
                    selected_pos = pos
            return selected_pos

        def select_lcv_value(pos, domain, state, domains, assigned):
            """
            Chọn giá trị ít ràng buộc nhất (LCV), đúng lý thuyết.
            pos: Vị trí ô đang gán.
            domain: Tập giá trị hợp lệ của ô.
            state: Ma trận hiện tại.
            domains: Từ điển chứa tập giá trị hợp lệ.
            assigned: Tập các giá trị đã gán.
            Trả về: Danh sách giá trị sắp xếp theo số giá trị bị loại bỏ (ít nhất đến nhiều nhất).
            """
            value_scores = []
            for value in domain:
                temp_state = [row[:] for row in state]
                temp_state[pos[0]][pos[1]] = value
                _, new_domains = forward_check(temp_state, pos, value, domains, assigned)
                eliminated = sum(len(domains[p]) - len(new_domains[p]) for p in new_domains if p != pos)
                value_scores.append((eliminated, value))
            value_scores.sort()
            return [value for _, value in value_scores]

        def backtrack_with_fc(state, assigned, positions, domains):
            """
            Hàm đệ quy để thực hiện backtracking với Forward Checking.
            state: Ma trận hiện tại (có thể chứa None).
            assigned: Tập các vị trí và giá trị đã gán.
            positions: Danh sách các ô chưa gán.
            domains: Từ điển chứa tập giá trị hợp lệ cho các ô.
            """
            if len(assigned) == 9:  # Đã gán hết 9 ô
                state_tuple = tuple(tuple(row) for row in state)
                if state_tuple == self.goal and self.is_solvable(state):
                    path.append(state_tuple)
                    return path
                return None

            # Kiểm tra sớm trạng thái mục tiêu khi gán từ 7 ô trở lên
            if len(assigned) >= 7:
                temp_state = [row[:] for row in state]
                temp_assigned = assigned.copy()
                temp_positions = [p for p in positions if p not in assigned]
                temp_domains = {k: v[:] for k, v in domains.items()}
                for p in temp_positions:
                    remaining_values = [v for v in range(9) if v not in temp_assigned.values()]
                    if not remaining_values:
                        return None
                    value = remaining_values[0]  # Chọn giá trị đầu tiên
                    temp_state[p[0]][p[1]] = value
                    temp_assigned[p] = value
                    temp_tuple = tuple(tuple(row) for row in temp_state)
                    path.append(temp_tuple)  # Thêm trạng thái trung gian
                    success, temp_domains = forward_check(temp_state, p, value, temp_domains, temp_assigned)
                    if not success:
                        path.pop()
                        return None
                state_tuple = tuple(tuple(row) for row in temp_state)
                if state_tuple == self.goal and self.is_solvable(temp_state):
                    return path
                path.pop(len(temp_positions))  # Xóa các trạng thái trung gian nếu thất bại
                return None

            # Chọn ô có ít giá trị hợp lệ nhất (MRV)
            pos = select_mrv_variable(positions, domains, state)
            if pos is None:
                return None

            # Lấy tập giá trị hợp lệ và sắp xếp theo LCV
            domain = get_domain(state, pos, set(assigned.values()))
            sorted_values = select_lcv_value(pos, domain, state, domains, assigned)

            # Tạo bản sao trạng thái
            state_tuple = tuple(tuple(row if row is not None else (None, None, None)) for row in state)
            if state_tuple in visited:
                return None
            visited.add(state_tuple)
            explored_states.append(state_tuple)

            # Thử gán các giá trị theo thứ tự LCV
            for value in sorted_values:
                new_state = [row[:] for row in state]
                new_state[pos[0]][pos[1]] = value
                new_assigned = assigned.copy()
                new_assigned[pos] = value
                new_positions = [p for p in positions if p != pos]
                path.append(state_tuple)  # Thêm trạng thái trước khi gán

                # Thực hiện Forward Checking
                success, new_domains = forward_check(new_state, pos, value, domains, new_assigned)
                if success:
                    result = backtrack_with_fc(new_state, new_assigned, new_positions, new_domains)
                    if result is not None:
                        return result
                path.pop()  # Quay lui: xóa trạng thái nếu không thành công

            return None

        # Khởi tạo ma trận rỗng và tập giá trị ban đầu
        empty_state = [[None for _ in range(3)] for _ in range(3)]
        positions = [(i, j) for i in range(3) for j in range(3)]
        domains = {(i, j): list(range(9)) for i in range(3) for j in range(3)}
        assigned = {}
        result = backtrack_with_fc(empty_state, assigned, positions, domains)
        return result, explored_states

    def get_direction_from_action(self, action):
        if action == 0:  # Lên
            return 0, -1
        elif action == 1:  # Xuống
            return 0, 1
        elif action == 2:  # Phải
            return 1, 0
        elif action == 3:  # Trái
            return -1, 0
        return 0, 0
