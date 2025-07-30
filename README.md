# Scoreboard
---

## Feature Demo
Some features and functions I developed so far. Check the link below to see how it works.
[Tournament Software](https://www.youtube.com/playlist?list=PLqC7Br1667IWQhBWm3f_S0-OXqkR5kZiD)

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
    - __init__.py         # Initializes the app module
    - auth.py             # Handles authentication-related logic
    - blueprints.py       # Manages Flask blueprints
    - extensions.py       # Extensions used in the project (e.g., Flask extensions)
    - form.py             # Defines forms for user input
    - match_generator.py  # match generator
    - models.py           # Database-related utilities and models
    - routes.py           # Defines application routes
    - scheduler.py        # match scheduler
  - frontend/src/
    ├── components/
    │   └── layout/
    │       └── BaseLayout.jsx
    ├── pages/
    │   ├── auth/
    │   │   ├── LoginPage.jsx
    │   │   ├── RegisterPage.jsx
    │   │   ├── LoginForm.jsx
    │   │   ├── RegisterForm.jsx
    │   │   └── index.js
    │   ├── admin/
    │   │   ├── CreateTournamentPage.jsx
    │   │   ├── ManageMatchPage.jsx
    │   │   ├── UsersPage.jsx
    │   │   ├── AssignUmpirePage.jsx
    │   │   ├── UploadSchedulePage.jsx
    │   │   ├── CreateMatchPage.jsx
    │   │   ├── ChangesUserRolePage.jsx
    │   │   ├── SchedulerPage.jsx
    │   │   └── index.js
    │   ├── tournament/
    │   │   ├── TournamentPage.jsx
    │   │   ├── SignUpTournamentPage.jsx
    │   │   ├── MatchGeneratorPage.jsx
    │   │   └── index.js
    │   ├── match/
    │   │   ├── MatchesPage.jsx
    │   │   ├── ScoreboardPage.jsx
    │   │   ├── UmpirePage.jsx
    │   │   └── index.js
    │   ├── HomePage.jsx
    │   └── index.js
    ├── services/
    │   ├── api.js
    │   └── socketService.js
    ├── context/
    │   └── AuthContext.jsx
    ├── styles/
    │   ├── pages/
    │   │   ├── auth/
    │   │   ├── admin/
    │   │   ├── tournament/
    │   │   └── match/
    │   ├── global.css
    │   ├── index.css
    │   └── App.css
    ├── utils/
    │   └── MatchCard.html
    ├── assets/
    │   └── logo.svg
    ├── App.js
    ├── index.js
    └── reportWebVitals.js
  - config.py             # Configuration file for the project
  - database.db           # SQLite database file
  - requirements.txt      # List of dependencies for the project
  - run.py 
  

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

### 2025/06/16
- Modify the database table structure, add 'category' into match
- Adding the 'category' attribute into check all matches page
---

### 2025/06/17
- Integrate 'Assign Umpire Page' with 'Manage Math Page'
- IDEAS: Update 'Create Match Page', use the Match Card template
- IDEAS: New backend features -- schelulder, make sure every player can have one match break before next match
---

### 2025/06/25
- Update homepage, add icons and integrate functions together
- IDEAS: for the User Management, need to integrate check all users and update user role
- IDEAS: filter function in check all matches, filter by status, search by player
---

### 2025/06/26
- Integrate 'update schedule' and 'scheduler'
- After uploading the round robin, it will automatically download the match schedule
- IDEAS: integrate update user role and check all users in one page
- UPDATE: login page
---

### 2025/06/27
- Integrate check all users and update user role in one page
---

### 2025/07/01
- Implemented the match-generator page
- Update register page
- IDEA: create sign up for tournament features, so that the data can be parsed and processed correctly in backend
---

### 2025/07/03
- Implement the draft of the sign-up-tournament function
- IDEAS: integrate the sign-up-tournament and the scheduler function 
---

### 2025/07/08
- Implemented the sign-up system, create tournament page
- File path reconstruct
- Redesigned the Database Model 
---

### 2025/07/09
- Implemented the CheckRegistrationPage, to check the registration of each tournament
- Sign-Up page update, user have to login before signing up a tournament
---

### 2025/07/10
- Implemented the filter function in view registration
- Redesigned the blueprint structure. Now into three levels.
- Services: deal with data manipulation and logic operations (algorithm)
- Blueprints: are separated into individual, can be test repectively.
- Each Blueprint has its own route.py, and it handles all the routing for the blueprint itself
- Blueprint.py is used to register and manipulate all blueprints
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Tournament  │  │   Match     │  │    Auth     │          │
│  │   Page      │  │   Page      │  │    Page     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Request
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Blueprint Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ tournament  │  │    match    │  │    auth     │          │
│  │   .py       │  │    .py      │  │    .py      │          │
│  │ (Routing)   │  │ (Routing)   │  │ (Routing)   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                             │
│  ✅ only deel with routing                                  │
│  ✅ receive HTTP request                                    │
│  ✅ call Service layer                                      │
│  ✅ return HTTP response                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ call Service
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ tournament  │  │    match    │  │    user     │          │
│  │ _service.py │  │ _service.py │  │ _service.py │          │
│  │ (Business)  │  │ (Business)  │  │ (Business)  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                             │
│  ✅ handle service logic and algorithm                      │
│  ✅ data transform and format                               │
│  ✅ complex algorithm                                       │
│  ✅ call Model layer                                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Database manipulation
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Model Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Tournament  │  │    Match    │  │    User     │          │
│  │   Model     │  │   Model     │  │   Model     │          │
│  │ (Database)  │  │ (Database)  │  │ (Database)  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                             │
│  ✅ Database structure definition                           │
│  ✅ Basic CRUD manipulation                                 │
│  ✅ Relationship definition                                 │
└─────────────────────────────────────────────────────────────┘
```
- Advantages of new Architecture
1. Single Task Rule
-- Blueprint: handle only routing
-- Service: handle only logic and algorithm
-- Model: handle only Database
2. Reuseable
-- Same service can be useed by different blueprint
3. Easier to test
4. Easier to maintain

- This is the MVC(Model-View-Controller) architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    My Architecture                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │    Model    │  │    View     │  │ Controller  │          │
│  │ (Database)  │  │ (Frontend)  │  │ (Blueprint) │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                             │
│  ┌─────────────┐                                            │
│  │   Service   │  ← additional service layer                │
│  │   Layer     │                                            │
│  └─────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```
---

### 2025/07/11
- IDEAS: let host to upload the .xlsx file of tournament. The system must provide a format, and 
the host must upload the file using the provided format.
- IDEAS: Genearate match by registration records
- Done implementing the create match function at the view registration page.
- Done checking the generated match at /matches
- Done updating the check match by tournament
---

### 2025/07/13
- Implemented the external registration function allowing the host to upload .xlsx or .csv file to register
---

### 2025/07/14
- Generate test file for external registration
- Fixed the model structure
- External registration is completed.
---

### 2025/07/15
- Integrate the match-scheduler function with database.

## mapping table of excel file to database

| Excel Column | Database Column | Data type | Info |
|------------|------------|----------|------|
| **Round** | - | Integer | number of batch |
| **Court** | - | String | court number |
| **Match_Type** | `match.event_type` | String | game-type(single or double） |
| **Category** | `event.category` | String | Category（MS, WS, MD, WD, XD） |
| **Group** | `group.name` | String | Group name |
| **Player1/Team1** | `match.player1_name` 或 `match.team1_player1_name + match.team1_player2_name` | String | Player1/Team1 |
| **Player2/Team2** | `match.player2_name` 或 `match.team2_player1_name + match.team2_player2_name` | String | Player2/Team2 |
| **Consecutive_Players** | - | String | Consecutive players |
| **Status** | `match.status` | String | Match status（Scheduled, Completed, Cancelled） |
| **Score1** | `match.player1_score` | Integer | Player1/Team1 Score |
| **Score2** | `match.player2_score` | Integer | Player2/Team2 Score |
| **Umpire** | `match.umpire_id` | String | Umpire id |
| **Notes** | - | String | Notes (for stats） |

## stats information

| Excel Column | Details | Info |
|------------|------|------|
| **Round** | "Stats info" | Stats info column |
| **Notes** | Number of Affected players | Number of Consecutive players |
| **Player1/Team1** | Player Name | Affected Player's name |
| **Notes** | "Consecutive x times" | number of consecutive games |

## Color Info

| Color | Info |
|------|------|
| 🟡 **Yellow** | games with consecutive players |
| 🟢 **Green** | Unaffected game |
| 🔵 **Blue** | Stats info |
| 🔴 **Red** | Affected players |

## Database Relationship Info

```sql
-- Match 表與其他表的關聯
Match.event_id → Event.id
Match.group_id → Group.id
Match.player1_id → User.id (single player1)
Match.player2_id → User.id (single player2)
Match.team1_player1_id → User.id (Double team1 player1)
Match.team1_player2_id → User.id (Double team1 player2)
Match.team2_player1_id → User.id (Double team2 player1)
Match.team2_player2_id → User.id (Double team2 player2)
Match.umpire_id → User.id (umpire id)
```

## Example:

| Round | Court | Match_Type | Category | Flight | Player1/Team1 | Player2/Team2 | Consecutive_Players | Status | Score1 | Score2 | Umpire | Notes |
|-------|-------|------------|----------|--------|---------------|---------------|-------------------|--------|--------|--------|--------|-------|
| 1 | Court1 | Single | MS | A | John Smith | Jane Doe | John Smith, Jane Doe | Scheduled | 0 | 0 | | |
| 1 | Court2 | Double | MD | B | Mike & Tom | Alex & Bob | Mike, Tom | Scheduled | 0 | 0 | | |
| 2 | Court1 | Single | WS | A | Sarah Wilson | Emma Davis | | Scheduled | 0 | 0 | | |

## Stats Example:

| Round | Court | Match_Type | Category | Flight | Player1/Team1 | Player2/Team2 | Consecutive_Players | Status | Score1 | Score2 | Umpire | Notes |
|-------|-------|------------|----------|--------|---------------|---------------|-------------------|--------|--------|--------|--------|-------|
| Stats Info | | | | | | | | | | | | |
| Number of Affected players | | | | | | | | | | | | 3 |
| | | | | | John Smith | | | | | | | consecutive 2 times |
| | | | | | Jane Doe | | | | | | | consecutive 1 time |
| | | | | | Mike | | | | | | | cnosecutive 1 time |

---

**注意事項：**
- Consecutive players are sorted
- Stats info is marked by different color
- empty row is used to separate match schedule with stats info
---

### 2025/07/16
- Fixed the upload registration errors (causing issues with the generate match function)
---

### 2025/07/22
- Fixed the scheduling algorithm, only matches will be scheduled. Exempt for BYE matches.
- Fixed the dependencies issues for the scheduler algorithm.
- Created a ScheduleService to operate the schedule service.
---

### 2025/07/23
- Add schedule in database model
- Add a schedule page for each tournament
---

### 2025/07/25
- Modularized my code
- Add Tournament description.
- Displaying description in sign-up page
---

### 2025/07/26
- Fix score update emit()
- Fix umpire scoreboard page
- Fix registered time in the check registration page
- Add modify registration.status functions
- Modified ScoreboardPage layout
---

### 2025/07/28
- Implemented winner to the match-card
- Modified match card layout
- Update create match logic, consider bye matches, assign winner when creating.
---