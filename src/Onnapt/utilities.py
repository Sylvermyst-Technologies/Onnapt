'''
Created on 21 Oct 2014

    Copyright (c) 2014 Brendan Gray and Sylvermyst Technologies

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    
'''


import math
from datetime import datetime


def timeToStr(time, nDecimals = 2):
    '''
    Takes a time in seconds, and returns a string with the format:
        0.00  for times less than 1 minute
        0:00.00 for times between 1 minute and 1 hour
        0:00:00.00 for times greater than 1 hour
    Digits after nDecimals are dropped (not rounded)
    '''
    factor = (10**nDecimals)
    subseconds = int((time % 1) * factor)

    if time<0:
        sign = '-'
        time = -time
    else:
        sign = ''
        

    if nDecimals > 0:
        subsecondsString = ".{:0>"+str(nDecimals)+"d}"
    else:
        subsecondsString = ""
    
    if time < 60:
        seconds = int(time)
        return sign+("{:d}"+subsecondsString).format(seconds, subseconds)
    elif time < 3600:
        seconds = int(time % 60)
        minutes = int(time // 60)
        return sign+("{:d}:{:0>2d}"+subsecondsString).format(minutes, seconds, subseconds)
    else:
        seconds = int(time % 60)
        minutes = int((time / 60) % 60)
        hours = int(time // 3600)
        return sign+("{:d}:{:0>2d}:{:0>2d}"+subsecondsString).format(hours, minutes, seconds, subseconds)
        

def makeAllWhitespaceSpaces(string):
    '''
    Replaces all whitespace in a string with spaces. Multiple spaces are replaced by a single space. 
    '''
    lineString = string.strip()
    lastWasSpace = False
    newLineString = ''
    for j in range(len(lineString)):
        if lineString[j] in ['\t', ' ']:
            if not lastWasSpace:
                newLineString += ' '
                lastWasSpace = True
        else: 
            newLineString += lineString[j]
            lastWasSpace = False
    return newLineString



def createArray(m, n=0):
    '''
    Initialises a list of length m,
    or an m x n nested list.
    '''
    check2D = n>1
    array = []
    for i in range(m):
        if check2D:
            row = []
            for j in range(n):
                row.append(0)
            array.append(row)
        else:
            array.append(0)
    return array


def getCurrentDateStamp():
    '''
    Returns the date and time right now as a string.
    '''
    now = str(datetime.now())
    if ('.' in now) and (len(now) > now.index('.')+3):
        now = now[:now.index('.')+3]
    return now
    
    
def listWithout(l, skipList):
    '''
    Returns the list l, but with all elements from skipList removed.
    '''
    newList = []
    for element in l:
        if not element in skipList:
            newList.append(element)
    return newList


def binaryListtoNumber(bList):
        '''
        Takes a list of 1s and 0s, and returns the integer value of the binary number.
        Not that the binary numbers are in reverse (units on the left)
        '''
        
        value = 0
        power = 0
        for i in range(len(bList)):
            value += bList[i] * (2**power)
            power += 1
        return value


def test():
    testTimes = [0, 0.554654, 5.2546, 25.45869476 , 124.23124, 3599.8888, 3600, 3601, 4854.546546]
    for t in testTimes:
        print(timeToStr(t,2), "    ", t)
        
    print()
    print()
    print(makeAllWhitespaceSpaces('   SIZE         804\t\t\t   532'))
    
    print()
    print()
    a = [1,2,3,4,5]
    print(listWithout(a, [1, 3]))
        

if __name__ == '__main__':
    test()