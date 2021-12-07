from typing import Iterator
import pygame,time, math,heapq
# math library is only used to calculate log2 and sqrt
# Colors
pygame.init()
pygame.display.set_caption("Path-finding algorithms visualizer")
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
SKY_BLUE=(0,255,255)
COLOR_OF_AVAILABLE=WHITE
COLOR_OF_OBSTACLE=GRAY
COLOR_OF_VISITED=MAGENTA
COLOR_OF_PATH=YELLOW
COOL_DOWN=1
"""Starting width and height when choosing N and M"""
WIDTH =800
M=None
N = None
SQUARE_SIDE=None
HEIGHT=700
FONT_SIZE=30
PANEL_HEIGHT=None
"""GRID is N*M matrix that is the grid. It is essentially a two-dimensional arrary with the one-dimensional arrays containing square onbjects"""
GRID = []
SPEED_OF_FILLING=1
"""returns True if x and y are inside a certain border, otherwise returns Flase"""



def inside(x, y,lo_x=0,lo_y=0,hi_x=M, hi_y=N):
    if hi_x==None: hi_x=M # Just fixes some bug that happens because inside thinks that N and M are still None even after they change
    if hi_y==None: hi_y=N
    return x >= lo_x and x < hi_x and y <hi_y and y >=lo_y

"""Math functions"""
def ceil(number):
    if round(number)>=number:return round(number)
    return round(number)+1
def floor(number):
    if round(number)<=number: return round(number) 
    else: return round(number)-1

"""Used in the starting screen to get input for N, M and Speed"""
class Input_box:

    def __init__(self, x, y, w, h,subject ,text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.subject=FONT.render(subject,True,self.color) # The text to the left of the input box
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the Input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key != pygame.K_RETURN:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.subject,(self.rect.x-self.subject.get_width()-10,self.rect.y+5))
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

"""This Linked list class is used to store the updates for the animations. It uses the same syntax for c++ queue as I am used to it"""
class Linked_list():
    """Three senarios:
        1. If the list is empty then the first element is gonna have all its atributes to be none
        2. If the list has only one element then the first element is gonna be its own tail and next is gonna be none
        3. Other wise i-the element is gonna have its next as (i-1)-the element, which in its self is a linked list with (i-1) in size
    """
    
    def __init__(self,head=None):
        self.head=head
        self.next=None
        if head:self.tail=self
        else: self.tail=None

    def empty(self):
        return self.head==None

    def push(self,element):
        new_tail=Linked_list(element)
        if self.empty():
            self.head=element
            self.tail=self
        else:
            if self.next==None:
                self.next=new_tail
            self.tail.next=new_tail
            self.tail=new_tail
    
    def front(self):
        return self.head
    
    def pop(self):
        assert not self.empty()
        if self.next==None:
            self.head=None
            self.tail=None
        else:
            self.head=self.next.head
            self.next=self.next.next

"""Used for updates that are pushed to the GUI"""
class Update:
    def __init__(self, shape, x=0,y=0,color=0,radius=0,width=0,height=0):
        self.shape=shape
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.radius=radius
        self.color=color
    
    def draw(self,screen):
        if self.shape=="circle":
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.radius)
        elif self.shape=="rect":
            pygame.draw.rect(screen,self.color,(self.x,self.y,self.width,self.height))

class Square:
    """A square object to help keep track of the many variables that each square has"""

    def __init__(self, x, y, color,on_path=False,visited=False,last_time_pressed=0,is_obstacle=False):
        self.x = x
        self.y = y
        self.color = color
        self.is_obstacle = is_obstacle
        self.last_time_pressed=last_time_pressed # This is used for the cool down of changing status
        self.on_path=on_path 
        self.visited=visited

    """returs a list of the adjecant squares that are available (are not obstalces) to the square"""
    def __lt__(self,other): # So that square objects can be used in tuples in heaps
        return 0 # doesn't matter, zero is chosen arbtirarly
    def get_neighbours(self):
        neighbours = []
        x = self.x
        y = self.y
        if inside(x + 1, y) and not GRID[y][x + 1].is_obstacle:
            neighbours.append(GRID[y][x + 1])
        if inside(x, y + 1) and not GRID[y + 1][x].is_obstacle:
            neighbours.append(GRID[y + 1][x])
        if inside(x - 1, y) and not GRID[y][x - 1].is_obstacle:
            neighbours.append(GRID[y][x - 1])
        if inside(x, y - 1) and not GRID[y - 1][x].is_obstacle:
            neighbours.append(GRID[y - 1][x])
        return neighbours

    """Flips the availablity of a square"""
    def flip(self):
        if time.time()-self.last_time_pressed<COOL_DOWN: return #So that it doesn't change status too many times a second while holding the mouse button down
        self.is_obstacle= not self.is_obstacle
        if self.is_obstacle: self.color=COLOR_OF_OBSTACLE
        else: self.color=COLOR_OF_AVAILABLE
        self.last_time_pressed=time.time()
    
    """Creates an animation of an expanding figure within a square which fills the entire square"""

    def fill(self,color):
        updates=Linked_list()
        """Expanding square"""
        half_side=0
        while half_side < floor(SQUARE_SIDE/2)-1: # If it fills the entire square it is gonna fill the grid lines
            u=Update("rect",ceil(self.x*SQUARE_SIDE+SQUARE_SIDE/2-half_side),ceil(self.y*SQUARE_SIDE+SQUARE_SIDE/2+PANEL_HEIGHT-half_side),color,width=half_side*2,height=half_side*2)
            updates.push(u)
            half_side+=SPEED_OF_FILLING
        updates.push(Update("color",self.x,self.y,color))
        return updates

    def draw(self,screen):
        pygame.draw.rect(
            screen, self.color, (self.x*SQUARE_SIDE+1, self.y*SQUARE_SIDE+PANEL_HEIGHT+1, SQUARE_SIDE-1, SQUARE_SIDE-1), 0 # withou +1 and -1 the squares would cover the grid lines
        )
        
class Button:
    """A button object that is used for the viual buttos in the GUI"""

    def __init__(self, color, x, y, width, height, text, text_color,status_last_time_drawn=None, shown=True):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.text_color = text_color
        self.shown=shown
        self.status_last_time_drawn=status_last_time_drawn

    """Draws the button object on the screen"""

    def draw(self, screen,flip_colors=False,outline=""):
        self.status_last_time_drawn=flip_colors 
        if outline:
            """This draws a frame around the button witht the color (outline)"""
            pygame.draw.rect(
                screen,
                outline,
                (self.x - 2, self.y - 2, self.width + 4, self.height + 4),
                0,
            )

        button_color=self.color
        text_color=self.text_color
        if flip_colors:
            button_color=self.text_color
            text_color=self.color
        pygame.draw.rect(
            screen, button_color, (self.x, self.y, self.width, self.height), 0
        )

        font = pygame.font.SysFont("inkfree", FONT_SIZE)
        text = font.render(self.text, 1, text_color)
        """this is done so that the text is centred"""
        screen.blit(
            text,
            (
                self.x + (self.width / 2 - text.get_width() / 2),
                self.y + (self.height / 2 - text.get_height() / 2),
            ),
        )

    """Returns wether the mouse is over the button"""

    def isOver(self):
        pos=pygame.mouse.get_pos()
        if pos[0] > self.x and pos[0] < self.x + self.width and pos[1]>self.y and pos[1]<self.y+self.height:
                return True
        return False
def distance_for_A_star(a,b,iteartion,distance_to_start_square):
    return abs(a.x-b.x)+abs(a.y-b.y)+distance_to_start_square+iteartion/10**9 # Manhattan distance to finish square + distnace to start square and if two squares have   
                                                                              # the same total distance take the one that was visited first
                                        
def distance_for_unweighted_bfs(a,b,iteration,distance_to_start_square): # Just take the one that was visited first
    return iteration

def BFS(start, finish,updates,animating,distance_funciton=distance_for_unweighted_bfs):
    iteartion=0
    q=[(distance_funciton(start,finish,iteartion,0),start)]
    heapq.heapify(q)
    start_time=time.time()
    reached_from=[[None for i in range(M)] for i in range(N)]
    distance_to_start_square=[[10000000 for i in range(M)] for i in range(N)]
    reached_from[start.y][start.x]=start
    distance_to_start_square[start.y][start.x]=0
    found =False
    while len(q):
        w,cur=heapq.heappop(q)
        for neighbour in cur.get_neighbours():
            iteartion+=1
            x=neighbour.x
            y=neighbour.y
            if reached_from[y][x]==None:
                reached_from[y][x]=cur
                distance_to_start_square[y][x]=distance_to_start_square[cur.y][cur.x]+1
                GRID[y][x].visited=True
                if neighbour==finish:
                    found=True
                    break
                if animating:
                    to_update=neighbour.fill(COLOR_OF_VISITED)
                    while not to_update.empty():
                        updates.push(to_update.front())
                        to_update.pop()
                else: updates.push(Update("color",neighbour.x,neighbour.y,COLOR_OF_VISITED))
                heapq.heappush(q,(distance_funciton(finish,neighbour,iteartion,distance_to_start_square[y][x]),neighbour))
        if found:
            break        

    """This makes sure that there is a path"""
    if reached_from[finish.y][finish.x]==None:
        # updates.push(Update("path does not exist"))
        return
    """ This adds the squares along the path"""
    cur=reached_from[finish.y][finish.x]
    while cur!=start:
        cur.on_path=True
        updates.push(Update("color",cur.x,cur.y,COLOR_OF_PATH))
        cur=reached_from[cur.y][cur.x]
    print("bfs/A* took ",time.time()-start_time," seconds")

"""DFS is usually implemented recursively, but the python interpteret in my computer crashes after 1103 steps of recursion even after setting recursion limit to be high.
For that reason,and to avoid other potential issues that can happen with recursion in python, I am using my own stack and implementing an iterative DFS"""

def DFS(cur,start,finish,updates,animating):
    stack=[]
    # Each element in the stack is a tuple of a square and how many of the square's neighbours have been processed
    stack.append((start,0))
    start_time=time.time()
    while len(stack):
        cur,processed=stack[-1]
        if processed==len(cur.get_neighbours()):
            stack.pop()
            continue
        if cur==finish:
            stack.pop()
            while len(stack)>1: # First element is the starting square
                stack[-1][0].on_path=True
                updates.push(Update("color",stack[-1][0].x,stack[-1][0].y,COLOR_OF_PATH))
                stack.pop()
            break
        if cur!=start and processed==0:
            if animating:
                to_update=cur.fill(COLOR_OF_VISITED)
                while not to_update.empty():
                    updates.push(to_update.front())
                    to_update.pop()
            else: updates.push(Update("color",cur.x,cur.y,COLOR_OF_VISITED))
        cur.visited=True
        
        neigbour=cur.get_neighbours()[processed]
        stack[-1]=(cur,processed+1)
        if not neigbour.visited:
            stack.append((neigbour,0))
    print("dfs took",time.time()-start_time," seconds")

def draw_lines_in_grid(screen):
    i=0
    while i<=WIDTH:
        pygame.draw.line(screen, BLACK,(round(i),PANEL_HEIGHT),(round(i),HEIGHT))
        i+=SQUARE_SIDE
    i=PANEL_HEIGHT
    while i<=HEIGHT:
        pygame.draw.line(screen,BLACK,(0,round(i)),(WIDTH,round(i)))
        i+=SQUARE_SIDE
"""Adds squares to the GRID"""
def add_squares():
    for y in range(N):
        row=[]
        for x in range(M):
            row.append(Square(x,y,COLOR_OF_AVAILABLE))
        GRID.append(row)

def draw_squares(screen,start_square,finish_square):
    for row in GRID:
        for element in row:
            temp=element.color
            if (element.x,element.y)==start_square:
                element.color=GREEN
            elif (element.x,element.y)==finish_square:
                element.color=BLUE
            element.draw(screen)
            element.color=temp
        
def pause_slash_start_animation(button,screen,paused):
    paused[0]=not paused[0]
    button.text="Start animation" if button.text=="Pause animation" else "Pause animation"
    button.draw(screen)
    pygame.display.flip()

def start(started,start_square,finish_square,updates,start_button,screen,algorithm):
    start_button.draw(screen,outline=BLACK)
    started[0]=True 
    if algorithm=="DFS":
        DFS(GRID[start_square[1]][start_square[0]],GRID[start_square[1]][start_square[0]],GRID[finish_square[1]][finish_square[0]],updates,True)
    elif algorithm=="BFS":
        BFS(GRID[start_square[1]][start_square[0]],GRID[finish_square[1]][finish_square[0]],updates,True)
    elif algorithm=="A*":
        BFS(GRID[start_square[1]][start_square[0]],GRID[finish_square[1]][finish_square[0]],updates,True,distance_for_A_star)


def clear(updates,started):
    updates.head=None
    updates.next=None
    updates.tail=None
    for i in range(len(GRID)):
        for j in range(len(GRID[0])):
            if not started[0]:GRID[i][j].is_obstacle=False
            GRID[i][j].color=COLOR_OF_AVAILABLE if not GRID[i][j].is_obstacle else COLOR_OF_OBSTACLE
            GRID[i][j].visited=False
    started[0]=False

def initiate_buttons():
    buttons=[]
    shift=0
    sum_of_widths=0
    start_button=Button(SKY_BLUE,sum_of_widths,0,round(WIDTH/6),PANEL_HEIGHT-shift,"Start",GRAY)
    sum_of_widths+=round(WIDTH/6)
    pause_button=Button(SKY_BLUE,sum_of_widths,0,round(WIDTH/2.2),PANEL_HEIGHT-shift,"Pause animation",GRAY)
    sum_of_widths+=round(WIDTH/2.2)
    clear_button= Button(SKY_BLUE,sum_of_widths,0,round(WIDTH/6),PANEL_HEIGHT,"Clear",GRAY)
    sum_of_widths+=round(WIDTH/6)
    button_list=[Button(SKY_BLUE,sum_of_widths,0,WIDTH-sum_of_widths,(PANEL_HEIGHT-shift),"BFS",GRAY) for i in range(3)]
    buttons.append(clear_button)
    buttons.append(start_button)
    buttons.append(pause_button)
    button_list[1].text="DFS"
    button_list[0].text="A*"
    for i in button_list:
        buttons.append(i)
    return buttons,button_list

def handle_buttons(screen,buttons,button_list,started=[False]):
    for button in buttons:
        if started[0] and button.text!="Clear":
            if button.status_last_time_drawn:
                button.draw(screen,False,outline=BLACK) # Here all buttons but clear are forced to be blue after start
            continue # I don't want other buttons to be activated after start
        Flip_colors=button.isOver()  # doesn't flip color of start button if the animation has already started
        if button.shown and (button.status_last_time_drawn != Flip_colors or button in button_list):
            button.draw(screen,flip_colors=Flip_colors,outline=BLACK)
            if button.text=="Clear" or len(button.text)>=3 and button.text[-3:]=="ion": pygame.display.flip() # Cler and pause/start animation should be updated when animating
        
        if len(button_list)==0:continue # This means that function is called from handle_buttons_during_animation
        """This part animates the list of buttons"""
        speed=0.5*math.log2(N*M) # Speed is a function of the number of squares so that bigger grid has higher speed
        if button is button_list[1]:
            for i in button_list:
                if i.isOver():
                    button.y=min(button.y+speed,PANEL_HEIGHT)
                    break
            else: button.y=max(button.y-speed,0)
        if button is button_list[0]:
            for i in button_list:
                if i.isOver():
                    button.y=min(button.y+speed*2,PANEL_HEIGHT*2)
                    break
            else: button.y=max(button.y-speed*2,0)

"""This function handles the clear and the pause/start animation buttons during animation. As other buttons are not needed it is more efficient"""
def handle_buttons_during_animation(screen,buttons,started,updates,paused):
    handle_buttons(screen,buttons,[])
    clear_button=buttons[0]
    pause_button=buttons[1]
    for event in pygame.event.get():
        if event.type==pygame.MOUSEBUTTONDOWN:
            if clear_button.isOver():
                clear(updates,started)
            if pause_button.isOver():
                pause_slash_start_animation(pause_button,screen,paused)


def push_updates_to_GUI(screen,updates,animating,button_list,buttons,started,paused):
    buttons=[buttons[0],buttons[2]] # The clear and ths pause/start animation buttons
    while not updates.empty():
        if not paused[0]:
            updated=False
            if updates.front().shape=="color":
                # When animating in real time the squares on path should not be uptaed to any color but the color of the path
                if (updates.front().color==COLOR_OF_PATH) or animating[0] or not GRID[updates.front().y][updates.front().x].on_path:
                    if GRID[updates.front().y][updates.front().x].color!=updates.front().color: # If the color of the square is already the color it should be updated 
                        updated=True                                                            # to then don't update (makes theings much faster when finding path in real time)
                        GRID[updates.front().y][updates.front().x].color=updates.front().color
                        GRID[updates.front().y][updates.front().x].draw(screen)
            elif not paused[0]:
                updated=True
                updates.front().draw(screen)
            updates.pop()
            if updated:
                #draw_lines_in_grid(screen)
                pygame.display.flip() # This takes alot of time so it is only triggered if something actually happens
        handle_buttons_during_animation(screen,buttons,started,updates,paused)
    animating[0]=False

def find_path_in_real_time(updates,start,finish,algorithm):
    # Resets the squares' status
    for row in GRID:
        for el in row:
            el.visited=False
            el.on_path=False
    if algorithm=="BFS":
        BFS(start,finish,updates,False)
    elif algorithm=="DFS":
        DFS(start,start,finish,updates,False)
    elif algorithm=="A*":
        BFS(start,finish,updates,False,distance_for_A_star)
    # Resets the colors of squares
    for row in GRID:
        for el in row:
            if el==start or el ==finish or el.visited: continue
            el.color= COLOR_OF_OBSTACLE if el.is_obstacle else COLOR_OF_AVAILABLE
    
def change_square_status(button_list,start_square,finish_square):
    mouse_pos=pygame.mouse.get_pos()
    if mouse_pos[1]>button_list[0].y+button_list[0].height: # checks wether the y-coordinates of the mouse is greater than height of the list
        x=int(mouse_pos[0]//SQUARE_SIDE)
        y=int((mouse_pos[1]-PANEL_HEIGHT)//SQUARE_SIDE)
        if time.time()-GRID[start_square[1]][start_square[0]].last_time_pressed<0.01*math.sqrt(N*M): # This checks that start/finish square was clicked in the last f(numeber of squares)
            if(x,y)!=finish_square:start_square=(x,y)                                                # seconds and drags it if so. I have the time as a function of 
        elif time.time()-GRID[finish_square[1]][finish_square[0]].last_time_pressed<0.01*math.sqrt(N*M): # of numbers of squares because the program gets slower with largers grids
            if(x,y)!=start_square:finish_square=(x,y)
        elif(x,y)!= start_square and (x,y) !=finish_square:GRID[y][x].flip()
        GRID[y][x].last_time_pressed=time.time()
    return start_square,finish_square

"""Determines opacity of the text shown in the starting screen"""
def opacity_as_a_function_of_time(time):
    if time<1:
        return round(time*255)
    if time>4:
        return (5-time)*255
    return 255

"""A starting screen to let the user choose N and M, which is the number of rows and columns respectively. Width (which is fixed to 600)
has to be a multiple of the number of columns, otherwise SQUARE_SIDE will be non-integer.
Height will be set automatically so that the grid could have N rows and M columns of SQUARES not rectangles"""
def determine_size(running):
    global N,M,SQUARE_SIDE,SPEED_OF_FILLING,WIDTH,HEIGHT,PANEL_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    input_box1 = Input_box(100, 100, 140, 32,"N")
    input_box2 = Input_box(100, 200, 140, 32,"M")
    input_box3 = Input_box(100, 300, 140, 32,"Speed")
    input_boxes = [input_box1, input_box2,input_box3]
    last_time_shown_message=0
    while running[0]:
        screen.fill((30,30,30))
        if N==None:
            for event in pygame.event.get():
                for box in input_boxes :
                    box.handle_event(event)
                if event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN:
                    N=input_boxes[0].text
                    M=input_boxes[1].text
                    SPEED_OF_FILLING=input_boxes[2].text
                    try:
                        N=int(N)
                        M=int(M)
                        SPEED_OF_FILLING=int(SPEED_OF_FILLING)
                        assert (600%M)==0
                        assert N<=200 and N>0
                        assert M<=200 and M>0
                        assert SPEED_OF_FILLING>=1 and SPEED_OF_FILLING <=500
                        SPEED_OF_FILLING/=100
                    except:
                        last_time_shown_message=time.time()
                        N=None
                        M=None
        if time.time()-last_time_shown_message<5:
            first_line=FONT.render("N and M must be integers between 1 and 200, M must be a divisor of 600",True,COLOR_INACTIVE)
            second_line=FONT.render("Speed has to be an integer between 1 and 500",True,COLOR_INACTIVE)
            first_line.set_alpha(opacity_as_a_function_of_time(time.time()-last_time_shown_message))
            second_line.set_alpha(opacity_as_a_function_of_time(time.time()-last_time_shown_message))
            screen.blit(first_line,(20,470))
            screen.blit(second_line,(160,500))

        if event.type == pygame.QUIT:
            running[0]=False
            return None,None
        for box in input_boxes:
            box.update()
            box.draw(screen)
        pygame.display.flip()
        if N!=None:
            WIDTH=600
            SQUARE_SIDE=WIDTH/M
            HEIGHT=SQUARE_SIDE*N
            PANEL_HEIGHT=round(HEIGHT/10)
            HEIGHT+=PANEL_HEIGHT
            return

    
def main():
    """Initiatites the GUI"""
    running = [True]
    determine_size(running)
    if running[0]==False:return
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(WHITE)
    buttons,button_list=initiate_buttons()
    start_square=(0,0)
    finish_square=(M-1,N-1)
    clear_button=buttons[0]
    start_button=buttons[1]
    add_squares()
    updates=Linked_list() # This is used as a stack to push all updates onto so that they can pushed to the GUI later
    """Booleans that are used to get the status of the program. Lists are used instead of actual booleans so that they are mutable"""
    started=[False]
    animating=[False]
    paused=[False]
    """This loop is the main loop for the GUI"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    while running[0]:
        """Draws the squares"""
        something_changed=False
        draw_squares(screen,start_square,finish_square)
        draw_lines_in_grid(screen)
        handle_buttons(screen,buttons,button_list,started)
        """This part hadnles the event. I tried to put in a funtion but it became messy with too many parameters so I chose to keep it in the main function"""
        if pygame.mouse.get_pressed()[0]:
            if pygame.mouse.get_pos()[1]>PANEL_HEIGHT:something_changed=True # so that it doesn't do 2 BFSs when it starts
            start_square,finish_square=change_square_status(button_list,start_square,finish_square)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running[0]=False
            elif event.type==pygame.MOUSEBUTTONDOWN:
                if clear_button.isOver():
                    clear(updates,started)
                if not started[0]:
                    for i in button_list:
                        if i.isOver():
                            i.text,button_list[2].text=button_list[2].text,i.text
                            break
                    if start_button.isOver():
                        if not started[0]:
                            start(started,start_square,finish_square,updates,start_button,screen,button_list[2].text)
                            animating[0]=True
        push_updates_to_GUI(screen,updates,animating,button_list,buttons,started,paused)

        """ The function should be called if:
        1.The program has been started
        2. something has changed fromlsat time the function has been called 
        3. All updates have been pushed to GUI """
        if started[0] and something_changed and updates.empty(): 
            find_path_in_real_time(updates,GRID[start_square[1]][start_square[0]],GRID[finish_square[1]][finish_square[0]],button_list[2].text)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
    pygame.quit()
