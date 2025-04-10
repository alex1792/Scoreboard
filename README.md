# Scoreboard
Scoreboard project  
I want to build a live scoreboard system for all kind of ball games. The umpire can 
update the score by using smartphones, other users can check the live score by accessing 
the scoreboard page.  
  
As for backend, the admin can manipulate users to be an umpire or not. Maintaining the 
database etc.

## introduction
Homepage: 主頁面, 註冊與登入, 登入可以看到更多功能, 訪客只能訪問scoreboard而已
Scoreboard: 分數頁面, 裁判可以更新分數, 訪客只能查看分數

額外功能:紀錄當前比賽的分數紀錄 以防裁判更新錯誤要修改

## Project Structure
```
- Scoreboard:
  - app:
    - static:
      - style.css  # Stylesheet for the application
    - templates:
      - auth:
        - login.html     # Login page template
        - register.html  # Registration page template
      - scoreboard:
        - admin.html      # Manage Users to be umpire or not
        - create_match.html # Create a new match
        - home.html       # Home page template
        - manage_match.html # Delete match by match_id
        - matches.html    # List all the matches in database
        - scoreboard.html # Scoreboard page template
        - umpire.html     # Umpire page template
        - users.html      # Query all users in database, it can show the ID, username, is_judge
      - base.html         # Base layout template for the application
    - __init__.py         # Initializes the app module
    - auth.py             # Handles authentication-related logic
    - blueprints.py       # Manages Flask blueprints
    - db.py               # Database-related utilities and models
    - extensions.py       # Extensions used in the project (e.g., Flask extensions)
    - form.py             # Defines forms for user input
    - routes.py           # Defines application routes
  - config.py             # Configuration file for the project
  - database.db           # SQLite database file
  - requirements.txt      # List of dependencies for the project
  - run.py                # Main entry point to run the application

```

## all pages links:
home: http://127.0.0.1:5001/  
scoreboard: http://127.0.0.1:5001/scoreboard  
update_score(login required): http://127.0.0.1:5001/update_score  
admin(only 'alex' can access): http://127.0.0.1:5001/admin  
users: http://127.0.0.1:5001/users 

## activate and deactivate virtual environment
. .venv/bin/activate  
deactivate

## 開發日誌：
2025/04/02 - 完成登入功能  
2025/04/03 - 完成增加分數, 只有登入後才能增加分數  
2025/04/04 - 加入更新完比分 所有用戶都會即時看到更新的分數  
2025/04/05 - 加入編輯user是否為裁判的功能, 目前設定只有alex才能manage其他user是不是裁判  
2025/04/06 - 加入只有裁判可以使用編輯分數的按鈕  
2025/04/07 - 加入減分按鈕, 修改scoreboard.html, 讓他繼承base.html; 加入/users的頁面來query all users in database  
2025/04/08 - 新增一些Query function到Database class中, 現在在routes.py要執行query, 直接db = Database('database.db'); db.query_function(); db.close()三步驟即可. 加入管理match的功能與頁面 現在可以一件清空database中的所有match, 也可以delete match by match_id. 加入顯示match status: schedule, ongoing, finished 並且同步更新在scoreboard中
2025/04/09 - 查看所有match的頁面改成是match_id, player1_name, player2_name, score1, score2, status;合併braodcast分數更新與狀態更新功能到同一個broadcast function內
目前在check_all_match中也可以即時更新分數與狀態, 並且加入了不同的css增加美觀  
