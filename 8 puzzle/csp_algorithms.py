from AI import AI
from collections import deque
from collections import defaultdict
import random
import time

class csp_algorithms(AI):
    def __init__(self, initial, goal):
        super().__init__(initial, goal)

    def backtracking_search(self, depth_limit=9):
        visited = set() 
        explored_states = []  
        path = [] 

        def is_valid_assignment(state, pos, value):
            i, j = pos
            if i == 0 and j == 0 and value != 1:
                return False

            for r in range(3):
                for c in range(3):
                    if (r, c) != pos and state[r][c] == value:
                        return False

            if j > 0 and state[i][j - 1] is not None and value != 0 and state[i][j - 1] != value - 1:
                return False
            if j < 2 and state[i][j + 1] is not None and value != 0 and state[i][j + 1] != value + 1:
                return False

            if i > 0 and state[i - 1][j] is not None and value != 0 and state[i - 1][j] != value - 3:
                return False
            if i < 2 and state[i + 1][j] is not None and value != 0 and state[i + 1][j] != value + 3:
                return False

            return True

        def is_solvable(state):
            flat = [state[i][j] for i in range(3) for j in range(3) if state[i][j] is not None and state[i][j] != 0]
            inversions = 0
            for i in range(len(flat)):
                for j in range(i + 1, len(flat)):
                    if flat[i] > flat[j]:
                        inversions += 1
            return inversions % 2 == 0

        def backtrack(state, assigned, pos_index):
            # Base case: All cells assigned
            if pos_index == 9:
                state_tuple = tuple(tuple(row) for row in state)
                if state_tuple == self.goal and is_solvable(state):
                    path.append(state_tuple)
                    return path
                return None

            # Get the next cell position
            i, j = divmod(pos_index, 3)
            if i >= 3 or j >= 3:
                return None

            # Create a state tuple for checking visited states
            state_tuple = tuple(tuple(row if row is not None else (None, None, None)) for row in state)
            if state_tuple in visited:
                return None
            visited.add(state_tuple)
            explored_states.append(state_tuple)

            # Try assigning each possible value
            for value in range(9):
                if value not in assigned and is_valid_assignment(state, (i, j), value):
                    # Assign the value
                    new_state = [row[:] for row in state]
                    new_state[i][j] = value
                    new_assigned = assigned | {value}

                    # Add current state to path before recursion
                    path.append(state_tuple)

                    # Recurse to the next cell
                    result = backtrack(new_state, new_assigned, pos_index + 1)
                    if result is not None:
                        return result

                    # Backtrack: Remove the state from path
                    path.pop()

            return None

        # Initialize empty matrix and start backtracking
        empty_state = [[None for _ in range(3)] for _ in range(3)]
        result = backtrack(empty_state, set(), 0)
        return result, explored_states
    
    def forward_checking_search(self, depth_limit=9):
        visited = set()  # Lưu các trạng thái đã thăm
        explored_states = []  # Lưu các trạng thái đã khám phá
        path = []  # Lưu đường đi từ rỗng đến mục tiêu

        def get_domain(state, pos, assigned):
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
            min_domain_size = float('inf')
            selected_pos = None
            for pos in positions:
                domain_size = len(domains[pos])
                if domain_size < min_domain_size:
                    min_domain_size = domain_size
                    selected_pos = pos
            return selected_pos

        def select_lcv_value(pos, domain, state, domains, assigned):
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


        empty_state = [[None for _ in range(3)] for _ in range(3)]
        positions = [(i, j) for i in range(3) for j in range(3)]
        domains = {(i, j): list(range(9)) for i in range(3) for j in range(3)}
        assigned = {}
        result = backtrack_with_fc(empty_state, assigned, positions, domains)
        return result, explored_states
    
    def min_conflicts_search(self, max_iterations=1000, max_no_improvement=20, timeout=2.0):

        def count_conflicts(state):
            conflicts = 0
            value_counts = defaultdict(int)

            # Constraint: (0,0) must be 1
            if state[0][0] != 1:
                conflicts += 1

            # Constraint: Each number appears exactly once
            for i in range(3):
                for j in range(3):
                    val = state[i][j]
                    value_counts[val] += 1
                    if value_counts[val] > 1:
                        conflicts += value_counts[val] - 1

            # Row constraint: state[i][j+1] = state[i][j] + 1 (except blank)
            for i in range(3):
                for j in range(2):
                    if state[i][j] != 0 and state[i][j + 1] != 0:
                        if state[i][j + 1] != state[i][j] + 1:
                            conflicts += 1

            # Column constraint: state[i+1][j] = state[i][j] + 3 (except blank)
            for j in range(3):
                for i in range(2):
                    if state[i][j] != 0 and state[i + 1][j] != 0:
                        if state[i + 1][j] != state[i][j] + 3:
                            conflicts += 1

            # Solvability constraint (only check if state is complete)
            if all(state[i][j] is not None for i in range(3) for j in range(3)):
                if not self.is_solvable(state):
                    conflicts += 1

            return conflicts

        def get_conflicting_positions(state):
            """
            Identify positions that cause conflicts.

            Returns:
                list: List of (i, j) positions with conflicts.
            """
            conflicts = []
            value_counts = defaultdict(int)
            conflict_positions = set()

            # Check (0,0) must be 1
            if state[0][0] != 1:
                conflict_positions.add((0, 0))

            # Check unique values
            for i in range(3):
                for j in range(3):
                    val = state[i][j]
                    value_counts[val] += 1
                    if value_counts[val] > 1:
                        conflict_positions.add((i, j))

            # Check row constraints
            for i in range(3):
                for j in range(2):
                    if state[i][j] != 0 and state[i][j + 1] != 0:
                        if state[i][j + 1] != state[i][j] + 1:
                            conflict_positions.add((i, j))
                            conflict_positions.add((i, j + 1))

            # Check column constraints
            for j in range(3):
                for i in range(2):
                    if state[i][j] != 0 and state[i + 1][j] != 0:
                        if state[i + 1][j] != state[i][j] + 3:
                            conflict_positions.add((i, j))
                            conflict_positions.add((i + 1, j))

            # Check solvability
            if all(state[i][j] is not None for i in range(3) for j in range(3)):
                if not self.is_solvable(state):
                    for i in range(3):
                        for j in range(3):
                            conflict_positions.add((i, j))

            return list(conflict_positions)

        def select_min_conflict_value(state, i, j, current_value, assigned_values):
            """
            Select a value for position (i, j) that minimizes conflicts, possibly by swapping.

            Args:
                state: Current state of the puzzle.
                i, j: Position to assign a value.
                current_value: Current value at (i, j).
                assigned_values: Set of values already used.

            Returns:
                tuple: (new_value, swap_pos) where new_value is the value to assign,
                       and swap_pos is the position to swap with (or None if no swap).
            """
            value_scores = []
            state_copy = [row[:] for row in state]

            # Try swapping with other positions
            for r in range(3):
                for c in range(3):
                    if (r, c) != (i, j):
                        state_copy = [row[:] for row in state]
                        state_copy[i][j], state_copy[r][c] = state_copy[r][c], state_copy[i][j]
                        conflicts = count_conflicts(state_copy)
                        value_scores.append((conflicts, state[r][c], (r, c)))

            # Try assigning new values not in assigned_values
            for value in range(9):
                if value not in assigned_values - ({current_value} if current_value is not None else set()):
                    if (i, j) == (0, 0) and value != 1:
                        continue
                    state_copy = [row[:] for row in state]
                    state_copy[i][j] = value
                    conflicts = count_conflicts(state_copy)
                    value_scores.append((conflicts, value, None))

            if not value_scores:
                return None, None

            value_scores.sort()
            return value_scores[0][1], value_scores[0][2]

        def initialize_state():
            """
            Generate a random initial assignment for all variables.

            Returns:
                list: A 3x3 matrix with a valid initial assignment.
            """
            state = [[None for _ in range(3)] for _ in range(3)]
            numbers = list(range(9))
            random.shuffle(numbers)
            state[0][0] = 1  # Enforce (0,0) = 1
            numbers.remove(1)
            idx = 0
            for i in range(3):
                for j in range(3):
                    if (i, j) != (0, 0):
                        state[i][j] = numbers[idx]
                        idx += 1
            return state

        start_time = time.time()
        current_state = initialize_state()
        path = [tuple(tuple(row) for row in current_state)]
        num_explored_states = 1
        best_conflicts = float('inf')
        best_state = [row[:] for row in current_state]
        no_improvement_count = 0
        assigned_values = set(range(9))
        assigned_positions = {(i, j) for i in range(3) for j in range(3)}

        for iteration in range(max_iterations):
            if time.time() - start_time > timeout:
                print("Timeout reached")
                return None, num_explored_states

            current_state_tuple = tuple(tuple(row) for row in current_state)
            conflicts = count_conflicts(current_state)

            # Check if current state is a solution
            if current_state_tuple == self.goal and self.is_solvable(current_state):
                print(f"Solution found after {iteration} iterations")
                return path, num_explored_states

            if conflicts < best_conflicts:
                best_conflicts = conflicts
                best_state = [row[:] for row in current_state]
                no_improvement_count = 0
            else:
                no_improvement_count += 1

            # Restart with a new random assignment if no improvement
            if no_improvement_count >= max_no_improvement:
                current_state = initialize_state()
                assigned_values = set(range(9))
                assigned_positions = {(i, j) for i in range(3) for j in range(3)}
                current_state_tuple = tuple(tuple(row) for row in current_state)
                path.append(current_state_tuple)
                num_explored_states += 1
                conflicts = count_conflicts(current_state)
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_state = [row[:] for row in current_state]
                no_improvement_count = 0
                continue

            # Select a conflicting position
            conflicting_positions = get_conflicting_positions(current_state)
            if not conflicting_positions:
                if conflicts == 0 and self.is_solvable(current_state):
                    print(f"Solution found after {iteration} iterations")
                    return path, num_explored_states
                else:
                    # No conflicts but not a solution, restart
                    current_state = initialize_state()
                    assigned_values = set(range(9))
                    assigned_positions = {(i, j) for i in range(3) for j in range(3)}
                    current_state_tuple = tuple(tuple(row) for row in current_state)
                    path.append(current_state_tuple)
                    num_explored_states += 1
                    continue

            # Randomly select a conflicting position
            i, j = random.choice(conflicting_positions)
            current_value = current_state[i][j]

            # Select a value (or swap) that minimizes conflicts
            new_value, swap_pos = select_min_conflict_value(current_state, i, j, current_value, assigned_values)

            if new_value is None:
                continue

            # Update state
            current_state_list = [row[:] for row in current_state]
            if swap_pos:
                r, c = swap_pos
                current_state_list[i][j], current_state_list[r][c] = current_state_list[r][c], current_state_list[i][j]
            else:
                current_state_list[i][j] = new_value
                assigned_values.remove(current_value)
                assigned_values.add(new_value)

            current_state = current_state_list
            current_state_tuple = tuple(tuple(row) for row in current_state)
            path.append(current_state_tuple)
            num_explored_states += 1

        # Check if the best state is a solution
        if tuple(tuple(row) for row in best_state) == self.goal and self.is_solvable(best_state):
            print("Returning best state as solution")
            return path, num_explored_states
        print("No solution found")
        return None, num_explored_states
    
    def backtracking_puzzle(self, depth_limit=9):
        visited = set()  # Lưu các trạng thái đã duyệt
        explored_states = []  # Lưu các trạng thái đã khám phá
        solution_path = []  # Lưu đường đi đến mục tiêu

        def is_valid_assignment(state, pos, value):
            i, j = pos
            # Ràng buộc: Ô (0,0) phải là 1
            if i == 0 and j == 0 and value != 1:
                return False

            # Kiểm tra giá trị trùng lặp
            for r in range(3):
                for c in range(3):
                    if (r, c) != pos and state[r][c] == value:
                        return False

            # Ràng buộc lân cận
            if j > 0 and state[i][j - 1] is not None and value != 0 and state[i][j - 1] != value - 1:
                return False
            if j < 2 and state[i][j + 1] is not None and value != 0 and state[i][j + 1] != value + 1:
                return False
            if i > 0 and state[i - 1][j] is not None and value != 0 and state[i - 1][j] != value - 3:
                return False
            if i < 2 and state[i + 1][j] is not None and value != 0 and state[i + 1][j] != value + 3:
                return False

            return True

        def is_solvable(state):
            flat = [state[i][j] for i in range(3) for j in range(3) if state[i][j] is not None and state[i][j] != 0]
            inversions = 0
            for i in range(len(flat)):
                for j in range(i + 1, len(flat)):
                    if flat[i] > flat[j]:
                        inversions += 1
            return inversions % 2 == 0

        def backtrack(state, assigned, pos_index, current_depth):
            # Kiểm tra giới hạn độ sâu
            if current_depth > depth_limit:
                return None

            # Base case: Đã gán hết 9 ô
            if pos_index == 9:
                state_tuple = tuple(tuple(row) for row in state)
                if state_tuple == self.goal:
                    solution_path.append(state_tuple)
                    return solution_path
                return None

            # Lấy vị trí ô tiếp theo
            i, j = divmod(pos_index, 3)

            # Kiểm tra trạng thái đã duyệt
            state_tuple = tuple(tuple(row) for row in state)
            if state_tuple in visited:
                return None
            visited.add(state_tuple)
            explored_states.append(state_tuple)

            # Thử gán các giá trị từ 0 đến 8
            for value in range(9):
                if value not in assigned and is_valid_assignment(state, (i, j), value):
                    # Sao chép trạng thái, đảm bảo là danh sách
                    new_state = [list(row) for row in state]
                    new_state[i][j] = value
                    new_state_tuple = tuple(tuple(row) for row in new_state)

                    # Thêm trạng thái mới vào đường đi
                    solution_path.append(new_state_tuple)
                    assigned.add(value)

                    # Gọi đệ quy
                    result = backtrack(new_state, assigned, pos_index + 1, current_depth + 1)
                    if result is not None:
                        return result

                    # Quay lui
                    solution_path.pop()
                    assigned.remove(value)

            return None

        # Kiểm tra trạng thái ban đầu
        if not is_solvable(self.initial):
            return [], explored_states

        # Khởi tạo trạng thái ban đầu (chuyển thành danh sách nếu cần)
        initial_state = [list(row) for row in self.initial]
        solution_path = [tuple(tuple(row) for row in self.initial)]
        result = backtrack(initial_state, set(), 0, 0)

        return result if result is not None else [], explored_states

