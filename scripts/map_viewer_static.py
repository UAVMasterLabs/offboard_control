#!/usr/bin/env python
from numpy import array

def print_map(data):
	data = array(data).reshape(64,64)
	data[32,32] = 2
	swap = {0:' ',-1:'o',100:'*',2:'R',3:'+'}
	map = ''.join([swap[x] if i%64 else '\n'+swap[x] for i,x in enumerate(data.T.flatten())])
	print map	


with open('none_path.txt','r') as inf:
	data = inf.readlines()[0]

data = [int(x) for x in data.split(',')]

print_map(data)
