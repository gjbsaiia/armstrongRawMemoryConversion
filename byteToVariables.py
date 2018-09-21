#!/usr/bin/python

# Griffin Saiia, Armstrong flash dump reader

# mogrify -format jpg *.bmp
# command to convert .bmp images to .jpg

import os
import sys

# starts in flash memory at 0x003000
# strips memory dump log into variables
class UI_t:
	def __init__(self):
		self.valid = "" # 1 byte   A
		self.screen = "" # 1 bytes  B
		self.screen_last = "" # 1 bytes  C
		self.butUsed = "" # 1 bytes  D
		self.touchUsed = "" # 1 bytes  E
		self.language = "" # 1 byte  F
		self.volume_amp = "" # 1 byte  G
		self.volume_chirp = "" # 1 byte  H
		self.volume_alarm = "" # 1 byte  I
		self.brightness = "" # 1 byte  J
		self.demoMode = "" # 1 byte  K
		self.sideBar = sideBar() # 9 bytes  L
		self.popUp = popUp() # 6 bytes  M
		self.pageTimer0 = "" # 4 bytes  N
		self.pageTimer1 = "" # 4 bytes  O
		self.pageTimerMain = "" # 4 bytes  P
		self.screenLockTimer = "" # 4 bytes  Q
		self.noReturnTimer = "" # 4 bytes R
		self.flowOverride = "" # 1 byte S
		self.flowRate = "" # 2 bytes  T
		self.flow = slidert() # 26 bytes  U
		self.o2 = slidert() # 26 bytes  V
		self.pmax = slidert() # 26 bytes  W
		self.pmin = slidert() # 26 bytes  X
		self.apnoea = slidert() # 26 bytes  Y
		self.breathingFreq = slidert() # 26 bytes Z
		self.nebuliser = "" # 1 bytes  AA
		self.selectMode = "" # 1 byte  BB
class sideBar:
	def __init__(self):
		self.endis = "" # 1 byte En
		self.but1 = "" # 1 byte B1
		self.but2 = "" # 1 byte B2
		self.but3 = "" # 1 byte B3
		self.timer_n = "" # 4 bytes Tn
		self.startStop = "" # 1 bytes SS
class popUp:
	def __init__(self):
		self.type = "" # 1 byte Ty
		self.back = "" # 1 byte Ba
		self.next = "" # 1 byte Nx
		self.timeout = "" # 4 bytes TO
class slidert:
	def __init__(self):
		self.endMin = "" # 2 bytes Em
		self.endMax = "" # 2 bytes EM
		self.limitMin = "" # 2 bytes lm
		self.limitMax = "" # 2 bytes lM
		self.pixM = "" # 4 bytes pM
		self.endMinPix = "" # 2 bytes emP
		self.endMaxPix = "" # 2 bytes eMP
		self.limitMinPix = "" # 2 bytes lmP
		self.limitMaxPix = "" # 2 bytes lMP
		self.val = "" # 2 bytes va
		self.val_last = "" # 2 bytes vaL
		self.valLastPix = "" # 2 bytes

UI_struct = UI_t()

def main():
	print("-------------------------------------------------")
	print("flash dump byte array converter")
	print("-------------------------------------------------")
	while(1):
		try:
			logPath = raw_input("Enter log file name: ")
			print("-------------------------------------------------")
			data = getContents(logPath)
			break
		except IOError:
			print("couldn't find file. please try again.")
			print("-------------------------------------------------")
	extractData(data)
	command = raw_input("convert from hex to decimal? (y/n) ")
	if(command == "y"):
		convertFromHex()
	command = raw_input("print to text file? (y/n) ")
	if(command == "y"):
		splitted = logPath.split(".")
		convertLog = splitted[0]+"Converted.txt"
	else:
		convertLog = ""
	printConverted(convertLog)


# dictionary that indexs each struct with byte size, value, and description
dic = {1 : [1, UI_struct.valid, "valid"],
	2 : [1, UI_struct.screen, "current screen"],
	3 : [1, UI_struct.screen_last, "last screen"],
	4 : [1,	UI_struct.butUsed, "button used"],
	5 : [1, UI_struct.touchUsed, "touch used"],
	6 : [1, UI_struct.language, "language"],
	7 : [1, UI_struct.volume_amp, "volume amps"],
	8 : [1, UI_struct.volume_chirp, "volume chirp"],
	9 : [1, UI_struct.volume_alarm, "volume alarm"],
	10 : [1, UI_struct.brightness, "brightness"],
	11 : [1, UI_struct.demoMode, "demo mode"],
	# if UI_struct contains 4th element containing specifier
	12 : [9, UI_struct.sideBar, "Sidebar Struct", "STRUCT"],
	# uses byte count of struct as loop limit, decrement with each element
	19 : [7, UI_struct.popUp, "pop up struct", "STRUCT"],
	24 : [4, UI_struct.pageTimer0, "page timer 0"],
	25 : [4, UI_struct.pageTimer1, "page timer 1"],
	26 : [4, UI_struct.pageTimerMain, "page timer main return"],
	27 : [4, UI_struct.screenLockTimer, "screen lock timer"],
	28 : [4, UI_struct.noReturnTimer, "no return timer"],
	29 : [1, UI_struct.flowOverride, "flow override"],
	30 : [2, UI_struct.flowRate, "flow rate"],
	31 : [26, UI_struct.flow, "flow slider struct", "STRUCT"],
	44: [26, UI_struct.o2, "o2 slider struct", "STRUCT"],
	57 : [26, UI_struct.pmax, "p max slider struct", "STRUCT"],
	70 : [26, UI_struct.pmin, "p min slider struct", "STRUCT"],
	83 : [26, UI_struct.apnoea, "apnoea slider struct", "STRUCT"],
	96 : [26, UI_struct.breathingFreq, "breathing frequency slider struct", "STRUCT"],
	109 : [1, UI_struct.nebuliser,  "nebuliser"],
	110 : [1, UI_struct.selectMode,  "selected mode"]}

sidebarDic = {13 : [1, UI_struct.sideBar.endis, "end is"],
	14 : [1, UI_struct.sideBar.but1, "button 1"],
	15 : [1, UI_struct.sideBar.but2, "button 2"],
	16 : [1, UI_struct.sideBar.but3, "button 3"],
	17 : [4, UI_struct.sideBar.timer_n, "sidebar timer"],
	18 : [1, UI_struct.sideBar.startStop, "mode (start/stop)"]}

popupDic = {20 : [1, UI_struct.popUp.type, "pop up type"],
	21 : [1, UI_struct.popUp.back, "prev page"],
	22 : [1, UI_struct.popUp.next, "next page"],
	23 : [4, UI_struct.popUp.timeout, "pop up timeout"]}

sliderDic = { 32 : [2, UI_struct.flow.endMin, "left end of bar"],
	33 : [2, UI_struct.flow.endMax, "right end of bar"],
	34 : [2, UI_struct.flow.limitMin, "minimum limit"],
	35 : [2, UI_struct.flow.limitMax, "maximum limit"],
	36 : [4, UI_struct.flow.pixM, "converted from decimal to pixels"],
	37 : [2, UI_struct.flow.endMinPix, "pixels at left end of bar"],
	38 : [2, UI_struct.flow.endMaxPix, "pixels at right end of bar"],
	39 : [2, UI_struct.flow.limitMinPix, "pixel minimum limit"],
	40 : [2, UI_struct.flow.limitMaxPix, "pixel maximum limit"],
	41 : [2, UI_struct.flow.val, "current pointer value"],
	42 : [2, UI_struct.flow.val_last, "current displayed value"],
	43 : [2, UI_struct.flow.valLastPix, "pixels of displayed value"],
	#
	45 : [2, UI_struct.o2.endMin, "left end of bar"],
	46 : [2, UI_struct.o2.endMax, "right end of bar"],
	47 : [2, UI_struct.o2.limitMin, "minimum limit"],
	48 : [2, UI_struct.o2.limitMax, "maximum limit"],
	49 : [4, UI_struct.o2.pixM, "converted from decimal to pixels"],
	50 : [2, UI_struct.o2.endMinPix, "pixels at left end of bar"],
	51 : [2, UI_struct.o2.endMaxPix, "pixels at right end of bar"],
	52 : [2, UI_struct.o2.limitMinPix, "pixel minimum limit"],
	53 : [2, UI_struct.o2.limitMaxPix, "pixel maximum limit"],
	54 : [2, UI_struct.o2.val, "current pointer value"],
	55 : [2, UI_struct.o2.val_last, "current displayed value"],
	56 : [2, UI_struct.o2.valLastPix, "pixels of displayed value"],
	#
	58 : [2, UI_struct.pmax.endMin, "left end of bar"],
	59 : [2, UI_struct.pmax.endMax, "right end of bar"],
	60 : [2, UI_struct.pmax.limitMin, "minimum limit"],
	61 : [2, UI_struct.pmax.limitMax, "maximum limit"],
	62 : [4, UI_struct.pmax.pixM, "converted from decimal to pixels"],
	63 : [2, UI_struct.pmax.endMinPix, "pixels at left end of bar"],
	64 : [2, UI_struct.pmax.endMaxPix, "pixels at right end of bar"],
	65 : [2, UI_struct.pmax.limitMinPix, "pixel minimum limit"],
	66 : [2, UI_struct.pmax.limitMaxPix, "pixel maximum limit"],
	67 : [2, UI_struct.pmax.val, "current pointer value"],
	68 : [2, UI_struct.pmax.val_last, "current displayed value"],
	69 : [2, UI_struct.pmax.valLastPix, "pixels of displayed value"],
	#
	71 : [2, UI_struct.pmin.endMin, "left end of bar"],
	72 : [2, UI_struct.pmin.endMax, "right end of bar"],
	73 : [2, UI_struct.pmin.limitMin, "minimum limit"],
	74 : [2, UI_struct.pmin.limitMax, "maximum limit"],
	75 : [4, UI_struct.pmin.pixM, "converted from decimal to pixels"],
	76 : [2, UI_struct.pmin.endMinPix, "pixels at left end of bar"],
	77 : [2, UI_struct.pmin.endMaxPix, "pixels at right end of bar"],
	78 : [2, UI_struct.pmin.limitMinPix, "pixel minimum limit"],
	79 : [2, UI_struct.pmin.limitMaxPix, "pixel maximum limit"],
	80 : [2, UI_struct.pmin.val, "current pointer value"],
	81 : [2, UI_struct.pmin.val_last, "current displayed value"],
	82 : [2, UI_struct.pmin.valLastPix, "pixels of displayed value"],
	#
	84 : [2, UI_struct.apnoea.endMin, "left end of bar"],
	85 : [2, UI_struct.apnoea.endMax, "right end of bar"],
	86 : [2, UI_struct.apnoea.limitMin, "minimum limit"],
	87 : [2, UI_struct.apnoea.limitMax, "maximum limit"],
	88 : [4, UI_struct.apnoea.pixM, "converted from decimal to pixels"],
	89 : [2, UI_struct.apnoea.endMinPix, "pixels at left end of bar"],
	90 : [2, UI_struct.apnoea.endMaxPix, "pixels at right end of bar"],
	91 : [2, UI_struct.apnoea.limitMinPix, "pixel minimum limit"],
	92 : [2, UI_struct.apnoea.limitMaxPix, "pixel maximum limit"],
	93 : [2, UI_struct.apnoea.val, "current pointer value"],
	94 : [2, UI_struct.apnoea.val_last, "current displayed value"],
	95 : [2, UI_struct.apnoea.valLastPix, "pixels of displayed value"],
	#
	97 : [2, UI_struct.breathingFreq.endMin, "left end of bar"],
	98 : [2, UI_struct.breathingFreq.endMax, "right end of bar"],
	99 : [2, UI_struct.breathingFreq.limitMin, "minimum limit"],
	100 : [2, UI_struct.breathingFreq.limitMax, "maximum limit"],
	101 : [4, UI_struct.breathingFreq.pixM, "converted from decimal to pixels"],
	102 : [2, UI_struct.breathingFreq.endMinPix, "pixels at left end of bar"],
	103 : [2, UI_struct.breathingFreq.endMaxPix, "pixels at right end of bar"],
	104 : [2, UI_struct.breathingFreq.limitMinPix, "pixel minimum limit"],
	105 : [2, UI_struct.breathingFreq.limitMaxPix, "pixel maximum limit"],
	106 : [2, UI_struct.breathingFreq.val, "current pointer value"],
	107 : [2, UI_struct.breathingFreq.val_last, "current displayed value"],
	108 : [2, UI_struct.breathingFreq.valLastPix, "pixels of displayed value"]}

# loads entries into array
def getContents(path):
	lines = []
	data = []
	with open(path) as entries:
		lines = entries.readlines()
		entries.close()
	for line in lines:
		entry = processLine(line)
		if(entry != []):
			data += entry
	return data

# process a line from the .txt file to a byte array
def processLine(line):
	try:
	 	splitted = line.split("   ")
		splitted2 = splitted[2].split("\n")
		byteLine = splitted2[0].split(" ")
		justBytes = []
		for each in byteLine:
			if(not isSpace(each)):
				justBytes.append(each)
		return justBytes
	except IndexError:
		return []

# breaks byte array into variables
def extractData(data):
	i = 1
	byteCount = 0
	struct = 0
	while( i < 111 ):
		if(i == 30):
			byteCount += 1
		flag = True
		limit = byteCount + (dic[i])[0]
		if(len(dic[i]) > 3):
			flag = False
			returned = extractStructData(data, i+1, dic[i][0], byteCount, struct)
			i = returned[0]
			byteCount = returned[1]
			struct += 1
		else:
			if(i < 110):
				next = dic[i + 1]
		if(len(dic[i]) == 3 and flag):
			test = ""
			while( byteCount < limit ):
				dic[i][1] += data[byteCount]
				test += data[byteCount]
				byteCount += 1
			i += 1
		if(len(next) > 3):
			if(struct == 0):
				byteCount += 1
			if(struct == 1):
				byteCount += 3
			if(struct > 2):
				byteCount += 2

def extractStructData(data, i, limit, byteCount, id):
	if(id == 0):
		while(limit > 0):
			limit -= sidebarDic[i][0]
			size = byteCount + sidebarDic[i][0]
			if(len(sidebarDic[i]) > 3):
				i += 1
				newId = id + 1
				returned = extractStructData(data, i, sidebarDic[i][0], byteCount, newId)
				i = returned[0]
				byteCount = returned[1]
			else:
				while( byteCount < size ):
					sidebarDic[i][1] += data[byteCount]
					byteCount += 1
				i += 1
		return [i, byteCount]
	if(id == 1):
		j = 0
		while(limit > 0):
			limit -= popupDic[i][0]
			size = byteCount + popupDic[i][0]
			if(len(popupDic[i]) > 3):
				i += 1
				newId = id + 1
				returned = extractStructData(data, i, popupDic[i][0], byteCount, newId)
				i = returned[0]
				byteCount = returned[1]
			else:
				while( byteCount < size ):
					popupDic[i][1] += data[byteCount]
					byteCount += 1
				i += 1
			if(j == 2):
				limit -= 1
				byteCount += 1
			j += 1
		return [i, byteCount]
	if(id > 1):
		while(limit > 0):
			limit -= sliderDic[i][0]
			size = byteCount + sliderDic[i][0]
			if(len(sliderDic[i]) > 3):
				i += 1
				newId = id + 1
				returned = extractStructData(data, i, sliderDic[i][0], byteCount, newId)
				i = returned[0]
				byteCount = returned[1]
			else:
				while( byteCount < size ):
					sliderDic[i][1] += data[byteCount]
					byteCount += 1
				i += 1
		return [i, byteCount]

def convertFromHex():
	i = 1
	struct = 0
	while( i < 111 ):
		if(len(dic[i]) > 3):
			i = convertStructData(i+1, dic[i][0], struct)
			struct += 1
		else:
			dic[i][1] = int(dic[i][1], 16)
			i += 1

def convertStructData(i, limit, id):
	if(id == 0):
		while(limit > 0):
			limit -= sidebarDic[i][0]
			sidebarDic[i][1] = int(sidebarDic[i][1], 16)
			i += 1
		return i
	if(id == 1):
		while(limit > 0):
			limit -= popupDic[i][0]
			popupDic[i][1] = int(popupDic[i][1], 16)
			i += 1
		return i
	if(id > 1):
		while(limit > 0):
			limit -= sliderDic[i][0]
			sliderDic[i][1] = int(sliderDic[i][1], 16)
			i += 1
		return i

# function to print out UI_t struct
def printConverted(convertLog):
	print("------------------------------------------------------------")
	print("Flash Dump:UI_t")
	print("------------------------------------------------------------")
	flag = False
	if(convertLog != ""):
		name = ""
		splitted = convertLog.split("/")
		if(len(splitted) < 2):
			splitted2 = convertLog.split(".")
			name = splitted2[0]
		else:
			splitted2 = splitted[len(splitted)-1].split(".")
			name = splitted2[0]
		with open(convertLog, "w+") as file:
			file.write("------------------------------------------------------------\n")
			file.write("Flash Dump: UI_t ---> "+name+"\n")
			file.write("------------------------------------------------------------\n")
		file.close()
		flag = True
	else:
		flag = False
	i = 1
	struct = 0
	while( i < 111 ):
		attrib = dic[i]
		if( len(attrib) > 3 ):
			print("")
			print(attrib[2]+":")
			if(flag):
				with open(convertLog, "a+") as file:
					file.write("\n")
					file.write(attrib[2]+":"+"\n")
				file.close()
			i += 1
			i = printStruct(attrib[1], i, attrib[0], struct, convertLog, flag)
			struct += 1
			print""
			if(flag):
				with open(convertLog, "a+") as file:
					file.write("\n")
				file.close()
		else:
			print(attrib[2]+": "+str(attrib[1]))
			if(flag):
				with open(convertLog, "a+") as file:
					file.write(attrib[2]+": "+str(attrib[1])+"\n")
				file.close()
			i += 1

# helper function to print elements in sub structs
def printStruct(struct, i, limit, id, convertLog, flag):
	data = []
	if(id == 0):
		while(limit > 0):
			data = sidebarDic[i]
			if( len(data) > 3 ):
				print(data[2]+":")
				i += 1
				i = printStruct(data[1], i, data[0])
			else:
				print("   "+data[2]+": "+str(data[1]))
				if(flag):
					with open(convertLog, "a+") as file:
						file.write("   "+data[2]+": "+str(data[1])+"\n")
					file.close()
				limit -= data[0]
				i += 1
		return i
	if(id == 1):
		j = 0
		while(limit > 0):
			data = popupDic[i]
			if( len(data) > 3 ):
				print(data[2]+":")
				i += 1
				i = printStruct(data[1], i, data[0])
			else:
				print("   "+data[2]+": "+str(data[1]))
				if(flag):
					with open(convertLog, "a+") as file:
						file.write("   "+data[2]+": "+str(data[1])+"\n")
					file.close()
				limit -= data[0]
				i += 1
			if(id == 1 and j == 2):
				limit -= 1
			j += 1
		return i
	if(id > 1):
		while(limit > 0):
			data = sliderDic[i]
			if( len(data) > 3 ):
				print(data[2]+":")
				i += 1
				i = printStruct(data[1], i, data[0])
			else:
				print("   "+data[2]+": "+str(data[1]))
				if(flag):
					with open(convertLog, "a+") as file:
						file.write("   "+data[2]+": "+str(data[1])+"\n")
					file.close()
				limit -= data[0]
				i += 1
		return i


#simple little function to check if string is number
def isSpace(value):
    try:
		if(value == ""):
			return True
		else:
			return False
    except ValueError:
        return False

# to run it from command line
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("")
		print('Interrupted')
        try:
			sys.exit(0)
	except SystemExit:
			os._exit(0)
