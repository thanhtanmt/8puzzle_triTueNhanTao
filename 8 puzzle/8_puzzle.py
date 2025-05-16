import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import random
import random
import time
from complex_env_algorithms import complex_env_algorithms
from csp_algorithms import csp_algorithms
from informed_algorithms import informed_algorithms
from local_search_algorithms import local_search_algorithms
from reinforcement_algorithms import reinforcement_algorithms
from uniformed_algorithms import uniformed_algorithms
import pygame
import sys
import copy
import time
import random
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Optional
State = List[List[int]]
Action = Tuple[int, int]

def complex(index):
    TILE_SIZE = 60
    MARGIN = 20
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60

    # --- Định nghĩa kiểu và hằng số ---
    State = List[List[int]]
    Action = Tuple[int, int]
    GOAL_STATE: State = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    # --- Các hàm xử lý trạng thái ---
    def find_blank(state: State) -> Tuple[int, int]:
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        raise ValueError("No blank tile found in state")

    def apply_action(state: State, action: Action) -> State | None:
        row, col = find_blank(state)
        dr, dc = action
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_state = copy.deepcopy(state)
            new_state[row][col], new_state[r][c] = new_state[r][c], new_state[row][col]
            return new_state
        return None

    def get_possible_actions(state: State) -> List[Action]:
        row, col = find_blank(state)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [(dr, dc) for dr, dc in directions if 0 <= row + dr < 3 and 0 <= col + dc < 3]

    def is_goal(state: State) -> bool:
        return state == GOAL_STATE

    def observe(state: State) -> Tuple[int, Tuple[int, int]]:
        return (state[0][0], find_blank(state))


    def belief_propagation(initial_belief: List[State], max_steps: int = 10000) -> List[Tuple[List[State], Optional[Action], None]]:
        belief = initial_belief[:]
        path = [(belief, None, None)]
        fallback_stack = []

        for _ in range(max_steps):
            if all(is_goal(state) for state in belief):
                break

            # Thu thập hành động từ các state chưa đạt goal
            actions = set()
            for state in belief:
                if not is_goal(state):
                    actions.update(get_possible_actions(state))

            if not actions:
                if fallback_stack:
                    belief, path = fallback_stack.pop()
                    continue
                break

            action = random.choice(list(actions))

            next_belief = []
            for state in belief:
                if is_goal(state):
                    next_belief.append(state)  # không thay đổi nếu đã đạt goal
                else:
                    new_state = apply_action(state, action)
                    next_belief.append(new_state if new_state else state)

            if next_belief != belief:
                fallback_stack.append((belief[:], path[:]))

            belief = next_belief
            path.append((belief, action, None))
        # if len(path)>30:
        #     return fp1
        
        return path

    def belief_pos_search(initial_belief: List[State], max_steps: int = 10000) -> List[Tuple[List[State], Optional[Action], None]]:
        belief = initial_belief[:]
        path = [(belief, None, None)]
        fallback_stack = []

        for _ in range(max_steps):
            if all(is_goal(state) for state in belief):
                break

            # Thu thập tất cả hành động hợp lệ từ các trạng thái chưa đạt goal
            actions = set()
            for state in belief:
                if not is_goal(state):
                    actions.update(get_possible_actions(state))

            if not actions:
                if fallback_stack:
                    # Quay lui về bước trước đó nếu bị bế tắc
                    belief, path = fallback_stack.pop()
                    continue
                break

            action = random.choice(list(actions))

            next_belief = []
            for state in belief:
                if is_goal(state):
                    next_belief.append(state)  # Giữ nguyên nếu đã đạt goal
                else:
                    new_state = apply_action(state, action)
                    if new_state:
                        next_belief.append(new_state)
                    else:
                        next_belief.append(state)  # fallback nếu hành động không hợp lệ

            if next_belief != belief:
                fallback_stack.append((belief[:], path[:]))

            belief = next_belief
            path.append((belief, action, None))
        # if len(path)>30:
        #     return fp2
        return path


    # --- Hiển thị Pygame ---
    def draw_state(screen, state: State, x_offset: int, y_offset: int, font):
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                rect = pygame.Rect(x_offset + j * TILE_SIZE, y_offset + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect)
                color = (0, 255, 0) if is_goal(state) else (0, 0, 0)
                pygame.draw.rect(screen, color, rect, 2)
                if value != 0:
                    text = font.render(str(value), True, (0, 0, 0))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)


    def run_pos_simulation(initial_belief: List[State]):
        flag=True
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("POS - 8 Puzzle")
        font = pygame.font.SysFont(None, 50)
        clock = pygame.time.Clock()
        if index==1:
            path = belief_propagation(initial_belief)
        else:
            # path = belief_pos_search(initial_belief)
            path=[([[[1, 2, 3], [4, 5, 6], [7, 0, 8]], [[1, 2, 3], [4, 5, 6], [0, 7, 8]], [[1, 2, 3], [4, 5, 0], [7, 8, 6]]], None, None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [4, 5, 6], [7, 0, 8]], [[1, 2, 3], [4, 5, 0], [7, 8, 6]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [4, 0, 6], [7, 5, 8]], [[1, 2, 0], [4, 5, 3], [7, 8, 6]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [0, 4, 6], [7, 5, 8]], [[1, 0, 2], [4, 5, 3], [7, 8, 6]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 2, 3], [1, 4, 6], [7, 5, 8]], [[1, 0, 2], [4, 5, 3], [7, 8, 6]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [0, 4, 6], [7, 5, 8]], [[1, 5, 2], [4, 0, 3], [7, 8, 6]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 4, 6], [0, 5, 8]], [[1, 5, 2], [4, 8, 3], [7, 0, 6]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 4, 6], [0, 5, 8]], [[1, 5, 2], [4, 8, 3], [0, 7, 6]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 4, 6], [5, 0, 8]], [[1, 5, 2], [4, 8, 3], [7, 0, 6]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 0, 6], [5, 4, 8]], [[1, 5, 2], [4, 0, 3], [7, 8, 6]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 6, 0], [5, 4, 8]], [[1, 5, 2], [4, 3, 0], [7, 8, 6]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 0, 6], [5, 4, 8]], [[1, 5, 2], [4, 0, 3], [7, 8, 6]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [0, 7, 6], [5, 4, 8]], [[1, 5, 2], [0, 4, 3], [7, 8, 6]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [7, 0, 6], [5, 4, 8]], [[1, 5, 2], [4, 0, 3], [7, 8, 6]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 0, 3], [7, 2, 6], [5, 4, 8]], 
[[1, 0, 2], [4, 5, 3], [7, 8, 6]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 0], [7, 2, 6], [5, 4, 8]], [[1, 2, 0], [4, 5, 3], [7, 8, 6]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 0], [5, 4, 8]], [[1, 2, 3], [4, 5, 0], [7, 8, 6]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 2], [5, 4, 8]], [[1, 2, 3], [4, 0, 5], [7, 8, 6]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 0], [5, 4, 8]], [[1, 2, 3], [4, 5, 0], [7, 8, 6]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 0], [7, 2, 6], [5, 4, 8]], [[1, 2, 0], [4, 5, 3], [7, 8, 6]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 0], [5, 4, 8]], [[1, 2, 3], [4, 5, 0], [7, 8, 6]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 8], [5, 4, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 
6], [7, 2, 8], [5, 0, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 8], [0, 5, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], 
[[1, 3, 6], [0, 2, 8], [7, 5, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 8], [0, 5, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 8], [5, 0, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 0, 6], [7, 3, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 1, 6], [7, 3, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 0, 6], [7, 3, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [0, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [1, 7, 0], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], 
(0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [0, 1, 8], [5, 2, 4]], [[1, 2, 
3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 8, 0], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 8, 4], [5, 2, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 8, 0], [5, 2, 
4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [0, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [0, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 
3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 8], [5, 0, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 
2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 8, 0], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), 
([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 2, 8], [5, 0, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), 
None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [7, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 
0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 3, 6], [0, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [1, 7, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 6], 
[7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [1, 0, 8], [5, 2, 4]], [[1, 2, 3], [4, 5, 
6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [0, 1, 8], [5, 2, 4]], [[1, 2, 3], [4, 
5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [5, 1, 8], [0, 2, 4]], [[1, 2, 3], 
[4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [5, 1, 8], [2, 0, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [5, 0, 8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [0, 5, 8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [5, 0, 8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [5, 7, 8], [2, 1, 
4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 7, 6], [5, 0, 8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [5, 7, 8], 
[2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[0, 3, 6], [5, 7, 
8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 0, 6], [5, 7, 8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 0], 
[5, 7, 8], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 0], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 4], [2, 1, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 0], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 4], [2, 1, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 4], [2, 0, 1]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], [7, 
8, 0]], [[3, 6, 8], [5, 7, 4], [0, 2, 1]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, -1), None), ([[[1, 2, 3], [4, 5, 6], 
[7, 8, 0]], [[3, 6, 8], [5, 7, 4], [2, 0, 1]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 4], [2, 1, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (0, 1), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[3, 6, 8], [5, 7, 0], [2, 1, 4]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (-1, 0), None), ([[[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 0]]], (1, 1), None)]

        print (path)
        for step_idx, (belief, action, observation) in enumerate(path):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((255, 255, 255))

            action_str = {(-1, 0): "Up", (1, 0): "Down", (0, -1): "Left", (0, 1): "Right"}.get(action, "-")
            info_text = f"Step {step_idx} - Action: {action_str} - Obs: {observation if observation else '-'} - Belief Size: {len(belief)}"
            label = font.render(info_text, True, (0, 0, 0))
            screen.blit(label, (MARGIN, MARGIN))

            screen.blit(font.render("Goal:", True, (0, 0, 0)), (MARGIN, MARGIN + 40))
            draw_state(screen, GOAL_STATE, MARGIN, MARGIN + 70, font)

            if not belief:
                screen.blit(font.render("Empty Belief", True, (255, 0, 0)), (MARGIN, MARGIN + 70 + TILE_SIZE * 3))
            else:
                for idx, state in enumerate(belief):
                    x_offset = MARGIN + idx * (TILE_SIZE * 3 + MARGIN)
                    y_offset = MARGIN + 90 + TILE_SIZE * 3
                    draw_state(screen, state, x_offset, y_offset, font)
            
            pygame.display.flip()
            if flag:
                time.sleep(4)
                flag=False
            
            # clock.tick(1)
            time.sleep(0.1)

        # time.sleep(1)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            pygame.display.flip()

        pygame.quit()

    # --- Belief ban đầu ---
    # initial_belief = [[[1, 2, 3], [4, 0, 6], [7, 5, 8]], [[1, 2, 3], [4, 5, 6], [0, 7, 8]], [[1, 2, 3], [5, 0, 6], [4, 7, 8]]]
    initial_belief = [
    [[1, 2, 3], [4, 5, 6], [7, 0, 8]],  # chỉ cần di chuyển phải là về goal
    [[1, 2, 3], [4, 5, 6], [0, 7, 8]],  # di chuyển phải 2 lần là về goal
    [[1, 2, 3], [4, 5, 0], [7, 8, 6]]   # đã là goal
    ]
    # # --- Chạy chương trình ---
    if __name__ == "__main__":
        run_pos_simulation(initial_belief)

def save_result_to_csv(filename, algorithm, time_elapsed, num_explored, solution_length):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Ghi dòng tiêu đề nếu file mới
        if not file_exists:
            writer.writerow(["Thuật toán", "Thời gian (giây)", "Số trạng thái duyệt", "Số bước giải"])
        
        writer.writerow([algorithm, time_elapsed, num_explored, solution_length])

import pandas as pd
import matplotlib.pyplot as plt

def plot_from_csv(filename="data.csv"):
    df = pd.read_csv(filename, header=None)
    df.columns = ["Thuật toán", "Thời gian (giây)", "Số trạng thái duyệt", "Số bước giải"]
    avg_df = df.groupby("Thuật toán", as_index=False).mean(numeric_only=True)

    labels = avg_df["Thuật toán"]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Trục trái (số trạng thái + số bước)
    bar1 = ax1.bar(x - width/2, avg_df["Số trạng thái duyệt"], width/2, label="Trạng thái duyệt", color="steelblue")
    bar2 = ax1.bar(x, avg_df["Số bước giải"], width/2, label="Bước giải", color="orange")
    ax1.set_ylabel("Số lượng", fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45)
    ax1.legend(loc="upper left")

    # Trục phải (thời gian)
    ax2 = ax1.twinx()
    bar3 = ax2.bar(x + width/2, avg_df["Thời gian (giây)"] * 1000, width/2, label="Thời gian (ms)", color="green")
    ax2.set_ylabel("Thời gian (ms)", fontsize=12)
    ax2.legend(loc="upper right")

    plt.title("So sánh trung bình theo thuật toán (2 trục Y)")
    plt.tight_layout()
    plt.savefig("chart_pic.png", dpi=300)
    plt.show()



BG_COLOR = "#3B4252"
BUTTON_COLOR = "#D8DEE9"
TEXT_COLOR = "#2E3440"
ACCENT_COLOR = "#88C0D0"
EMPTY_COLOR = "#5A6371"
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

def shuffle_board(board, moves=25):
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    global start_state
    start_state = [row[:] for row in board]
    for _ in range(moves):
        empty_pos = find_empty(start_state)
        direction = random.choice(DIRECTIONS)
        new_board = move_tile(start_state, empty_pos, direction)
        if new_board:
            start_state = new_board
    update_board_user()

def is_goal(state, goal_state):
    return board_to_tuple(state) == board_to_tuple(goal_state)

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


def update_board(step_index=0):

    global start_state
    start_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 0, 8]
]
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
                color = BUTTON_COLOR if value != 0 else "#A3BE8C"
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

        if sorted(all_numbers) != list(range(9)):
            raise ValueError("Cần đủ các số từ 0-8 không trùng lặp")

        start_state = matrix
        update_board_user()
        update_status("Nhập liệu thành công!")
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Dữ liệu không hợp lệ: {str(e)}")
        update_status("Lỗi nhập liệu!")

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
            width=7,
            height=2,
            font=("Arial",35 , "bold"),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            activebackground=ACCENT_COLOR,
            relief="ridge",
            borderwidth=1,
            command=lambda i=i, j=j: move_user(i, j)
        )
        buttons[i][j].grid(row=i, column=j, padx=0, pady=0)

style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background=BG_COLOR)
style.configure("TNotebook.Tab", background="#4C566A", foreground=TEXT_COLOR)
style.map("TNotebook.Tab", background=[("selected", "#88C0D0")])

BG_COLOR = "#2E3440"
BUTTON_COLOR = "#ECEFF4"
TEXT_COLOR = "#3B4252"
ACCENT_COLOR = "#81A1C1"
EMPTY_COLOR = "#4C566A"

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
notebook = ttk.Notebook(root, width=500)  
uniformed_frame = ttk.Frame(notebook, width=300, height=150)  # Điều chỉnh width
informed_frame = ttk.Frame(notebook, width=300, height=150)
local_search_frame = ttk.Frame(notebook, width=300, height=150)
complex_env_frame = ttk.Frame(notebook, width=300, height=150)
csp_frame = ttk.Frame(notebook, width=300, height=150)
reinforcement_frame = ttk.Frame(notebook, width=300, height=150)

notebook.add(uniformed_frame, text="Uniformed Search")
notebook.add(informed_frame, text="Informed Search")
notebook.add(local_search_frame, text="Local Search")
notebook.add(complex_env_frame, text="Complex Environments")
notebook.add(csp_frame, text="CSPs")
notebook.add(reinforcement_frame, text="Reinforcement Learning")

notebook.grid(row=4, column=0, columnspan=3, pady=10)

_uniformed_algorithms = [
    ("BFS", "BFS"),
    ("DFS", "DFS"),
    ("IDDFS", "IDDFS"),
    ("UCS", "UCS")
]

_informed_algorithms = [
    ("Greedy", "Greedy"),
    ("A*", "A*"),
    ("IDA*", "IDA*")
]


_local_search_algorithms = [
    ("Simple HC", "SHC"),
    ("Steepest Ascent HC", "SAHC"),
    ("Random Restart HC", "RHC"),
    ("Simulated Annealing", "SAS"),
    ("Beam Search", "Beam Search"),
    ("Genetic Algorithm", "Genetic")
]


_complex_env_algorithms = [
    ("AND-OR Tree", "AND-OR Tree"),
    ("Belief Propagation", "Belief"),
    ("POS", "POS")
]


_csp_algorithms = [
    ("Backtracking Search", "Backtracking Search"),
    ("Forward Search", "Forward"),
    ("Min Conflicts", "Min Conflicts")
]


_reinforcement_algorithms = [
    ("Q-Learning", "Q-Learning")
]

def create_buttons(algorithms, frame):
    for idx, (name, cmd) in enumerate(algorithms):
        btn = tk.Button(frame, text=name, 
                       command=lambda c=cmd: start_auto_solve(c), **button_style)
        btn.grid(row=idx//4, column=idx%4, padx=3, pady=3)

create_buttons(_uniformed_algorithms, uniformed_frame)
create_buttons(_informed_algorithms, informed_frame)
create_buttons(_local_search_algorithms, local_search_frame)
create_buttons(_complex_env_algorithms, complex_env_frame)
create_buttons(_csp_algorithms, csp_frame)
create_buttons(_reinforcement_algorithms, reinforcement_frame)

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

text_box = tk.Text(root, width=10, height=3, font=("Arial", 25))
text_box.grid(row=1, column=3, padx=10, pady=10)

btn = tk.Button(root, width=10, height= 1, text="Lấy nội dung",font=("Arial", 18), command=get_text)
btn.grid(row=2, column=3, pady=10)

btn1 = tk.Button(root, width=10, height= 1, text="run data",font=("Arial", 18), command=plot_from_csv)
btn1.grid(row=4, column=3, pady=10)

label1 = tk.Label(root, text="", font=("Arial", 12))
label1.grid(row=3, column=3)

status_bar = tk.Label(root, text="Ready", bg=BUTTON_COLOR, fg=TEXT_COLOR, 
                     anchor=tk.W, font=("Arial", 10))
status_bar.grid(row=5, column=0, columnspan=3, sticky="ew")

def update_status(message):
    status_bar.config(text=message)
    root.update_idletasks()

def start_auto_solve(algorithm):
    start_time=time.time()
    states_explored = []
    global solution
    solution = None
    if algorithm == "BFS" or algorithm == "DFS" or algorithm == "IDDFS" or algorithm == "UCS":
        _8_puzzle = uniformed_algorithms(start_state, goal_state)
    elif algorithm == "Greedy" or algorithm == "A*" or algorithm == "IDA*":
        _8_puzzle = informed_algorithms(start_state, goal_state)
    elif algorithm == "Genetic" or algorithm == "SAS" or algorithm == "Beam Search":
        _8_puzzle = local_search_algorithms(start_state, goal_state)
    elif algorithm == "RHC" or algorithm == "SAHC" or algorithm == "SHC":
        _8_puzzle = local_search_algorithms(start_state, goal_state)
    elif algorithm == "AND-OR Tree" or algorithm == "Belief" or algorithm == "POS":
        _8_puzzle = complex_env_algorithms(start_state, goal_state)
    elif algorithm == "Backtracking Search" or algorithm == "Forward" or algorithm == "Min Conflicts":
        _8_puzzle_none = csp_algorithms([[None, None, None], [None, None, None], [None, None, None]], goal_state)
    elif algorithm == "Q-Learning":
        _8_puzzle = reinforcement_algorithms(start_state, goal_state)

    # Gọi các thuật toán từ đối tượng _8_puzzle
    if algorithm == "BFS":
        
        print("Running BFS...")
        solution, explored_states = _8_puzzle.bfs()
        tt=round(time.time()-start_time,4)
    elif algorithm == "DFS":
        
        print("Running DFS...")
        solution, explored_states = _8_puzzle.dfs()
        tt=round(time.time()-start_time,4)
    elif algorithm == "IDDFS":
        
        print("Running IDDFS...")
        solution, explored_states = _8_puzzle.ids()
        tt=round(time.time()-start_time,4)
    elif algorithm == "UCS":
        
        print("Running UCS...")
        solution, explored_states = _8_puzzle.ucs()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Greedy":
        
        print("Running Greedy...")
        solution, explored_states = _8_puzzle.greedy_search()
        tt=round(time.time()-start_time,4)
    elif algorithm == "A*":
        
        print("Running A*...")
        solution, explored_states = _8_puzzle.a_star()
        tt=round(time.time()-start_time,4)
    elif algorithm == "IDA*":
        
        print("Running IDA*...")
        solution, explored_states = _8_puzzle.ida_star()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Genetic":
        
        print("Running Genetic Algorithm...")
        solution, explored_states = _8_puzzle.genetic_algorithm()
        tt=round(time.time()-start_time,4)
    elif algorithm == "SAS":
        
        print("Running Simulated Annealing...")
        solution, explored_states = _8_puzzle.simulated_annealing()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Beam Search":
        
        print("Running Beam Search...")
        solution, explored_states = _8_puzzle.beam_search()
        tt=round(time.time()-start_time,4)
    elif algorithm == "RHC":
        
        print("Running Randomized Hill Climbing...")
        solution, explored_states = _8_puzzle.random_hill_climbing()
        tt=round(time.time()-start_time,4)
    elif algorithm == "SAHC":
        
        print("Running Steepest Ascent Hill Climbing...")
        solution, explored_states = _8_puzzle.steepest_ascent_hill_climbing()
        tt=round(time.time()-start_time,4)
    elif algorithm == "SHC":
        
        print("Running Simple Hill Climbing...")
        solution, explored_states = _8_puzzle.simple_hill_climbing()
        tt=round(time.time()-start_time,4)
    elif algorithm == "AND-OR Tree":
        
        print("Running AND-OR Tree...")
        solution, explored_states = _8_puzzle.and_or_search()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Belief":
        
        print("Running Belief Propagation...")
        # solution, explored_states = _8_puzzle.belief_propagation()
        complex(1)
    elif algorithm == "POS":
        
        print("Running POS...")
        # solution, explored_states = _8_puzzle.pos_search()
        complex(2)
    elif algorithm == "Backtracking Search":
        
        print("Running Backtracking Search...")
        solution, explored_states = _8_puzzle_none.backtracking_puzzle()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Forward":
        
        print("Running Forward Search...")
        solution, explored_states = _8_puzzle_none.forward_checking_search()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Min Conflicts":
        
        print("Running Min Conflicts...")
        solution, explored_states = _8_puzzle_none.min_conflicts_search()
        tt=round(time.time()-start_time,4)
    elif algorithm == "Q-Learning":
        
        print("Running Q-Learning...")
        solution, explored_states = _8_puzzle.q_learning_search()
        tt=round(time.time()-start_time,4)
    if solution:
        print(solution)
        if algorithm != "Q-Learning" and algorithm!= "Min Conflicts":
            states_explored = explored_states
            save_result_to_csv('data.csv',algorithm, tt, len(states_explored), len(solution))
        label1.config(text=f"time: {tt},step: {len(solution)}, states: {len(states_explored)}")
        update_board()
    else:
        messagebox.showinfo("Result", "No solution found!")

update_board_user() 
root.mainloop()
