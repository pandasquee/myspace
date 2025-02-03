# Space Object Database Attributes

## Database (.db) Attributes

### Structure Attributes
* `structure["type"]` - Type of space object
* `structure["displacement"]` - Ship displacement
* `structure["cargo_hold"]` - Cargo hold capacity
* `structure["max_structure"]` - Maximum structural integrity
* `structure["superstructure"]` - Current structural integrity
* `structure["max_repair"]` - Maximum repair capacity
* `structure["repair"]` - Current repair capacity

### Power Systems
* `main["exist"]` - Main power system exists (0/1)
* `main["damage"]` - Main power system damage
* `main["gw"]` - Main power output in gigawatts
* `main["in"]` - Main power input
* `main["out"]` - Main power output

* `aux["exist"]` - Auxiliary power system exists (0/1)
* `aux["damage"]` - Auxiliary power system damage
* `aux["gw"]` - Auxiliary power output in gigawatts
* `aux["in"]` - Auxiliary power input
* `aux["out"]` - Auxiliary power output

* `batt["exist"]` - Battery system exists (0/1)
* `batt["damage"]` - Battery system damage
* `batt["gw"]` - Battery capacity in gigawatts
* `batt["in"]` - Battery charging rate
* `batt["out"]` - Battery discharge rate

### Power Allocation
* `alloc["helm"]` - Power allocation to helm
* `alloc["tactical"]` - Power allocation to tactical
* `alloc["operations"]` - Power allocation to operations
* `alloc["movement"]` - Power allocation to movement
* `alloc["shields"]` - Power allocation to shields overall
* `alloc["shield"][i]` - Power allocation to individual shields (array)
* `alloc["cloak"]` - Power allocation to cloaking
* `alloc["beams"]` - Power allocation to beam weapons
* `alloc["missiles"]` - Power allocation to missile systems
* `alloc["sensors"]` - Power allocation to sensors
* `alloc["ecm"]` - Power allocation to ECM
* `alloc["eccm"]` - Power allocation to ECCM
* `alloc["transporters"]` - Power allocation to transporters
* `alloc["tractors"]` - Power allocation to tractor beams
* `alloc["miscellaneous"]` - Miscellaneous power allocation

### Movement & Navigation
* `move["ratio"]` - Movement power ratio
* `move["in"]` - Movement power input
* `move["out"]` - Movement power output
* `move["v"]` - Current velocity

* `course["d"]` - Course direction vectors (3x3 array)

* `coords["x"]` - X coordinate
* `coords["y"]` - Y coordinate
* `coords["z"]` - Z coordinate

### Engines
* `engine["warp_exist"]` - Warp drive exists (0/1)
* `engine["warp_damage"]` - Warp drive damage
* `engine["warp_max"]` - Maximum warp speed
* `engine["warp_cruise"]` - Cruise warp speed

* `engine["impulse_exist"]` - Impulse drive exists (0/1)
* `engine["impulse_damage"]` - Impulse drive damage
* `engine["impulse_max"]` - Maximum impulse speed
* `engine["impulse_cruise"]` - Cruise impulse speed

### Weapons
* `beam["exist"]` - Beam weapons exist (0/1)
* `beam["banks"]` - Number of beam weapon banks
* `beam["freq"]` - Beam weapon frequency
* `beam["in"]` - Beam weapon power input
* `beam["out"]` - Beam weapon power output

* `missile["exist"]` - Missile systems exist (0/1)
* `missile["tubes"]` - Number of missile tubes
* `missile["freq"]` - Missile frequency
* `missile["in"]` - Missile system power input
* `missile["out"]` - Missile system power output

### Weapon Banks
* `blist[i]["name"]` - Beam bank name
* `blist[i]["damage"]` - Beam bank damage
* `blist[i]["bonus"]` - Beam bank bonus
* `blist[i]["cost"]` - Beam bank power cost
* `blist[i]["range"]` - Beam bank range
* `blist[i]["arcs"]` - Beam bank firing arcs
* `blist[i]["active"]` - Beam bank active status
* `blist[i]["lock"]` - Beam bank target lock
* `blist[i]["load"]` - Beam bank load status
* `blist[i]["recycle"]` - Beam bank recycle time

* `mlist[i]["name"]` - Missile tube name
* `mlist[i]["damage"]` - Missile tube damage
* `mlist[i]["warhead"]` - Missile warhead type
* `mlist[i]["cost"]` - Missile tube power cost
* `mlist[i]["range"]` - Missile range
* `mlist[i]["arcs"]` - Missile firing arcs
* `mlist[i]["active"]` - Missile tube active status
* `mlist[i]["lock"]` - Missile tube target lock
* `mlist[i]["load"]` - Missile tube load status
* `mlist[i]["recycle"]` - Missile tube recycle time

### Shields
* `shield["exist"]` - Shield system exists (0/1)
* `shield["ratio"]` - Shield power ratio
* `shield["maximum"]` - Maximum shield strength
* `shield["freq"]` - Shield frequency
* `shield["visibility"]` - Shield visibility
* `shield[i]["damage"]` - Individual shield damage (array)
* `shield[i]["active"]` - Individual shield active status (array)

### Sensors
* `sensor["contacts"]` - Number of sensor contacts
* `sensor["counter"]` - Sensor contact counter

* `sensor["lrs_exist"]` - Long range sensors exist (0/1)
* `sensor["lrs_active"]` - Long range sensors active
* `sensor["lrs_damage"]` - Long range sensor damage
* `sensor["lrs_resolution"]` - Long range sensor resolution

* `sensor["srs_exist"]` - Short range sensors exist (0/1)
* `sensor["srs_active"]` - Short range sensors active
* `sensor["srs_damage"]` - Short range sensor damage
* `sensor["srs_resolution"]` - Short range sensor resolution

* `sensor["ew_exist"]` - Electronic warfare system exists (0/1)
* `sensor["ew_active"]` - Electronic warfare active
* `sensor["ew_damage"]` - Electronic warfare system damage

### Contact List
* `slist[i]["key"]` - Contact database reference
* `slist[i]["num"]` - Contact number
* `slist[i]["lev"]` - Contact classification level

### Technology Levels
* `tech["firing"]` - Weapons technology level
* `tech["fuel"]` - Fuel system technology level
* `tech["stealth"]` - Stealth technology level
* `tech["cloak"]` - Cloaking technology level
* `tech["sensors"]` - Sensor technology level
* `tech["main_max"]` - Main power technology level
* `tech["aux_max"]` - Auxiliary power technology level
* `tech["armor"]` - Armor technology level
* `tech["ly_range"]` - Light year range capability

### Fuel Systems
* `fuel["antimatter"]` - Antimatter fuel level
* `fuel["deuterium"]` - Deuterium fuel level
* `fuel["reserves"]` - Power reserves

### Miscellaneous Systems
* `cloak["exist"]` - Cloaking device exists (0/1)
* `cloak["cost"]` - Cloaking device power cost
* `cloak["damage"]` - Cloaking device damage
* `cloak["freq"]` - Cloaking frequency
* `cloak["active"]` - Cloaking device active status

* `trans["exist"]` - Transporter exists (0/1)
* `trans["cost"]` - Transporter power cost
* `trans["damage"]` - Transporter damage
* `trans["freq"]` - Transporter frequency
* `trans["d_lock"]` - Transporter destination lock
* `trans["s_lock"]` - Transporter source lock

* `tract["exist"]` - Tractor beam exists (0/1)
* `tract["cost"]` - Tractor beam power cost
* `tract["damage"]` - Tractor beam damage
* `tract["freq"]` - Tractor beam frequency
* `tract["active"]` - Tractor beam active status
* `tract["lock"]` - Tractor beam lock target

### Status
* `status["crippled"]` - Crippled status (0=none, 1=crippled, 2=heavy damage)
* `status["tractoring"]` - Currently tractoring another object
* `status["tractored"]` - Currently being tractored

### IFF System
* `iff["frequency"]` - IFF (Identification Friend/Foe) frequency

### Other
* `power["total"]` - Total power available
* `power["main"]` - Main power available
* `power["aux"]` - Auxiliary power available
* `power["batt"]` - Battery power available
* `language` - Communication language setting

## Additional Coordinate Attributes (.db)
From the new file, we can see additional coordinate attributes:

* `coords["xd"]` - Destination X coordinate
* `coords["yd"]` - Destination Y coordinate
* `coords["zd"]` - Destination Z coordinate
* `coords["xo"]` - Origin X coordinate
* `coords["yo"]` - Origin Y coordinate
* `coords["zo"]` - Origin Z coordinate

### Additional Status Flags (.db)
* `status["active"]` - Object is active (1/0)
* `status["docked"]` - Docked status (1/0)
* `status["landed"]` - Landed status (1/0)
* `status["connected"]` - Connected to other object (1/0)
* `status["autopilot"]` - Autopilot engaged (1/0)

### Version Tracking (.db)
* `power["version"]` - Power systems version tracker
* `engine["version"]` - Engine systems version tracker
* `sensor["version"]` - Sensor systems version tracker
* `cloak["version"]` - Cloak systems version tracker
* `move["version"]` - Movement systems version tracker

## Non-Database (.ndb) Attributes

### Real-Time Position and Movement
* `ndb.position` - Current position tuple (x, y, z)
* `ndb.velocity` - Current velocity magnitude
* `ndb.speed_mode` - Current speed mode (e.g., IMPULSE, WARP)

### Real-Time Course Management
* `ndb.yaw_in` - Desired yaw angle
* `ndb.pitch_in` - Desired pitch angle
* `ndb.roll_in` - Desired roll angle
* `ndb.yaw_out` - Current yaw angle
* `ndb.pitch_out` - Current pitch angle
* `ndb.roll_out` - Current roll angle

### Real-Time Power Systems
* `ndb.power_main` - Current main reactor output
* `ndb.power_aux` - Current auxiliary power output
* `ndb.power_batt` - Current battery power output
* `ndb.power_consumption` - Current power consumption
* `ndb.power_available` - Total power currently available

### Real-Time Engine Status
* `ndb.warp_active` - Warp drive active status
* `ndb.impulse_active` - Impulse drive active status
* `ndb.engine_status` - Dictionary tracking engine damage states

### Real-Time Weapons
* `ndb.blist` - Real-time beam weapon bank states
* `ndb.mlist` - Real-time missile tube states
* `ndb.active_weapons` - Sets tracking active weapon banks/tubes

### Real-Time Shield Systems
* `ndb.shield_active` - Current shield active state
* `ndb.shield_facings` - Real-time shield facing states

### Real-Time Sensor Systems
* `ndb.sensor_contacts` - Current sensor contact list
* `ndb.active_sensor_mode` - Current sensor operation mode
* `ndb.sensor_range` - Current effective sensor range

### Update System Management
* `ndb.update_buffer` - Queue of pending state updates
* `ndb.update_interval` - Time between general updates
* `ndb.physics_interval` - Time between physics updates
* `ndb.sensor_interval` - Time between sensor updates
* `ndb.needs_save` - Flag indicating state needs persistence
* `ndb.last_update` - Timestamp of last update
* `ndb.last_physics_update` - Timestamp of last physics update
* `ndb.last_power_update` - Timestamp of last power update
* `ndb.last_shield_update` - Timestamp of last shield update
* `ndb.last_weapon_update` - Timestamp of last weapon update
* `ndb.last_sensor_update` - Timestamp of last sensor update

### Performance Tracking
* `ndb.update_stats` - Dictionary tracking update statistics including:
  - updates_processed
  - errors_encountered
  - last_error
  - average_batch_size
  - last_save_time
  - physics_load
  - system_load

## Course Data Structure
The course data is stored using a CourseData class with these attributes:
* `yaw_in` - Yaw input value
* `yaw_out` - Yaw output value
* `pitch_in` - Pitch input value
* `pitch_out` - Pitch output value
* `roll_in` - Roll input value
* `roll_out` - Roll output value
* `d` - Direction vectors (List[List[float]])
* `rate` - Turn rate
* `version` - Version tracking number