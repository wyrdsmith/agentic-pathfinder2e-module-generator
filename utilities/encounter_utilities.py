import random
from models.quest import Quest
from models.act import Act
from models.scene import Scene
from models.enemy import Enemy
from models.reward import Reward
from models.obstacle import Obstacle, ObstacleSkill
from tools.log_tools import *
from tools.npc_tools import get_skills_with_descriptions
from tools.encounter_tools import get_possible_enemies, get_possible_hazards, get_obstacle_skill_dc, get_obstacle_hazard_stats
from tools.reward_tools import get_item_details, get_possible_item_rewards, get_random_item
from agents.encounter_enemies_agent import get_encounter_enemy_agent
from agents.encounter_hazards_agent import get_encounter_hazard_agent
from agents.obstacle_concepts_agent import get_obstacle_concepts_creation_agent, get_obstacle_concepts_extraction_agent
from agents.obstacle_skills_agent import get_obstacle_skills_agent
from agents.obstacle_hazard_stats_agent import get_obstacle_hazard_stats_agent
from agents.encounter_rewards_agent import get_encounter_rewards_agent
from agents.encounter_details_agent import get_encounter_details_creation_agent, get_encounter_details_extraction_agent

def generate_encounter_enemies(current_quest: Quest):
    log_status("Generating encounter enemies for quest...")
    
    # Instantiate the Agent
    encounter_enemies_agent = get_encounter_enemy_agent()

    log_output("Selected Combat Encounter Enemies:")
    # Iterate through each encounter
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "combat" and scene.encounter.encounter_type == "combat":
                # Get a list of enemies that fall under the encounter experience budget and where the encounter
                # budget is cleanly divisible by the xp_value of the enemy. This cheats the enemy selection by
                # letting the agent select the most fitting enemy, rather than selecting multiple enemies that fit a budget.
                # We can then use the xp_value to determine the number of enemies in the encounter.
                possible_enemies = get_possible_enemies(current_quest.party_level, scene.encounter.xp_budget)
                
                prompt = "# Quest Information:\n"
                prompt += f"Quest Theme: {current_quest.theme}\n"
                prompt += f"Quest Setting: {current_quest.setting}\n"
                prompt += f"Quest Summary: {current_quest.summary}\n\n"
                prompt += "# Act Information:\n"
                prompt += f"Act Summary: {act.summary}\n\n"
                prompt += "# Scene Information:\n"
                prompt += f"Scene Summary: {scene.summary}\n"
                prompt += f"Scene Location: {scene.location}\n\n"
                prompt += "# Available Enemies:\n"
                for enemy in possible_enemies:
                    prompt += f"Name: {enemy.name}\n"
                    prompt += f"- Description: {enemy.description}\n"
                prompt += "# Task:\n\n"
                prompt += "Select the most appropriate enemy for the scene."
                
                with console.status(f"[bold cyan]AI Agent is selecting appropriate enemy for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = encounter_enemies_agent.run_sync(prompt)
                enemy_name = result.output.strip()
                
                selected_enemy = next((enemy for enemy in possible_enemies if enemy.name == enemy_name), None)

                if selected_enemy is None:
                    log_error(f"Enemy name provided by agent ({enemy_name}) did not match any of the available enemies. Trying again...")
                    prompt += "Remember that you must select an enemy from the available enemies list and output the exact name of the enemy. Do not output the count of enemies or any other information."

                retry_count = 0
                while selected_enemy is None and retry_count < 10:
                    with console.status(f"[bold cyan]AI Agent is re-selecting appropriate enemy for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = encounter_enemies_agent.run_sync(prompt)
                    enemy_name = result.output.strip()
                    
                    selected_enemy = next((enemy for enemy in possible_enemies if enemy.name == enemy_name), None)
                    retry_count += 1

                if selected_enemy is None:
                    selected_enemy = random.choice(possible_enemies)
                    log_error(f"Enemy name provided by agent did not match any of the available enemies. Falling back to random selection...")

                enemy_count = scene.encounter.xp_budget // selected_enemy.xp_value
                for _ in range(max(enemy_count, 1)):
                    selected_enemy.url = "https://2e.aonprd.com" + selected_enemy.url
                    scene.encounter.enemies.append(selected_enemy)

                # Log chosen enemies for encounter
                log_output(f" - Act {act.act_number}, Scene {scene.scene_number} - {selected_enemy.name} ({selected_enemy.xp_value} XP) x {enemy_count}")

                # Set GM Information for encounter
                scene.encounter.gm_information = f"This is a combat encounter between the players and {enemy_count} x {selected_enemy.name} (Level {selected_enemy.level}). Use the stat block for the enemy provided at the enemy's Archives of Nethys URL."
            else:
                pass

    log_success("Quest combat encounter enemies selected...")
    
    return current_quest

def generate_encounter_hazards(current_quest: Quest) -> Quest:
    """
    Generates the hazards for each hazard type encounter.

    Args:
        current_quest: The Quest object to generate hazards for.
    
    Returns:
        Quest: The Quest object with hazards generated.
    """
    log_status("Generating encounter hazards for quest...")
    
    log_output("Quest Hazard Encounters:")
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "hazard" and scene.encounter.encounter_type == "hazard":
                possible_hazards = get_possible_hazards(scene.encounter.level)
                if not possible_hazards:
                    log_error(f"No hazards found for encounter level {scene.encounter.level}.")
                    continue
                elif len(possible_hazards) == 1:
                    selected_hazard = possible_hazards[0]
                else:
                    encounter_hazard_agent = get_encounter_hazard_agent()
                    prompt = "# Quest Information:\n"
                    prompt += f"Quest Theme: {current_quest.theme}\n"
                    prompt += f"Quest Setting: {current_quest.setting}\n"
                    prompt += f"Quest Summary: {current_quest.summary}\n\n"
                    prompt += "# Act Information:\n"
                    prompt += f"Act Summary: {act.summary}\n\n"
                    prompt += "# Scene Information:\n"
                    prompt += f"Scene Summary: {scene.summary}\n"
                    prompt += f"Scene Location: {scene.location}\n\n"
                    prompt += "# Available Hazards:\n"
                    for hazard in possible_hazards:
                        prompt += f"Name: {hazard.name}\n"
                        prompt += f"- Description: {hazard.description}\n"
                    prompt += "# Task:\n\n"
                    prompt += "Select the most appropriate hazard for the scene."
                    
                    with console.status(f"[bold cyan]AI Agent is selecting appropriate hazard for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = encounter_hazard_agent.run_sync(prompt)
                    hazard_name = result.output.strip()
                    
                    selected_hazard = next((hazard for hazard in possible_hazards if hazard.name == hazard_name), None)

                    if selected_hazard is None:
                        log_error(f"Hazard name provided by agent ({hazard_name}) did not match any of the available hazards. Trying again...")
                        prompt += "Remember that you must select a hazard from the available hazards list and output the exact name of the hazard. Do not output the count of hazards or any other information."
            
                    while selected_hazard is None:
                        with console.status(f"[bold cyan]AI Agent is re-selecting appropriate hazard for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                            result = encounter_hazard_agent.run_sync(prompt)
                        hazard_name = result.output.strip()
                        
                        selected_hazard = next((hazard for hazard in possible_hazards if hazard.name == hazard_name), None)
                
                selected_hazard.url = "https://2e.aonprd.com" + selected_hazard.url
                scene.encounter.hazard = selected_hazard
                log_output(f" - Act {act.act_number}, Scene {scene.scene_number} - {selected_hazard.name} (Level {selected_hazard.level})")

                # Set GM Information for encounter
                scene.encounter.gm_information = f"This is a hazard encounter between the players and a {selected_hazard.name} (Level {selected_hazard.level}). Remember that the players should be unaware of the hazard's presence despite what the scene and encounter introduction may describe. Use the stat block for the hazard provided at the hazard's Archives of Nethys URL."

    log_success("Quest hazard encounters generated...")

    return current_quest

def generate_quest_obstacles(current_quest: Quest) -> Quest:
    """
    Generates the obstacles for each skill challenge scene in the quest.

    Args:
        current_quest: The Quest object to generate obstacles for.
    
    Returns:
        Quest: The Quest object with obstacles generated.
    """
    log_status("Generating obstacles for quest...")

    obstacle_concepts_creation_agent = get_obstacle_concepts_creation_agent()
    obstacle_concepts_extraction_agent = get_obstacle_concepts_extraction_agent()

    obstacle_skills_agent = get_obstacle_skills_agent()

    obstacle_hazard_stats_agent = get_obstacle_hazard_stats_agent()
    
    log_output("Quest Obstacles:")
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "skill challenge" and scene.encounter.encounter_type == "skill challenge":
                log_output(f" - Act {act.act_number}, Scene {scene.scene_number}:")

                # Get list of obstacles
                prompt = "# Scene Information:\n"
                prompt += f" - Summary: {scene.summary}\n"
                prompt += f" - Location: {scene.location}\n\n"
                prompt += "# Task:\n"
                prompt += "Create a series of 6 to 10 obstacles for the players to overcome in the current scene."

                with console.status(f"[bold cyan]AI Agent is creating obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = obstacle_concepts_creation_agent.run_sync(prompt)
                raw_obstacle_concepts = result.output

                with console.status(f"[bold cyan]AI Agent is extracting obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = obstacle_concepts_extraction_agent.run_sync(raw_obstacle_concepts)
                obstacle_concepts = result.output

                while len(obstacle_concepts) < 6 or len(obstacle_concepts) > 10:
                    log_error(f"Incorrect number of obstacles were generated for Act {act.act_number}, Scene {scene.scene_number}. Retrying...")
                    with console.status(f"[bold cyan]AI Agent is re-generating obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = obstacle_concepts_creation_agent.run_sync(prompt)
                    raw_obstacle_concepts = result.output

                    with console.status(f"[bold cyan]AI Agent is re-extracting obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = obstacle_concepts_extraction_agent.run_sync(raw_obstacle_concepts)
                    obstacle_concepts = result.output
                
                scene.encounter.obstacles = []
                for obstacle_concept in obstacle_concepts:
                    obstacle = Obstacle(
                        name = obstacle_concept.name,
                        description = obstacle_concept.description,
                        success_resolution = obstacle_concept.success_resolution,
                        failure_resolution = obstacle_concept.failure_resolution,
                        is_hazard = obstacle_concept.is_hazard
                    )

                    log_output(f" - - {obstacle.name}: {obstacle.description}")
                    log_output(f" - - - Success: {obstacle.success_resolution}")
                    log_output(f" - - - Failure: {obstacle.failure_resolution}")
                    
                    # Get skills to overcome the obstacle
                    prompt = "# Obstacle Information:\n"
                    prompt += f" - Name: {obstacle.name}\n"
                    prompt += f" - Description: {obstacle.description}\n"
                    prompt += f" - Success Resolution: {obstacle.success_resolution}\n"
                    prompt += f" - Failure Resolution: {obstacle.failure_resolution}\n\n"
                    prompt += "# Available Skills:\n\n"
                    prompt += get_skills_with_descriptions() + "\n\n"
                    prompt += "# Task:\n"
                    prompt += "Create a list of four skills with their difficulties from the available skills that could be used to overcome the obstacle."
                                      
                    with console.status(f"[bold cyan]AI Agent is selecting skills for obstacle "
                        f"'{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", 
                        spinner="dots"):  
                        result = obstacle_skills_agent.run_sync(prompt)
                    obstacle_skills = result.output

                    while len(obstacle_skills) != 4:
                        log_error(f"Incorrect number of skills were generated for obstacle '{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}. Retrying...")
                        with console.status(f"[bold cyan]AI Agent is re-generating skills for obstacle '{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):  
                            result = obstacle_skills_agent.run_sync(prompt)
                        obstacle_skills = result.output

                    log_output(" - - - Skills:")
                    for skill in obstacle_skills:
                        obstacle_skill = ObstacleSkill(
                            skill = skill.skill,
                            difficulty = get_obstacle_skill_dc(scene.encounter.level, skill.difficulty)
                        )
                        log_output(f" - - - - {obstacle_skill.skill}: DC {obstacle_skill.difficulty}")
                        obstacle.skills.append(obstacle_skill)
                    
                    log_output(f" - - - Is Hazard: {obstacle.is_hazard}")
                    if obstacle.is_hazard:
                        log_output(" - - - Hazard Stats:")

                        # Get hazard stats
                        prompt = "# Hazardous Obstacle Information:\n"
                        prompt += f" - Name: {obstacle.name}\n"
                        prompt += f" - Description: {obstacle.description}\n"
                        prompt += f" - Success Resolution: {obstacle.success_resolution}\n"
                        prompt += f" - Failure Resolution: {obstacle.failure_resolution}\n\n"
                        prompt += "# Task:\n"
                        prompt += "Determine the hazard type and save type for the hazard."

                        with console.status(f"[bold cyan]AI Agent is determining the hazard type and save type for the obstacle "
                            f"'{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", 
                            spinner="dots"):
                            result = obstacle_hazard_stats_agent.run_sync(prompt)
                        hazard_stats = result.output

                        obstacle.hazard_stats = get_obstacle_hazard_stats(hazard_stats.hazard_type, hazard_stats.save_type, max(-1, scene.encounter.level))
                        
                        log_output(f" - - - - Hazard Level: {obstacle.hazard_stats.level}")
                        log_output(f" - - - - Hazard Type: {obstacle.hazard_stats.hazard_type}")
                        log_output(f" - - - - Attack: {obstacle.hazard_stats.attack}")
                        log_output(f" - - - - Damage: {obstacle.hazard_stats.damage}")
                        log_output(f" - - - - Save Type: {obstacle.hazard_stats.save_type}")
                        log_output(f" - - - - Save DC: {obstacle.hazard_stats.area_dc}")            
            
                    scene.encounter.obstacles.append(obstacle)

                # Set number of rounds the party has to complete the skill challenge: 2 * the number of obstacles
                scene.encounter.rounds = 2 * len(scene.encounter.obstacles)
                log_output(f" - Rounds: {scene.encounter.rounds}")
                
                # Set victory points required for success: 3 + 2 * number of obstacles
                scene.encounter.victory_points_required = 3 + (2 * len(scene.encounter.obstacles))
                log_output(f" - Victory Points required: {scene.encounter.victory_points_required}")

                # Set GM Information for encounter
                scene.encounter.gm_information = f"A skill challenge uses the Victory Point subsystem found at https://2e.aonprd.com/Rules.aspx?ID=3028. The players have a limited number of rounds ({scene.encounter.rounds}) to overcome all obstacles, attempting a skill check each round against the current obstacle. A critical success earns the party 2 victory points. A success earns the party 1 victory point. A failure results in nothing happening. A critical failure results in the loss of a victory point. If an obstacle is a hazard and a character fails their check, they must make a basic save and take the listed damage for the hazard on a failure (half on success, none on critical success, double on critical failure)."

    log_success("Quest obstacles generated...")

    return current_quest

def generate_encounter_rewards(current_quest: Quest) -> Quest:
    """
    Generates the encounter rewards for each scene's encounter.

    Args:
        current_quest: The Quest object to generate encounter rewards for.
    
    Returns:
        The Quest object with encounter rewards generated.
    """
    log_status("Generating encounter rewards for quest...")

    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter.reward_budget == 0:
                continue
            possible_reward_items = get_possible_item_rewards(current_quest.party_level, scene.encounter.reward_budget)
            
            log_output(f"Act {act.act_number}, Scene {scene.scene_number}:")
            log_output(f" - Encounter Reward Budget: {scene.encounter.reward_budget} gp")
            
            prompt = "# Current Scene Information:\n"
            prompt += f"Current Scene Summary: {scene.summary}\n"
            prompt += f"Current Scene Location: {scene.location}\n"
            prompt += f"Current Scene Encounter Type: {scene.encounter.encounter_type}\n"
            if scene.encounter.encounter_type == 'combat':
                prompt += f"Current Scene Encounter Enemy: {scene.encounter.enemies[0].name}\n"
                prompt += f"Current Scene Encounter Enemy Description: {scene.encounter.enemies[0].description}\n"
                prompt += f"Current Scene Encounter Enemy Count: {len(scene.encounter.enemies)}\n"
            elif scene.encounter.encounter_type == 'social':
                prompt += "Current Scene Encounter NPCs:\n"
                for quest_npc in current_quest.npcs:
                    for scene_role in quest_npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f" - NPC Name: {quest_npc.name}\n"
                            prompt += f" - - Scene Role: {scene_role.role}\n"
            elif scene.encounter.encounter_type == 'hazard':
                prompt += f"Current Scene Encounter Hazard: {scene.encounter.hazard.name}\n"
                prompt += f"Current Scene Encounter Hazard Description: {scene.encounter.hazard.description}\n"
            else:
                prompt += "Current Scene Encounter Obstacles:\n"
                for obstacle in scene.encounter.obstacles:
                    prompt += f" - Name: {obstacle.name}\n"
                    prompt += f" - Description: {obstacle.description}\n"
            prompt += "\n"
            prompt += "# Available Reward Items:\n"
            prompt += possible_reward_items
            prompt += "\nSelect  the most appropriate or best reward item."
            
            with console.status(f"[bold cyan]AI Agent is selecting an encounter reward for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                result = get_encounter_rewards_agent().run_sync(prompt)
            reward_item_name = result.output.strip()
            
            reward_item = get_item_details(reward_item_name)

            retry_limit = 0
            while reward_item is None and retry_limit < 10:
                log_error("Item not found. Re-selecting...")
                with console.status(f"[bold cyan]AI Agent is re-selecting an encounter reward for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = get_encounter_rewards_agent().run_sync(prompt)
                reward_item_name = result.output.strip()
                reward_item = get_item_details(reward_item_name)
                retry_limit += 1

            if reward_item is None:
                log_error("Item not found after retries. Selecting random reward item...")
                reward_item_name = get_random_item(current_quest.party_level, scene.encounter.reward_budget)
                reward_item = get_item_details(reward_item_name)

            scene.encounter.rewards.append(reward_item)

            remaining_budget = scene.encounter.reward_budget - reward_item.price
            if remaining_budget > 0:
                currency_reward = Reward(
                    name="Coins and Gems",
                    reward_type="currency",
                    price=remaining_budget,
                    description=f"An assortment of coins and gems worth {remaining_budget} gp.",
                    url=""
                )
                scene.encounter.rewards.append(currency_reward)
            
            log_output(" - Encounter Rewards:")
            for reward in scene.encounter.rewards:
                log_output(f" - - {reward.name} ({reward.price} gp): {reward.description}")
    
    log_success("Encounter rewards generated...")

    return current_quest

def generate_encounter_details(current_quest: Quest) -> Quest:
    """
    Generates the encounter details for each scene: the introduction, description and resolution
    
    Args:
        current_quest: The Quest object to generate encounter details for.
    
    Returns:
        The Quest object with encounter details generated.
    """

    log_status("Generating encounter details for quest...")

    encounter_details_creation_agent = get_encounter_details_creation_agent()
    encounter_details_extraction_agent = get_encounter_details_extraction_agent()
    
    for act in current_quest.acts:
        for scene in act.scenes:
            log_output(f"Act {act.act_number}, Scene {scene.scene_number}:")
            prompt = "# Scene Information:\n"
            prompt += f"Scene Summary: {scene.summary}\n"
            prompt += f"Scene Location: {scene.location}\n"
            prompt += f"Scene Introduction: {scene.introduction}\n"
            prompt += f"Scene Description: {scene.description}\n"
            prompt += f"Scene Resolution: {scene.resolution}\n"
            prompt += "# Encounter Information:\n"
            prompt += f"Encounter Type: {scene.encounter.encounter_type}\n"
            if scene.encounter.encounter_type == 'combat':
                prompt += f"Encounter Enemy: {scene.encounter.enemies[0].name}\n"
                prompt += f"Encounter Enemy Description: {scene.encounter.enemies[0].description}\n"
                prompt += f"Encounter Enemy Count: {len(scene.encounter.enemies)}\n"
            elif scene.encounter.encounter_type == 'social':
                prompt += "Encounter NPCs:\n"
                for quest_npc in current_quest.npcs:
                    for scene_role in quest_npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f" - NPC Name: {quest_npc.name}\n"
                            prompt += f" - - Scene Role: {scene_role.role}\n"
            elif scene.encounter.encounter_type == 'hazard':
                prompt += f"Encounter Hazard: {scene.encounter.hazard.name}\n"
                prompt += f"Encounter Hazard Description: {scene.encounter.hazard.description}\n"
            else:
                prompt += "Encounter Obstacles:\n"
                for obstacle in scene.encounter.obstacles:
                    prompt += f" - Name: {obstacle.name}\n"
                    prompt += f" - Description: {obstacle.description}\n"
            prompt += "\n"
            prompt += "# Task:\n\n"
            prompt += "Expand the information of the scene's encounter into three detailed sections."

            with console.status(f"[bold cyan]AI Agent is generating encounter details for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                result = encounter_details_creation_agent.run_sync(prompt)
                raw_encounter_details = result.output

            with console.status(f"[bold cyan]AI Agent is extracting encounter details for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                result = encounter_details_extraction_agent.run_sync(raw_encounter_details)
                encounter_details = result.output
            
            scene.encounter.introduction = encounter_details.introduction
            log_output(f" - Encounter Introduction: {scene.encounter.introduction}")
            scene.encounter.description = encounter_details.description
            log_output(f" - Encounter Description: {scene.encounter.description}")
            scene.encounter.resolution = encounter_details.resolution
            log_output(f" - Encounter Resolution: {scene.encounter.resolution}")
    
    log_success("Encounter details generated...")

    return current_quest