from rsoft_circuit import RSoftCircuit

pl_params = {
    "Num_Cores_Ring": 5,
    "Angular_Sep": "360 / Num_Cores_Ring",
    "Rotate_View": 0,
    "Taper_Length": 55000,
    "Taper_Slope": 14.9,
    "Diameter_MM": 10,
    "Diameter_SM_Clad": 125,
    "Core_Ring_Radius": "Diameter_SM_Clad / (2 * sin(180 / Num_Cores_Ring))",
    "Core_Ring_Diameter": "2 * Core_Ring_Radius",
    "Diameter_Center_Clad": "Core_Ring_Diameter-Diameter_SM_Clad",
    "Capillary_Diameter": "Core_Ring_Diameter+Diameter_SM_Clad",
    "Diameter_SM_Core": 8.2,
    "Index_Capillary": 1.4345,
    "Index_SM1500G80_Clad_1550": 1.44399,
    "Index_SM1500G80_Core_1550": 1.45636,
    "Index_SMF28_Clad_1550": 1.44692,
    "Index_SMF28_Core_1550": 1.45213,
    "Delta_Centre_Clad": "Index_SM1500G80_Clad_1550 - Index_Capillary",
    "Delta_Centre_Core": "Index_SM1500G80_Core_1550 - Index_Capillary",
    "Delta_Clad": "Index_SMF28_Clad_1550 - Index_Capillary",
    "Delta_Core": "Index_SMF28_Core_1550 - Index_Capillary",
}

center_core_segment = {
    "structure": "STRUCT_FIBER",
    "comp_name": "CENTER_CORE",
    "width_taper": "TAPER_LINEAR",
    "height_taper": "TAPER_LINEAR",
    "begin.x": 0,
    "begin.z": 0,
    "begin.height": "Diameter_SM_Core",
    "begin.width": "Diameter_SM_Core",
    "begin.delta": "Delta_Centre_Core",
    "end.x": 0,
    "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=1),
    "end.height": "Diameter_SM_Core / Taper_Slope",
    "end.width": "Diameter_SM_Core / Taper_Slope",
    "end.delta": "Delta_Centre_Core",
}

center_cladding_segment = {
    "structure": "STRUCT_FIBER",
    "comp_name": "CENTER_CLADDING",
    "width_taper": "TAPER_LINEAR",
    "height_taper": "TAPER_LINEAR",
    "begin.x": 0,
    "begin.z": 0,
    "begin.height": "Diameter_Center_Clad",
    "begin.width": "Diameter_Center_Clad",
    "begin.delta": "Delta_Centre_Clad",
    "end.x": 0,
    "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=8),
    "end.height": "Diameter_Center_Clad / Taper_Slope",
    "end.width": "Diameter_Center_Clad / Taper_Slope",
    "end.delta": "Delta_Centre_Clad",
}

core_segment = {
    "structure": "STRUCT_FIBER",
    "comp_name": "_CORE",
    "width_taper": "TAPER_LINEAR",
    "height_taper": "TAPER_LINEAR",
    "position_y_taper": "TAPER_LINEAR",
    "position_taper": "TAPER_LINEAR",
    "begin.x": 0,
    "begin.y": 0,
    "begin.z": 0,
    "begin.height": "Diameter_SM_Core",
    "begin.width": "Diameter_SM_Core",
    "begin.delta": "Delta_Core",
    "end.x": 0,
    "end.y": 0,
    "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=1),
    "end.height": "Diameter_SM_Core / Taper_Slope",
    "end.width": "Diameter_SM_Core / Taper_Slope",
    "end.delta": "Delta_Core",
}

cladding_segment = {
    "structure": "STRUCT_FIBER",
    "comp_name": "_CLADDING",
    "width_taper": "TAPER_LINEAR",
    "height_taper": "TAPER_LINEAR",
    "position_y_taper": "TAPER_LINEAR",
    "position_taper": "TAPER_LINEAR",
    "begin.x": 0,
    "begin.y": 0,
    "begin.z": 0,
    "begin.height": "Diameter_SM_Clad",
    "begin.width": "Diameter_SM_Clad",
    "begin.delta": "Delta_Clad",
    "end.x": 0,
    "end.y": 0,
    "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=1),
    "end.height": "Diameter_SM_Clad / Taper_Slope",
    "end.width": "Diameter_SM_Clad / Taper_Slope",
    "end.delta": "Delta_Clad",
}

capillary_segment = {
    "structure": "STRUCT_FIBER",
    "comp_name": "CAPILLARY",
    "width_taper": "TAPER_LINEAR",
    "height_taper": "TAPER_LINEAR",
    "begin.x": 0,
    "begin.z": 0,
    "begin.height": "Capillary_Diameter",
    "begin.width": "Capillary_Diameter",
    "begin.delta": 0,
    "end.x": 0,
    "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=7),
    "end.height": "Capillary_Diameter / Taper_Slope",
    "end.width": "Capillary_Diameter / Taper_Slope",
    "end.delta": 0,
}

"""Define photonic lantern here"""
six_core_PL = RSoftCircuit(
    pl_params,
    eim=0,
    background_index="Index_Capillary",
    cad_aspectratio_x=500,
    cad_aspectratio_y=500,
)

"""Adding cores to simulation"""
# Add center core
six_core_PL.add_segment(**center_core_segment)

# Add 5 surrounding cores
for i in range(5):
    core_segment.update(
        **{
            "comp_name": f"{i}_CORE",
            "begin.x": f"Core_Ring_Radius*cos({i}*Angular_Sep+Rotate_View)",
            "begin.y": f"Core_Ring_Radius*sin({i}*Angular_Sep+Rotate_View)",
            "end.x": f"Core_Ring_Radius*cos({i}*Angular_Sep+Rotate_View)/Taper_Slope",
            "end.y": f"Core_Ring_Radius*sin({i}*Angular_Sep+Rotate_View)/Taper_Slope",
            "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=i + 2),
        }
    )
    six_core_PL.add_segment(**core_segment)


"""Adding a material-less core that encompass all"""
six_core_PL.add_segment(**capillary_segment)

"""Adding Cladding to simulation"""
# Add center cladding
six_core_PL.add_segment(**center_cladding_segment)

# Add 5 surrounding cladding
for j in range(5):
    cladding_segment.update(
        **{
            "comp_name": f"{j}_CLADDING",
            "begin.x": f"Core_Ring_Radius*cos({j}*Angular_Sep+Rotate_View)",
            "begin.y": f"Core_Ring_Radius*sin({j}*Angular_Sep+Rotate_View)",
            "end.x": f"Core_Ring_Radius*cos({j}*Angular_Sep+Rotate_View)/Taper_Slope",
            "end.y": f"Core_Ring_Radius*sin({j}*Angular_Sep+Rotate_View)/Taper_Slope",
            "end.z": RSoftCircuit.relative_dist("Taper_Length", segment_id=j + 2 + 7),
        }
    )
    six_core_PL.add_segment(**cladding_segment)

"""Add pathway and pathway monitors"""
for ii in range(1, 8):
    six_core_PL.add_pathways(segment_ids=ii)
    six_core_PL.add_pathways_monitor(pathway_id=ii)

"""Add launch field"""
port_num = 2
six_core_PL.add_launch_field(
    launch_pathway=7,
    launch_type="LAUNCH_GAUSSIAN",
    launch_width="Diameter_SM_Core",
    launch_height="Diameter_SM_Core",
    launch_position=f"Core_Ring_Radius*cos({port_num}*Angular_Sep+Rotate_View)",
    launch_position_y=f"Core_Ring_Radius*cos({port_num}*Angular_Sep+Rotate_View)",
)

six_core_PL.write("output/six_core_PL.ind")
