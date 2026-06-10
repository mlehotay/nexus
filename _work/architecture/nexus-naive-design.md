# Generic World Engine Architecture

## A Modular Successor Architecture for NetHack

---

# 1. Goals

The engine should evolve from:

> “A hardcoded roguelike about the Amulet of Yendor”

into:

> “A reusable simulation engine capable of loading arbitrary worlds, rulesets, quests, and dungeon structures.”

The design must support:

* Multiple independent worlds
* Arbitrary branches and subworlds
* Custom physics/rule systems
* Data-driven gameplay
* Procedural or authored content
* Modding
* Deterministic saves/replay
* Long-term extensibility

The engine should preserve:

* NetHack-style emergence
* Deep interactions
* Turn-based determinism
* Simulation-first architecture

while removing:

* hardcoded lore assumptions
* hardcoded branch logic
* hardcoded victory conditions
* branch-specific C logic

---

# 2. High-Level Architecture

The engine is divided into:

```text
Core Engine
    ↓
Simulation Systems
    ↓
World Runtime
    ↓
Loaded World Packages
```

---

# 3. Core Concepts

## 3.1 Entity

Everything dynamic is an entity.

Examples:

* Player
* Monsters
* Items
* Doors
* Traps
* Projectiles
* Altars
* Clouds
* Gods
* Vehicles

Entities are IDs plus attached components.

---

## 3.2 Components

Components are pure data.

Examples:

```text
Position
Health
Inventory
AI
Faction
Renderable
PhysicsBody
Flammable
Container
Edible
DivineAlignment
QuestState
```

Components contain no logic.

---

## 3.3 Systems

Systems implement simulation behavior.

Examples:

```text
MovementSystem
CombatSystem
FireSystem
VisionSystem
PrayerSystem
SpawnSystem
GoalSystem
FluidSystem
AIPlanningSystem
```

Systems process entities possessing relevant components.

---

## 3.4 Events

All meaningful actions generate events.

Examples:

```text
MoveEvent
DamageEvent
DeathEvent
PrayerEvent
RegionEnteredEvent
GoalCompletedEvent
ItemAcquiredEvent
```

Events enable:

* triggers
* scripting
* replay
* networking
* debugging
* deterministic simulation

---

# 4. World Structure

## 4.1 World Hierarchy

```text
World
  └── Branch
        └── Level
              └── Region
                    └── Tile
```

Each layer may override rules.

---

## 4.2 World

The top-level package.

Contains:

* lore
* global rules
* global spawn tables
* global factions
* cosmology
* progression rules

Examples:

* Dungeons of Doom
* Sci-fi colony
* Mythic overworld
* Underwater civilization

---

## 4.3 Branch

A branch is:

* topology
* ruleset
* progression domain
* content namespace

Examples:

* Sokoban
* Gehennom
* Quest branch
* Volcano
* Moon base
* Dream realm

Branches are NOT hardcoded.

---

## 4.4 Level

Levels define:

* geometry
* generation method
* local rules
* triggers
* local state

Can be:

* procedural
* fixed
* hybrid

---

## 4.5 Region

Regions are semantic zones.

Examples:

* temple
* lava chamber
* holy ground
* underwater area
* anti-magic field

Regions override localized rules.

---

# 5. Rules Architecture

## 5.1 Rule Resolution Hierarchy

Rules resolve from most specific to least specific:

```text
Tile
→ Region
→ Level
→ Branch
→ World
→ Global engine defaults
```

Example:

```text
Player prays
```

Resolution chain:

```text
Tile prayer override?
Region prayer override?
Branch prayer override?
World prayer override?
Default prayer system?
```

Thus:

* Gehennom prayer penalties
* Sokoban teleport restrictions
* Astral plane alignment effects

become data-driven rule overrides.

---

# 6. Physics Profiles

Physics are modular rule bundles.

## 6.1 Examples

### Standard

```text
normal gravity
normal teleportation
normal digging
normal movement
```

### Sokoban

```text
restricted pushing
anti-cheese logic
fixed puzzle state
```

### Underwater

```text
limited breathing
fluid resistance
distorted vision
floating objects
```

### Zero Gravity

```text
drift momentum
inertia movement
projectile continuation
```

---

## 6.2 Physics Interface

Systems query physics traits:

```text
CanPush()
CanDig()
CanTeleport()
CanFly()
MovementCost()
FluidResistance()
```

Profiles override these behaviors.

---

# 7. Data-Driven World Packages

---

## 7.1 Package Layout

```text
worlds/
  my_world/
    manifest.yaml
    world.yaml
    branches/
    levels/
    maps/
    entities/
    items/
    monsters/
    factions/
    rules/
    goals/
    dialogue/
    scripts/
    assets/
```

---

## 7.2 Manifest

Defines metadata and dependencies.

Example:

```yaml
id: forgotten_kingdom
version: 1.0
requires_engine: ">=0.5"
dependencies:
  - base_rules
```

---

# 8. Map System

Maps support:

* ASCII layouts
* tiled layouts
* procedural generators
* layered metadata

---

## 8.1 Tile Layers

Each tile may contain:

```text
terrain
liquid
gas
items
entities
field effects
lighting
metadata
```

---

## 8.2 Procedural Generators

Generators are composable.

Examples:

```yaml
generator:
  type: bsp_dungeon
  room_density: 0.7
  lava_chance: 0.1
```

---

# 9. Spawn System

Spawn tables are declarative.

Example:

```yaml
spawns:
  monsters:
    goblin: 40
    ogre: 10
    dragon: 1
```

Modifiers:

* biome
* depth
* faction control
* world state
* player reputation

---

# 10. Goals and Victory Conditions

Victory is data-driven.

---

## 10.1 Goal Definitions

Example:

```yaml
goals:
  - id: recover_crown
    type: possess_item
    item: crown_of_ashes

  - id: activate_gate
    type: trigger_state
    state: portal_open

  - id: escape
    type: reach_region
    region: surface_exit
```

---

## 10.2 Goal Engine

The engine listens to events.

Example:

```text
ItemAcquiredEvent
→ GoalSystem evaluates goals
→ GoalCompletedEvent emitted
```

---

## 10.3 Composite Goals

Supports:

```text
AND
OR
SEQUENCE
OPTIONAL
REPEATABLE
FACTION-SPECIFIC
```

Example:

```yaml
type: sequence
steps:
  - recover_artifact
  - defeat_guardian
  - exit_dimension
```

---

# 11. Trigger System

Triggers are declarative first.

---

## 11.1 Trigger Example

```yaml
triggers:
  - when: player_enters_region
    region: cursed_temple
    actions:
      - spawn: high_priest
      - message: "The altar cracks open."
```

---

## 11.2 Trigger Sources

```text
entity enters
entity dies
item acquired
turn elapsed
ritual completed
dialogue choice
weather change
```

---

# 12. Scripting System

Scripts are escape hatches.

Most content should NOT require scripting.

---

## 12.1 Preferred Architecture

Prefer:

```text
data → engine systems
```

over:

```text
arbitrary code
```

---

## 12.2 Script Engine

Recommended:

* Lua
* WASM
* embedded DSL

Avoid:

* raw C modules

Reasons:

* sandboxing
* hot reload
* mod safety
* serialization stability

---

## 12.3 Script Scope

Scripts may:

* react to events
* spawn entities
* modify state
* alter dialogue
* trigger cinematics

Scripts may NOT:

* directly mutate engine internals
* bypass serialization
* allocate arbitrary unmanaged memory

---

# 13. State Model

World state is explicit and serializable.

---

## 13.1 Persistent State

Examples:

```yaml
world_state:
  king_dead: true
  gate_open: false
  temple_corrupted: true
```

---

## 13.2 Deterministic Simulation

Required:

* fixed RNG seeds
* event ordering guarantees
* stable turn execution

Enables:

* replay
* debugging
* multiplayer lockstep
* reproducibility

---

# 14. AI Architecture

NPCs are agents.

---

## 14.1 AI Layers

```text
Perception
→ Memory
→ Goal Selection
→ Planning
→ Action Execution
```

---

## 14.2 AI Models

Possible:

* utility AI
* GOAP
* behavior trees
* finite state machines

---

## 14.3 Knowledge Separation

Separate:

* actual world
* perceived world
* remembered world

Supports:

* stealth
* misinformation
* hallucination
* hidden entities

---

# 15. Modding Architecture

Mods are layered packages.

---

## 15.1 Load Order

```text
base engine
→ core rules
→ world package
→ expansion packages
→ local overrides
```

---

## 15.2 Inheritance

Example:

```yaml
inherits: standard_dungeon
```

Allows partial overrides.

---

# 16. Validation System

All packages validated before runtime.

Checks:

* missing entities
* invalid references
* unreachable maps
* impossible goals
* broken triggers
* cyclic dependencies

---

# 17. Save Format

Save files contain:

* world state
* entity state
* RNG state
* script state
* event queue
* loaded package versions

Must support migration/versioning.

---

# 18. Networking and Replay (Future)

Because the engine is event-driven and deterministic:

* multiplayer becomes possible
* replay files become trivial
* debugging becomes dramatically easier

---

# 19. Migration Strategy from NetHack

## Phase 1

Abstract:

* branch rules
* victory conditions
* spawn tables

## Phase 2

Convert:

* monsters
* objects
* regions
* special levels

into data definitions.

## Phase 3

Introduce:

* event bus
* trigger engine
* scripting layer

## Phase 4

Remove hardcoded assumptions:

* Amulet victory
* fixed branches
* role quests
* deity behavior

## Phase 5

Support fully external world packages.

---

# 20. Design Philosophy

The engine should model:

```text
entities
interactions
rules
state transitions
```

—not story assumptions.

Stories emerge from:

* world packages
* goals
* factions
* systems
* player behavior

The engine itself should remain:

* simulation-oriented
* deterministic
* modular
* content-agnostic
* extensible
* data-driven

That is the architectural shift from:

> “a roguelike with hardcoded lore”

to:

> “a reusable simulation engine capable of expressing many roguelikes and worlds.”
