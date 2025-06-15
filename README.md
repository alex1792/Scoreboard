# Scoreboard
---

## Project Overview

- Provides real-time scoring, viewing, and management of games
- Umpire can instantly update scores; all users can view the latest results
- Admin can assign umpires and manage matches and users

## Key Features

- User login and registration
- Real-time score update and viewing
- Multi-match management and umpire assignment
- Role-based access control (Admin / Umpire / User)
- Match status management (Scheduled / Ongoing / Finished)

## Tech Stack

- **Backend:** Python Flask, SQLAlchemy, SQLite
- **Frontend:** React.js
- **Version Control:** Git

## Highlights

- Clear architecture with robust permission control
- Supports multiple matches and collaborative management
- Ongoing database and feature enhancement

---

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
    - models.py           # Database-related utilities and models
    - extensions.py       # Extensions used in the project (e.g., Flask extensions)
    - form.py             # Defines forms for user input
    - routes.py           # Defines application routes
  - config.py             # Configuration file for the project
  - database.db           # SQLite database file
  - requirements.txt      # List of dependencies for the project
  - run.py                # Main entry point to run the application

```

## activate and deactivate virtual environment
### Backend (Flask)
```
. .venv/bin/activate  
deactivate
```
---
### frontend (React)
```
. .venv/bin/activate
cd frontend
npm start
```

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

### 2025/05/26
- Modified matches.html
- Modified scoreboard.html, and scoreoard.css
---

### 2025/05/30
- Modified frontend
---


### 2025/05/31
- ideas: in all matches, add a attribute match_type {men single, men double, women single, women double, mix doble} and show it on the score card
- ideas: for doubles, if player name is too long, use abbreviation
- ideas: use Figma to design the frontend
- ideas: use react frarme for the project
---

### 2025/06/03
- Introduce REACT frame to the project
- Frontend and Backend are separated
- Not every page is correctly addapted to the REACT frame
- Login info received, but not updating the frontend page
- The rest of the page is not tested yet
---

### 2025/06/09
- ScoreboarPage.jsx implemented
- To be fix: umpire updating score still return 422, "subject must be a string" ✅
- Solve: make sure the token when created is string type. create_access_token(identity=str(user.id))
---

### 2025/06/10
- Fix login and logout in BaseLayout.jsx
- Fix Check All Users page
- Note: When return 422 "Subject must be a string", check the token, make sure when
  you creating the token, it must be a string. create_access_token(identity=str(user.id))
- To be fixed: Update Score via socketio.emit() ✅
---

### 2025/06/11
- Add missing link: AssignUmpire, ManageMatch, CreateMatch, AssignUmpire
- Backend Functions to be implemented: ManageMatch
- Note: The 'Websocket is closed before the connection is etablished' warning message is generated from React server.   
- Since React server has a default hot-reload mechanism, it will establish a websocket at localhost:3000 to monitor file changes.   


- This connection may be temporarily disconnected due to browser refresh, network latency, or other reasons, causing you to see this warning.  


- This warning message will not affect your socket.io service, as well as the functionality provided in the page.
---

### 2025/06/12
- Create a page to let users to uploade game schedule (.xlsx file)
- Use the schedule file to create games 
- Adjust delete game page
---

### 2025/06/13
- Analyze the schedule file and create matches
- Database table structure modified
- Fix register function
---

### 2025/06/14
- Modulize the JavaScript function, write socket functions into socketServerice.js
- Fix update score function and socre-update-listener
---