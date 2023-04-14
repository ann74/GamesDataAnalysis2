# Запрос о количестве участников, выбравших тот или иной тип боя"
team_build_type_query = """SELECT typs.cat_name as team_build_type, count(account_db_id) as amount_members
FROM arena_members
LEFT JOIN arenas on arenas.arena_id = arena_members.arena_id
LEFT JOIN (SELECT * FROM catalog_items WHERE cat_type = "TEAM_BUILD_TYPE") as typs
 on typs.cat_value = arenas.team_build_type_id
group by team_build_type;"""

# Запрос о количестве участников, выбравших тот или иной тип боя сгруппированный среди реальных пользователей и ботов"
team_build_type_by_users_and_bots_query = """SELECT typs.cat_name as team_build_type, count(account_db_id) as amount_members, account_db_id>0 as users
FROM arena_members
LEFT JOIN arenas on arenas.arena_id = arena_members.arena_id
LEFT JOIN (SELECT * FROM catalog_items WHERE cat_type = "TEAM_BUILD_TYPE") as typs
 on typs.cat_value = arenas.team_build_type_id
GROUP BY users, team_build_type
ORDER by users DESC;"""

# Запрос о количестве разных типов боев, сгруппированных по типам карт
team_build_type_by_maps_query = """SELECT maps.cat_name as map_type, typs.cat_name as team_build_type, count(arena_id) as amount
FROM arenas
LEFT JOIN (SELECT * FROM catalog_items WHERE cat_type = "TEAM_BUILD_TYPE") as typs
 on typs.cat_value = arenas.team_build_type_id
LEFT JOIN (SELECT * FROM catalog_items WHERE cat_type = "ARENA_TYPES") as maps on maps.cat_value = arenas.map_type_id
GROUP BY map_type, team_build_type;"""

# Запрос для анализа эффективности кораблей
ship_effectivity_query = """SELECT item_class as ship_class, item_name as ship_name, item_desc2 as country, avg(is_alive)*100 as alived,
    avg(am.team_id = arenas.winner_team_id)*100 as winner, avg(ships_killed) as frags,
    (avg(damage) / avg(received_damage)) as positive_damage, avg(exp), avg(distance), count(am.arena_id)
FROM arena_members as am
LEFT JOIN glossary_ships as gs on am.vehicle_type_id = gs.item_cd
LEFT JOIN arenas on am.arena_id = arenas.arena_id
WHERE account_db_id < 0
GROUP BY ship_name
HAVING count(am.arena_id) >= 50
ORDER BY ship_class;"""