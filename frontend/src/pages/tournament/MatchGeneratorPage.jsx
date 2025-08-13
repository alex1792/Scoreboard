import { useState } from 'react';
import { uploadAndDownload } from '../../api/api';
import '../../styles/pages/tournament/MatchGenerator.css';
import { API_URLS } from '../../config/urls';

const MatchGenerator = () => {
    const [file, setFile] = useState(null);
    const [matchRules, setMatchRules] = useState({});
    const [roundRobinGroupSize, setRoundRobinGroupSize] = useState(4);

    const allCategories = ['MS', 'WS', 'MD', 'WD', 'XD'];
    const allFlights = ['A', 'B', 'C'];

    // initialize all combinations
    const initializeRules = () => {
        const rules = {};
        allCategories.forEach(cat => {
            allFlights.forEach(flight => {
                const key = `${cat}-${flight}`;
                rules[key] = {
                    enabled: true,
                    type: 'e', // defounlt elimination
                    groupSize: 4
                };
            });
        });
        setMatchRules(rules);
    };

    // initialize when component loads
    useState(() => {
        initializeRules();
    }, []);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleRuleChange = (key, field, value) => {
        setMatchRules(prev => ({
            ...prev,
            [key]: {
                ...prev[key],
                [field]: value
            }
        }));
    };

    const selectAll = (type) => {
        const newRules = {};
        Object.keys(matchRules).forEach(key => {
            newRules[key] = {
                ...matchRules[key],
                type: type
            };
        });
        setMatchRules(newRules);
    };

    const toggleAll = (enabled) => {
        const newRules = {};
        Object.keys(matchRules).forEach(key => {
            newRules[key] = {
                ...matchRules[key],
                enabled: enabled
            };
        });
        setMatchRules(newRules);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            alert('Please select a file to upload.');
            return;
        }

        // check if there are enabled combinations
        const enabledCombinations = Object.entries(matchRules).filter(([key, rule]) => rule.enabled);
        if (enabledCombinations.length === 0) {
            alert('Please enable at least one category-flight combination.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        
        // build rules string
        const rulesString = enabledCombinations.map(([key, rule]) => {
            if (rule.type === 'r') {
                return `${key}:r,${rule.groupSize}`;
            } else {
                return `${key}:e`;
            }
        }).join(';');
        
        formData.append('rules', rulesString);

        uploadAndDownload(API_URLS.UPLOAD_PARTICIPANTS, formData, 'all_matches.xlsx');
    };

    const getEnabledCount = () => Object.values(matchRules).filter(rule => rule.enabled).length;

    return (
        <div className="match-generator">
            <h2>Generate Match Schedule</h2>
            
            {/* File Upload Section */}
            <div className="upload-section">
                <h3>Upload Participants File</h3>
                <input 
                    type="file" 
                    onChange={handleFileChange} 
                    accept=".csv, .xlsx" 
                    className="file-input"
                />
                {file && <p className="file-info">Selected: {file.name}</p>}
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="action-buttons">
                    <button onClick={() => selectAll('e')} className="action-btn elimination-btn">
                        Set All to Elimination
                    </button>
                    <button onClick={() => selectAll('r')} className="action-btn roundrobin-btn">
                        Set All to Round Robin
                    </button>
                    <button onClick={() => toggleAll(true)} className="action-btn enable-btn">
                        Enable All
                    </button>
                    <button onClick={() => toggleAll(false)} className="action-btn disable-btn">
                        Disable All
                    </button>
                </div>
            </div>

            {/* Round Robin Group Size */}
            <div className="group-size-section">
                <h3>Round Robin Group Size</h3>
                <p>This setting applies to all Round Robin matches</p>
                <select 
                    value={roundRobinGroupSize} 
                    onChange={(e) => setRoundRobinGroupSize(parseInt(e.target.value))}
                    className="group-size-select"
                >
                    <option value={3}>3 players per group</option>
                    <option value={4}>4 players per group</option>
                    <option value={5}>5 players per group</option>
                    <option value={6}>6 players per group</option>
                    <option value={7}>7 players per group</option>
                    <option value={8}>8 players per group</option>
                    <option value={9}>9 players per group</option>
                    <option value={10}>10 players per group</option>
                </select>
            </div>

            {/* Match Rules Table */}
            <div className="rules-table-section">
                <h3>Match Rules Configuration</h3>
                <div className="table-container">
                    <table className="rules-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                {allFlights.map(flight => (
                                    <th key={flight}>Flight {flight}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {allCategories.map(category => (
                                <tr key={category}>
                                    <td className="category-cell">{category}</td>
                                    {allFlights.map(flight => {
                                        const key = `${category}-${flight}`;
                                        const rule = matchRules[key];
                                        
                                        return (
                                            <td key={flight} className="rule-cell">
                                                <div className="rule-controls">
                                                    <label className="enable-checkbox">
                                                        <input
                                                            type="checkbox"
                                                            checked={rule?.enabled || false}
                                                            onChange={(e) => handleRuleChange(key, 'enabled', e.target.checked)}
                                                        />
                                                        Enable
                                                    </label>
                                                    
                                                    {rule?.enabled && (
                                                        <div className="rule-type-controls">
                                                            <label className="rule-type-radio">
                                                                <input
                                                                    type="radio"
                                                                    name={`type-${key}`}
                                                                    value="e"
                                                                    checked={rule?.type === 'e'}
                                                                    onChange={(e) => handleRuleChange(key, 'type', e.target.value)}
                                                                />
                                                                <span className="radio-label">Elimination</span>
                                                            </label>
                                                            
                                                            <label className="rule-type-radio">
                                                                <input
                                                                    type="radio"
                                                                    name={`type-${key}`}
                                                                    value="r"
                                                                    checked={rule?.type === 'r'}
                                                                    onChange={(e) => handleRuleChange(key, 'type', e.target.value)}
                                                                />
                                                                <span className="radio-label">Round Robin</span>
                                                            </label>
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Summary and Generate Button */}
            <div className="summary-section">
                <div className="combination-info">
                    <p>Enabled combinations: <strong>{getEnabledCount()}</strong></p>
                    <p>Round Robin group size: <strong>{roundRobinGroupSize} players</strong></p>
                    <div className="rules-summary">
                        <h4>Selected Rules:</h4>
                        {Object.entries(matchRules)
                            .filter(([key, rule]) => rule.enabled)
                            .map(([key, rule]) => (
                                <div key={key} className="rule-summary-item">
                                    <span className="rule-key">{key}:</span>
                                    <span className={`rule-type ${rule.type}`}>
                                        {rule.type === 'e' ? 'Elimination' : `Round Robin (${roundRobinGroupSize})`}
                                    </span>
                                </div>
                            ))}
                    </div>
                </div>
                <button 
                    type="button" 
                    onClick={handleUpload}
                    disabled={!file || getEnabledCount() === 0}
                    className="generate-btn"
                >
                    Generate Matches
                </button>
            </div>
        </div>
    );
};

export default MatchGenerator;