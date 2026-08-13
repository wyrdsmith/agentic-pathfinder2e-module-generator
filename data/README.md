# Instant Pathfinder Data

All data collected from Archives of Nethys for the purposes of this project is based on what is allowed to be published under Paizo's publishing license. No harm is intended in the use and republication of this data. Any data used in the Pathfinder 2e rules is not my original creation and belongs to Paizo Inc. as the publisher of the Pathfinder Roleplaying Game.

Note: No unique rarity items, creatures or other game elements have been included, only common, uncommon and rare rarities.

## Data Format

All data is stored initially in JSON format. This is for ease of initial development and acquisition. Data was pulled from Archives of Nethys manually (or were exported using AON's export feature when available) using presented tables and then formatted into JSON. See below for the specific source for each JSON data file. The JSON data is then imported into an SQLite database where it is stored in a more structured format. The schema for the database does not employ foreign keys as joining or searching based on strings is sufficient for the size of the data being used.

## Data Sources and Notes

### Ancestries `data/ancestries.json`
#### Source
Based on exported data found at https://2e.aonprd.com/Search.aspx?include-types=ancestry&display=table&columns=rarity+url+summary
#### Notes
This list includes all available entries under "Ancestries" and no restrictions were applied. Summary was renamed to Description.

### Classes `data/classes.json`
#### Source
Based on exported data found at https://2e.aonprd.com/Search.aspx?include-types=class&sort=name-asc&display=table&columns=rarity+url+summary
#### Notes
This list includes all available entries under "Classes" and no restrictions were applied. For the purposes of module generation, only a few columns are used. Summary was renamed to Description.

### Creature Experience `data/creature_experience.json`
#### Source
This table is based on Table 10-2: Creature XP and Role found at https://2e.aonprd.com/Rules.aspx?ID=2716
#### Notes
No modifications were made to this table besides removal of text in the level_adjustment column.

### Creature Stats `data/creature_stats.json`
#### Source
Based on the Creature Numbers table found under Gamemastering > Creature Numbers of the GM Screen available at https://2e.aonprd.com/GMScreen.aspx
#### Notes
It is assumed High, Medium and Low refer to the save bonuses for the creature.

### Creatures `data/creatures.json`
#### Source
Based on exported data found at https://2e.aonprd.com/Search.aspx?include-types=creature&sort=name-asc&display=table&columns=rarity+url+summary+trait+level
#### Notes
No creatures with a unique rarity are included.

### Difficulties `data/difficulties.json`
#### Source
Based on the Level-Based DCs table found at https://2e.aonprd.com/Rules.aspx?ID=2629
#### Notes
This table is used to set appropriate DCs for skill checks, saves and most other encounter DCs for a given encounter level.

### Encounter Experience `data/encounter_experience.json`
#### Source
Based on the XP Budget table found at https://2e.aonprd.com/Rules.aspx?ID=2717
#### Notes
While the table describes the ecounter budget for each challenge rating, the experience value is used to calculate the total experience earned over the course of the adventure module. It is assumed that the encounter at a given challenge rating provides that amount of experience to each character in a party of a given size. Parties larger or smaller than 4 have the XP budget adjusted by the adjustment column found in the table. This adjustment is not included in the final experience total calculated for the module. While this is an oversimplification of the xp rewards for an encounter, it is necessary for the limitations of the module generator.

### Hazard Stats `data/hazard_stats.json`
#### Source
Based on the Hazard Numbers table found under Gamemastering > Hazards on the GM Screen at https://2e.aonprd.com/GMScreen.aspx
#### Notes
These stats are only used for generating traps and simple hazards for use in skill challenge encounter generation.

### Hazards `data/hazards.json`
#### Source
Based on the hazards found at https://2e.aonprd.com/Hazards.aspx
#### Notes
No hazards with a unique rarity are included.

### Item Categories `data/item_categories.json`
#### Source
Generated based on unique values found in the Items table.
#### Notes
Categories are used to limit selection of item rewards for encounters.

### Items `data/items.json`
#### Source
Based on exported data found at https://2e.aonprd.com/Search.aspx?include-types=item&sort=name-asc&display=table&columns=rarity+url+summary+trait+level+item_category+item_subcategory+price
#### Notes
No items with a unique rarity are included.

### Rarities `data/rarities.json`
#### Source
Compiled manually based on Pathfinder 2e Rarity tags.
#### Notes
Unique is not included. Probability is used in calculating inclusion in data returned to LLMs from tool calls. This means rare items or ancestries are less likely to be included in adventure modules.

### Skill Action Sample Tasks `data/skill_action_sample_tasks.json`
#### Source
Manually generated based on sample tasks for each skill action found under Skills > Skill Actions on the GM Screen at https://2e.aonprd.com/GMScreen.aspx
#### Notes
Data includes training level and a description of the task to provide context to LLMs when determining if a skill is applicable to a given situation.

### Skill Actions `data/skill_actions.json`
#### Source
Manually generated based on skill actions found under Skills > Skill Actions on the GM Screen at https://2e.aonprd.com/GMScreen.aspx
#### Notes
General skill actions such as Recall Knowledge have been added to their relevant skills.

### Skills `data/skills.json`
#### Source
Based on exported data from search query at https://2e.aonprd.com/Search.aspx?include-types=skill&skills-operator=or&display=table
#### Notes
Description is included for the purposes of providing context to LLMs for determining when a skill check may be necessary based on the narrative.

### Threat Levels `data/threat_levels.json`
#### Source
Based on rules regarding encounter building found at https://2e.aonprd.com/Rules.aspx?ID=2716
#### Notes
This is not an accurate representation of the rules regarding encounter building, but represents a simplified approach to determining the threat level of an encounter and its associated experience point budget. Thus, if an LLM determines that an encounter should be severe, it uses the level adjustment to adjust the experience point budget of the encounter which is based on party level.

### Trainings `data/trainings.json`
#### Source
Manually generated based off the Simple Skill DC table found at https://2e.aonprd.com/Rules.aspx?ID=2628 and the level at which a character can be expected to have that level of training or mastery.
#### Notes
Descriptions were written by the developer to provide context to LLMs for skill training levels to provide appropriate narrative challenges for each skill check.

### Treasure Encounter `data/treasure_encounter.json`
#### Source
Based on the Treasure by Encounter table found at https://2e.aonprd.com/Rules.aspx?ID=2738
#### Notes
This table provides the treasure value for an encounter for a given level and threat level.

### Treasure Level `data/treasure_level.json`
#### Source
Based on the Party Treasure by Level table found at https://2e.aonprd.com/Rules.aspx?ID=2656
#### Notes
This table lists the total treasure a party is expected to obtain each level. This data is used to review total treasure found in the adventure module to ensure it meets expected levels.

# Name Seeds Data for Markov Chain Name Generation
All name seeds were produced by Gemini 3.1 Pro by providing sample names taken from the ancestry details page on Archives of Nethys, any naming conventions provided by Pathfinder, and my own observations of the names. The focus of the name generation was on syllable and interesting name quirks appropriate to each ancestry.

## Data Format
The seed data follows the naming convention of `<ancestry>_names.csv` where each csv file is just a comma separated list of names. These names should provide a good baseline for name generation for each ancestry and should provide a good variety of names for use in adventure modules. Some ancestries have more defined names, such as `[adjective]+[noun]`. In these instances a name is randomly selected from the database rather than generated via markov chain.