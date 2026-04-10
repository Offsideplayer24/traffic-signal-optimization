"""
Enhanced Traffic Simulation with Algorithm Comparison
Integrates Greedy and Dynamic Programming approaches
Algorithms Fall 2025
Members - Steve George & Kaushal Nair

HOW TO RUN:
1.First unzip the file and make sure before running the file make sure the images folder is in the same folder where the traffic_simulation_enhanced.py file is saved.
"""

import random
import math
import time
import threading
import pygame
import sys
import os
from collections import defaultdict
from typing import List, Dict, Tuple

# ==================== CONFIGURATION ====================

# Default timing values
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10  # Minimum green time constraint
defaultMaximum = 60   # Maximum green time constraint

# Simulation parameters
simTime = 120
timeElapsed = 0
noOfSignals = 4
noOfLanes = 2

# Current state
currentGreen = 0
nextGreen = 1
currentYellow = 0

# Algorithm selection: "greedy" or "dp"
ALGORITHM = "dp"  # Change this to switch algorithms

# Vehicle timing
carTime = 2
bikeTime = 1
rickshawTime = 2.25
busTime = 2.5
truckTime = 2.5

# Detection time
detectionTime = 5

# Vehicle counts (for queue tracking)
queueCounts = {'right': [0, 0, 0], 'down': [0, 0, 0], 
               'left': [0, 0, 0], 'up': [0, 0, 0]}

# Performance metrics
metrics = {
    'total_queue_history': [],
    'per_lane_queue': defaultdict(list),
    'vehicles_crossed': {'right': 0, 'down': 0, 'left': 0, 'up': 0},
    'total_wait_time': 0,
    'green_time_history': []
}

# Speeds
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'rickshaw': 2, 'bike': 2.5}

# Coordinates
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 
     'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 
     'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 
            'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 
            'up': {0: [], 1: [], 2: [], 'crossed': 0}}

vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Signal coordinates
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]

# Stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580, 580, 580], 'down': [320, 320, 320], 
         'left': [810, 810, 810], 'up': [545, 545, 545]}

# Mid points for turning
mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450},
       'left': {'x': 695, 'y': 425}, 'up': {'x': 695, 'y': 400}}

rotationAngle = 3
gap = 15
gap2 = 15

pygame.init()
simulation = pygame.sprite.Group()

signals = []


# ==================== CLASSES ====================

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = str(green)
        self.totalGreenTime = 0


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        self.waitTime = 0  # Track waiting time
        
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)

        if direction == 'right':
            if (len(vehicles[direction][lane]) > 1 and 
                vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = (vehicles[direction][lane][self.index-1].stop - 
                           vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap)
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
            
        elif direction == 'left':
            if (len(vehicles[direction][lane]) > 1 and 
                vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = (vehicles[direction][lane][self.index-1].stop + 
                           vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap)
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
            
        elif direction == 'down':
            if (len(vehicles[direction][lane]) > 1 and 
                vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = (vehicles[direction][lane][self.index-1].stop - 
                           vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap)
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
            
        elif direction == 'up':
            if (len(vehicles[direction][lane]) > 1 and 
                vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = (vehicles[direction][lane][self.index-1].stop + 
                           vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap)
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
            
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        if self.direction == 'right':
            if (self.crossed == 0 and 
                self.x + self.currentImage.get_rect().width > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                metrics['vehicles_crossed'][self.direction] += 1
                
            if self.willTurn == 1:
                if (self.crossed == 0 or 
                    self.x + self.currentImage.get_rect().width < mid[self.direction]['x']):
                    if ((self.x + self.currentImage.get_rect().width <= self.stop or 
                         (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and 
                        (self.index == 0 or 
                         self.x + self.currentImage.get_rect().width < 
                         (vehicles[self.direction][self.lane][self.index-1].x - gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.x += self.speed
                else:
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, 
                                                                   -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index == 0 or 
                            self.y + self.currentImage.get_rect().height < 
                            (vehicles[self.direction][self.lane][self.index-1].y - gap2) or 
                            self.x + self.currentImage.get_rect().width < 
                            (vehicles[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += self.speed
            else:
                if ((self.x + self.currentImage.get_rect().width <= self.stop or 
                     self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and 
                    (self.index == 0 or 
                     self.x + self.currentImage.get_rect().width < 
                     (vehicles[self.direction][self.lane][self.index-1].x - gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.x += self.speed

        elif self.direction == 'down':
            if (self.crossed == 0 and 
                self.y + self.currentImage.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                metrics['vehicles_crossed'][self.direction] += 1
                
            if self.willTurn == 1:
                if (self.crossed == 0 or 
                    self.y + self.currentImage.get_rect().height < mid[self.direction]['y']):
                    if ((self.y + self.currentImage.get_rect().height <= self.stop or 
                         (currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and 
                        (self.index == 0 or 
                         self.y + self.currentImage.get_rect().height < 
                         (vehicles[self.direction][self.lane][self.index-1].y - gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.y += self.speed
                else:
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, 
                                                                   -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index == 0 or 
                            self.x > (vehicles[self.direction][self.lane][self.index-1].x + 
                                     vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or 
                            self.y < (vehicles[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= self.speed
            else:
                if ((self.y + self.currentImage.get_rect().height <= self.stop or 
                     self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and 
                    (self.index == 0 or 
                     self.y + self.currentImage.get_rect().height < 
                     (vehicles[self.direction][self.lane][self.index-1].y - gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.y += self.speed

        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                metrics['vehicles_crossed'][self.direction] += 1
                
            if self.willTurn == 1:
                if self.crossed == 0 or self.x > mid[self.direction]['x']:
                    if ((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or 
                         self.crossed == 1) and 
                        (self.index == 0 or 
                         self.x > (vehicles[self.direction][self.lane][self.index-1].x + 
                                  vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.x -= self.speed
                else:
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, 
                                                                   -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index == 0 or 
                            self.y > (vehicles[self.direction][self.lane][self.index-1].y + 
                                     vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or 
                            self.x > (vehicles[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= self.speed
            else:
                if ((self.x >= self.stop or self.crossed == 1 or 
                     (currentGreen == 2 and currentYellow == 0)) and 
                    (self.index == 0 or 
                     self.x > (vehicles[self.direction][self.lane][self.index-1].x + 
                              vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.x -= self.speed

        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                metrics['vehicles_crossed'][self.direction] += 1
                
            if self.willTurn == 1:
                if self.crossed == 0 or self.y > mid[self.direction]['y']:
                    if ((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or 
                         self.crossed == 1) and 
                        (self.index == 0 or 
                         self.y > (vehicles[self.direction][self.lane][self.index-1].y + 
                                  vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or 
                         vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.y -= self.speed
                else:
                    if self.turned == 0:
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, 
                                                                   -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if self.rotateAngle == 90:
                            self.turned = 1
                    else:
                        if (self.index == 0 or 
                            self.x < (vehicles[self.direction][self.lane][self.index-1].x - 
                                     vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or 
                            self.y > (vehicles[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += self.speed
            else:
                if ((self.y >= self.stop or self.crossed == 1 or 
                     (currentGreen == 3 and currentYellow == 0)) and 
                    (self.index == 0 or 
                     self.y > (vehicles[self.direction][self.lane][self.index-1].y + 
                              vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or 
                     (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.y -= self.speed


# ==================== ALGORITHM FUNCTIONS ====================

def calculate_queue_lengths():
    """Calculate current queue length for each direction"""
    global queueCounts
    
    for direction in directionNumbers.values():
        for lane in range(3):  # 0, 1, 2
            count = 0
            for vehicle in vehicles[direction][lane]:
                if vehicle.crossed == 0:
                    count += 1
            queueCounts[direction][lane] = count


def greedy_set_time():
    """
    Greedy Heuristic: Assign green time to direction with longest total queue
    Time Complexity: O(n) where n = number of directions
    """
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws
    
    print(f"\n[GREEDY] Detecting vehicles for direction: {directionNumbers[nextGreen]}")
    
    # Calculate queue for each direction
    direction_queues = {}
    
    for i in range(noOfSignals):
        direction = directionNumbers[i]
        total_queue = 0
        noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
        
        # Count vehicles in bike lane
        for vehicle in vehicles[direction][0]:
            if vehicle.crossed == 0:
                noOfBikes += 1
        
        # Count vehicles in other lanes
        for lane in range(1, 3):
            for vehicle in vehicles[direction][lane]:
                if vehicle.crossed == 0:
                    vclass = vehicle.vehicleClass
                    if vclass == 'car':
                        noOfCars += 1
                    elif vclass == 'bus':
                        noOfBuses += 1
                    elif vclass == 'truck':
                        noOfTrucks += 1
                    elif vclass == 'rickshaw':
                        noOfRickshaws += 1
        
        # Calculate weighted queue (based on vehicle pass times)
        weighted_queue = ((noOfCars * carTime) + (noOfRickshaws * rickshawTime) + 
                         (noOfBuses * busTime) + (noOfTrucks * truckTime) + 
                         (noOfBikes * bikeTime))
        
        direction_queues[i] = weighted_queue
        
        if i == nextGreen:
            # Calculate green time for next signal
            greenTime = math.ceil(weighted_queue / (noOfLanes + 1))
            
            # Apply constraints
            if greenTime < defaultMinimum:
                greenTime = defaultMinimum
            elif greenTime > defaultMaximum:
                greenTime = defaultMaximum
            
            print(f"[GREEDY] Direction {direction}: Queue={weighted_queue:.1f}, Green Time={greenTime}s")
            
            signals[nextGreen].green = greenTime
            metrics['green_time_history'].append(greenTime)


def dp_set_time():
    """
    Dynamic Programming: Optimize schedule for next few cycles
    Lookahead DP that looks ahead at queue states
    """
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws
    
    print(f"\n[DP] Computing optimal schedule for direction: {directionNumbers[nextGreen]}")
    
    # Get current state for all directions
    direction_states = {}
    
    for i in range(noOfSignals):
        direction = directionNumbers[i]
        noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
        
        for vehicle in vehicles[direction][0]:
            if vehicle.crossed == 0:
                noOfBikes += 1
        
        for lane in range(1, 3):
            for vehicle in vehicles[direction][lane]:
                if vehicle.crossed == 0:
                    vclass = vehicle.vehicleClass
                    if vclass == 'car':
                        noOfCars += 1
                    elif vclass == 'bus':
                        noOfBuses += 1
                    elif vclass == 'truck':
                        noOfTrucks += 1
                    elif vclass == 'rickshaw':
                        noOfRickshaws += 1
        
        weighted_queue = ((noOfCars * carTime) + (noOfRickshaws * rickshawTime) + 
                         (noOfBuses * busTime) + (noOfTrucks * truckTime) + 
                         (noOfBikes * bikeTime))
        
        direction_states[i] = {
            'queue': weighted_queue,
            'cars': noOfCars,
            'bikes': noOfBikes,
            'buses': noOfBuses,
            'trucks': noOfTrucks,
            'rickshaws': noOfRickshaws
        }
    
    # Simple DP: Try different green times and estimate resulting queue state
    best_green = defaultMinimum
    best_cost = float('inf')
    
    for green_time in range(defaultMinimum, defaultMaximum + 1, 5):
        # Estimate cost: vehicles cleared from current direction vs accumulation in others
        vehicles_cleared = green_time / 2  # Approximate
        
        # Cost = remaining queue in current + accumulated queue in others
        remaining_current = max(0, direction_states[nextGreen]['queue'] - vehicles_cleared)
        
        # Other directions accumulate
        accumulated_others = sum(
            direction_states[i]['queue'] + (green_time * 0.5)  # 0.5 vehicles/sec arrival rate
            for i in range(noOfSignals) if i != nextGreen
        )
        
        total_cost = remaining_current + accumulated_others
        
        if total_cost < best_cost:
            best_cost = total_cost
            best_green = green_time
    
    print(f"[DP] Direction {directionNumbers[nextGreen]}: " + 
          f"Queue={direction_states[nextGreen]['queue']:.1f}, " + 
          f"Optimal Green Time={best_green}s")
    
    signals[nextGreen].green = best_green
    metrics['green_time_history'].append(best_green)


def setTime():
    """Wrapper function to call appropriate algorithm"""
    if ALGORITHM == "greedy":
        greedy_set_time()
    else:
        dp_set_time()


# ==================== SIMULATION CONTROL ====================

def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen, 
                       defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)
    repeat()


def repeat():
    global currentGreen, currentYellow, nextGreen
    
    while signals[currentGreen].green > 0:
        printStatus()
        updateValues()
        collectMetrics()
        
        if signals[(currentGreen + 1) % noOfSignals].red == detectionTime:
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
        
        time.sleep(1)
    
    currentYellow = 1
    
    # Reset stops
    for i in range(0, 3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    
    while signals[currentGreen].yellow > 0:
        printStatus()
        updateValues()
        time.sleep(1)
    
    currentYellow = 0
    
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    
    repeat()


def printStatus():
    print(f"\n[{ALGORITHM.upper()}] Time: {timeElapsed}s")
    for i in range(0, noOfSignals):
        status = "GREEN" if i == currentGreen and currentYellow == 0 else \
                 "YELLOW" if i == currentGreen else "RED"
        print(f"  {status} Signal {i+1} ({directionNumbers[i]}): " + 
              f"r={signals[i].red} y={signals[i].yellow} g={signals[i].green}")


def updateValues():
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


def collectMetrics():
    """Collect performance metrics at each time step"""
    calculate_queue_lengths()
    
    total_queue = sum(sum(queueCounts[d]) for d in directionNumbers.values())
    metrics['total_queue_history'].append(total_queue)
    
    for direction in directionNumbers.values():
        direction_queue = sum(queueCounts[direction])
        metrics['per_lane_queue'][direction].append(direction_queue)


def generateVehicles():
    while True:
        vehicle_type = random.randint(0, 4)
        if vehicle_type == 4:
            lane_number = 0
        else:
            lane_number = random.randint(0, 1) + 1
        
        will_turn = 0
        if lane_number == 2:
            temp = random.randint(0, 4)
            will_turn = 1 if temp <= 2 else 0
        
        temp = random.randint(0, 999)
        direction_number = 0
        a = [400, 800, 900, 1000]
        
        if temp < a[0]:
            direction_number = 0
        elif temp < a[1]:
            direction_number = 1
        elif temp < a[2]:
            direction_number = 2
        elif temp < a[3]:
            direction_number = 3
        
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, 
                directionNumbers[direction_number], will_turn)
        time.sleep(0.75)


def simulationTime():
    global timeElapsed, simTime
    
    while True:
        timeElapsed += 1
        time.sleep(1)
        
        if timeElapsed == simTime:
            print("\n" + "="*60)
            print(f"SIMULATION COMPLETE - {ALGORITHM.upper()} Algorithm")
            print("="*60)
            
            print("\nLane-wise Vehicle Counts:")
            totalVehicles = 0
            for i in range(noOfSignals):
                count = vehicles[directionNumbers[i]]['crossed']
                print(f"  Lane {i+1} ({directionNumbers[i]}): {count} vehicles")
                totalVehicles += count
            
            print(f"\nTotal vehicles crossed: {totalVehicles}")
            print(f"Total time: {timeElapsed}s")
            print(f"Vehicles per second: {float(totalVehicles)/float(timeElapsed):.2f}")
            
            # Calculate average queue length
            if metrics['total_queue_history']:
                avg_queue = sum(metrics['total_queue_history']) / len(metrics['total_queue_history'])
                max_queue = max(metrics['total_queue_history'])
                print(f"Average queue length: {avg_queue:.2f}")
                print(f"Maximum queue length: {max_queue}")
            
            print("\n" + "="*60)
            
            # Save metrics to file
            save_metrics()
            
            os._exit(1)


def save_metrics():
    """Save metrics for later analysis"""
    filename = f"metrics_{ALGORITHM}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Algorithm: {ALGORITHM}\n")
        f.write(f"Simulation Time: {simTime}s\n\n")
        
        f.write("Vehicles Crossed by Direction:\n")
        total = 0
        for direction in directionNumbers.values():
            count = vehicles[direction]['crossed']
            f.write(f"  {direction}: {count}\n")
            total += count
        f.write(f"  TOTAL: {total}\n\n")
        
        if metrics['total_queue_history']:
            f.write(f"Average Queue Length: {sum(metrics['total_queue_history'])/len(metrics['total_queue_history']):.2f}\n")
            f.write(f"Maximum Queue Length: {max(metrics['total_queue_history'])}\n")
        
        f.write(f"\nQueue History: {metrics['total_queue_history']}\n")


# ==================== MAIN CLASS ====================

class Main:
    # Start threads
    thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=())
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization", target=initialize, args=())
    thread2.daemon = True
    thread2.start()

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screen setup
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    background = pygame.image.load('images/mod_int.png')
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption(f"TRAFFIC SIMULATION - {ALGORITHM.upper()} Algorithm")

    # Load signal images
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    # Start vehicle generation
    thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_metrics()
                sys.exit()

        screen.blit(background, (0, 0))
        
        # Display signals
        for i in range(0, noOfSignals):
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow if signals[i].yellow > 0 else "STOP"
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green if signals[i].green > 0 else "SLOW"
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red if signals[i].red > 0 else "GO"
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        
        # Display timers and vehicle counts
        signalTexts = ["", "", "", ""]
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])
            
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountText = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountText, vehicleCountCoods[i])

        # Display elapsed time and algorithm
        timeText = font.render(f"Time: {timeElapsed}s - {ALGORITHM.upper()}", True, black, white)
        screen.blit(timeText, (1050, 50))
        
        # Display current total queue
        if metrics['total_queue_history']:
            queueText = font.render(f"Queue: {metrics['total_queue_history'][-1]}", 
                                   True, black, white)
            screen.blit(queueText, (1050, 90))

        # Display vehicles
        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            vehicle.move()
        
        pygame.display.update()


Main()
