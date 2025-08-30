import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { generateScheduleFromDatabase, downloadBlob } from '../../api/api';
import { useNavigate } from 'react-router-dom';

const GenerateSchedulePage = () => {
    const { tournamentId } = useParams();
    const navigate = useNavigate();
    const [totalCourt, setTotalCourt] = useState(6);
    const [isGenerating, setIsGenerating] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('');

    const handleGenerateSchedule = async (e) => {
        e.preventDefault();
        setIsGenerating(true);
        setMessage('');

        try {
            const blob = await generateScheduleFromDatabase(tournamentId, totalCourt);
            downloadBlob(blob, `tournament_${tournamentId}_schedule.xlsx`);
            setMessage('Schedule generated and downloaded successfully!');
            setMessageType('success');
        } catch (error) {
            setMessage(`Error generating schedule: ${error.message}`);
            setMessageType('error');
        } finally {
            setIsGenerating(false);
            navigate(`/tournaments/${tournamentId}/schedule`);
        }
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <h1>Generate Match Schedule</h1>
                <p>Generate a match schedule from existing tournament matches in the database.</p>
            </div>

            <div style={{ 
                background: '#f8f9fa', 
                padding: '1.5rem', 
                borderRadius: '8px', 
                marginBottom: '2rem',
                borderLeft: '4px solid #3498db'
            }}>
                <h3>How it works</h3>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                    <li>Reads all matches from the tournament in the database</li>
                    <li>Generates an optimized schedule to minimize consecutive player appearances</li>
                    <li>Creates an Excel file with the scheduled matches organized by batches</li>
                    <li>Highlights matches where players appear in consecutive batches</li>
                </ul>
            </div>

            <div style={{ 
                background: '#ffffff', 
                padding: '1.5rem', 
                border: '2px solid #e9ecef', 
                borderRadius: '8px',
                marginBottom: '2rem'
            }}>
                <h3>Schedule Settings</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontWeight: '600', color: '#495057' }}>
                        Number of Courts Available:
                    </label>
                    <select
                        value={totalCourt}
                        onChange={(e) => setTotalCourt(parseInt(e.target.value))}
                        disabled={isGenerating}
                        style={{
                            padding: '0.75rem',
                            border: '2px solid #e9ecef',
                            borderRadius: '6px',
                            fontSize: '1rem',
                            background: '#ffffff'
                        }}
                    >
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                            <option key={num} value={num}>{num}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div style={{ textAlign: 'center' }}>
                <button
                    onClick={handleGenerateSchedule}
                    disabled={isGenerating}
                    style={{
                        background: 'linear-gradient(135deg, #3498db, #2980b9)',
                        color: 'white',
                        border: 'none',
                        padding: '1rem 2rem',
                        fontSize: '1.1rem',
                        fontWeight: '600',
                        borderRadius: '8px',
                        cursor: isGenerating ? 'not-allowed' : 'pointer',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        boxShadow: '0 4px 6px rgba(52, 152, 219, 0.2)',
                        opacity: isGenerating ? 0.6 : 1
                    }}
                >
                    {isGenerating ? 'Generating...' : 'Generate Schedule'}
                </button>
            </div>

            {message && (
                <div style={{
                    padding: '1rem',
                    borderRadius: '6px',
                    fontWeight: '500',
                    textAlign: 'center',
                    marginTop: '1rem',
                    background: messageType === 'success' ? '#d4edda' : '#f8d7da',
                    color: messageType === 'success' ? '#155724' : '#721c24',
                    border: `1px solid ${messageType === 'success' ? '#c3e6cb' : '#f5c6cb'}`
                }}>
                    {message}
                </div>
            )}
        </div>
    );
};

export default GenerateSchedulePage; 