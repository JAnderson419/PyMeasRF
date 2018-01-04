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
pna.write(":DISPlay:WINDow1:TRACe1:FEED 'myMeas1'")


pna.write(":DISPlay:WINDow2:STATE ON")
pna.write(":CALCulate:PARameter:DEFine:EXT 'MyMeas2', S11")
pna.write(":DISPlay:WINDow2:TRACe2:FEED 'MyMeas2'")

pna.write("SENS1:SWE:MODE SINGle")
pna.write("SENS2:SWE:MODE SINGle")
# #Set the sweeps slow
# pna.write("SENS1:SWE:TIME 2")
# pna.write("SENS2:SWE:TIME 2")

# #Take 10 points of data
# pna.write("SENS1:SWE:POIN 10")
# pna.write("SENS2:SWE:POIN 10")

# #Put both channels in hold mode
# pna.write("SENS1:SWE:MODE HOLD")
# pna.write("SENS2:SWE:MODE HOLD")
