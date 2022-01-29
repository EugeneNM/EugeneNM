# -------------------------------------------------------------------------------
# Name:        sudoku solver
# Purpose:
#
# Author:      Евгений
#
# Created:     23.01.2022
# Copyright:   (c) Евгений 2022
# Licence:     free
# -------------------------------------------------------------------------------

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import stdout
from os.path import join, abspath
from time import process_time

def line_to_sudoku(line_sud):
    '''Функция переводит строковое представление судоку в двумерный список'''
    return [[int(line_sud[x * 9 + y]) for y in range(9)] for x in range(9)]

def printer_sudoku(s, out=stdout):
    '''Функция принимает судоку в виде двумерного списка
        и выводит на печать в рамке'''
    print('+-------+-------+-------+', file=out)
    for k in range(9):
        print('|', s[k][0], s[k][1], s[k][2], '|',
                   s[k][3], s[k][4], s[k][5], '|',
                   s[k][6], s[k][7], s[k][8], '|', file=out)
        if k % 3 == 2:
            print('+-------+-------+-------+', file=out)
    print('\n', file=out)

def sudoku_solver(sol):
    '''Функция поиска решений судоку в три этапа. Принимает не решенную судоку
        и возвращает решенную, или False, если решить не удалось'''
    # этап 1 - поиск и простановка однозначных вариантов
    flag = True
    while flag:
        flag = False
        min_set_val = None
        for ri in range(9):
            for ci in range(9):
                if sol[ri][ci]:
                    continue
                set_val = search_value(ri, ci, sol)
                count_val = len(set_val)
                if not count_val:
                    return False  # решений нет
                if count_val == 1:
                    sol[ri][ci], = set_val
                    flag = True
                else:
                    if not min_set_val or count_val < len(min_set_val[1]):
                        min_set_val = (ri, ci), set_val
        if not min_set_val:
            return sol
        if not flag:
            # этап 2 - поиск из множества возможных и простановка вариантов,
            # которые нельзя поставить в другие ячейки            
            all_set = [[search_value(r, c, sol) if sol[r][c] == 0 else set()
                    for c in range(9)] for r in range(9)]
            for ri in range(9):
                if flag:
                    break
                block_x = 3 * (ri // 3)
                for ci in range(9):
                    spis, var = all_set[ri][:ci] + all_set[ri][ci + 1:], set()
                    for i in spis:
                        var |= i
                    set_val = all_set[ri][ci] - var
                    if len(set_val) == 1:
                        sol[ri][ci], = set_val
                        flag = True
                        break
                    else:
                        var = set()
                        for i in range(9):
                            if i != ri:
                                var |= all_set[i][ci]
                        set_val = all_set[ri][ci] - var
                        if len(set_val) == 1:
                            sol[ri][ci], = set_val
                            flag = True
                            break
                        else:
                            var = set()
                            block_y = 3 * (ci // 3)
                            for x in range(3):
                                for y in range(3):
                                    if block_x + x != ri or block_y + y != ci:
                                        var |= all_set[block_x + x][block_y + y]
                            set_val = all_set[ri][ci] - var
                            if len(set_val) == 1:
                                sol[ri][ci], = set_val
                                flag = True
                                break
    (r, c), set_value = min_set_val
    # этап 3 - рекурсивная подстановка всех возможных значений,
    # когда однозначных вариантов не осталось
    for value in set_value:
        sol_copy = [[y for y in x] for x in sol]
        sol_copy[r][c] = value
        result = sudoku_solver(sol_copy)
        if not result:
            continue
        return result
    return False

def search_value(ri, ci, sudo):
    '''Функция поиска всех возможных вариантов
        значений для конкретной ячейки судоку'''
    block_x = 3 * (ri // 3)
    block_y = 3 * (ci // 3)
    return (set(range(1, 10)) - set(sudo[ri]) - {line[ci] for line in sudo} -
        {sudo[block_x + x][block_y + y] for x in range(3) for y in range(3)})

def verification(sudoku):
    '''Функция проверки судоку на правильность решения'''
    for line in sudoku:
        if 0 in line or len(set(line)) != 9:
            return False
    for i in range(9):
        column = {line[i] for line in sudoku}
        if 0 in column or len(column) != 9:
            return False
    for bloc_x in range(0, 8, 3):
        for bloc_y in range(0, 8, 3):
            bloc = {sudoku[bloc_x + x][bloc_y + y]
                    for x in range(3) for y in range(3)}
            if 0 in bloc or len(bloc) != 9:
                return False
    return True

with open(abspath(join('..', 'Data', 'sudoku_100.txt')),
        encoding='utf-8') as read:
    sudoku_list = read.readlines()

with open(abspath(join('..', 'Data', 'sudoku_solved.txt')),
        'wt', encoding='utf-8') as write:
    time_result, count = process_time(), 0
    for line in sudoku_list:
        line = line.strip()
        if len(line) == 81 and line.isdigit():
            count += 1
            sudoku = line_to_sudoku(line)
            print(f'\nСудоку {count:3} для решения:', file=write)
            printer_sudoku(sudoku, out=write)
            
            sudoku_time = process_time()
            sudoku_res = sudoku_solver(sudoku)
            s_t = process_time() - sudoku_time
            
            if sudoku_res:
                print(f'Судоку {count:3}  решена за {s_t:>6.3f} сек:',
                    file=write)
                printer_sudoku(sudoku_res, out=write)
                print(f'Судоку {count:3}  решена за {s_t:>6.3f} сек.')
                if not verification(sudoku_res):
                    print('Решена не правильно!!!')
            else:
                print(f'''Судоку {count:3}  НЕ решена.
                    На попытку решения затрачено {s_t:>6.3f} сек.''')
                print(f'''\n\nСудоку {count:3}  НЕ решена.
                    На попытку решения затрачено {s_t:>6.3f} сек.\n''',
                    file=write)
    time_result = process_time() - time_result
    print(f'\nНа решение {count} судоку затрачено {time_result:>7.3f} сек.\n')
    print(f'\nНа решение {count} судоку затрачено {time_result:>7.3f} сек.',
        file=write)
