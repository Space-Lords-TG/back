from src.application.config_loader import config

ARENA_TUTORIAL_TEXT = f"""
На арене игроки могут сразиться друг с другом из любого места галактики. Формат сражения: 1 на 1.
Противники подбираются так, чтобы общая мощь кораблей отличалась друг от друга не  более, чем на {config["game"]["match_power_threshold"]}. Урон пушек во время боя случайным образом меняет значение в интервале ±{config["game"]["damage_deviation"]}%.
Награда за бой зависит от результата и от разницы мощи кораблей. Полученный здоровьем урон не восстанавливается автоматически — необходимо отремонтировать корпус.\n\n
"""

SHIP_TUTORIAL_TEXT = """
Здесь описаны все характеристики твоего корабля:
- Скорость -- количество выстрелов за единицу времени.
- Урон -- количество повреждений, которое наносится при атаке.
- Крит. частота -- вероятность нанести крит. удар.
- Крит. урон -- множитель урона при крит. ударе.
- Защита -- кол-во урона, вычитаемое из любой атаки противника.
- Манёвренность -- шанс уклониться от атаки.
- Щиты -- поглощают весь урон до полного истощения. Восстанавливаются бесплатно после каждого боя.
- Здоровье -- при падении до нуля корабль выходит из строя. Вычитается только при полностью истощённых щитах. Для восстановления необходим ремонт корабля.

На корабле установленны модули:
- пушка отвечает на урон, крит. частота, крит. урон и скорость;
- корпус влияет на здоровье, щиты, защиту и манёвренность.

В подменю можно посмотреть, заменить и улучшить выбранные модули. Пушки улучшаются за кристаллы, а корпуса -- за металл.

Для восстановления здоровья корабля необходимо произвести ремонт, стоимость и время которого зависит от потерянного здоровья.\n\n
"""

DEFAULT_TUTORIAL_TEXT = """
В этом меню содержится информация о статусе корабля и имеющихся ресурсах. Если корабль находится на орбите планеты, можно посмотреть её характеристики.\n\n
"""

PLANET_TUTORIAL_TEXT = """
На этом экране содержися информация о планете, её характеристики можно посмотреть только при выходе на её орбиту.
По каждой планете отображается:
- название
- тип
- объём производимых ресурсов
- вместимость ресурсов
- статус

От типа планеты зависит производимый на ней ресурс: металл производят каменные планеты, кристаллы -- ледяные, а газ -- газовые.
Произведённые планетой ресурсы необходимо своевременно собирать, т.к. они перестанут производиться, если склад заполнится.

Планета может обладать тремя состояниями:
- свободна, на ней можно построить аванпост;
- занята, тогда для использования нужно победить в бою её владельца;
- принадлежит тебе, в таком случае её можно улучшать и собирать ресурсы.\n\n
"""

ARENA_STATS_TEXT = """Арена

Характеристики вашего корабля:
Скорость: {speed_gun:.0f}
Урон: {damage_gun:.0f}
Шанс крита: {crit_rate_gun:.2f}%
Крит. урон: {crit_damage_gun:.2f}x
Защита: {armor_hull:.0f}
Щиты: {shields_hull:.0f}
Манёвренность: {maneuver_hull:.2f}

Вы можете встать в очередь, система найдёт подходящего оппонента.

Бой начнётся автоматически.
"""

ARENA_QUEUE_TEXT = """<b>Ваш корабль сейчас на ремонте!</b>

Вы не можете участвовать в битве, пока ремонт не завершён.

Завершение ремонта: <b>{time_str}</b>
"""

ARENA_QUEUE_ZERO_HEALTH_TEXT = """<b>Здоровье вашего корабля равно 0.</b>

Вы не можете участвовать в битве, пока не отремонтируете корабль.
"""

ARENA_QUEUE_REPAIR_TEXT = """<b>Ваш корабль сейчас на ремонте!</b>

Вы не можете участвовать в битве, пока ремонт не завершён.

Завершение ремонта: <b>{time_str}</b>
"""

ARENA_IN_QUEUE_TEXT = """<b>Арена</b>

<b>Поиск противника...</b>

Вы находитесь в очереди.
Ожидаем подходящего соперника...

Характеристики вашего корабля:
Скорость: {speed_gun:.2f}
Урон: {damage_gun:.2f}
Шанс крита: {crit_rate_gun:.2f}%
Крит. урон: {crit_damage_gun:.2f}x
Защита: {armor_hull:.2f}
Щиты: {shields_hull:.2f}
Манёвренность: {maneuver_hull:.2f}

Мощь: {power_score:.2f}
"""

# Ship module texts
SHIP_MAIN_TEXT = """Ваш корабль:

Скорость: {speed_gun}
Урон: {damage_gun}
Шанс крита: {crit_rate_gun}%
Крит. урон: {crit_damage_gun}x
Защита: {armor_hull}
Щиты: {shields_hull}
Манёвренность: {maneuver_hull}
Здоровье корабля: {health}/{max_health_hull}

Установленные модули:
Оружие — <b>{name_gun}</b>
Корпус — <b>{name_hull}</b>

Вы можете настроить модули в этом меню.
"""

WEAPON_INFO_TEXT = """<b>Оружие</b>

На данный момент установлено:
<b>{name_gun}</b>
Уровень: {level_gun}

Характеристики:
Урон: {damage_gun}
Крит. частота: {crit_rate_gun}%
Крит. урон: {crit_damage_gun}x
Скорость: {speed_gun}

Мощь: {power_gun:.2f}

Стоимость улучшения:
{cost:,} кристаллов
"""

WEAPON_UPGRADE_PREVIEW_TEXT = """<b>Оружие</b>

Вы хотите улучшить:
<b>{name_gun}</b>
Уровень: {current_level} ➜ {next_level}

Урон: {current_damage:.2f} ➜ {next_damage:.2f}
Крит. частота: {current_crit_rate:.2f}% ➜ {next_crit_rate:.2f}%
Крит. урон: {current_crit_damage:.2f}x ➜ {next_crit_damage:.2f}x
Скорость: {current_speed:.2f} ➜ {next_speed:.2f}

Мощь: {current_power:.2f} ➜ {next_power:.2f}

Стоимость улучшения:
{cost:,} кристаллов
"""

WEAPON_UPGRADE_SUCCESS_TEXT = """<b>Оружие улучшено!</b>

<b>{name_gun}</b> теперь имеет:
Уровень: {level_gun}
Урон: {damage_gun:.2f}
Крит. шанс: {crit_rate_gun:.2f}%
Крит. урон: {crit_damage_gun:.2f}x
Скорость: {speed_gun:.2f}

Мощь: {power_gun:.2f}
"""

WEAPON_CHANGE_TEXT = """<b>Оружие</b>

На данный момент установлено:
<b>{name_gun}</b>
Уровень: {level_gun}

Характеристики:
Урон: {damage_gun:.2f}
Крит. частота: {crit_rate_gun:.2f}%
Крит. урон: {crit_damage_gun:.2f}x
Скорость: {speed_gun:.2f}

Мощь: {power_gun:.2f}

Вы можете выбрать оружие для замены:
"""

WEAPON_CHANGE_SUCCESS_TEXT = """<b>Оружие заменено!</b>

<b>{name_gun}</b> устновлен.
Уровень: {level_gun}

Новые характеристики:
Урон: {damage_gun:.2f}
Крит. шанс: {crit_rate_gun:.2f}%
Крит. урон: {crit_damage_gun:.2f}x
Скорость: {speed_gun:.2f}

Мощь: {power_gun:.2f}
"""

HULL_INFO_TEXT = """<b>Корпус:</b>

На данный момент установлен:
<b>{name_hull}</b>
Уровень: {level_hull}

Характеристики:
Здоровье: {max_health_hull:.0f}
Защита: {armor_hull:.0f}
Щиты: {shields_hull:.0f}
Манёвренность: {maneuver_hull:.2f}

Мощь: {power_hull:.2f}

Стоимость улучшения:
{cost:,} металлов
"""

HULL_UPGRADE_PREVIEW_TEXT = """<b>Улучшение корпуса</b>

<b>{name_hull}</b>
Уровень: {current_level} ➜ {next_level}

Здоровье: {current_health:.0f} ➜ {next_health:.0f}
Защита: {current_armor:.2f} ➜ {next_armor:.2f}
Щиты: {current_shields:.2f} ➜ {next_shields:.2f}
Манёвренность: {current_maneuver:.2f} ➜ {next_maneuver:.2f}

Мощь: {current_power:.2f} ➜ {next_power:.2f}

Стоимость улучшения:
{cost:,} металлов
"""

HULL_UPGRADE_SUCCESS_TEXT = """<b>Корпус улучшен!</b>

<b>{name_hull}</b>
Уровень: {level_hull}

Новые характеристики:
Здоровье: {max_health_hull:.0f}
Защита: {armor_hull:.0f}
Щиты: {shields_hull:.0f}
Манёвренность: {maneuver_hull:.2f}

Мощь: {power_hull:.2f}
"""

HULL_CHANGE_TEXT = """<b>Корпус</b>

На данный момент установлен:
<b>{name_hull}</b>
Уровень: {level_hull}

Характеристики:
Здоровье: {max_health_hull:.0f}
Защита: {armor_hull:.0f}
Щиты: {shields_hull:.0f}
Манёвренность: {maneuver_hull:.2f}

Мощь: {power_hull:.2f}

Вы можете выбрать корпус для замены:
"""

HULL_CHANGE_SUCCESS_TEXT = """<b>Корпус заменён!</b>

<b>{name_hull}</b>
Уровень: {level_hull}

Новые характеристики:
Здоровье: {max_health_hull:.0f}
Защита: {armor_hull:.0f}
Щиты: {shields_hull:.0f}
Манёвренность: {maneuver_hull:.2f}

Мощь: {power_hull:.2f}
"""

REPAIR_INFO_TEXT = """<b>Ремонт корпуса:</b>

Текущее здоровье корпуса:
{current_health:.0f} / {max_health:.0f} ({(health_percent):.1f}%)

{repair_status}
"""

REPAIR_COSTS_TEXT = """Стоимость ремонта:
{cost_metals} металлов
{cost_crystalls} кристаллов

Время ремонта:
{cooldown_minutes} мин {cooldown_seconds} сек
"""

REPAIR_STARTED_TEXT = """<b>Ремонт запущен!</b>

Восстановится здоровье: {restored_health} / {max_health}
Списано кристаллов: {cost_crystalls}
Списано металлов: {cost_metals}
Завершение через: {cooldown_minutes} мин {cooldown_seconds} сек
"""

REPAIR_IN_PROGRESS_TEXT = """Оставшееся время ремонта:
{minutes_left} мин {seconds_left} сек

<i>Завершение в {end_time}</i>
"""

REPAIR_COMPLETE_TEXT = """Корпус полностью отремонтирован.
"""

NOT_ENOUGH_RESOURCES_TEXT = """<b>Недостаточно ресурсов</b>

Нужно: {required}
У вас: {available}
"""

# Planet module texts
PLANET_FREE_TEXT = """Планета
{name}

Доступные ресурсы:
{production_rate} {resource_type}/час

Вместимость (уровень {level}):
{capacity} {resource_type}

Планета свободна

Стоимость постройки аванпоста:
{claim_cost_metal} металла
{claim_cost_fuel} топлива
"""

PLANET_OWNED_TEXT = """Планета
{name}
Уровень {level}

Производство:
{production_rate} {resource_type}/час

Накоплено ресурсов:
{stored}/{capacity} {resource_type}

Доступно улучшение до уровня {next_level}:
{upgrade_cost_crystals} кристаллов
{upgrade_cost_metal} металлов
Вы владеете этой планетой.
"""

PLANET_UPGRADE_PREVIEW_TEXT = """Планета (улучшение)
Вы хотите улучшить:
{name}

Текущие показатели / улучшение:
Кристаллы: {current_crystal_rate}/час -> {next_crystal_rate}/час
Металлы: {current_metal_rate}/час -> {next_metal_rate}/час
Вместимость:
{current_crystal_capacity} (К), {current_metal_capacity} (М)
-> {next_crystal_capacity} (К), {next_metal_capacity} (М)

Стоимость улучшения:
{upgrade_cost_crystals} кристаллов
{upgrade_cost_metal} металлов
"""

PLANET_ENEMY_TEXT = """Планета
{name}

Производство:
{production_rate} {resource_type}/час
Планета занята игроком {owner_name}
Скорость: {owner_speed}
Урон: {owner_damage}
Шанс крита: {owner_crit_rate}%
Крит. урон: {owner_crit_damage}%
Защита: {owner_armor}
Щиты: {owner_shields}
Манёвренность: {owner_maneuver}
Здоровье: {owner_health}
"""

PLANET_FIGHT_RESULT_TEXT = """Результаты боя

Вы: {player_name} ({player_power} 💪)
Противник: {enemy_name} ({enemy_power} 💪)
Статистика боя:
Нанесено урона: {damage_dealt}
Получено урона: {damage_received}
Раундов: {rounds}
Оставшаяся прочность: {health_left} ({health_percent}%)

Итог: {result}!
{additional_message}
"""

PLANET_CLAIM_SUCCESS_TEXT = """Аванпост построен!
Теперь вы владеете планетой {name}.

Получено начальных ресурсов:
{initial_resources} {resource_type}
"""

PLANET_GATHER_SUCCESS_TEXT = """Ресурсы собраны!

С планеты {name} получено:
{gathered_amount} {resource_type}

Текущие запасы:
{remaining_amount}/{capacity} {resource_type}
"""

PLANET_UPGRADE_SUCCESS_TEXT = """Планета улучшена!

{name} теперь имеет:
Уровень: {level}
Производство: {production_rate} {resource_type}/час
Вместимость: {capacity} {resource_type}
"""

PLANET_NOT_ENOUGH_RESOURCES_TEXT = """<b>Недостаточно ресурсов</b>

Нужно:
{required_crystals} кристаллов (у вас: {available_crystals})
{required_metal} металлов (у вас: {available_metal})
{required_fuel} топлива (у вас: {available_fuel})
"""

# Main menu texts
DEFAULT_MENU_TEXT = """Главный экран
<b>Добро пожаловать!</b>

Вы можете настроить свой корабль воспользовавшись кнопками ниже.
Разделы "карта" и "просмотр планеты" in development.
Так же вы можете сразиться с другими игроками на арене,
система найдёт вам подходящего оппонента.

<b>Ваши ресурсы</b>
Кристаллы: {crystalls}
Металлы: {metals}
Газы: {gas}
"""

RESOURCES_TEXT = """<b>Ваши ресурсы</b>
Кристаллы: {crystalls}
Металлы: {metals}
Газы: {gas}
"""

# Map module texts
MAP_TEXT = """Текущая система:
<b>{current_system}</b>

Выберите, к какой планете переместиться:
{planet_list}"""

PLANET_TRAVEL_TEXT = """Текущая планета:
{current_planet}

Пункт назначения:
{destination_planet}

Расстояние:
{distance} пк.

Время в пути:
{travel_time}.

Текущий движок:
{engine_speed} пк/час.
"""

SECTORS_TEXT = """
Текущая система:
<b>{current_system}</b>

Выберите, в какую систему переместиться:
{sectors_list}
"""

SECTOR_TRAVEL_TEXT = """Текущая система:
{current_system}

Пункт назначения:
{destination_sector}

Расстояние:
{distance} пк.

Время в пути:
{travel_time}.

Текущий движок:
{engine_speed} пк/час.
"""

FLIGHT_REQUEST_TEXT = """Запрос на перемещение принят!

Направление: {destination}
Расстояние: {distance} пк
Ожидаемое время прибытия: {arrival_time}
"""

PLANET_LIST_ITEM = """{name} ({distance} пк)"""
SECTOR_LIST_ITEM = """{name} ({distance} пк)"""

# Admin module texts
ADMIN_MAIN_TEXT = """Админка

Вы находитесь на главном экране админки.

Выберите действие:
"""

ADMIN_UTM_LIST_TEXT = """Админка

Список UTM меток (Название тега: кол-во вызовов start с этой меткой):
{utm_list}
"""

ADMIN_CREATE_UTM_TEXT = """Админка

Введите тег для новой UTM метки:
<code>/utm ТЕГ_МЕТКИ</code>
"""

ADMIN_REGISTRATION_INFO_TEXT = """Админка

Введите команду для просмотра зарегистрированных пользователей:
<code>/get_users day/week/month/year/all</code>
"""

ADMIN_PLAYER_TABLES_TEXT = """Админка

Введите команду для просмотра таблиц игрока:
<code>/get_user_info ИМЯ_ПОЛЬЗОВАТЕЛЯ</code>
"""

ADMIN_SET_RESOURCES_TEXT = """Админка

Введите команду для установки ресурсов игрока:
<code>/set_resources ИМЯ_ПОЛЬЗОВАТЕЛЯ ТИП_РЕСУРСА КОЛИЧЕСТВО</code>

Пример: /set_resources john_doe metals 1000
Доступные типы ресурсов: metals, crystalls, gas
"""

ADMIN_BROADCAST_TEXT = """Админка

Введите команду для оповещения игроков:
<code>/broadcast СООБЩЕНИЕ</code>
"""

UTM_LINK_TEMPLATE = "https://t.me/{bot_name}?start={tag}"
UTM_ITEM_TEXT = "{tag}: {used}\nСсылка: <code>{link}</code>\n"
