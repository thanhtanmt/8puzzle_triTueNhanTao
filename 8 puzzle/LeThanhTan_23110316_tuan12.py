from collections import deque
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import random
import heapq
import math
import random

BG_COLOR = "#2E3440"
BUTTON_COLOR = "#ECEFF4"
TEXT_COLOR = "#3B4252"
ACCENT_COLOR = "#88C0D0"
EMPTY_COLOR = "#4C566A"
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def board_to_tuple(board):
    return tuple(tuple(row) for row in board)
def find_empty(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return i, j  

def move_tile(board, empty_pos, direction):
    x, y = empty_pos
    dx, dy = direction
    new_x, new_y = x + dx, y + dy
    
    if 0 <= new_x < 3 and 0 <= new_y < 3:
        new_board = [list(row) for row in board]
        new_board[x][y], new_board[new_x][new_y] = new_board[new_x][new_y], new_board[x][y]
        return new_board
    return None 

def shuffle_board(board, moves=20):
    global start_state
    start_state = [row[:] for row in board]
    for _ in range(moves):
        empty_pos = find_empty(start_state)
        direction = random.choice(DIRECTIONS)
        new_board = move_tile(start_state, empty_pos, direction)
        if new_board:
            start_state = new_board
    update_board_user()

def dls_8_puzzle(board, goal, depth, path, visited):
    if board == goal:
        return path
    if depth == 0:
        return None
    
    visited.add(board_to_tuple(board))
    empty_pos = find_empty(board)
    
    for direction in DIRECTIONS:
        new_board = move_tile(board, empty_pos, direction)
        if new_board and board_to_tuple(new_board) not in visited:
            result = dls_8_puzzle(new_board, goal, depth - 1, path + [new_board], visited)
            if result:
                return result
    
    return None

def iddfs_8_puzzle(start, goal, max_depth=50):
    for depth in range(max_depth):
        visited = set()
        result = dls_8_puzzle(start, goal, depth, [], visited)
        if result:
            return result
    return None

def hill_climbing(start, goal):
    """Thuật toán Hill Climbing cho bài toán 8 puzzle, trả về toàn bộ path."""
    current_board = start
    current_h = manhattan_distance(current_board, goal)
    path = [current_board]  

    while True:
        empty_pos = find_empty(current_board)
        next_board = None
        next_h = current_h  

        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board:
                h = manhattan_distance(new_board, goal)
                if h < next_h:
                    next_board, next_h = new_board, h

        if next_board is None or next_h >= current_h:  
            messagebox.showinfo("Result", "Hill Climbing bị kẹt tại local optimum!")
            return path  

        current_board = next_board
        current_h = next_h
        path.append(current_board)  

        if current_board == goal:
            return path  

def ida_star_search(start, goal):
    """Thuật toán IDA*."""
    def search(path, g, bound):
        current_board = path[-1]
        f = g + manhattan_distance(current_board, goal)
        
        if f > bound:
            return f 

        if current_board == goal:
            return path

        min_bound = float('inf')
        empty_pos = find_empty(current_board)
        
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board:
                new_path = path + [new_board]
                new_g = g + 1
                result = search(new_path, new_g, bound)
                if isinstance(result, list): 
                    return result
                min_bound = min(min_bound, result)
        
        return min_bound  

    bound = manhattan_distance(start, goal)
    while True:
        result = search([start], 0, bound)
        if isinstance(result, list): 
            return result
        if result == float('inf'):
            return None  
        bound = result  

def manhattan_distance(board, goal):
    """Tính tổng khoảng cách Manhattan của tất cả các ô số."""
    distance = 0
    for i in range(3):
        for j in range(3):
            value = board[i][j]
            if value != 0:
                goal_x, goal_y = [(r, c) for r in range(3) for c in range(3) if goal[r][c] == value][0]
                distance += abs(i - goal_x) + abs(j - goal_y)
    return distance

def a_star_search(start, goal):
    """Thuật toán A* tìm đường đi tối ưu từ trạng thái start đến goal."""
    priority_queue = [] 
    heapq.heappush(priority_queue, (0, start, []))  
    visited = set()
    visited.add(board_to_tuple(start))
    
    while priority_queue:
        _, current_board, path = heapq.heappop(priority_queue)
        
        if current_board == goal:
            return path
        
        empty_pos = find_empty(current_board)
        
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board:
                board_tuple = board_to_tuple(new_board)
                if board_tuple not in visited:
                    visited.add(board_tuple)
                    g_cost = len(path) + 1
                    h_cost = manhattan_distance(new_board, goal)
                    f_cost = g_cost + h_cost
                    heapq.heappush(priority_queue, (f_cost, new_board, path + [new_board]))
    
    return None

def ucs(start, goal):
    """Thuật toán UCS (Uniform Cost Search) tìm đường đi tối ưu từ trạng thái start đến goal."""
    priority_queue = []  
    heapq.heappush(priority_queue, (0, start, []))  
    visited = set()
    visited.add(board_to_tuple(start))

    while priority_queue:
        cost, current_board, path = heapq.heappop(priority_queue)
        
        if current_board == goal:
            return path
        
        empty_pos = find_empty(current_board)
        
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board:
                board_tuple = board_to_tuple(new_board)
                if board_tuple not in visited:
                    visited.add(board_tuple)
                    heapq.heappush(priority_queue, (cost + 1, new_board, path + [new_board]))
    
    return None

def greedy_search(start, goal):
    """Thuật toán Greedy Search tìm đường đi tối ưu từ trạng thái start đến goal dựa trên heuristic."""
    priority_queue = [] 
    heapq.heappush(priority_queue, (manhattan_distance(start, goal), start, [])) 
    visited = set()
    visited.add(board_to_tuple(start))

    while priority_queue:
        _, current_board, path = heapq.heappop(priority_queue)
        
        if current_board == goal:
            return path
        
        empty_pos = find_empty(current_board)
        
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board:
                board_tuple = board_to_tuple(new_board)
                if board_tuple not in visited:
                    visited.add(board_tuple)
                    f_cost = manhattan_distance(new_board, goal)
                    heapq.heappush(priority_queue, (f_cost, new_board, path + [new_board]))
    
    return None

def bfs_8_puzzle(start, goal):
    queue = deque([(start, [])])
    visited = set() 
    visited.add(board_to_tuple(start))

    while queue:
        current_board, path = queue.popleft()
        
        # if current_board == goal:
        if is_finished(current_board):
            return path
        empty_pos = find_empty(current_board)

        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board and board_to_tuple(new_board) not in visited:
                queue.append((new_board, path + [new_board])) 
                visited.add(board_to_tuple(new_board))
    return None 

def dfs_8_puzzle(start, goal):
    stack = deque([(start, [])])
    visited = set()
    visited.add(board_to_tuple(start))

    while stack:
        current_board, path = stack.pop()
        
        if current_board == goal:
            return path
        
        empty_pos = find_empty(current_board)
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board and board_to_tuple(new_board) not in visited:
                stack.append((new_board, path + [new_board]))
                visited.add(board_to_tuple(new_board))
    return None 

def h(state, goal_state):
    return sum(1 for i in range(9) if state[i] != goal_state[i])

def get_neighbors(state):
    neighbors = []
    idx = state.index(0)
    row, col = divmod(idx, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  

    for dr, dc in moves:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r * 3 + c
            new_state = list(state)
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            neighbors.append(tuple(new_state))
    return neighbors

def beam_search(start_state, goal_state, beam_width=2):
    frontier = [(h(start_state, goal_state), start_state, [])]
    
    while frontier:
        frontier.sort()
        frontier = frontier[:beam_width]
        next_frontier = []

        for _, state, path in frontier:
            if state == goal_state:
                return path + [state]
            for neighbor in get_neighbors(state):
                next_frontier.append((h(neighbor, goal_state), neighbor, path + [state]))

        frontier = next_frontier
    return None

def simulated_annealing(start_state, goal_state):
    def h(state, goal_state):
        flat_state = [tile for row in state for tile in row]
        flat_goal = [tile for row in goal_state for tile in row]
        return sum(1 for i in range(9) if flat_state[i] != flat_goal[i])


    def get_neighbors(state):
        neighbors = []
        empty_i, empty_j = -1, -1
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    empty_i, empty_j = i, j
                    break
            if empty_i != -1:
                break
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_i, new_j = empty_i + dx, empty_j + dy
            if 0 <= new_i < 3 and 0 <= new_j < 3:
                new_state = [list(row) for row in state]
                new_state[empty_i][empty_j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[empty_i][empty_j]
                neighbors.append(tuple(tuple(row) for row in new_state))
        return neighbors


    current = tuple(start_state)
    temperature = 100.0
    cooling_rate = 0.99
    min_temp = 1e-3
    max_steps = 10000

    path = [current]

    for _ in range(max_steps):
        if current == goal_state:
            return path

        neighbors = get_neighbors(current)
        next_state = random.choice(neighbors)
        delta_e = h(current, goal_state) - h(next_state, goal_state)


        if delta_e > 0 or random.random() < math.exp(delta_e / temperature):
            current = next_state
            path.append(current)

        temperature *= cooling_rate
        if temperature < min_temp:
            break

    return path if current == goal_state else None

def start_and_or_tree_search():
    global solution
    flat_start = tuple(sum(start_state, [])) 
    flat_goal = tuple(sum(goal_state, []))
    plan = and_or_tree_search(flat_start, flat_goal)

    if plan:
        current = list(flat_start)
        solution = []
        for action in plan:
            next_state = move(tuple(current), action)
            if next_state:
                board_2d = [list(next_state[i*3:(i+1)*3]) for i in range(3)]
                solution.append(board_2d)
                current = list(next_state)
        update_board(0)
    else:
        messagebox.showinfo("Result", "Không tìm được lời giải với AND-OR Tree Search.")

def is_goal(state, goal_state):
    return state == goal_state

def is_finished(state):
    for i in range(3):
        for j in range(3):
            if j< 2 and state[j][i]!= state[j+1][i]-3:
                return False
            if i< 2 and  state[j][i]!=state[j][i+1]-1:
                return False
    return True

def move(state, action):
    index = state.index(0)
    row, col = divmod(index, 3)
    new_state = list(state)
    if action == 'up' and row > 0:
        swap = index - 3
    elif action == 'down' and row < 2:
        swap = index + 3
    elif action == 'left' and col > 0:
        swap = index - 1
    elif action == 'right' and col < 2:
        swap = index + 1
    else:
        return None 
    new_state[index], new_state[swap] = new_state[swap], new_state[index]
    return tuple(new_state)

def get_successors(state):
    actions = ['up', 'down', 'left', 'right']
    results = []
    for action in actions:
        next_state = move(state, action)
        if next_state:
            results.append((action, [next_state])) 
    return results

def and_or_tree_search(state, goal_state):
    def or_search(state, path):
        if is_goal(state, goal_state):
            return []
        if state in path:
            return None
        plan = and_search(get_successors(state), path + [state])
        return plan

    def and_search(successors, path):
        for action, result_states in successors:
            plans = []
            for result_state in result_states:
                plan = or_search(result_state, path)
                if plan is None:
                    break
                plans.append(plan)
            else:
                return [action] + [p for plan in plans for p in plan]
        return None

    return or_search(state, [])

def move_user(i, j):
    global start_state
    empty_x, empty_y = find_empty(start_state)
    if (abs(empty_x - i) + abs(empty_y - j)) == 1:
        start_state[empty_x][empty_y], start_state[i][j] = start_state[i][j], start_state[empty_x][empty_y]
        update_board_user()

def update_board_user():
    for i in range(3):
        for j in range(3):
            value = start_state[i][j]
            buttons[i][j].config(text=str(value) if value != 0 else "", bg="white" if value != 0 else "lightgray")

start_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 0, 8]
]

goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

def simple_hill_climbing(start, goal):
    current_board = start
    path = [current_board]

    while True:
        empty_pos = find_empty(current_board)
        next_board = None
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board and manhattan_distance(new_board, goal) < manhattan_distance(current_board, goal):
                next_board = new_board
                break

        if not next_board:
            return path
        current_board = next_board
        path.append(current_board)

        if current_board == goal:
            return path

def steepest_ascent_hill_climbing(start, goal):
    current_board = start
    path = [current_board]
    while True:
        empty_pos = find_empty(current_board)
        next_board = None
        best_h = manhattan_distance(current_board, goal)
        for direction in DIRECTIONS:
            new_board = move_tile(current_board, empty_pos, direction)
            if new_board:
                h = manhattan_distance(new_board, goal)
                if h < best_h:
                    next_board, best_h = new_board, h
        if not next_board:
            return path
        current_board = next_board
        path.append(current_board)

def random_restart_hill_climbing(start, goal, max_restarts=10):
    for _ in range(max_restarts):
        solution = simple_hill_climbing(start, goal)
        if solution[-1] == goal:
            return solution
        # Khởi tạo lại trạng thái bắt đầu ngẫu nhiên
        start = [[random.randint(1, 8) if (i, j) != find_empty(start) else 0 for j in range(3)] for i in range(3)]
    return None

def update_board(step_index=0):
    if step_index < len(solution):
        prev_board = solution[step_index-1] if step_index > 0 else None
        current_board = solution[step_index]
        
        diff = []
        for i in range(3):
            for j in range(3):
                if prev_board and prev_board[i][j] != current_board[i][j]:
                    diff.append((i, j))
        
        for i in range(3):
            for j in range(3):
                value = current_board[i][j]
                color = BUTTON_COLOR if value != 0 else EMPTY_COLOR
                if (i, j) in diff:
                    buttons[i][j].config(bg=ACCENT_COLOR)
                else:
                    buttons[i][j].config(bg=color)
                buttons[i][j].config(text=str(value) if value != 0 else "")
        
        root.after(500, update_board, step_index + 1)
    else:
        for i in range(3):
            for j in range(3):
                buttons[i][j].config(bg=BUTTON_COLOR)

def get_text():
    global start_state
    user_input = text_box.get("1.0", tk.END).strip()
    
    try:
        # Kiểm tra và chuyển đổi dữ liệu
        rows = [line for line in user_input.split('\n') if line.strip()]
        if len(rows) != 3:
            raise ValueError("Cần 3 dòng dữ liệu")
            
        matrix = []
        all_numbers = []
        for row in rows:
            numbers = list(map(int, row.split()))
            if len(numbers) != 3:
                raise ValueError("Mỗi dòng cần 3 số")
            matrix.append(numbers)
            all_numbers.extend(numbers)
            
        # Kiểm tra số hợp lệ
        if sorted(all_numbers) != list(range(9)):
            raise ValueError("Cần đủ các số từ 0-8 không trùng lặp")
            
        # Cập nhật trạng thái ban đầu
        start_state = matrix
        update_board_user()
        update_status("Nhập liệu thành công!")
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {str(e)}")
        update_status("Lỗi nhập liệu!")
        
def update_status(message):
    status_bar.config(text=message)
    root.update_idletasks()


solution = []
root = tk.Tk()
root.title("8 Puzzle Solver")
root.configure(bg=BG_COLOR)
root.geometry("900x600")

SIZE = 3
buttons = [[None for _ in range(SIZE)] for _ in range(SIZE)]

for i in range(SIZE):
    for j in range(SIZE):
        buttons[i][j] = tk.Button(
            root,
            text="",
            width=6,
            height=3,
            font=("Arial", 24, "bold"),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            relief="ridge",
            borderwidth=1,
            command=lambda i=i, j=j: move_user(i, j)
        )
        buttons[i][j].grid(row=i, column=j, padx=0, pady=0)

# Cấu hình giao diện
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background=BG_COLOR)
style.configure("TNotebook.Tab", background=BUTTON_COLOR, foreground=TEXT_COLOR)
style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)])

# Định nghĩa các màu sắc và các biến liên quan
BG_COLOR = "#2E3440"
BUTTON_COLOR = "#ECEFF4"
TEXT_COLOR = "#3B4252"
ACCENT_COLOR = "#88C0D0"
EMPTY_COLOR = "#4C566A"

# Cấu hình cho nút bấm
button_style = {
    "font": ("Arial", 10, "bold"),
    "bg": BUTTON_COLOR,
    "fg": TEXT_COLOR,
    "activebackground": ACCENT_COLOR,
    "borderwidth": 2,
    "relief": "groove",
    "padx": 8,
    "pady": 4
}

# Tạo Notebook và các Tab cho từng nhóm thuật toán
notebook = ttk.Notebook(root, width=500)  
uniformed_frame = ttk.Frame(notebook, width=300, height=150)  # Điều chỉnh width
informed_frame = ttk.Frame(notebook, width=300, height=150)
local_search_frame = ttk.Frame(notebook, width=300, height=150)
complex_env_frame = ttk.Frame(notebook, width=300, height=150)
csp_frame = ttk.Frame(notebook, width=300, height=150)
reinforcement_frame = ttk.Frame(notebook, width=300, height=150)

# Thêm các tab vào notebook
notebook.add(uniformed_frame, text="Uniformed Search")
notebook.add(informed_frame, text="Informed Search")
notebook.add(local_search_frame, text="Local Search")
notebook.add(complex_env_frame, text="Complex Environments")
notebook.add(csp_frame, text="CSPs")
notebook.add(reinforcement_frame, text="Reinforcement Learning")

notebook.grid(row=4, column=0, columnspan=3, pady=10)

# Danh sách các thuật toán cho mỗi nhóm
uniformed_algorithms = [
    ("BFS", "BFS"),
    ("DFS", "DFS"),
    ("IDDFS", "IDDFS"),
    ("UCS", "UCS")
]

informed_algorithms = [
    ("Greedy", "GS"),
    ("A*", "A*"),
    ("IDA*", "IDA*")
]

local_search_algorithms = [
    ("Simple HC", "Simple Hill Climbing"),
    ("Steepest HC", "Steepest Ascent Hill Climbing"),
    ("Random Restart HC", "Random Restart Hill Climbing"),
    ("Simulated Annealing", "simulated_annealing"),
    ("Beam Search", "beam_search"),
    ("Genetic Algorithm", "genetic_algorithm")
]

complex_env_algorithms = [
    ("AND-OR Tree", "AND-OR Tree")
]

csp_algorithms = [
    ("Backtracking Search", "backtracking_search"),
    ("Forward Search", "forward_search"),
    ("Min Conflicts", "min_conflicts")
]

reinforcement_algorithms = [
    ("Q-Learning", "q_learning")
]

# Hàm tạo nút cho mỗi nhóm thuật toán
def create_buttons(algorithms, frame):
    for idx, (name, cmd) in enumerate(algorithms):
        btn = tk.Button(frame, text=name, 
                       command=lambda c=cmd: start_auto_solve(c), **button_style)
        btn.grid(row=idx//4, column=idx%4, padx=3, pady=3)

# Gọi hàm để thêm các nút vào từng tab
create_buttons(uniformed_algorithms, uniformed_frame)
create_buttons(informed_algorithms, informed_frame)
create_buttons(local_search_algorithms, local_search_frame)
create_buttons(complex_env_algorithms, complex_env_frame)
create_buttons(csp_algorithms, csp_frame)
create_buttons(reinforcement_algorithms, reinforcement_frame)

# Phần giao diện cho nút "Random Puzzle"
random_frame = tk.Frame(root, bg=BG_COLOR)
random_frame.grid(row=0, column=3, columnspan=3, pady=10)

random_button = tk.Button(
    random_frame,
    text="Random Puzzle",
    font=("Arial", 10, "bold"),
    padx=20, pady=10,
    width=15, height=2,
    command=lambda: shuffle_board(goal_state, 30)
)

random_button.grid(row=0, column=3, padx=4, pady=4) 

# Khung nhập liệu
text_box = tk.Text(root, width=20, height=4, font=("Arial", 8))
text_box.grid(row=1, column=4, padx=10, pady=10)

btn = tk.Button(root, text="Lấy nội dung", command=get_text)
btn.grid(row=1, column=3, pady=10)


# Thanh trạng thái
status_bar = tk.Label(root, text="Ready", bg=BUTTON_COLOR, fg=TEXT_COLOR, 
                     anchor=tk.W, font=("Arial", 10))
status_bar.grid(row=5, column=0, columnspan=3, sticky="ew")

# Hàm cập nhật trạng thái
def update_status(message):
    status_bar.config(text=message)
    root.update_idletasks()

# Hàm bắt đầu giải quyết tự động
def start_auto_solve(algorithm):
    global solution
    if algorithm == "BFS":
        solution = bfs_8_puzzle(start_state, goal_state)
    elif algorithm == "DFS":
        solution = dfs_8_puzzle(start_state, goal_state)
    elif algorithm == "IDDFS":
        solution = iddfs_8_puzzle(start_state, goal_state)
    elif algorithm == "UCS":
        solution = ucs(start_state, goal_state)
    elif algorithm == "GS":
        solution = greedy_search(start_state, goal_state)
    elif algorithm == "A*":
        solution = a_star_search(start_state, goal_state)
    elif algorithm == "IDA*":
        solution = ida_star_search(start_state, goal_state)
    elif algorithm == "Hill Climbing":
        solution = hill_climbing(start_state, goal_state)
    elif algorithm == "Simple Hill Climbing":
        solution = simple_hill_climbing(start_state, goal_state)
    elif algorithm == "Steepest Ascent Hill Climbing":
        solution = steepest_ascent_hill_climbing(start_state, goal_state)
    elif algorithm == "Random Restart Hill Climbing":
        solution = random_restart_hill_climbing(start_state, goal_state)
    elif algorithm == "simulated_annealing":
        solution = simulated_annealing(start_state, goal_state)
    elif algorithm == "beam_search":
        solution = beam_search(start_state, goal_state)

    if solution:
        update_board()
    else:
        messagebox.showinfo("Result", "No solution found!")



update_board_user() 
root.mainloop()
