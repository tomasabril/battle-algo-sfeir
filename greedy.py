#Tomás Abril - SFEIR

import csv
import time

# setup        <------------
#file_location = 'inputtest.csv'
file_location = '10_entry.csv'
output = 0 # 0 for csv, 1 for text
# 0 round_robin
# 1 round_robin, skip colors that have no effect
# 2 greedy                                  << fast
# 3 extra greedy, look up one more turn     << better but slower
strategy = 3
# end of setup <------------

board = []
border = []
visited = []
colors = []
answer = []
size = 0
round_robin_color = 0

####
def print_board(border, visited):
    i = 0
    for line in board:
        j = 0
        for item in line:
            if (i, j) in visited:
                print('-', end=' ')
            elif (i, j) in border:
                print('*', end=' ')
            else:
                print(item, end=' ')
            j += 1
        i += 1
        print('|')
    print('_________________________________________')

def read_input():
    with open(file_location, newline='') as f:
        reader = csv.reader(f)
        i = 0
        j = 0
        for row in reader:
            j = 0
            board.append([])
            for col in row:
                value = int(col)
                j += 1
                board[i].append(value)
                if value not in colors:
                    colors.append(value)
            i += 1
        global size
        size = i

    #colors.sort()
    #colors.reverse()
    if output == 1:
        print(f'Initial board:')
        print(f'colors for this game: {colors}')
        print_board(border, visited)
        print()

# what would be the new border if we changed to this color
def changes_for_color(new_color, fborder, fvisited):
    #look at neighbors of current border, if they are of the same color add them to new_in_border
    new_in_border = []
    new_border = fborder.copy()

    while new_border:
        block = new_border.pop()
        neighbors = get_neighbors(block)
        for n in neighbors:
            #ignoring neighbors already in border and already visited
            if n in fborder or n in fvisited or n in new_border or n in new_in_border:
                continue
            if board[n[0]][n[1]] == new_color:
                new_border.append(n)
        new_in_border.append(block)
    
    #return new border after adding blocks of input new_color
    return new_in_border

def get_neighbors(block):
    neighbors = []
    #above
    if block[1] - 1 >= 0:
        newblock = (block[0], block[1] -1)
        neighbors.append(newblock)
    #right
    if block[0] + 1 < size:
        newblock = (block[0] + 1, block[1])
        neighbors.append(newblock)
    #below
    if block[1] + 1 < size:
        newblock = (block[0], block[1] + 1)
        neighbors.append(newblock)
    #left
    if block[0] - 1 >= 0:
        newblock = (block[0] - 1, block[1])
        neighbors.append(newblock)
    
    return neighbors

def change_color(new_color):
    global border

    border_with_added_blocks = changes_for_color(new_color, border, visited)
    border = border_with_added_blocks.copy()

    #look at current border, if block only touches visited or border move it to visited
    to_remove = []
    for block in border:
        neighbors = get_neighbors(block)
        check_in_border = all(item in border + visited for item in neighbors)
        if check_in_border:
            to_remove.append(block)
    for block in to_remove:
        visited.append(block)
        border.remove(block)

def simulate_change_color(new_color, fborder, fvisited):
    inside_border = fborder.copy()
    inside_visited = fvisited.copy()

    border_with_added_blocks = changes_for_color(new_color, inside_border, inside_visited)
    new_border = border_with_added_blocks.copy()

    #look at current border, if block only touches visited or border move it to visited
    to_remove = []
    for block in new_border:
        neighbors = get_neighbors(block)
        check_in_border = all(item in new_border + inside_visited for item in neighbors)
        if check_in_border:
            to_remove.append(block)
    for block in to_remove:
        inside_visited.append(block)
        new_border.remove(block)
    return (new_border, inside_visited)

# of all possible colors return which results in the most changes
def greedy_next_color():
    max = 0
    color_max = 0
    for color in colors:
        count = len(changes_for_color(color, border, visited)) - len(border)
        #print(f'for color {color} we get {count} changes')
        if count > max:
            max = count
            color_max = color
    #print(f'lets go with: color {color_max} we get {max} changes')
    #print('-')
    return color_max

# similar to normal greedy, but look 2 turns ahead and select color with the most changes
def extra_greedy():
    max = 0
    max_first_turn = 0
    max_second_turn = 0
    color_max = 0
    for color in colors:
        count = len(changes_for_color(color, border.copy(), visited.copy())) - len(border)
        #if this color end the game return it
        if count == 0:
            continue

        #second turn
        simulated_border, simulated_visited = simulate_change_color(color, border.copy(), visited.copy())
        inside_max = 0
        #print(f'first color {color} has {count} changes')
        for next_color in colors:
            next_count = len(changes_for_color(next_color, simulated_border, simulated_visited)) - len(simulated_border)
            #print(f'second color {next_color} got {next_count} changes')
            if next_count > inside_max:
                inside_max = next_count
        total_count = count + inside_max
        #print(f'___for first color {color} we get {total_count} of total changes')

        if total_count > max:
            max = total_count
            max_second_turn = inside_max
            max_first_turn = count
            color_max = color

    if output == 1:
        print(f'choosing color {color_max} with {max_first_turn} changes + {max_second_turn} on next turn <<<<<<<\n')
    return color_max

def round_robin():
    global round_robin_color
    round_robin_color += 1
    if round_robin_color > colors[-1]:
        round_robin_color = 0
    return round_robin_color

def round_robin_nonull():
    global round_robin_color
    while True:
        round_robin_color += 1
        if round_robin_color > colors[-1]:
            round_robin_color = 0
        if len(changes_for_color(round_robin_color, border, visited)) > len(border):
            break
    return round_robin_color


###-- main algorithm --###
if __name__ == "__main__":
    if output == 1:
        start_time = time.time()

    # read csv
    read_input()

    # we start with the color on the top left
    border.append((0, 0))
    change_color(board[0][0])
    if output == 1:
        print(f'Starting of top left with color {board[0][0]}')
        print_board(border, visited)

    while True:
        if strategy == 3:
            next = extra_greedy()
        elif strategy == 2:
            next = greedy_next_color()
        elif strategy == 1:
            next = round_robin_nonull()
        elif strategy == 0:
            next = round_robin()
        
        change_color(next)
        answer.append(next)

        if output == 1:
            print_board(border, visited)
        
        if not border:
            break

    if output == 1:
        print(f'\nThe answer({len(answer)}) is {answer}')
        print("--- %s seconds ---" % (time.time() - start_time))
    if output == 0:
        # generate csv with answer
        vertical = [[item] for item in answer]
        with open('answer.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(vertical)

####
