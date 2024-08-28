'''
Copyright © 2024 Merck & Co., Inc., Rahway, NJ, USA and its affiliates. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''



'''
This script intends to run a Bradford assay standard curve on Opentrons OT2.
Note that this script only runs a reference standard as of now.

Volumes of reagents needed:
1.5mL of Reference Standard Stock on tube rack A1;
1mL of SSS on tube rack A2
13mL of Bradford assay reagent
'''

#importing the API
from opentrons import protocol_api
import numpy as np

metadata = {'apiLevel': '2.12'}

def run(protocol: protocol_api.ProtocolContext):

    tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap',1) #Tube rack that holds the reference standard and the SSS goes on deck position #1
    final_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 3) #Final plate (the plate to be read) goes on deck position #3
    diluent = protocol.load_labware('axygen_1_reservoir_90ml', 4)  #Diluent reservoir goes on deck position #4
    pierce_reagent = protocol.load_labware('axygen_1_reservoir_90ml', 5) #Bradford reagent reservoir goes on deck position #5
    stamping_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', 6) #Stamping plate (as defined in the manuscript) goes on deck position #6
 
    tiprack_1_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 7) #four 300uL tip racks go on deck positions #7, 8, 9 and 10
    tiprack_2_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)  
    tiprack_3_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    tiprack_4_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)

    p300 = protocol.load_instrument('p300_single_gen2', 'right',tip_racks=[tiprack_1_300, tiprack_2_300])  #Using only the 300uL pipette (single pipette on the right, multichannel pipette on the left)
    p300_multi = protocol.load_instrument('p300_multi_gen2', 'left',tip_racks=[tiprack_3_300, tiprack_4_300])

#Step 1: Adding 500ul diluent to all wells in column 1-4 to the stamping plate
    p300_multi.pick_up_tip()
    for i in range(4):
        p300_multi.transfer(volume=250, source = diluent['A1'], dest = stamping_plate.columns()[i], new_tip='never',trash = False)
    for i in range(4):
        p300_multi.transfer(volume=250, source = diluent['A1'], dest = stamping_plate.columns()[i], new_tip='never',trash = False)
    p300_multi.return_tip()

# Step 2: Preparing 3 replicates of the 75, 100, 150 and 200ug/mL standard points in the stamping plate
    #75ug/mL: (E1-3), 100ug/mL: (F1-3); 150ug/mL (G1-3); 200ug/mL (H1-3) mcg/ml points to the stamping plate 

#   Total volume of diluent needed is 740,720,680, and 960 respectuively. However, due to the max capacity of the tips being 300uL, we break up the addition of the diluent in 3 different stages with volumes <300uL as in the array dil_vol1_b
    dil_vol1_b = [240,220,180,250] #we are doing this due to the maximum capacity of the tips being 300uL
#   remaining volume for wells H1, H2 and H3 is 210uL to reach 960uL total diluent

    dest_1 = ['E1','F1','G1','H1'] #well locations for 75-200 ug/mL standard points are in the arrats dest_1, dest_2 and dest_3
    dest_2 = ['E2','F2','G2','H2']
    dest_3 = ['E3','F3','G3','H3']
    dest1 =[dest_1,dest_2,dest_3] #triplicating the destination since we are adding the standard in triplicate

    samp_vol1=[60,80,120,240] #standard volume needed (these ratios make up the dilutions rangning from 75 to 200 mcg/mL)

    #replicating in 3
    for j in range (3):
        p300.pick_up_tip()      
        #dispensing diluent to stamping plate
        for i in range(len(dil_vol1_b)):
            p300.transfer(volume = dil_vol1_b[i], source = diluent['A1'], dest = stamping_plate[dest1[j][i]], new_tip = 'never',trash = False) 
        #dispensing that remaining 210uL of diluent described in line 64 to the wells H1, H2 and H3 to reach a total of 960uL
        p300.transfer(volume = 210, source = diluent['A1'], dest = stamping_plate[dest1[j][3]], new_tip = 'never',trash = False)
        p300.return_tip()

        #dispensing standard to stamping plate
        for i in range(3): 
            p300.transfer(volume = samp_vol1[i], source = tube_rack['B1'], dest = stamping_plate[dest1[j][i]], new_tip = 'always',trash = False, mix_after=(3,200)) 
        p300.transfer(volume = samp_vol1[3], source = tube_rack['B2'], dest = stamping_plate[dest1[j][3]], new_tip = 'always',trash = False, mix_after=(3,200)) 


# Step 3: adding 3 replicates of diluent and standard control to 0(A1-3), 15(B1-3), 25(C1-3) and 50(D1-3) mcg/ml points to the stamping plate
#   Total volume of diluent needed is 300, 240, 200 and 100 uL,respectuively as shown in the array dil_vol2_b
    
    dil_vol2_b = [300 , 240 , 200 , 100]
    
    dest_4 = ['A1','B1','C1','D1'] #well locations for 0-50 ug/mL standard points are in the arrays dest_4, dest_4 and dest_6
    dest_5 = ['A2','B2','C2','D2']
    dest_6 = ['A3','B3','C3','D3']
    
    dest2 =[dest_4,dest_5,dest_6] #triplicating the destination since we are adding the standard in triplicate
    
    samp_vol2 = [60,100,200] #reference standard volume needed to make up the  0-50 ug/mL reference points

    Hdest = ['H1','H2','H3'] #taking from the reference prepared in  wells H1, H2 and H3 to prepare the 0-50ug/mL dilutions 

        #replicating in 3
    for j in range (3): 
    #dispensing diluent
        p300.pick_up_tip()      
        for i in range(len(dil_vol2_b)):
            p300.transfer(volume = dil_vol2_b[i], source = diluent['A1'], dest = stamping_plate[dest2[j][i]], new_tip = 'never',trash = False)
        p300.return_tip()

    #dispensing standard control from 200mcg/ml
        for i in range(len(samp_vol2)):
            p300.transfer(volume = samp_vol2[i], source = stamping_plate[Hdest[j]], dest = stamping_plate[dest2[j][i+1]], new_tip = 'always',trash = False, mix_after=(3,200))


# Step 4: adding 280 uL of SSS to wells  A4, B4 and C4 in stamping plate
    ctrl_vol = 280
    ctrl_dest = ['A4','B4','C4']
    for i in range(len(ctrl_dest)):
        p300.transfer(volume = ctrl_vol, source = tube_rack['A1'], dest = stamping_plate[ctrl_dest[i]],new_tip = 'always',trash = False)

# Step 5: incubate for 30 minutes in diluent
    protocol.delay(minutes=30)

#Step 6: adding 25uL of sample to 225uL reagent in final plate
    p300_multi.pick_up_tip()
    for i in range(12):
        p300_multi.transfer(volume=225, source = pierce_reagent['A1'], dest = final_plate.columns()[i], new_tip='never',trash = False)
    p300_multi.return_tip()

    
    for i in range(12):
        p300_multi.transfer(volume=25, source = stamping_plate.columns()[i], dest = final_plate.columns()[i], new_tip='always',trash = False, mix_after=(3,200))

#Step 7: incubating in Pierce reagent for 5 minutes
    protocol.delay(minutes = 5)

# Now you have successfully prepared the layout of the plate with the appropriate dilutions, setup and reagents/sample ratios. Move to a plate reader.
