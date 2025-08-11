import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchInfoToBackend } from '../../api/api';
import '../../styles/pages/admin/CreateTournamentPage.css';

const TournamentCreatePage = () => {
    const navigate = useNavigate();
    const [tournamentData, setTournamentData] = useState({
        name: '',
        start_date: '',
        end_date: '',
        location: '',
        description: '',
        start_time: '09:00',
        end_time: '18:00',
        match_duration: 30,
    });
    const [selectedEvents, setSelectedEvents] = useState([]);
    const [groups, setGroups] = useState({});
    const [newGroupNames, setNewGroupNames] = useState({});
    const [groupFormats, setGroupFormats] = useState({});

    const allEvents = ["Men's Single", "Women's Single", "Men's Doubles", "Women's Doubles", "Mixed Doubles"];
    const formatOptions = [
        { value: 'elimination', label: 'Elimination' },
        { value: 'round_robin', label: 'Round Robin' },
    ];

    // 處理基本資料變更
    const handleTournamentChange = (e) => {
        const { name, value } = e.target;
        setTournamentData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // 添加處理 textarea 的函數
    const handleTextareaChange = (e) => {
        const { name, value } = e.target;
        setTournamentData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    // 添加處理鍵盤事件的函數
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && e.shiftKey) {
            // Shift + Enter: 允許換行
            return;
        } else if (e.key === 'Enter') {
            // 只有 Enter: 阻止預設行為（提交表單）
            e.preventDefault();
        }
    };

    // 處理 Event 勾選 - 修正版本
    const handleEventChange = (eventName) => {
        setSelectedEvents(prev => {
            const isCurrentlySelected = prev.includes(eventName);
            
            if (isCurrentlySelected) {
                // 移除 event 時，也要移除相關的 groups
                setGroups(currentGroups => {
                    const newGroups = { ...currentGroups };
                    delete newGroups[eventName];
                    return newGroups;
                });
                
                // 移除相關的 formats
                setGroupFormats(currentFormats => {
                    const newFormats = { ...currentFormats };
                    Object.keys(newFormats).forEach(key => {
                        if (key.startsWith(`${eventName}-`)) {
                            delete newFormats[key];
                        }
                    });
                    return newFormats;
                });
                
                // 移除相關的 newGroupName
                setNewGroupNames(currentNames => {
                    const newGroupNames = { ...currentNames };
                    delete newGroupNames[eventName];
                    return newGroupNames;
                });
                
                return prev.filter(e => e !== eventName);
            } else {
                return [...prev, eventName];
            }
        });
    };

    // 處理 group name 輸入變更
    const handleGroupNameChange = (eventName, value) => {
        setNewGroupNames(prev => ({
            ...prev,
            [eventName]: value
        }));
    };

    // 新增 Group
    const handleAddGroup = (eventName) => {
        const groupName = newGroupNames[eventName]?.trim();
        if (!groupName) {
            alert('Please enter a group name');
            return;
        }
        
        const groupId = `${eventName}-${Date.now()}`;
        const newGroup = {
            id: groupId,
            name: groupName,
            event: eventName
        };
        
        setGroups(prev => ({
            ...prev,
            [eventName]: [...(prev[eventName] || []), newGroup]
        }));
        
        // 清空該 event 的 group name
        setNewGroupNames(prev => ({
            ...prev,
            [eventName]: ''
        }));
    };

    // 移除 Group
    const handleRemoveGroup = (eventName, groupId) => {
        setGroups(prev => ({
            ...prev,
            [eventName]: prev[eventName].filter(g => g.id !== groupId)
        }));
        
        // 移除相關的 format
        setGroupFormats(prev => {
            const newFormats = { ...prev };
            delete newFormats[groupId];
            return newFormats;
        });
    };

    // 處理 Format 選擇
    const handleFormatChange = (groupId, format) => {
        setGroupFormats(prev => ({
            ...prev,
            [groupId]: format
        }));
    };

    // 提交表單
    const handleSubmit = async () => {
        // 驗證基本資料
        if (!tournamentData.name || !tournamentData.start_date || !tournamentData.end_date || !tournamentData.location) {
            alert('Please fill in all tournament information');
            return;
        }

        if (tournamentData.start_date > tournamentData.end_date) {
            alert('Starting date cannot be after ending date');
            return;
        }
        
        if (selectedEvents.length === 0) {
            alert('Please select at least one event');
            return;
        }
        
        // 驗證每個 event 都有 groups
        for (const event of selectedEvents) {
            if (!groups[event] || groups[event].length === 0) {
                alert(`Please add at least one group for ${event}`);
                return;
            }
        }
        
        // 驗證每個 group 都有 format
        for (const event of selectedEvents) {
            for (const group of groups[event]) {
                if (!groupFormats[group.id]) {
                    alert(`Please select format for group ${group.name} in ${event}`);
                    return;
                }
            }
        }

        // Add this validation in handleSubmit function
        if (!tournamentData.start_time || !tournamentData.end_time || !tournamentData.match_duration) {
            alert('Please fill in all time settings');
            return;
        }

        if (tournamentData.start_time >= tournamentData.end_time) {
            alert('Start time must be before end time');
            return;
        }

        if (tournamentData.match_duration < 15 || tournamentData.match_duration > 120) {
            alert('Match duration must be between 15 and 120 minutes');
            return;
        }
        
        // 準備提交資料 - 合併 scheduleSettings 到 tournamentData
        const submitData = {
            tournament: {
                ...tournamentData,
                start_time: tournamentData.start_time,
                end_time: tournamentData.end_time,
                match_duration: parseInt(tournamentData.match_duration)
            },
            events: selectedEvents.map(eventName => ({
                name: eventName,
                groups: groups[eventName].map(group => ({
                    name: group.name,
                    format: groupFormats[group.id]
                }))
            }))
        };
        
        console.log('Submitting:', submitData);
        
        try {
            // 這裡調用 API 來創建 tournament
            const response = await fetchInfoToBackend('http://localhost:5001/api/tournaments/create_tournament', submitData);
            console.log('Response:', response);
            alert('Tournament created successfully!');
            navigate('/tournaments');
        } catch (error) {
            alert('Failed to create tournament: ' + error.message);
        }
    };

    return (
        <div className="tournament-create-page">
            <div className="container">
                <h1>Create New Tournament</h1>
                
                {/* Tournament 基本資料 */}
                <div className="section">
                    <h2>Tournament Information</h2>
                    <div className="form-group">
                        <label>Tournament Name:</label>
                        <input
                            type="text"
                            name="name"
                            value={tournamentData.name}
                            onChange={handleTournamentChange}
                            placeholder="Enter tournament name"
                        />
                    </div>
                    <div className="form-group">
                        <label>Start Date:</label>
                        <input
                            type="date"
                            name="start_date"
                            value={tournamentData.start_date}
                            onChange={handleTournamentChange}
                        />
                    </div>
                    <div className="form-group">
                        <label>Ending Date:</label>
                        <input
                            type="date"
                            name="end_date"
                            value={tournamentData.end_date}
                            onChange={handleTournamentChange}
                        />
                    </div>
                    <div className="form-group">
                        <label>Location:</label>
                        <input
                            type="text"
                            name="location"
                            value={tournamentData.location}
                            onChange={handleTournamentChange}
                            placeholder="Enter location"
                        />
                    </div>
                    <div className="form-group">
                        <label>Tournament Description:</label>
                        <textarea
                            name="description"
                            value={tournamentData.description}
                            onChange={handleTextareaChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Enter tournament description (Shift + Enter for new line)"
                            rows={4}
                            className="description-textarea"
                        />
                    </div>
                </div>

                {/* Schedule Settings */}
                <div className="section">
                    <h2>Schedule Settings</h2>
                    <div className="form-group">
                        <label>Start Time:</label>
                        <input
                            type="time"
                            name="start_time"
                            value={tournamentData.start_time}
                            onChange={handleTournamentChange}
                        />
                    </div>
                    <div className="form-group">
                        <label>End Time:</label>
                        <input
                            type="time"
                            name="end_time"
                            value={tournamentData.end_time}
                            onChange={handleTournamentChange}
                        />
                    </div>
                    <div className="form-group">
                        <label>Match Duration (minutes):</label>
                        <input
                            type="number"
                            name="match_duration"
                            value={tournamentData.match_duration}
                            onChange={handleTournamentChange}
                            min="15"
                            max="120"
                            step="5"
                        />
                    </div>
                </div>

                {/* Event 選擇 */}
                <div className="section">
                    <h2>Select Events</h2>
                    <div className="events-grid">
                        {allEvents.map(event => (
                            <label key={event} className="event-checkbox">
                                <input
                                    type="checkbox"
                                    checked={selectedEvents.includes(event)}
                                    onChange={() => handleEventChange(event)}
                                />
                                <span>{event}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Groups 配置 */}
                {selectedEvents.length > 0 && (
                    <div className="section">
                        <h2>Configure Groups</h2>
                        {selectedEvents.map(eventName => (
                            <div key={eventName} className="event-groups">
                                <h3>{eventName}</h3>
                                
                                {/* 新增 Group */}
                                <div className="add-group">
                                    <input
                                        type="text"
                                        value={newGroupNames[eventName] || ''}
                                        onChange={(e) => handleGroupNameChange(eventName, e.target.value)}
                                        placeholder="Enter group name"
                                        onKeyPress={(e) => e.key === 'Enter' && handleAddGroup(eventName)}
                                    />
                                    <button 
                                        onClick={() => handleAddGroup(eventName)}
                                        className="btn-add-group"
                                    >
                                        Add Group
                                    </button>
                                </div>
                                
                                {/* 顯示 Groups */}
                                <div className="groups-list">
                                    {groups[eventName]?.map(group => (
                                        <div key={group.id} className="group-item">
                                            <span className="group-name">{group.name}</span>
                                            <select
                                                value={groupFormats[group.id] || ''}
                                                onChange={(e) => handleFormatChange(group.id, e.target.value)}
                                                className="format-select"
                                            >
                                                <option value="">Select Format</option>
                                                {formatOptions.map(option => (
                                                    <option key={option.value} value={option.value}>
                                                        {option.label}
                                                    </option>
                                                ))}
                                            </select>
                                            <button 
                                                onClick={() => handleRemoveGroup(eventName, group.id)}
                                                className="btn-remove"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* 提交按鈕 */}
                <div className="actions">
                    <button onClick={() => navigate('/admin/tournaments')} className="btn-cancel">
                        Cancel
                    </button>
                    <button onClick={handleSubmit} className="btn-submit">
                        Create Tournament
                    </button>
                </div>
            </div>
        </div>
    );
};

export default TournamentCreatePage; 