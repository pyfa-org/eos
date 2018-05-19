[![Build Status](https://travis-ci.org/pyfa-org/eos.svg?branch=master)](https://travis-ci.org/pyfa-org/eos) [![PyPI](https://img.shields.io/pypi/v/Eos.svg)](https://pypi.python.org/pypi/Eos/)

# Eos

Currently you can use engine following way:

    from eos import *
    from eos.item_filter import *


    data_handler = JsonDataHandler('data_folder/phobos/')  # Folder with Phobos data dump
    cache_handler = JsonCacheHandler('data_folder/cache/eos_tq.json.bz2')
    SourceManager.add('tiamat', data_handler, cache_handler, make_default=True)

    skill_groups = set(row['groupID'] for row in data_handler.get_evegroups() if row['categoryID'] == 16)
    skills = set(row['typeID'] for row in data_handler.get_evetypes() if row['groupID'] in skill_groups)

    fit = Fit()
    fit.ship = Ship(32311)  # Navy Typhoon

    for skill_id in skills:
        fit.skills.add(Skill(skill_id, level=5))

    # 4x 800mm with hail
    fit.modules.high.equip(ModuleHigh(2929, state=State.overload, charge=Charge(12779)))
    fit.modules.high.equip(ModuleHigh(2929, state=State.overload, charge=Charge(12779)))
    fit.modules.high.equip(ModuleHigh(2929, state=State.overload, charge=Charge(12779)))
    fit.modules.high.equip(ModuleHigh(2929, state=State.overload, charge=Charge(12779)))
    # 4x Torp launcher with nova rages
    fit.modules.high.equip(ModuleHigh(2420, state=State.overload, charge=Charge(24519)))
    fit.modules.high.equip(ModuleHigh(2420, state=State.overload, charge=Charge(24519)))
    fit.modules.high.equip(ModuleHigh(2420, state=State.overload, charge=Charge(24519)))
    fit.modules.high.equip(ModuleHigh(2420, state=State.overload, charge=Charge(24519)))

    fit.modules.mid.equip(ModuleMid(5945, state=State.overload))  # Top named 100MN MWD
    fit.modules.mid.equip(ModuleMid(4833, state=State.active, charge=Charge(32014)))  # Named med cap injector with 800
    fit.modules.mid.equip(ModuleMid(9622, state=State.active))  # Named EM hardener
    fit.modules.mid.equip(ModuleMid(5443, state=State.active))  # Best named scram
    fit.modules.mid.equip(ModuleMid(2281, state=State.active))  # T2 invuln

    fit.modules.low.equip(ModuleLow(2048, state=State.online))   # T2 DC
    fit.modules.low.equip(ModuleLow(519, state=State.online))    # T2 gyrostab
    fit.modules.low.equip(ModuleLow(519, state=State.online))    # T2 gyrostab
    fit.modules.low.equip(ModuleLow(22291, state=State.online))  # T2 BCU
    fit.modules.low.equip(ModuleLow(22291, state=State.online))  # T2 BCU
    fit.modules.low.equip(ModuleLow(4405, state=State.online))   # T2 DDA
    fit.modules.low.equip(ModuleLow(4405, state=State.online))   # T2 DDA

    fit.rigs.add(Rig(26082))  # T1 therm rig
    fit.rigs.add(Rig(26088))  # T1 extender
    fit.rigs.add(Rig(26088))  # T1 extender

    # 8x Ogre II
    fit.drones.add(Drone(2446, state=State.active))
    fit.drones.add(Drone(2446, state=State.active))
    fit.drones.add(Drone(2446, state=State.active))
    fit.drones.add(Drone(2446, state=State.active))
    fit.drones.add(Drone(2446, state=State.active))
    fit.drones.add(Drone(2446, state=State.offline))
    fit.drones.add(Drone(2446, state=State.offline))
    fit.drones.add(Drone(2446, state=State.offline))

    fit.implants.add(Implant(13231))  # 3% torp dmg
    fit.implants.add(Implant(10228))  # 3% shield capacity
    fit.implants.add(Implant(24663))  # zor hyperlink
    fit.implants.add(Implant(13244))  # 3% turret dmg
    fit.implants.add(Implant(13219))  # 3% large projectile dmg

    fit.boosters.add(Booster(28672))  # Synth crash
    fit.boosters.add(Booster(28674))  # Synth drop

    fit.validate()

Fit validation method currently raises exception if any fit check fails, its argument contains dictionary which explains what is wrong. If we make additional drone active, following data will be returned:

    {<Drone(type_id=2446, state=3)>: {
        <Restriction.drone_bandwidth: 5>: ResourceErrorData(total_use=150.0, output=125.0, holder_use=25.0),
        <Restriction.launched_drone: 6>: SlotQuantityErrorData(slots_used=6, slots_max_allowed=5)},
    ...
    }

Keys of dictionary are problematic holders (in this case, all in-space drones of ship), values are dictionaries too, which list problems with given module. Keys of this dictionary are restriction IDs (eos.Restriction object), with 5 being drone bandwidth restriction, and 6 being quantity of drones this fit can use; values contain detailed data about the problem.

Attributes of any item are accessible via dictionary-like objects like phoon.attributes, e.g.:

    >>> fit.ship.attrs[37] # maxVelocity
    1858.3066943807341

Stats of fit can be fetched using 'stats' access point. For example, few regular ones:

    >>> fit.stats.agility_factor
    15.70747757338698
    >>> fit.stats.cpu.used
    823.0

And few more advanced (total uniform EHP of fit, and shield EHP vs EM damage):

    >>> fit.stats.get_ehp(DmgProfile(em=25, thermal=25, kinetic=25, explosive=25)).total
    95189.27348943402
    >>> fit.stats.get_ehp(DmgProfile(em=1, thermal=0, kinetic=0, explosive=0)).shield
    50013.69083371911

DPS can be fetched with various parameters, for example, should it take reload into consideration or not:

    >>> fit.stats.get_dps(reload=False).total
    1913.5769753125805
    >>> fit.stats.get_dps(reload=True).total
    1866.5853444855636

Specific damage type is accessible too (in this case, hail deals some kinetic damage):

    >>> fit.stats.get_dps(reload=False).kinetic
    136.64914857525073

Get effective DPS against passed resistance profile:

    >>> from eos.stats_container import ResistProfile

    >>> fit.stats.get_dps(tgt_resists=ResistProfile(em=0.2, thermal=0.3, kinetic=0.4, explosive=0.5)).total
    1060.4052373697928

Get dps using built-in filters:

    >>> from eos.item_filter import turret_filter, missile_filter, drone_filter, sentry_drone_filter

    >>> fit.stats.get_dps(turret_filter).total
    637.6960266845035
    >>> fit.stats.get_dps(missile_filter).total
    826.1217743481901
    >>> fit.stats.get_dps(drone_filter).total
    449.7591742798868

You can compose your own filters or combine existing:

    >>> fit.stats.get_dps(lambda h: turret_filter(h) or missile_filter(h)).total
    1463.8178010326938

Not all stats are implemented yet, more to come soon.
