// for local test use
const DEV_BASE_URL = 'http://localhost:5001';

// when you are hosting, make sure you use the PROD_BASE_URL
const PROD_BASE_URL = 'https://alex1792.pythonanywhere.com';

const BASE_URL = process.env.NODE_ENV === 'production' ? PROD_BASE_URL : DEV_BASE_URL;

export const API_URLS = {
    // home_bp,
    HOME: `${BASE_URL}/api/home`,

    // auth_bp,
    REGISTER: `${BASE_URL}/api/auth/register`,
    LOGIN: `${BASE_URL}/api/auth/login`,
    LOGOUT: `${BASE_URL}/api/auth/logout`,
    ME: `${BASE_URL}/api/auth/me`,
    VALIDATE: `${BASE_URL}/api/auth/validate`,

    // tournament_bp,
    ALL_TOURNAMENTS: `${BASE_URL}/api/tournaments`,
    TOURNAMENT: `${BASE_URL}/api/tournaments/<int:tournament_id>`,
    CREATE_TOURNAMENT: `${BASE_URL}/api/tournaments/create_tournament`,
    GENERATE_MATCHES: `${BASE_URL}/api/tournaments/<int:tournament_id>/generate_matches`,
    TOURNAMENT_MATCHES: `${BASE_URL}/api/tournaments/<int:tournament_id>/matches`,
    TOURNAMENT_SCHEDULE: `${BASE_URL}/api/tournaments/<int:tournament_id>/schedule`,
    DELETE_ALL_MATCHES: `${BASE_URL}/api/tournaments/<int:tournament_id>/delete_all_matches`,

    // registration_bp,
    SIGN_UP_TOURNAMENT: `${BASE_URL}/api/registrations/tournaments/<int:tournament_id>/registrations`,
    GET_REGISTRATIONS: `${BASE_URL}/api/registrations/tournament/<int:tournament_id>/registrations`,
    UPLOAD_REGISTRATION_FILE: `${BASE_URL}/api/registrations/tournament/<int:tournament_id>/upload`,
    UPDATE_REGISTRATION_STATUS: `${BASE_URL}/api/registrations/<int:registration_id>/status`,

    // match_bp,
    ALL_MATCHES: `${BASE_URL}/api/matches`,
    CREATE_MATCH: `${BASE_URL}/api/matches/create_match`,
    ASSIGN_UMPIRE: `${BASE_URL}/api/matches/<int:match_id>/umpire`,
    GET_MATCH_BY_UMPIRE: `${BASE_URL}/api/matches/umpire/<int:umpire_id>`,
    GET_MATCH_BY_MATCH_ID: `${BASE_URL}/api/matches/<int:match_id>`,
    UPDATE_SCORE: `${BASE_URL}/api/matches/<int:match_id>/score`,
    CLEAR_ALL_MATCHES: `${BASE_URL}/api/matches/clear_all_match`,
    DELETE_MATCH: `${BASE_URL}/api/matches/<int:match_id>`,
    NEXT_GAME: `${BASE_URL}/api/matches/<int:match_id>/next_game`,
    END_MATCH: `${BASE_URL}/api/matches/<int:match_id>/end_match`,

    // admin_bp,
    ALL_USERS: `${BASE_URL}/api/admin/users`,
    UPLOAD_ALL_MATCHES: `${BASE_URL}/api/admin/upload_all_matches`,
    UPLOAD_MATCH_SCHEDULE: `${BASE_URL}/api/admin/upload_match_schedule`,
    GENERATE_MATCH_SCHEDULE: `${BASE_URL}/api/admin/generate_match_schedule`,
    UPLOAD_PARTICIPANTS: `${BASE_URL}/api/admin/upload_participants`,
    GENERATE_SCHEDULE_FOR_TOURNAMENT: `${BASE_URL}/api/admin/<int:tournament_id>/generate_schedule_for_tournament`,

    // user_bp,
    GET_ALL_USERS: `${BASE_URL}/api/users`,
    GET_USER_BY_ID: `${BASE_URL}/api/users/<int:user_id>`,
    GET_CURRENT_USER_PROFILE: `${BASE_URL}/api/users/profile`,
    UPDATE_CURRENT_USER_PROFILE: `${BASE_URL}/api/users/profile`,
    UPDATE_USER: `${BASE_URL}/api/users/<int:user_id>`,
    DELETE_USER: `${BASE_URL}/api/users/<int:user_id>`,
    SEARCH_USERS: `${BASE_URL}/api/users/search`,
    GET_USER_STATS: `${BASE_URL}/api/users/stats`,

    // file_bp,
    UPLOAD_FILE: `${BASE_URL}/api/files/upload`,
    DOWNLOAD_FILE: `${BASE_URL}/api/files/download/<filename>`,
    LIST_FILES: `${BASE_URL}/api/files/list`,
    DELETE_FILE: `${BASE_URL}/api/files/<filename>`,

    // scoreboard_bp,
    SCOREBOARD: `${BASE_URL}/api/scoreboard`,
}

export const getMatchUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}`;
export const getTournamentUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}`;
export const getRegistrationUrl = (registrationId) => `${BASE_URL}/api/registrations/${registrationId}`;
export const getUserUrl = (userId) => `${BASE_URL}/api/users/${userId}`;
export const getFileUrl = (filename) => `${BASE_URL}/api/files/${filename}`;
export const getScoreboardUrl = () => `${BASE_URL}/api/scoreboard`;
       