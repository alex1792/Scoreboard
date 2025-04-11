# Scoreboard
Scoreboard project  
I want to build a live scoreboard system for all kind of ball games. The umpire can 
update the score by using smartphones or laptop, other users can check the live score by accessing 
the scoreboard page.  
  
As for backend, the admin can manipulate users to be an umpire or not. Maintaining the 
database etc.

## introduction
Homepage: 主頁面, 註冊與登入, 登入可以看到更多功能, 訪客只能訪問scoreboard而已
Scoreboard: 分數頁面, 裁判可以更新分數, 訪客只能查看分數

額外功能:紀錄當前比賽的分數紀錄 以防裁判更新錯誤要修改  

修改的想法：
  1. 可以透過check_all_match的頁面點進去看每一個match的scoreboard
  2. 建立多個match, 多個umpire, 管理每場match只能由特定的umpire去編輯分數
  3. 更好看的排版 javascript, css
  4. match-card的link要連結到正該scoreboard, 目前只會direct到固定一個

## Project Structure
```
- Scoreboard:
  - app:
    - static:
      - matches.css       # Stylesheet for matches.html
      - scoreboard.css    # Stylesheet for scoreboard.html
      - style.css         # Stylesheet for the application
    - templates:
      - auth:
        - login.html      # Login page template
        - register.html   # Registration page template
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

## 開發日誌
### 2025/04/02
- 完成登入功能
---

### 2025/04/03
- 完成增加分數功能（僅限登入後使用）
---

### 2025/04/04
- 加入分數更新的即時同步功能：  
  - 所有用戶均可即時看到更新的分數
---

### 2025/04/05
- 新增裁判管理功能：  
  - 設定只有 `alex` 能管理其他用戶是否為裁判
---

### 2025/04/06
- 限制分數編輯權限：  
  - 只有裁判可以使用編輯分數的按鈕
---

### 2025/04/07
- 新增減分按鈕  
- 修改 `scoreboard.html`：  
  - 繼承 `base.html`  
- 新增 `/users` 頁面：  
  - 用於查詢資料庫中的所有用戶
---

### 2025/04/08
- 擴展 Database class 功能：  
  - 新增多個 Query function，簡化在 `routes.py` 中執行查詢的流程：
    ```
    db = Database('database.db')
    db.query_function()
    db.close()
    ```
- 新增比賽管理功能與頁面：  
  - 一鍵清空資料庫中的所有比賽  
  - 根據 `match_id` 刪除比賽  
  - 顯示比賽狀態（schedule, ongoing, finished），並同步更新到記分板中  
---

### 2025/04/09
- 改善查看所有比賽的頁面：  
  - 顯示 `match_id`, `player1_name`, `player2_name`, `score1`, `score2`, `status`  
- 合併分數更新與狀態更新至同一個 broadcast function 中  
- 即時更新分數與狀態至 `check_all_match` 頁面  
- 增加不同 CSS 美化效果（尚待加強）
---

### 2025/04/10
- 修改排版：  
  - 將 HTML 中的 CSS 移至獨立 `.css` 文件  
- 改善 `check all matches` 頁面：  
  - 所有 match-card 均為超連結，指向記分板頁面
---

