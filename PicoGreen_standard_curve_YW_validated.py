'''
Copyright © 2023 Merck & Co., Inc., Rahway, NJ, USA and its affiliates. All rights reserved.

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

# need 700 and 840ul Standard stock and SSS respectively, add in 1200ul in 1.5ml tubes on tube_rack A1 and A2
# need 13ml pg_reagent

from opentrons import protocol_api
import numpy as np

metadata = {'apiLevel': '2.12'}

def run(protocol: protocol_api.ProtocolContext):

    tube_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap',1)
    final_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 3)
    diluent = protocol.load_labware('axygen_1_reservoir_90ml', 4)
    pg_reagent = protocol.load_labware('axygen_1_reservoir_90ml', 5)
    stamping_plate = protocol.load_labware('nest_96_wellplate_2ml_deep', 6)

    tiprack_1_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 7)
    tiprack_2_300 = protocol.load_labware('opentrons_96_tiprack_300ul', 8)  

    p300 = protocol.load_instrument('p300_single_gen2', 'right',tip_racks=[tiprack_1_300])
    p300_multi = protocol.load_instrument('p300_multi_gen2', 'left',tip_racks=[tiprack_2_300])


#step1 add diluent
    volume_1 = [151.67,151.67,220,220]
    dest_1 = ['F1','F3','A2','A4']
    p300.pick_up_tip()
    for i in range(4):
        p300.transfer(volume = volume_1[i], source = diluent['A1'], dest = stamping_plate[dest_1[i]],new_tip = 'never',trash = False)
    p300.return_tip()

#step2 500-50ng/mL standard curve
    volume_2 = [198,210,198.33,175,140,116.67,198,210,198.33,175,140,116.67]
    dest_2 = ['A2','B2','C2','D2','E2','F2','A4','B4','C4','D4','E4','F4']
    p300.pick_up_tip()
    for i in range(12):
        p300.transfer(volume = volume_2[i], source = diluent['A1'], dest = stamping_plate[dest_2[i]],new_tip = 'never',trash = False)
    p300.return_tip()

    volume_3 = [22,23.33,35,58.33,93.33,116.67,22,23.33,35,58.33,93.33,116.67]
    dest_3 = ['A2','B2','C2','D2','E2','F2','A4','B4','C4','D4','E4','F4']
    for i in range(12):
        p300.transfer(volume = volume_3[i], source = tube_rack['A1'], dest = stamping_plate[dest_3[i]],new_tip = 'always',trash = False, mix_after=(3,200))

#step3 25-2.5ng/mL standard curve
    volume_4 = [221.67,121.33,186.67,116.67,221.67,121.33,186.67,116.67]
    dest_4 = ['E1','F1','G1','H1','E3','F3','G3','H3']
    p300.pick_up_tip()
    for i in range(8):
        p300.transfer(volume = volume_4[i], source = diluent['A1'], dest = stamping_plate[dest_4[i]],new_tip = 'never',trash = False)
    p300.return_tip()

    volume_5 = [11.67,30.33,46.67,116.67]
    dest_5 = ['E1','F1','G1','H1']
    for i in range(4):
        p300.transfer(volume = volume_5[i], source = stamping_plate['A2'], dest = stamping_plate[dest_5[i]],new_tip = 'always',trash = False, mix_after=(3,200))

    dest_6 = ['E3','F3','G3','H3']
    for i in range(4):
        p300.transfer(volume = volume_5[i], source = stamping_plate['A4'], dest = stamping_plate[dest_6[i]],new_tip = 'always',trash = False, mix_after=(3,200))


#step4 1.0-0.1ng/mL standard curve
    volume_7 = [233.33,228.67,221.67,186.67,233.33,228.67,221.67,186.67]
    dest_7 = ['A1','B1','C1','D1','A3','B3','C3','D3']
    p300.pick_up_tip()
    for i in range(8):
        p300.transfer(volume = volume_7[i], source = diluent['A1'], dest = stamping_plate[dest_7[i]],new_tip = 'never',trash = False)
    p300.return_tip()

    volume_8 = [4.67,11.67,46.67]
    dest_8 = ['B1','C1','D1']
    for i in range(3):
        p300.transfer(volume = volume_8[i], source = stamping_plate['F1'], dest = stamping_plate[dest_8[i]],new_tip = 'always',trash = False, mix_after=(3,200))

    dest_9 = ['B3','C3','D3']
    for i in range(3):
        p300.transfer(volume = volume_8[i], source = stamping_plate['F3'], dest = stamping_plate[dest_9[i]],new_tip = 'always',trash = False, mix_after=(3,200))

#step5 add SSS
    volume_10 = [250,250,250]
    dest_10 = ['G2','H2','H4']
    for i in range(3):
        p300.transfer(volume = volume_10[i], source = tube_rack['A2'], dest = stamping_plate[dest_10[i]],new_tip = 'always',trash = False, mix_after=(3,200))

#step7 wait for 10min
    protocol.delay(minutes = 10)

#step8 transfer 100ul to final plate
    for i in range(4):
        p300_multi.transfer(volume=100, source = stamping_plate.columns()[i], dest = final_plate.columns()[i], new_tip='always',trash = False, mix_before=(3,200))

#step9 wait for 10min timer to be done

#step10 add 100ul pg reagent to final plate
    for i in range(4):
        p300_multi.transfer(volume=100, source = pg_reagent['A1'], dest = final_plate.columns()[i], new_tip='always',trash = False, mix_before=(3,200))

#This is the end of OT2 operation. Move final plate to Magellan 