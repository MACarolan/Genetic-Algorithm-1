# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 10:01:34 2018

@author: Michael Carolan
"""
from tkinter import *
import random
import time

###### Global parameters ######

# Size of field
width = 600
height = 600

# Dot Variables
pop_size = 1000
mut_rate = 0.05
num_steps = 100
max_stepsize = 20
duplication = 0.5
first_shot = 0.5
# Duplication + first_shot should not exceed 100%

# Change Simulation Speed (length of timestep in seconds)
speed = 0.01

# Starting Point
dot_start = (15,15)

# Goal (x,y coordinates and square radius centered around that point)
goal = (550, 550, 10)

# Visual
dot_size = max(int(width/100), 1)

###### World Object ######

class field:
    """Contains the environment, keeps independent time, tracks dots"""
    def __init__(self, canvas, dots=None):
        print(f"New {width}x{height} field created with {pop_size} Dots!")
        print(f"\nThe goal is centered at {goal[:2]}, with a width of {goal[2]}.")
        
        self.width = width
        self.height = height
        self.start = dot_start
        self.canvas = canvas
        
        #initialize dots
        if dots is None:
            self.dots = set()
            
            for dots in range(pop_size):
                new_dot = dot(canvas, self.start)
                self.dots.add(new_dot)
                
        #stores ordered dots after first generation
        self.dotlist = None
        
        self.time = 0

    def breed_dots(self):
        """
        Reproduction according to the following rules:
            1. Duplicate the top duplication% of dots (to prevent large 
               setbacks when experimenting with high mutation rates)
            
            2. Give the top first_shot% dots a chance to reproduce
            
            3. Randomly select dots and give them a chance to reproduce
               until the population is at capacity
        """
        if self.time != num_steps:
            print("This generation is not finished!")
            return
            
        # clear last generation's remains
        for dots in self.dots:
            self.canvas.delete(dots.body)
            
        new_dots = set()
        
        #Step 1
        copy = int(duplication*len(self.dots))
        
        for spots in range(copy):
            new = dot(self.canvas, self.start, self.dotlist[spots].directions, False)
            new_dots.add(new)
        
        #Step 2
        first = int(first_shot*len(self.dots))
        
        for spots in range(first):
            new = dot(self.canvas, self.start, self.dotlist[spots].directions)
            new_dots.add(new)
        
        #Step 3
        while len(new_dots) < pop_size:
#            breeder = random.choice(self.dotlist)
            for breeder in self.dotlist:
                chance = random.random()
                if chance < breeder.fitness:
                    new = dot(self.canvas, self.start, breeder.directions)
                    new_dots.add(new)
                if len(new_dots) == pop_size:
                    break
                
        self.dots = new_dots
        self.dotlist = None
        self.time = 0


    def timestep(self):
        """
        Advance time in the field up to num_steps, then prompt to
        move on to the next generation
        """
        deathcount = 0
        
        if self.time == num_steps:
            success = fitness(self, self.dots)
            dead = [dot for dot in self.dots if dot.died]
            
            print(f"\n{len(dead)} Dot{'s' if len(dead) != 1 else ''} died in this generation.\
                     \n\n{success} Dot{'s' if success != 1 else ''} managed to reach the goal.")
            
            return
        
        #move dots
        for dot in self.dots:
            if not dot.died and not dot.in_goal():
                dot.loc[0] += dot.directions[self.time][0]
                dot.loc[1] += dot.directions[self.time][1]
                if dot.out_of_bounds():
                    dot.died = True
                    deathcount += 1
                    canvas.itemconfig(dot.body, fill='blue')
                else:
                    #Move dot
                    x = dot.directions[self.time][0]
                    y = dot.directions[self.time][1]
                    self.canvas.move(dot.body, x, y)
                    
        if all([dots.died for dots in self.dots]):
            print(f"All {pop_size} Dots have died.\n")
            self.time = num_steps
            fitness(self, self.dots)
            return
        
        #advance time
        self.time += 1
    
        

###### Dots ######
    
class dot:
    """
    Evolutionary dots, born with random directions and reproduce
    based on calculated fitness
    """
    def __init__(self, canvas, start, directions=None, mutate=True):
        
        self.died = False
        
        #Visual representation
        self.canvas = canvas
        self.body = canvas.create_oval(start[0]-dot_size, start[1]-dot_size,
                                       start[0]+dot_size, start[1]+dot_size, fill='red')
        
        #fitness calculated at end of each generation
        self.fitness = 0
        
        #store mutable location
        self.loc = list(start)
        
        #First generation dot, randomize everything
        if directions is None:
            self.directions = []
            
            for steps in range(num_steps):
                self.directions.append(dot.make_vector())
    
        #For offspring dot, randomize some of the vectors
        elif mutate:
            self.directions = dot.mutate(directions)
            
        else:
            self.directions = list(directions)
            
        
    def mutate(directions):
        """
        Return a slightly mutated list of directions
        Dependent on global mut_rate
        """
        
        #make a copy for mutation
        directions = list(directions)
        for steps in range(len(directions)):
            mutagen = random.random()
                
            #mut_rate% chance a direction will be replaced
            if mutagen < mut_rate:
                directions[steps] = dot.make_vector()
                
        return directions
        
    
    def make_vector():
        """
        Makes randomized vector for dots
        Dependent on global max_step_size
        """
        x = random.randint(-max_stepsize, max_stepsize)
        y = random.randint(-max_stepsize, max_stepsize)
        return (x,y)
    
    
    def length(self):
        """Get length of total path"""
        length = 0
        
        for vector in self.directions:
            length += (vector[0]**2 + vector[1]**2)**(1/2)
        
        return length
    
    
    def in_goal(self):
        """
        Check if dot has reached goal
        Dependent on global goal
        """
        radius = goal[2]
        
        if self.loc[0] in range(goal[0] - radius, goal[0] + radius + 1):
            if self.loc[1] in range(goal[1] - radius, goal[1] + radius + 1):
                return True
            
        return False
    
    
    def dist_from_goal(self):
        """
        Calculate Euclidean distance from goal
        Dependent on global goal
        """
        dist = ((self.loc[0] - goal[0])**2 + (self.loc[1] - goal[1])**2)**(1/2)
        return abs(dist)
    
    
    def out_of_bounds(self):
        """Check if the dot has left the field"""
        if self.loc[0] not in range(0, width) or self.loc[1] not in range(0, height): 
            return True
        return False

###### Obstacles ######

###### Fitness Function ######
        
def fitness(field, dots):
    """
    Assign a 0-100 fitness level (likelihood of reproducing) to each dot
    
    Dot fitness is based on final Euclidean distance from the goal,
    with a bonus for the dots with the shortest path of the group
    
    Dependent on global pop_size
    """
    #dots that reached the goal, as a set so next step is quick
    finishers = set(dot for dot in dots if dot.in_goal())
     
    #separate dots that did not reach goal
    failed = [dot for dot in dots if dot not in finishers and not dot.died]
    
    #sort finishing dots
    finishers = sorted(finishers, 
                       key=lambda unit: unit.length())
    
    #sort failed dots
    failed = sorted(failed, 
                    key=lambda unit: unit.dist_from_goal())
    
    #discourage death
    dead = [dot for dot in dots if dot.died]
    
    #Dots get fitness in order
    ordered = finishers + failed + dead
    
    if finishers != []:
        ordered = list(finishers)
        while len(ordered) < pop_size:
            ordered.append(ordered[0])
    
    fitness = 100
    
    decrement = 100/pop_size
    
    for dot in ordered:
        dot.fitness = fitness/100
        fitness -= decrement
    
    field.dotlist = ordered
    
    return len(finishers)
        

###### Visuals ######
    
# General
tk = Tk()
tk.title('Moving Dots')
tk.wm_attributes('-topmost')
canvas = Canvas(tk, width=width, height=height)
canvas.config(bg='white')
canvas.pack()

# Goal
canvas.create_rectangle(goal[0]-goal[2], goal[1]-goal[2], 
                        goal[0]+goal[2], goal[1]+goal[2], fill='red', outline="white")

# Running The Visualization

F = field(canvas) 
gen = 1

while True:
    
    if F.time == num_steps:
        F.timestep()
        F.breed_dots()
        gen += 1
        print(f"\nGeneration {gen}")
    else:
        F.timestep()
    tk.update_idletasks()
    tk.update()
    time.sleep(speed)
