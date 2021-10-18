#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 11 17:48:35 2021

@author: satvik
"""

import pygame
import math
# import time
from queue import PriorityQueue

width = 1000;
win = pygame.display.set_mode((width,width))

pygame.display.set_caption("Pathfinder")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE= (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:
    def __init__(self,row,col,width,total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbors = []
        self.width = width 
        self.total_rows = total_rows 
    
    def get_pos(self):
        return self.row,self.col 
    
    def is_closed(self):
        return self.color==RED 
    
    def is_opened(self):
        return self.color==GREEN 
    
    def is_barrier(self):
        return self.color==BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color==PURPLE
    
    def reset(self):
        self.color = WHITE
        
    def make_closed(self):
        self.color = RED
        
    def make_open(self):
        self.color= GREEN
        
    def make_barrier(self):
        self.color=BLACK
        
    def make_start(self):
        self.color = ORANGE 
        
    def make_end(self):
        self.color = TURQUOISE
        
    def make_path(self):
        self.color = PURPLE
    
    def draw(self,win):
        pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.width))
    
    def update_neighbors(self,grid):
        self.neighbors = []
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():
            self.neighbors.append(grid[self.row+1][self.col])
            
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():
            self.neighbors.append(grid[self.row-1][self.col])
            
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():
            self.neighbors.append(grid[self.row][self.col+1])
            
        if self.col >0 and not grid[self.row][self.col-1].is_barrier():
            self.neighbors.append(grid[self.row][self.col-1])
    
    def __lt__(self, other):
        return False
    
def h(p1,p2):
    (row1,col1) = p1
    (row2,col2) = p2
    return abs(row1-row2) + abs(col1-col2)

def make_grid(rows,width):
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i,j,gap,rows)
            grid[i].append(node)
            
    return grid

def draw_grid(win,rows,width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0,i*gap), (width,i*gap))
        for j in range(rows):
            pygame.draw.line(win,GREY,(j*gap,0),(j*gap,width))
    
    
def draw(win,grid,rows,width):
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win,rows,width)
    pygame.display.update()
    
def get_clicked_pos(pos,rows,width):
    gap = width//rows
    y,x = pos
    
    row = y//gap
    col = x//gap 
    return row,col 

def reconstruct_path(came_from , end, draw):
    while end in came_from:
        end = came_from[end]
        end.make_path()
        draw()
    
    
    
def find_path(draw,grid,start,end):
    count = 0
    q = PriorityQueue()
    q.put((0,count,start))
    came_from = {}
    g_score = {node :float("inf") for row in grid for node in row}
    g_score[start]=0
    f_score = {node :float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(),end.get_pos())
    
    set_reached = {start}
    
    while not q.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = q.get()[2]
        set_reached.remove(current)
        
        if current == end:
            reconstruct_path(came_from , end,draw)
            end.make_end()
            return True
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current]+1
            
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score 
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(),end.get_pos())
                if neighbor not in set_reached:
                    count+=1
                    q.put((f_score[neighbor],count,neighbor))
                    set_reached.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
            
    return False
    

def main(win,width):
    ROWS = 50
    grid = make_grid(ROWS,width)
    
    start = None 
    end = None 
    
    run = True
    
    while run:
        draw(win,grid,ROWS,width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
        
            
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos,ROWS,width)
                node = grid[row][col]
                if not start and node!=end:
                    start = node 
                    start.make_start()
                elif not end and node!=start:
                    end = node 
                    end.make_end()
                elif node!=start and node!=end:
                    node.make_barrier()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row,col = get_clicked_pos(pos,ROWS,width)
                node = grid[row][col]
                node.reset()
                if node==start:
                    start = None
                elif node==end:
                    end = None 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    find_path(lambda : draw(win,grid,ROWS,width),grid,start,end)
                
                if event.key == pygame.K_c:
                    start = None 
                    end = None 
                    grid = make_grid(ROWS,width)
    
    pygame.quit()
                
main(win,width)
