// for local test use
export const DEV_BASE_URL = 'http://localhost:5001';

// when you are hosting, make sure you use the PROD_BASE_URL
export const PROD_BASE_URL = 'https://alex1792.pythonanywhere.com';

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
    CREATE_TOURNAMENT: `${BASE_URL}/api/tournaments/create_tournament`,


    // match_bp,
    ALL_MATCHES: `${BASE_URL}/api/matches`,
    CREATE_MATCH: `${BASE_URL}/api/matches/create_match`,
    CLEAR_ALL_MATCHES: `${BASE_URL}/api/matches/clear_all_match`,

    // admin_bp,
    ALL_USERS: `${BASE_URL}/api/admin/users`,
    UPLOAD_ALL_MATCHES: `${BASE_URL}/api/admin/upload_all_matches`,
    UPLOAD_MATCH_SCHEDULE: `${BASE_URL}/api/admin/upload_match_schedule`,
    GENERATE_MATCH_SCHEDULE: `${BASE_URL}/api/admin/generate_match_schedule`,
    UPLOAD_PARTICIPANTS: `${BASE_URL}/api/admin/upload_participants`,

    // user_bp,
    GET_ALL_USERS: `${BASE_URL}/api/users`,
    GET_CURRENT_USER_PROFILE: `${BASE_URL}/api/users/profile`,
    UPDATE_CURRENT_USER_PROFILE: `${BASE_URL}/api/users/profile`,
    SEARCH_USERS: `${BASE_URL}/api/users/search`,
    GET_USER_STATS: `${BASE_URL}/api/users/stats`,

    // file_bp,
    UPLOAD_FILE: `${BASE_URL}/api/files/upload`,
    LIST_FILES: `${BASE_URL}/api/files/list`,

    // scoreboard_bp,
    SCOREBOARD: `${BASE_URL}/api/scoreboard`,
}

// 函數形式的 URL（需要變數的）
export const getMatchUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}`;
export const getTournamentUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}`;
export const getRegistrationUrl = (registrationId) => `${BASE_URL}/api/registrations/${registrationId}`;
export const getUserUrl = (userId) => `${BASE_URL}/api/users/${userId}`;
export const getFileUrl = (filename) => `${BASE_URL}/api/files/${filename}`;
export const getScoreboardUrl = () => `${BASE_URL}/api/scoreboard`;

// 新增：需要 matchId 的函數
export const getMatchNextGameUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}/next_game`;
export const getMatchEndMatchUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}/end_match`;
export const getMatchScoreUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}/score`;
export const getMatchUmpireUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}/umpire`;
export const getMatchDeleteUrl = (matchId) => `${BASE_URL}/api/matches/${matchId}`;

// 新增：需要 tournamentId 的函數
export const getTournamentMatchesUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}/matches`;
export const getTournamentScheduleUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}/schedule`;
export const getTournamentGenerateMatchesUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}/generate_matches`;
export const getTournamentDeleteAllMatchesUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}/delete_all_matches`;

// 新增：需要 registrationId 的函數
export const getRegistrationStatusUrl = (registrationId) => `${BASE_URL}/api/registrations/${registrationId}/status`;

// 新增：需要 userId 的函數
export const getUserByIdUrl = (userId) => `${BASE_URL}/api/users/${userId}`;
export const updateUserUrl = (userId) => `${BASE_URL}/api/users/${userId}`;
export const deleteUserUrl = (userId) => `${BASE_URL}/api/users/${userId}`;

// 新增：需要 filename 的函數
export const downloadFileUrl = (filename) => `${BASE_URL}/api/files/download/${filename}`;
export const deleteFileUrl = (filename) => `${BASE_URL}/api/files/${filename}`;

// 新增：Registration 相關函數
export const getRegistrationsByTournamentUrl = (tournamentId) => `${BASE_URL}/api/registrations/tournament/${tournamentId}/registrations`;
export const signUpTournamentUrl = (tournamentId) => `${BASE_URL}/api/registrations/tournaments/${tournamentId}/registrations`;
export const uploadRegistrationFileUrl = (tournamentId) => `${BASE_URL}/api/registrations/tournament/${tournamentId}/upload`;
export const updateRegistrationStatusUrl = (registrationId) => `${BASE_URL}/api/registrations/${registrationId}/status`;

// 新增：Admin 相關函數
export const generateScheduleForTournamentUrl = (tournamentId) => `${BASE_URL}/api/admin/${tournamentId}/generate_schedule_for_tournament`;
export const uploadRoundRobinUrl = () => `${BASE_URL}/api/admin/upload_round_robin`;

// 新增：Match 相關函數
export const getMatchByUmpireUrl = (umpireId) => `${BASE_URL}/api/matches/umpire/${umpireId}`;

// 新增：Tournament 相關函數
export const getTournamentDetailsUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}`;

// delete tournament
export const getDeleteTournamentUrl = (tournamentId) => `${BASE_URL}/api/tournaments/${tournamentId}/delete_tournament`;


       