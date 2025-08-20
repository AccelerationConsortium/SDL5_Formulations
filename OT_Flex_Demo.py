from opentrons import protocol_api
from typing import List, Dict

metadata = {
    "protocolName": "Demo OT Flex Protocol",
    "description": "This protocol demonstrates how to run an experiment on the OT Flex",
}

requirements = {"robotType": "Flex", "apiLevel": "2.23"}

def get_mixture_combinations() -> List[Dict[str, float]]:
    mixtures = []
    for i in range(10):
        for j in range(10 - i):
            entry = {'Reagent_A': i * 10, 'Reagent_B': j * 10, 'Reagent_C': 10 * (10 - i - j)}
            print(entry)
            mixtures.append(entry)
    return mixtures

def run(protocol: protocol_api.ProtocolContext):
    protocol.home()
    # Define tips & labwares
    tips_1000_1 = protocol.load_labware("opentrons_flex_96_tiprack_1000ul", "B1")
    tips_1000_2 = protocol.load_labware("opentrons_flex_96_tiprack_1000ul", "C1")
    tips_50_1 = protocol.load_labware("opentrons_flex_96_tiprack_50ul", "B2")
    tips_50_2 = protocol.load_labware("opentrons_flex_96_tiprack_50ul", "C2")
    resevoir = protocol.load_labware('corning_12_wellplate_6.9ml_flat', 'A2')
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 'C3')
    # Define installed pipettes
    left = protocol.load_instrument("flex_1channel_1000", "left", tip_racks=[tips_1000_1, tips_1000_2])
    right =  protocol.load_instrument("flex_1channel_50", "right", tip_racks=[tips_50_1, tips_50_2])
    instruments = [right, left]
    # Define trash bin
    trash = protocol.load_trash_bin("A3")

    # Drop tips
    if left.has_tip:
        left.drop_tip(trash)
    if right.has_tip:
        right.drop_tip(trash)

    # Get list of mixtures to prepare
    mixtures = get_mixture_combinations()

    # Define liquid locations on the deck
    l1 = protocol.define_liquid(name='Reagent_A')
    l2 = protocol.define_liquid(name='Reagent_B')
    l3 = protocol.define_liquid(name='Reagent_C')
    resevoir.load_liquid(wells=[resevoir.wells_by_name()['A1']], volume=6000, liquid=l1)
    resevoir.load_liquid(wells=[resevoir.wells_by_name()['A2']], volume=6000, liquid=l2)
    resevoir.load_liquid(wells=[resevoir.wells_by_name()['A3']], volume=6000, liquid=l3)
    liquid_locations: Dict[str, protocol_api.Well] = {'Reagent_A': resevoir.wells_by_name()['A1'],
                                                      'Reagent_B': resevoir.wells_by_name()['A2'],
                                                      'Reagent_C': resevoir.wells_by_name()['A3'],}

    for i, mixture in enumerate(mixtures):
        protocol.comment(f'{i}, {mixture}')
        dest_well: protocol_api.Well = plate.wells()[i]
        for reagent_name, vol in mixture.items():
            if vol == 0:
                continue
            else:
                if vol <= 50:
                    pipette = instruments[0]
                else:
                    pipette = instruments[1]
                
                source_well = liquid_locations[reagent_name]

                pipette.pick_up_tip()

                pipette.transfer(volume=vol, source=source_well, dest=dest_well, new_tip='never')

                pipette.drop_tip()
                
                # The above 3 lines can be replaced with
                # pipette.transfer(volume=vol, source=source_well, dest=dest_well)


    return

if __name__ == '__main__':
    get_mixture_combinations()