# Tournament Management System

A comprehensive tournament management system with real-time scoring, user management, and tournament scheduling capabilities.

## 🌟 Live Demo

- **Website**: [Tournament Software](https://itsyuhungkung.sc-heduling.com)
- **Demo Videos**: [Tournament Software Demo Playlist](https://www.youtube.com/playlist?list=PLqC7Br1667IWQhBWm3f_S0-OXqkR5kZiD)

## Features

### Core Functionality
- **Real-time Score Updates**: Instant score synchronization across all users
- **Multi-match Management**: Handle multiple concurrent matches
- **Role-based Access Control**: Admin, Host, Umpire, and User roles
- **Tournament Management**: Create, manage, and schedule tournaments
- **User Registration System**: Internal and external registration support

### Advanced Features
- **Match Scheduling**: Intelligent scheduling with consecutive player detection
- **Excel Integration**: Upload tournament schedules and registration data
- **Real-time Communication**: WebSocket-based live updates
- **Responsive Design**: Modern UI with React frontend
- **Tournament Types**: Support for single/double matches across different categories

## 🛠 Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM(Object-Relational Mapping)
- **Authentication**: Flask-JWT-Extended
- **Real-time**: Flask-SocketIO
- **File Processing**: Pandas, OpenPyXL
- **CORS**: Flask-CORS

### Frontend
- **Framework**: React.js 19.1.0
- **Routing**: React Router DOM 7.6.1 (Document Object Model)
- **Authentication**: React Auth Kit 3.1.3
- **Real-time**: Socket.IO Client 4.8.1
- **Styling**: CSS3 with responsive design

## 📁 Project Structure


## Project Structure
```
scoreboard/
├── app/              # Flask backend application
│ ├── services/       # Business logic layer
│ │ ├── match_service.py  
│ │ ├── tournament_service.py
│ │ ├── user_service.py
│ │ └── schedule_service.py
│ ├── static/         # Static assets
│ ├── templates/      # HTML templates
│ ├── models.py       # Database models
│ ├── routes.py       # API routes
│ └── extensions.py   # Flask extensions
├── frontend/         # React frontend application
│ ├── src/
│ │ ├── components/   # Reusable components
│ │ ├── pages/        # Page components
│ │ │ ├── admin/      # Admin pages
│ │ │ ├── auth/       # Authentication pages
│ │ │ ├── match/      # Match management pages
│ │ │ └── tournament/ # Tournament pages
│ │ ├── context/      # React context
│ │ ├── api/          # API services
│ │ └── styles/       # CSS stylesheets
│ └── public/         # Public assets
├── config.py         # Configuration settings
├── requirements.txt  # Python dependencies
├── run.py            # Application entry point
└── README.md         # This file
```


## 🏗 Architecture

The system follows a **layered architecture** with clear separation of concerns:
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
|    (create, read, update, delete)                           |
│  ✅ Relationship definition                                 │
└─────────────────────────────────────────────────────────────┘
```
- Advantages of new Architecture
1. Single Task Rule
-- Blueprint: handle only routing
-- Service: handle only logic and algorithm
-- Model: handle only Database
2. Reuseable
-- Same service can be used by different blueprint
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


### Layer Responsibilities
- **Blueprint Layer**: Handle HTTP routing and request/response
- **Service Layer**: Business logic, algorithms, and data transformation
- **Model Layer**: Database operations and data structure definition

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Install Node.js and npm

#### macOS (using Homebrew)
```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js (includes npm)
brew install node

# Verify installation
node --version
npm --version
```

#### Windows
```bash
# Download and install from official website
# https://nodejs.org/en/download/

# Or using Chocolatey
choco install nodejs

# Verify installation
node --version
npm --version
```

#### Linux (Ubuntu/Debian)
```bash
# Using apt
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or using snap
sudo snap install node --classic

# Verify installation
node --version
npm --version
```

#### Using Node Version Manager (nvm) - Recommended
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal or run
source ~/.bashrc

# Install Node.js
nvm install 18
nvm use 18

# Verify installation
node --version
npm --version
```

### Backend Setup
```bash
# Clone the repository
git clone -b https://github.com/alex1792/scoreboard
cd scoreboard


# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python run.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Production Deployment
```bash
# Build frontend
cd frontend
npm run build

# Set environment variables
export REACT_APP_API_URL=https://itsyuhungkung.sc-heduling.com

# Serve frontend
serve -s build -l 3000
```

## 👥 User Roles & Permissions

### Admin
- Full system access
- User management
- Tournament creation and deletion
- Match management
- Umpire assignment

### Host
- Create and manage own tournaments
- Upload registration files
- Generate match schedules
- Manage tournament matches

### Umpire
- Update match scores
- View assigned matches
- Real-time score management

### User
- View tournaments and matches
- Register for tournaments
- View real-time scores

## 📊 Database Schema

### Key Tables
- **Users**: User accounts and roles
- **Tournaments**: Tournament information and settings
- **Matches**: Match details, scores, and status
- **Events**: Tournament categories (MS, WS, MD, WD, XD)
- **Groups**: Tournament groups/flights
- **Registrations**: Tournament registrations

### Relationships
```sql
Match.event_id → Event.id
Match.group_id → Group.id
Match.umpire_id → User.id
Tournament.host_id → User.id
```

## 📋 Excel File Format

The system supports Excel file uploads for tournament schedules and registrations:

| Excel Column | Database Field | Description |
|-------------|----------------|-------------|
| Round | - | Batch number |
| Court | - | Court number |
| Match_Type | match.event_type | Single/Double |
| Category | event.category | MS, WS, MD, WD, XD |
| Group | group.name | Group name |
| Player1/Team1 | match.player1_name | Player/Team 1 |
| Player2/Team2 | match.player2_name | Player/Team 2 |
| Status | match.status | Scheduled/Completed/Cancelled |
| Score1 | match.player1_score | Player 1 score |
| Score2 | match.player2_score | Player 2 score |
| Umpire | match.umpire_id | Umpire ID |

## Configuration

### Environment Variables
```bash
# Frontend (.env.production)
REACT_APP_API_URL=https://your-api-domain.com

# Backend
DATABASE_URL=sqlite:///database.db
JWT_SECRET_KEY=your-secret-key
```

### API Endpoints
- **Authentication**: `/auth/login`, `/auth/register`
- **Tournaments**: `/tournaments`, `/tournaments/<id>`
- **Matches**: `/matches`, `/matches/<id>`
- **Users**: `/users`, `/users/<id>`
- **Schedules**: `/schedules`, `/schedules/<id>`

## 🎯 Key Features in Detail

### Real-time Score Updates
- WebSocket-based live score synchronization
- Instant updates across all connected clients
- Support for multiple concurrent matches

### Tournament Management
- Create tournaments with custom settings
- Upload registration files (Excel/CSV)
- Generate match schedules automatically
- Track tournament progress and results

### Match Scheduling
- Intelligent scheduling algorithm
- Consecutive player detection
- Court assignment optimization
- Support for elimination and round-robin formats

### User Management
- Role-based access control
- User registration and authentication
- Profile management
- Permission-based feature access

## 🐛 Troubleshooting

### Common Issues
1. **WebSocket Connection**: Ensure Socket.IO server is running
2. **Database Issues**: Check database file permissions
3. **CORS Errors**: Verify CORS configuration in backend
4. **Build Errors**: Clear node_modules and reinstall dependencies

### Development Tips
- Use `npm start:dev` for development without HTTPS
- Check browser console for frontend errors
- Monitor Flask debug output for backend issues
- Use database browser tools to inspect SQLite database

## 📈 Future Enhancements

### Planned Features
- [ ] Advanced tournament brackets
- [ ] Player statistics and rankings
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Advanced reporting and analytics
- [ ] Integration with external tournament systems

### Technical Improvements
- [ ] Database migration system
- [ ] Automated testing suite
- [ ] Performance optimization
- [ ] Enhanced security features
- [ ] API documentation with Swagger

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍ Author

- **Yu Hung Kung** -  Initial development and Current maintainer

## �� Acknowledgments

- Flask community for the excellent web framework
- React team for the powerful frontend library
- Socket.IO for real-time communication capabilities
- All contributors and testers

---

**Note**: This system is actively maintained and updated. For the latest features and bug fixes, please check the repository regularly.

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

### 2025/07/29
- Support 3 games in each match
- Update determine winner function logic
- Modified database table model
- Display more info on the match-card
---

### 2025/07/31
- Update scoreboard page template
- Update next match when elimination match is finished
- Emit to frontend
- Fix creating match record bugs (not assigning prev_match_id to elimination match)
---

### 2025/08/01
- Add user role 'host' into the system
- Different user.role have different permission
- At homepage, different user.role can view different icons (admin can see more functions)
- Optimized the authorization function. Passing the role parameter the function can return whether you have the permission
- Integrate ManageMatchesPage with MatchesPage (admin and host can edit matches in the MatchesPage)
- Modified Database Model, craating new column 'tournament.host_id'
---

### 2025/08/03
- Write comments for services.py
- fix admin at matchesPage can not click match card
---

### 2025/08/08
- Add delete all match inside the matchesPage
- Fix the delete match button. After delelte, do not navigate to the scoreboard page.
---

### 2025/08/11
- Add schedule setting in CreateTournamentPage
- Update the SchedulePage
---

- Modularize API
- Set the urls be environmental variables(only need to modify once when deploy)
---

### 2025/08/13
- Deploy at pythonanywhere.com
- Modified the URLs (from localhost to real domian)
---

### 2025/08/16
- Modularize the Tournament Card
- Add delete tournament button on Tournament Card
- Only admin can delete every tournament, host can delete it's own tournament
---

### 2025/08/17
- Add role permission, easier to maintain the page permission
- Issue_1: frontend communicate with backend is using localhost:5001, not https://
- Issue_2: when backend api can only use http, not https, add a meta at the frontend/public/index.html
---

### 2025/08/18
- Solve Issue_1 spotted on Aug 17, create a new file /frontend/.env.production
- modified urls.js --> const BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? PROD_BASE_URL : DEV_BASE_URL);
- Then execute npm run build. This will correctly use domain url, not localhost
```
frontend/
├── .env.production          # new file
├── package.json
├── src/
│   └── config/
│       └── urls.js         # modified file
└── ...
```
```
# 1. make sure pwd is in frontend
cd frontend

# 2. set env variables
export REACT_APP_API_URL=https://itsyuhungkung.sc-heduling.com

# 3. build
npm install
npm run build

# 4. run frontend
serve -s build -l 3000
```
- cloudflare dashboard need to set three subdomain, socket.io, api, frontend
- socket.io and api using the domain with port 5001, frontend using port 3000
---

### 2025/08/24
- solve sign-up tournament problem
- ideas: show the brackets of elimination matches (like a path, who's in which round)
- ideas: summarize the stats down below the brackets page
---

### 2025/08/28
- Implemented Elimination bracket and round robin ranking board
- Websocket update in the bracket page
---

### 2025/08/29
- fix the update match status logic
- cascade update the match info if restart the elimination match
- cascade socketio emit match update
---

### 2025/09/08
- IDEAS: upload customized schedule
- IDEAS: player profile to show player's game history
- IDEAS: create another group, and create matches in that group
- IDEAS: ranking board down below the group page
- IDEAS: type score in the scoreboard page
- Fix schedule time errors
---

### 2025/09/09
- Fix scheduling bug
- Write more columns into the schedule.xlsx file
---

### 2025/09/10
- Create the player history page
---