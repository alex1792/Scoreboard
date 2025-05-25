# Scoreboard
Scoreboard project  
I want to build a live scoreboard system for all kind of ball games. The umpire can 
update the score by using smartphones or laptop, other users can check the live score by accessing 
the scoreboard page.  
  
As for backend, the admin can manipulate users to be an umpire or not. Maintaining the 
database etc.

## introduction
Homepage: Homepage with register and login function. When logged in, user can see more function. Guest can only access scoreboard.
Scoreboard: Scoreboard page, where umpire can update score, guests can check the score.

ideas (not implemented yet): Stack all the score adjustment history, implementing the recovery function to re-do the score update.

ideas for current version adjustment：
  1. check each score info(Scoreboard) via check_all_match page 
  2. create multiple matches, umpire. manage each match with assigning particular umpire to adjust the game.
  3. better javascript, css
  4. each match-card links individual scoreboard, now only links to the same scoreboard

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
assign_umpire: http://127.0.0.1:5001/assign_umpire

## activate and deactivate virtual environment
. .venv/bin/activate  
deactivate

## Developing Diary
### 2025/04/02
- Finish login function
---

### 2025/04/03
- Score adjustment funciton (only when logged in)
---

### 2025/04/04
- Score update in real time and syncronization:
  - Every user will upadte the score in real time.
---

### 2025/04/05
- Creating Manage Umpire funciton: 
  - only `alex` can access the manage function, can assign users to be an umpire or not
---

### 2025/04/06
- Set the upper bound of score and access to score adjustment:  
  - Only umpire can adjust the score by clicking the button  
---

### 2025/04/07
- Creating minus points button
- Update `scoreboard.html`：  
  - inherits `base.html`  
- Update `/users` page：  
  - used for query all users in database
---

### 2025/04/08
- Expand Database class functions：  
  - Adding more Query function, simplify the process of executing queries in `routes.py`：
    ```
    db = Database('database.db')
    db.query_function()
    db.close()
    ```
- Added new competition management functions and pages：  
  - Clear all matches in the database with one click  
  - Delete match according to `match_id` 
  - Showing (schedule, ongoing, finished), and synchronously update to the scoreboard  
---

### 2025/04/09
- Improvements to the page for viewing all matches: 
  - showing `match_id`, `player1_name`, `player2_name`, `score1`, `score2`, `status`  
- Combine score updates and status updates into the same broadcast function   
- Instantly update the score and status to the `check all_match` page
- Add different CSS beautification effects (to be enhanced)
---

### 2025/04/10
- Modify the layout：  
  - Move CSS from HTML to separate `.css` files  
- Improve `check all matches` page：  
  - All match-cards are hyperlinks pointing to the scoreboard page
---

### 2025/04/11
- Modify the layout
---

### 2025/05/01
- Add assigning umpire to each match in the update_score function. Slightly change the database table matches, adding a umpire_name in each match.
- http://127.0.0.1:5001/assign_umpire
---

### 2025/05/23
- Modify the structure by implementing SQLAlchemy, and improve permision checking on users
- Add the assign_umpire link to home page
- still have bugs to be fixed. (assign umpires, etc)
---

### 2025/05/24
- Fixing previous bugs
- Modified database tables structures and HTML code for better maintainance
- Remove redundant codes
- Issues to be resolved: assign user as umpire, need to update user.role ✅
- Issues to be resolved: when updating score, all pages that have scores should update ✅
---