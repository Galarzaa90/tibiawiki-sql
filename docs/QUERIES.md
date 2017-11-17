A collection of example SQL queries.  
Most queries are simple enough, specially when the information is all found in a single table, however, 
sometimes information is spread across tables, related through foreign keys.

### Creatures at least 15% weak to energy
```sql
SELECT title, energy
FROM creatures 
WHERE energy >= 115
ORDER BY energy DESC
```

Results:

| title | energy |
| ----- | ------ |
| Lionet (Creature) | 150
| Ice Overlord | 125
| Massive Water Elemental | 125
| Quara Constrictor | 125
| Quara Hydromancer | 125
| ... | ... 

### Fetch creatures that drop 'crown armor'
```sql
SELECT creatures.title as creature, chance
FROM creatures_drops
INNER JOIN creatures ON creatures.id = creature_id
WHERE item_id = (SELECT id FROM items WHERE name LIKE "crown armor")
ORDER BY chance DESC 
```

**Results**

| creature | chance |
| -------- | ------ |
| The Noxious Spawn | 28.125
| Hellgorak | 18.442
| Horadron | 16.1849
| Thul | 8.333
| Vile Grandmaster | 1.2637
| ... | ... 


### Get all items sold by 'Alesar'
```sql
SELECT item.name as item, npcs_buying.value as price, currency.name as currency
FROM npcs_buying
LEFT JOIN items item on item.id = item_id
LEFT JOIN items currency on currency.id = currency
WHERE npc_id = (SELECT id FROM npcs WHERE name LIKE 'alesar')
ORDER by price DESC
```

**Result**

| item | price | currency |
| ---- | ----- | -------- |
| onyx flail | 22000| gold coin
| ornamented  axe | 20000| gold coin
| giant sword | 17000| gold coin
| dreaded cleaver | 15000| gold coin
| vampire shield	| 15000| gold coin
| ... | ... | ...


### Quests that involve Juggernauts
```sql
SELECT quests.name as quest, quests.location, quests.level_required as "level required"
FROM quests_dangers
INNER JOIN quests ON quests.id = quest_id
WHERE creature_id = (SELECT id FROM creatures WHERE name LIKE 'juggernaut')
```
**Result**

| quest | location | level required |
| ----- | -------- | -------------- |
| Roshamuul Quest | Roshamuul | 0
| The Inquisition Quest | Various, starts in Thais | 100
| The Pits of Inferno Quest | Pits of Inferno, under the Plains of Havoc; entrance near the Necromant House. | 80