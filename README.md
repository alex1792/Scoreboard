# Scoreboard
Scoreboard project

## introduction
Homepage: 登入來修改分數, 訪客觀看scores
Socres: 非裁判可以查看即時分數
Umpire: 裁判可以更新分數

額外功能:紀錄當前比賽的分數紀錄 以防裁判更新錯誤要修改

尚未完成：修改分數

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
        - home.html       # Home page template
        - scoreboard.html # Scoreboard page template
        - umpire.html     # Umpire page template
        - admin.html      # Manage Users to be umpire or not
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
home: http://0.0.0.0:5001/  
scoreboard: http://0.0.0.0:5001/scoreboard  
update_score(login required): http://0.0.0.0:5001/update_score  
admin(only 'alex' can access): http://0.0.0.0:5001/admin  
users: http://0.0.0.0:5001/users  

## 開發日誌：
2025/04/02 - 完成登入功能  
2025/04/03 - 完成增加分數, 只有登入後才能增加分數  
2025/04/04 - 加入更新完比分 所有用戶都會即時看到更新的分數  
2025/04/05 - 加入編輯user是否為裁判的功能, 目前設定只有alex才能manage其他user是不是裁判  
2025/04/06 - 加入只有裁判可以使用編輯分數的按鈕  
2025/04/07 - 加入減分按鈕, 修改scoreboard.html, 讓他繼承base.html; 加入/users的頁面來query all users in database  
