#BasicPNACOMMS.py
#The purpose of this file is to demonstrate basic PNA functionality

import visa
import time
rm = visa.ResourceManager()
try:
    pna = rm.open_resource('TCPIP0::192.168.1.1::inst0::INSTR')
except visa.VisaIOError as e:
    print(e.args)
    exit
#pna.write(":SYST:FPReset")
#This turns on the display for window 2 and 
pna.write(":CALC:PAR:DEL 'MyMeas1'")
pna.write(":CALC:PAR:DEL 'MyMeas2'")
pna.write(":DISPlay:WINDow1:STATE ON")
pna.write(":DISPlay:WINDow2:STATE ON")
pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas1', S11")
pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas2', S22")
#pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas3', S21")
#pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas4', S22")


pna.write(":DISPlay:WINDow1:TRACe1:FEED 'MyMeas1'")
pna.write(":DISPlay:WINDow2:TRACe1:FEED 'MyMeas2'")
#pna.write(":DISPlay:WINDow1:TRACe2:FEED 'myMeas2'")
#pna.write(":DISPlay:WINDow1:TRACe3:FEED 'myMeas3'")
#pna.write(":DISPlay:WINDow1:TRACe4:FEED 'myMeas4'")
print('Beginning Kessel Run')
pna.timeout = 450000
pna.write("SENS1:SWE:MODE SINGle")
pna.query("*OPC?")
pna.timeout = 2000
#time.sleep(10)
#print("Finished in 4.2 Parsecs")

pna.write("CALCulate1:PARameter:SELect 'MyMeas1'")
pna.write("CALC:DATA:SNP:PORTs:Save '1,2', 'C:\\Documents\\pyvisa\\MyData.s2p'")



# #Set the sweeps slow
#pna.write("SENS1:SWE:TIME 2")

# #Take 10 points of data
#pna.write("SENS1:SWE:POIN 10")

# #Put both channels in hold mode
#pna.write("SENS1:SWE:MODE HOLD")

