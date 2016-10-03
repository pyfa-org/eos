# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================


"""
This file holds IDs of multiple EVE's entities.
"""


from enum import IntEnum, unique


@unique
class Attribute(IntEnum):
    """Attribute ID holder"""
    mass = 4
    hp = 9
    power_output = 11
    low_slots = 12
    med_slots = 13
    hi_slots = 14
    cpu_output = 48
    power = 30
    capacity = 38
    cpu = 50
    charge_rate = 56
    damage_multiplier = 64
    agility = 70
    launcher_slots_left = 101
    turret_slots_left = 102
    kinetic_damage_resonance = 109
    thermal_damage_resonance = 110
    explosive_damage_resonance = 111
    em_damage_resonance = 113
    em_damage = 114
    explosive_damage = 116
    kinetic_damage = 117
    thermal_damage = 118
    charge_size = 128
    volume = 161
    radius = 162
    required_skill_1 = 182
    required_skill_2 = 183
    required_skill_3 = 184
    missile_damage_multiplier = 212
    shield_capacity = 263
    armor_hp = 265
    armor_em_damage_resonance = 267
    armor_explosive_damage_resonance = 268
    armor_kinetic_damage_resonance = 269
    armor_thermal_damage_resonance = 270
    shield_em_damage_resonance = 271
    shield_explosive_damage_resonance = 272
    shield_kinetic_damage_resonance = 273
    shield_thermal_damage_resonance = 274
    required_skill_1_level = 277
    required_skill_2_level = 278
    required_skill_3_level = 279
    skill_level = 280
    drone_capacity = 283
    implantness = 331
    max_active_drones = 352
    charge_group_1 = 604
    charge_group_2 = 605
    charge_group_3 = 606
    charge_group_4 = 609
    charge_group_5 = 610
    module_reactivation_delay = 669
    max_group_active = 763
    crystal_volatility_chance = 783
    crystal_volatility_damage = 784
    crystals_get_damaged = 786
    max_group_online = 978
    boosterness = 1087
    upgrade_capacity = 1132
    rig_slots = 1137
    upgrade_cost = 1153
    drone_bandwidth = 1271
    drone_bandwidth_used = 1272
    required_skill_4 = 1285
    required_skill_4_level = 1286
    required_skill_5_level = 1287
    required_skill_6_level = 1288
    required_skill_5 = 1289
    required_skill_6 = 1290
    can_fit_ship_group_1 = 1298
    can_fit_ship_group_2 = 1299
    can_fit_ship_group_3 = 1300
    can_fit_ship_group_4 = 1301
    can_fit_ship_type_1 = 1302
    can_fit_ship_type_2 = 1303
    can_fit_ship_type_3 = 1304
    can_fit_ship_type_4 = 1305
    subsystem_slot = 1366
    max_subsystems = 1367
    fits_to_shiptype = 1380
    max_group_fitted = 1544
    rig_size = 1547
    allowed_drone_group_1 = 1782
    allowed_drone_group_2 = 1783
    reload_time = 1795
    can_fit_ship_group_5 = 1872
    can_fit_ship_group_6 = 1879
    can_fit_ship_group_7 = 1880
    can_fit_ship_group_8 = 1881


@unique
class Type(IntEnum):
    """Item ID holder"""
    character_static = 1381
    missile_launcher_operation = 3319  # Skill
    capital_ships = 20533  # Skill
    sentry_drone_interfacing = 23594  # Skill


@unique
class Group(IntEnum):
    """Group ID holder"""
    character = 1
    energy_weapon = 53
    projectile_weapon = 55
    hydrid_weapon = 74
    missile_launcher_cruise = 506
    missile_launcher_rocket = 507
    missile_launcher_torpedo = 508
    missile_launcher_light = 509
    missile_launcher_heavy = 510
    missile_launcher_rapid_light = 511
    missile_launcher_citadel = 524
    missile_launcher_heavy_assault = 771
    effect_beacon = 920
    missile_launcher_rapid_heavy = 1245
    ship_modifier = 1306


@unique
class Category(IntEnum):
    """Category ID holder"""
    ship = 6
    module = 7
    charge = 8
    skill = 16
    drone = 18
    implant = 20
    subsystem = 32


@unique
class Effect(IntEnum):
    """Effect ID holder"""
    missile_launching = 9
    target_attack = 10
    lo_power = 11
    hi_power = 12
    med_power = 13
    online = 16
    projectile_fired = 34
    emp_wave = 38
    launcher_fitted = 40
    turret_fitted = 42
    mining_laser = 67
    use_missiles = 101
    fof_missile_launching = 104
    rig_slot = 2663
    bomb_launching = 2971
    subsystem = 3772
    fighter_missile = 4729
    super_weapon_amarr = 4489
    super_weapon_caldari = 4490
    super_weapon_gallente = 4491
    super_weapon_minmatar = 4492


@unique
class EffectCategory(IntEnum):
    """Effect category ID holder"""
    # Applied when item is just present in fit - implants, skills, offlined modules
    passive = 0
    # Applied only when module is activated
    active = 1
    # Applied onto selected target
    target = 2
    # No effects with this category, so actual impact is unknown
    area = 3
    # Applied when module at least onlined
    online = 4
    # Applied only when module is overloaded
    overload = 5
    # Dungeon effects, several effects exist in this category, but not assigned to any item
    dungeon = 6
    # System-wide effects, like WH and incursion
    system = 7


@unique
class Operand(IntEnum):
    """Expression operand ID holder"""
    # Add two numbers to return result, used in conditions
    add = 1
    # Applies modification to items of gang-mates (not used in any effect), filtered by group,
    # format: [(groupFilter.targetAttribute).(operator)].AGGM(sourceAttribute)
    add_gang_grp_mod = 2
    # Applies modification directly to ships gang-mates,
    # format: ((targetAttribute).(operator)).AGIM(sourceAttribute)
    add_gang_itm_mod = 3
    # Applies modification to items of gang-mates (not used in any effect),
    # filtered by owner and skill requirement
    add_gang_own_srq_mod = 4
    # Applies modification to items of gang-mates, filtered by skill requirement,
    # format: (skill_requirement.targetAttribute).(operator)).AGRSM(sourceAttribute))
    add_gang_srq_mod = 5
    # Applies modification directly to some item,
    # format: ((location->targetAttribute).(operator)).AIM(sourceAttribute)
    add_itm_mod = 6
    # Applies modification to items belonging to some domain, filtered by group,
    # format: ((location..groupFilter->targetAttribute).(operator)).ALGM(sourceAttribute)
    add_loc_grp_mod = 7
    # Applies modification to all items belonging to some domain,
    # format: ((location->targetAttribute).(operator)).ALM(sourceAttribute)
    add_loc_mod = 8
    # Applies modification to items belonging to some domain, filtered by skill requirement
    # format: ((location[skill_requirement]->targetAttribute).(operator)).ALRSM(sourceAttribute)
    add_loc_srq_mod = 9
    # Logical AND operator
    and_ = 10
    # Applies modification to items belonging to some domain, filtered by owner of source,
    # format: ((location[skill_requirement]->targetAttribute).(operator)).AORSM(sourceAttribute)
    add_own_srq_mod = 11
    # Joins target items and attribute into target definition,
    # format: location->targetAttribute
    itm_attr = 12
    # Special operand, handles turret attack
    attack = 13
    # Special operand, used to define cargo scan
    cargo_scan = 14
    # Special operand, handles GM tools
    cheat_tele_dock = 15
    # Special operand, handles GM tools
    cheat_tele_gate = 16
    # Executes two statements, format: expression1; expression2
    splice = 17
    # Decreases value for some attribute by value of another one
    dec = 18
    # Special operand, defines area-of-effect decloak
    aoe_decloak = 19
    # Define operator, text in expressionValue field
    def_optr = 21
    # Define attribute, integer in expressionAttributeID field
    def_attr = 22
    # Define boolean constant, boolean in expressionValue field
    def_bool = 23
    # Define location, text in expressionValue field
    def_loc = 24
    # Define group, integer in expressionGroupID field
    def_grp = 26
    # Defines an integer constant, integer in expressionValue field
    def_int = 27
    # Define a type, integer in expressionTypeID field
    def_type = 29
    # Special operand, used in ECM Burst effects
    ecm_burst = 30
    # Joins operator and target (attribute of possibly filtered items) definitions,
    # format: (location->targetAttribute).(operator)
    optr_tgt = 31
    # Special operand, defines area-of-effect damage for modules like smartbombs and old doomsday
    aoe_dmg = 32
    # Check for equality, used in conditions
    eq = 33
    # Joins group and attribute into target definition, format: groupFilter.targetAttribute
    grp_attr = 34
    # Joins target item and its attribute, used in conditions
    itm_attr_cond = 35
    # Gets type of item in arg1
    get_type = 36
    # Check for arg1 being greater than arg2, used in conditions
    greater = 38
    # Check for arg1 being greater than or equal to arg2, used in conditions
    greater_eq = 39
    # Generic attribute reference, doesn't join anything, just refers attribute definition
    gen_attr = 40
    # If-then construct
    if_then = 41
    # Increases value of some attribute by the value of another one
    inc = 42
    # Special operand, handles missile launching
    missile_launch = 44
    # Special operand, handles defender missile launching
    defender_launch = 45
    # Special operand, handles friend-or-foe missile launching
    fof_launch = 47
    # Joins domain and group definitions into single filter, format: location..group
    loc_grp = 48
    # Joins domain and skill requirement definitions into single filter,
    # format: location[skill_requirement]
    loc_srq = 49
    # Special operand, handles transfer of ore from asteroid to cargo
    mine = 50
    # Logical OR operand, also used as else clause in if-then constructions
    or_ = 52
    # Special operand, defines cap booster effect
    power_booster = 53
    # Undos modification from items of gang-mates, filtered by group,
    # format: [(groupFilter.targetAttribute).(operator)].RGGM(sourceAttribute)
    rm_gang_grp_mod = 54
    # Undos modification directly from ships gang-mates,
    # format: ((targetAttribute).(operator)).RGIM(sourceAttribute)
    rm_gang_itm_mod = 55
    # Undos modification from items of gang-mates, filtered by owner and skill requirement
    rm_gang_own_srq_mod = 56
    # Undos modification from items of gang-mates, filtered by skill requirement,
    # format: (skill_requirement.targetAttribute).(operator)).RGRSM(sourceAttribute))
    rm_gang_srq_mod = 57
    # Undos modification directly from some item,
    # format: ((location->targetAttribute).(operator)).RIM(sourceAttribute)
    rm_itm_mod = 58
    # Undos modification from items belonging to some domain, filtered by group,
    # format: ((location..groupFilter->targetAttribute).(operator)).RLGM(sourceAttribute)
    rm_loc_grp_mod = 59
    # Undos modification from all items belonging to some domain,
    # format: ((location->targetAttribute).(operator)).RLM(sourceAttribute)
    rm_loc_mod = 60
    # Undos modification from items belonging to some domain, filtered by skill requirement,
    # format: ((location[skill_requirement]->targetAttribute).(operator)).RLRSM(sourceAttribute)
    rm_loc_srq_mod = 61
    # Undos modification from items belonging to some domain, filtered by owner of source,
    # format: ((location[skill_requirement]->targetAttribute).(operator)).RORSM(sourceAttribute)
    rm_own_srq_mod = 62
    # Joins skill requirement and attribute into target definition,
    # format: skill_requirement.targetAttribute
    srq_attr = 64
    # Direct assignment to one attribute value of another one
    assign = 65
    # Special operand, used to define ship scan
    ship_scan = 66
    # Subtracts one number from another and returns result, used in conditions
    sub = 68
    # Special operand, used to define ore scan
    survey_scan = 69
    # Special operand, used in auto-targeting systems
    tgt_hostile = 70
    # Special operand, used in passive targeting systems
    tgt_silent = 71
    # Special operand, most likely checks if you have enough skills to use
    # currently loaded charge, or have enough skills to work with current target
    tool_tgt_skills = 72
    # In erroneous cases, raises user error provided in arg1
    user_error = 73
    # Special operand, used to verify if target can have effect's
    # carrier applied onto it, otherwise raises error
    vrf_tgt_grp = 74
