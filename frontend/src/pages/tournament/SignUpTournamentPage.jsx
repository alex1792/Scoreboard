import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchInfoFromBackend, fetchInfoToBackend } from '../../api/api';
import '../../styles/pages/tournament/SignUpTournamentPage.css';
import { getTournamentUrl, signUpTournamentUrl } from '../../config/urls';

const SignUpTournamentPage = () => {
    const navigate = useNavigate();
    const { tournamentId } = useParams();
    
    const [tournament, setTournament] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [playerInfo, setPlayerInfo] = useState({
        firstName: '',
        lastName: ''
    });
    const [selectedEvents, setSelectedEvents] = useState([]);
    const [selectedGroups, setSelectedGroups] = useState({});
    // 為每個雙打項目儲存夥伴資訊
    const [partnerInfo, setPartnerInfo] = useState({});

    // Fetch tournament details
    useEffect(() => {
        const fetchTournament = async () => {
            try {
                console.log('Fetching tournament details for ID:', tournamentId);
                const data = await fetchInfoFromBackend(`${getTournamentUrl(tournamentId)}`);
                console.log('Tournament data:', data);
                
                if (data.status === 'success') {
                    setTournament(data.data);
                } else {
                    setError(data.message || 'Failed to load tournament details');
                }
            } catch (error) {
                console.error('Error fetching tournament:', error);
                setError('Failed to load tournament details');
            } finally {
                setLoading(false);
            }
        };

        if (tournamentId) {
            fetchTournament();
        }
    }, [tournamentId]);

    // Handle player info changes
    const handlePlayerInfoChange = (e) => {
        const { name, value } = e.target;
        setPlayerInfo(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // Handle partner info changes for specific event
    const handlePartnerInfoChange = (eventId, field, value) => {
        setPartnerInfo(prev => ({
            ...prev,
            [eventId]: {
                ...prev[eventId],
                [field]: value
            }
        }));
    };

    // Handle event selection
    const handleEventChange = (eventId) => {
        setSelectedEvents(prev => {
            const isSelected = prev.includes(eventId);
            if (isSelected) {
                // Remove event and its selected groups and partner info
                setSelectedGroups(current => {
                    const newGroups = { ...current };
                    delete newGroups[eventId];
                    return newGroups;
                });
                setPartnerInfo(current => {
                    const newPartnerInfo = { ...current };
                    delete newPartnerInfo[eventId];
                    return newPartnerInfo;
                });
                return prev.filter(id => id !== eventId);
            } else {
                return [...prev, eventId];
            }
        });
    };

    // Handle group selection
    const handleGroupChange = (eventId, groupId) => {
        setSelectedGroups(prev => ({
            ...prev,
            [eventId]: groupId
        }));
    };

    // Check if event is doubles
    const isDoublesEvent = (eventName) => {
        return eventName.includes('Doubles');
    };

    // Handle form submission
    const handleSubmit = async () => {
        // Validation
        if (!playerInfo.firstName || !playerInfo.lastName) {
            alert('Please fill in your first and last name');
            return;
        }

        if (selectedEvents.length === 0) {
            alert('Please select at least one event');
            return;
        }

        // Check if doubles events have partner info
        for (const eventId of selectedEvents) {
            const event = tournament.events.find(e => e.id === eventId);
            if (isDoublesEvent(event.name)) {
                const eventPartnerInfo = partnerInfo[eventId];
                if (!eventPartnerInfo || !eventPartnerInfo.firstName || !eventPartnerInfo.lastName) {
                    alert(`Please fill in your partner's name for ${event.name}`);
                    return;
                }
            }
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('Please Login to sign up a tournament');
            return;
        }

        // Prepare submission data
        const submissionData = {
            tournament_id: tournamentId,
            player_info: playerInfo,
            registrations: selectedEvents.map(eventId => {
                const event = tournament.events.find(e => e.id === eventId);
                const registration = {
                    event_id: eventId,
                    group_id: selectedGroups[eventId],
                    event_name: event.name,
                    is_doubles: isDoublesEvent(event.name)
                };
                
                // Add partner info for doubles events
                if (isDoublesEvent(event.name)) {
                    registration.partner_info = partnerInfo[eventId];
                }
                
                return registration;
            })
        };

        // const requestData = {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'Authorization': `Bearer ${token}`
        //     },
        //     body: JSON.stringify(submissionData)
        // }

        try {
            console.log('Submitting:', submissionData);
            const response = await fetchInfoToBackend(`${signUpTournamentUrl(tournament.id)}`, submissionData);
            console.log('Response:', response);
            if (response.status === 'success') {
                alert('Registration successful!');
                navigate('/tournaments');
            } else {
                alert('Registration failed: ' + response.message);
            }
        } catch (error) {
            alert('Registration failed: ' + error.message);
        }
    };

    if (error) {
        return (
            <div className="signup-tournament-page">
                <div className="container">
                    <div className="error-message">
                        Error: {error}
                    </div>
                    <button onClick={() => navigate('/tournaments')}>
                        Back to Tournaments
                    </button>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="signup-tournament-page">
                <div className="container">
                    <div className="loading">Loading tournament details...</div>
                </div>
            </div>
        );
    }

    if (!tournament) {
        return (
            <div className="signup-tournament-page">
                <div className="container">
                    <div className="error">Tournament not found</div>
                    <button onClick={() => navigate('/tournaments')}>
                        Back to Tournaments
                    </button>
                </div>
            </div>
        );
    }

    if (!tournament.events || tournament.events.length === 0) {
        return (
            <div className="signup-tournament-page">
                <div className="container">
                    <div className="error">No events available for this tournament</div>
                    <button onClick={() => navigate('/tournaments')}>
                        Back to Tournaments
                    </button>
                </div>
            </div>
        );
    }

    // 添加格式化函數
    const formatDescription = (description) => {
        if (!description) return '';
        return description.split('\n').map((line, index) => (
            <span key={index}>
                {line}
                {index < description.split('\n').length - 1 && <br />}
            </span>
        ));
    };

    return (
        <div className="signup-tournament-page">
            <div className="container">
                <h1>Sign Up for Tournament</h1>
                
                {/* Tournament Information */}
                <div className="section">
                    <h2>Tournament Information</h2>
                    <div className="tournament-info">
                        <div className="info-item">
                            <span className="label">Name:</span>
                            <span className="value">{tournament.name}</span>
                        </div>
                        <div className="info-item">
                            <span className="label">Start Date:</span>
                            <span className="value">{new Date(tournament.start_date).toLocaleDateString()}</span>
                        </div>
                        <div className="info-item">
                            <span className="label">End Date:</span>
                            <span className="value">{new Date(tournament.end_date).toLocaleDateString()}</span>
                        </div>
                        <div className="info-item">
                            <span className="label">Location:</span>
                            <span className="value">{tournament.location}</span>
                        </div>
                        {tournament.description && (
                            <div className="info-item description-item">
                                <span className="label">Description:</span>
                                <span className="value description-value">
                                    {formatDescription(tournament.description)}
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Player Information */}
                <div className="section">
                    <h2>Player Information</h2>
                    <div className="form-row">
                        <div className="form-group">
                            <label>First Name *</label>
                            <input
                                type="text"
                                name="firstName"
                                value={playerInfo.firstName}
                                onChange={handlePlayerInfoChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Last Name *</label>
                            <input
                                type="text"
                                name="lastName"
                                value={playerInfo.lastName}
                                onChange={handlePlayerInfoChange}
                                required
                            />
                        </div>
                    </div>
                </div>

                {/* Events Selection */}
                <div className="section">
                    <h2>Select Events</h2>
                    <div className="events-grid">
                        {tournament.events.map((event) => (
                            <div key={event.id} className="event-checkbox">
                                <input
                                    type="checkbox"
                                    id={`event-${event.id}`}
                                    checked={selectedEvents.includes(event.id)}
                                    onChange={() => handleEventChange(event.id)}
                                />
                                <label htmlFor={`event-${event.id}`}>
                                    <span>{event.name}</span>
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Groups Selection for Selected Events */}
                {selectedEvents.length > 0 && (
                    <div className="section">
                        <h2>Select Groups</h2>
                        {selectedEvents.map(eventId => {
                            const event = tournament.events.find(e => e.id === eventId);
                            return (
                                <div key={eventId} className="event-groups">
                                    <h3>{event.name}</h3>
                                    <div className="groups-list">
                                        {event.groups.map(group => (
                                            <div key={group.id} className="group-item">
                                                <input
                                                    type="radio"
                                                    id={`group-${group.id}`}
                                                    name={`group-${eventId}`}
                                                    value={group.id}
                                                    checked={selectedGroups[eventId] === group.id}
                                                    onChange={() => handleGroupChange(eventId, group.id)}
                                                />
                                                <label htmlFor={`group-${group.id}`}>
                                                    <span className="group-name">{group.name}</span>
                                                    <span className="group-format">({group.type})</span>
                                                </label>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Partner Information for Each Doubles Event */}
                {selectedEvents.map(eventId => {
                    const event = tournament.events.find(e => e.id === eventId);
                    if (isDoublesEvent(event.name)) {
                        return (
                            <div key={`partner-${eventId}`} className="section">
                                <h2>Partner Information for {event.name}</h2>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Partner First Name *</label>
                                        <input
                                            type="text"
                                            value={partnerInfo[eventId]?.firstName || ''}
                                            onChange={(e) => handlePartnerInfoChange(eventId, 'firstName', e.target.value)}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Partner Last Name *</label>
                                        <input
                                            type="text"
                                            value={partnerInfo[eventId]?.lastName || ''}
                                            onChange={(e) => handlePartnerInfoChange(eventId, 'lastName', e.target.value)}
                                            required
                                        />
                                    </div>
                                </div>
                            </div>
                        );
                    }
                    return null;
                })}

                {/* Actions */}
                <div className="actions">
                    <button className="btn-cancel" onClick={() => navigate('/tournaments')}>
                        Cancel
                    </button>
                    <button className="btn-submit" onClick={handleSubmit}>
                        Submit Registration
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SignUpTournamentPage; 