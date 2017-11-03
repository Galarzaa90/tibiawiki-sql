A collection of example SQL queries.

####Fetch creatures at least 15% weak to energy
```sql
SELECT title, energy FROM creatures WHERE energy > 115 ORDER BY energy DESC LIMIT 5
```

Results:

| title | energy |
| ----- | ------ |
| Lionet (Creature) | 150
| Ice Overlord | 125
| Massive Water Elemental | 125
| Quara Constrictor | 125
| Quara Hydromancer | 125

####Fetch creatures that drop 'crown armor'
```sql
SELECT creatures.title as "creature", chance FROM creatures, creatures_drops, items WHERE items.id = creatures_drops.item_id AND creatures.id = creatures_drops.creature_id AND items.name LIKE 'crown armor' ORDER BY chance DESC LIMIT 5
```
Results

| creature | chance |
| -------- | ------ |
| The Noxious Spawn | 28.125
| Hellgorak | 18.442
| Horadron | 16.1849
| Thul | 8.333
| Vile Grandmaster | 1.2637