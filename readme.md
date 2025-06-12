# Space Lords

Проект телеграмм-бота @space_lords_bot

1. Жанр -- текстовое MMO-RPG
2. Сеттинг -- космический
3. Аудитория -- PVP игроки, "киллеры"

# Структура проекта
```
.
├── .github/                       
│   └── workflows/                 
│       └── ci.yml                 
├── src/                           # Основной исходный код проекта
│   ├── application/               # Бизнес-логика приложения
│   │   ├── arena_service.py       
│   │   ├── config.toml            # Конфиг
│   │   ├── config_loader.py       # Загрузчик конфига
│   │   ├── player_service.py      
│   │   ├── ship_service.py        
│   │   └── utm_service.py         
│   ├── infrastructure/            
│   │   ├── database.py            # Работа с БД
│   │   └── models.py              # Модели данных для ORM
│   ├── presentation/              # Слой представления (UI/API)
│   │   ├── screens/               # Директория с экранами
│   │   │   ├── admin.py         
│   │   │   ├── arena.py          
│   │   │   ├── mainMenu.py      
│   │   │   ├── map.py            
│   │   │   ├── planet.py         
│   │   │   ├── registry.py        
│   │   │   └── ship.py           
│   │   └── utils/                 
│   │       └── getImage.py        
│   ├── arena_matchmaker.py    
│   ├── healthcheck.py         
│   └── main.py                
├── requirements.txt               
├── .flake8                        # Конфигурация линтера
├── .gitignore                     
├── Dockerfile                     
├── pyproject.toml                 # Конфигурация проекта
└── readme.md                      
``` 