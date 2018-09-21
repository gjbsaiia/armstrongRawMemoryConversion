# armstrongRawMemoryConversion
wrapper I wrote for arm processor memory dump, specific to a set of key variables</br>
takes into account memory packing, and breaks raw memory into variable blocks</br>
then it converts the values from hex to decimal</br>
used for testing at Marturion Ltd.</br>
</br>
## instructions:
    - print how 150 bytes from address 0x003000 into log file through serial port using technical menu</br>
    - this will give you the raw memory that defines struct UI_t</br>
    - label this log file with a name that captures the state of the Armstrong device, this name will be used throughout</br>
    - move byteToVariables.py to the same folder as your log, or include the path when asked for log file name.</br>
    - launch byteToVariables.py with python 2.7 ("python byteToVariables.py" in terminal)</br>
    - decide if you want hex conversion or not</br>
    - decide if you want a different logfile generated</br>
    - view print out in terminal, and/or in your new logfile
    
