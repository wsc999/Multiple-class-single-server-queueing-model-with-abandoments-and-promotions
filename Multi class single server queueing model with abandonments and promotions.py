### This code is created for simulate multiple class queueing system with abandonments and promotions
### The code is created under Anaconda environment
### "numpy" and "scipy" package is required to run the code

### Import packages 
import random
import math
import copy
import scipy as sp
import numpy as np
from scipy.stats import poisson as poi
from scipy.stats import expon


### Define type "patient". The "patient" objects store all the imformation generated of each patient during the simulation  
class patient():
    def __init__(self, initClass, arrTime, currentClass, classTime, clockTime, curedClass, diedClass, endTime):
        # The class of the patient when the patient arrives in the system. This attribute doesm't change
        self.initClass = initClass
        
        # The arrival time of the patient. This attribute doesm't change 
        self.arrTime = arrTime
        
        # The current class of the patient. This attribure will be updated
        self.currentClass = currentClass
        
        # The time that a ptient spend in each class. It is a list of length numClass+1. This attribure will be updated
        self.classTime = classTime
        
        # The clock time of the patient. This attribure will be updated
        self.clockTime = clockTime
        
        # The class in which the patient is cured. This attribute doesm't change
        self.curedClass = curedClass
        
        # The class in which the patient is died. This attribute doesm't change
        self.diedClass = diedClass
        
        # The time that the patient is died or cured. This attribute doesm't change
        self.endTime = endTime
    
    # Calculate the time a patient spend in the cuurent and worse class
    def worseTime(self):
        i = 1
        worseT = 0
        while i <= self.currentClass:
            worseT += self.classTime[i]
            i += 1
        return worseT


### Transfer the input parameters into desired form
def inputProcess(numClass, rho):
    classes = [i for i in range(numClass+1)]
    patientsList = []
    
    # Create the cumulative transition probability matrix 
    rhoC = copy.deepcopy(rho)
    for row in rhoC[1:]:
        for j in range(1, len(row)):
            row[j] = row[j] + row[j-1]

    return classes, patientsList, rhoC


### Generate a new patient    
def newPatient(inputClass, T):
    initClass = inputClass
    currentClass = initClass
    diedClass = currentClass
    classTime = [0 for i in range(numClass + 1)]
    clockTime = math.ceil(expon.rvs(scale = 1/alpha[inputClass]))
    return patient(initClass, T, currentClass, classTime, clockTime, 0, diedClass, 0)


### Generate new arrivals
def newArr(classes, patientsList, lambdas, alpha, T):
    for i in classes[1:]:
        # The number of arrivals at each time step
        rnum = poi.rvs(lambdas[i])
        
        for j in range(rnum):
            patientsList.append(newPatient(i, T))
    return patientsList


### Update patient Status 
def pUpdate(classes, patientsList, alpha, rhoC, T):
    if len(patientsList) > 0:
        for p in patientsList:
            if p.currentClass != -1 and p.currentClass != 0:
                p.classTime[p.currentClass] +=1
                p.clockTime -=1

                # The class of the patient changes when the clock time is 0
                if p.clockTime == 0:
                    rnum = random.random()
                    for j in range(len(rhoC[p.currentClass])):
                        if rnum <= rhoC[p.currentClass][j]:
                            p.currentClass = j
                            break

                    if p.currentClass != 0:
                        p.clockTime = math.ceil(expon.rvs(1/alpha[p.currentClass]))
                        p.diedClass = p.currentClass
                    if p.currentClass == 0:
                        p.endTime = T
                    
    return patientsList

### The queueing policy of the simulation. The function returns the index of the patient to serve in "patientList"
def policy(patientsList, classOrder):
    minClass = len(classOrder)
    maxWorseT = 0
    c = False
    for i in range(len(patientsList)):
        if patientsList[i].currentClass > 0:
            if classOrder.index(patientsList[i].currentClass) < minClass:
                minClass = classOrder.index(patientsList[i].currentClass)
                c = i
            if classOrder.index(patientsList[i].currentClass) <= minClass and patientsList[i].worseTime() > maxWorseT:
                maxWorseT = patientsList[i].worseTime()
                c = i


### The service procedure
def serv(classes, patientsList, mu, T, classOrder):
    # Number of donations arrivaled in time T
    rnum = poi.rvs(mu)
    
    for j in range(rnum):
        c = policy(patientsList, classOrder)
        if c:
            patientsList[c].curedClass = patientsList[c].currentClass
            patientsList[c].currentClass = -1
            patientsList[c].endTime = T
    return patientsList

### The main simulation function
### This function is called to run the simulation
### Inputs: 
### T_end: int. Total duration of the simulation
### numClass: int. The number of classes excluding the died class and cured class
### lambdas: list. len(lambdas) == numClass. The arrival rates of each class
### mu: int. The service rate.
### rho: list[list]. numClass by numClass+1. The transition probability
### alpha: list. len(alpha) == numClass. The clock rate of each class
### classOrder: list. The class priority order of the policy. example: if class 3 > class 2 > class 1, then [3, 2, 1] 
### The function returns a list containing all the "patient" type object 
def mainSim(T_end, numClass, lambdas, mu, rho, alpha, classOrder):
    classes, patientsList, rhoC = inputProcess(numClass, rho)
    T = 0
    while T <= T_end:
        # update patients status
        patientsList = pUpdate(classes, patientsList, alpha, rhoC, T)
         
        # check new arrivals
        patientsList = newArr(classes, patientsList, lambdas, alpha, T)     
   
        # check service
        patientsList = serv(classes, patientsList, mu, T, classOrder)
        
        T += 1
    return patientsList
