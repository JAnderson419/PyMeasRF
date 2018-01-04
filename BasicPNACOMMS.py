#BasicPNACOMMS.py
#The purpose of this file is to demonstrate basic PNA functionality

import visa

try:
    pna = rm.open_resource('TCPIP0::192.168.1.1::inst0::INSTR')
    except visa.VisaIOError as e:
      print(e.args)
      exit
#pna.write(":SYST:FPReset")
#This turns on the display for window 2 and 
pna.write(":DISPlay:WINDow1:STATE ON")
pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas1', S11")
pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas2', S12")
pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas3', S21")
pna.write(":CALCulate1:PARameter:DEFine:EXT 'MyMeas4', S22")
pna.write(":DISPlay:WINDow1:TRACe1:FEED 'myMeas1'")
pna.write(":DISPlay:WINDow1:TRACe2:FEED 'myMeas2'")
pna.write(":DISPlay:WINDow1:TRACe3:FEED 'myMeas3'")
pna.write(":DISPlay:WINDow1:TRACe4:FEED 'myMeas4'")


pna.write("SENS1:SWE:MODE SINGle")

# #Set the sweeps slow
# pna.write("SENS1:SWE:TIME 2")

# #Take 10 points of data
# pna.write("SENS1:SWE:POIN 10")

# #Put both channels in hold mode
# pna.write("SENS1:SWE:MODE HOLD")

