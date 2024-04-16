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



# This script intends to run a Bradford assay standard curve on Opentrons OT2.
# Note that this script only runs a reference standard as of now. Additional edits required for sample manipulation.
# Standard stock in B1 and B2 of tube_rack. SSS in A1 of tube_rack.
# This run takes 1 hr

#changing the script to stamp dye onto the entire final plate then the stamping plate onto the entire final plate

from opentrons import protocol_api
import numpy as np

metadata = {'apiLevel': '2.12'}

def run(protocol: protocol_api.ProtocolContext):

    tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap',1)
    final_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 3)
    diluent = protocol.load_labware('axygen_1_reservoir_90ml', 4)
    pierce_reagent = protocol.load_labware('axygen_1_reservoir_90ml', 5)
    stamping_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', 6)

    tiprack_1_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_2_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)  
    tiprack_3_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 9)
    tiprack_4_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 10)

    p300 = protocol.load_instrument('p300_single_gen2', 'right',tip_racks=[tiprack_1_300, tiprack_2_300])
    p300_multi = protocol.load_instrument('p300_multi_gen2', 'left',tip_racks=[tiprack_3_300, tiprack_4_300])

#add 500ul diluent to all wells in column 1-4
    p300_multi.pick_up_tip()
    for i in range(4):
        p300_multi.transfer(volume=250, source = diluent['A1'], dest = stamping_plate.columns()[i], new_tip='never',trash = False)
    for i in range(4):
        p300_multi.transfer(volume=250, source = diluent['A1'], dest = stamping_plate.columns()[i], new_tip='never',trash = False)
    p300_multi.return_tip()

# Step 1: adding 3 replicates of diluent and standard control to 75 (E1-3) 100 (F1-3) 150 (G1-3) and 200 (H1-3) mcg/ml points to the stamping plate 

#   dil_vol1 = [740,720,680,960] #diluent volume
    dil_vol1_b = [240,220,180,250] #we are doing this due to the maximum capacity of the tips being 300uL
#   dil_vol1_c = 210

    dest_1 = ['E1','F1','G1','H1']
    dest_2 = ['E2','F2','G2','H2']
    dest_3 = ['E3','F3','G3','H3']
    dest1 =[dest_1,dest_2,dest_3]

    samp_vol1=[60,80,120,240] #standard volume (these ratios make up the dilutions rangning from 75 to 200 mcg/mL)

    #replicating in 3
    for j in range (3):
        p300.pick_up_tip()      
        #dispensing diluent to stamping plate
        for i in range(len(dil_vol1_b)):
            p300.transfer(volume = dil_vol1_b[i], source = diluent['A1'], dest = stamping_plate[dest1[j][i]], new_tip = 'never',trash = False)

        p300.transfer(volume = 210, source = diluent['A1'], dest = stamping_plate[dest1[j][3]], new_tip = 'never',trash = False)
        p300.return_tip()

        #dispensing standard to stamping plate
        for i in range(3):
            p300.transfer(volume = samp_vol1[i], source = tube_rack['B1'], dest = stamping_plate[dest1[j][i]], new_tip = 'always',trash = False, mix_after=(3,200)) 
        p300.transfer(volume = samp_vol1[3], source = tube_rack['B2'], dest = stamping_plate[dest1[j][3]], new_tip = 'always',trash = False, mix_after=(3,200)) 


# Step 2: adding 3 replicates of diluent and standard control to 0(A1-3), 15(B1-3), 25(C1-3) and 50(D1-3) mcg/ml points to the stamping plate

#   dil_vol2 = [800,740,700,600] #diluent volume
#   dil_vol2_a = 250
    dil_vol2_b = [300 , 240 , 200 , 100]
    dest_4 = ['A1','B1','C1','D1']
    dest_5 = ['A2','B2','C2','D2']
    dest_6 = ['A3','B3','C3','D3']
    dest2 =[dest_4,dest_5,dest_6]
    samp_vol2 = [60,100,200] #these ratios will make up the dilutions from 0-50

    Hdest = ['H1','H2','H3'] #location of highest concentration of standard to make these smaller dilutions

    for j in range (3): 
    #dispensing diluent
        p300.pick_up_tip()      
        for i in range(len(dil_vol2_b)):
            p300.transfer(volume = dil_vol2_b[i], source = diluent['A1'], dest = stamping_plate[dest2[j][i]], new_tip = 'never',trash = False)
        p300.return_tip()

    #dispensing standard control from 200mcg/ml
        for i in range(len(samp_vol2)):
            p300.transfer(volume = samp_vol2[i], source = stamping_plate[Hdest[j]], dest = stamping_plate[dest2[j][i+1]], new_tip = 'always',trash = False, mix_after=(3,200))


    #adding 280 uL of control to A4 to C4 in stamping plate
    ctrl_vol = 280
    ctrl_dest = ['A4','B4','C4']
    for i in range(len(ctrl_dest)):
        p300.transfer(volume = ctrl_vol, source = tube_rack['A1'], dest = stamping_plate[ctrl_dest[i]],new_tip = 'always',trash = False)

    #incubate for 30 minutes in benozanase (diluent)
    protocol.delay(minutes=30)

#Step 3: adding 25uL of sample to 225uL reagent in final plate
    p300_multi.pick_up_tip()
    for i in range(12):
        p300_multi.transfer(volume=225, source = pierce_reagent['A1'], dest = final_plate.columns()[i], new_tip='never',trash = False)
    p300_multi.return_tip()

    
    for i in range(12):
        p300_multi.transfer(volume=25, source = stamping_plate.columns()[i], dest = final_plate.columns()[i], new_tip='always',trash = False, mix_after=(3,200))

#Step 4: incubating in Pierce reagent for 5 minutes
    protocol.delay(minutes = 5)

# Now you have successfully prepared the layout of the plate with the appropriate dilutions, setup and reagents/sample ratios. Move to a plate reader.