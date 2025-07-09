import { useState } from 'react';
import { Link } from 'react-router-dom';
import { uploadFile } from '../../api/api';

const UploadSchedule = () => {
    const [file, setFile] = useState(null);

    const handleChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if(!file) {
            alert('Please select a file to upload.');
            return;
        }
        const formData = new FormData();
        formData.append('file', file);

        // console.log('Uplaoding file:', file);
        uploadFile('http://localhost:5001/api/admin/upload_match_schedule', formData);
    };

    return (
        <div style={{ padding: '2rem' }}>
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '2rem'
            }}>
                <h2>Upload Match Schedule</h2>
                <Link to="/admin/match-generator" style={{ 
                    display: 'inline-block', 
                    padding: '10px 20px', 
                    backgroundColor: '#4CAF50', 
                    color: 'white', 
                    textDecoration: 'none', 
                    borderRadius: '8px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    border: 'none',
                    fontSize: '14px'
                }}>
                    Generate All Matches
                </Link>
                <Link to="/admin/scheduler" style={{ 
                    display: 'inline-block', 
                    padding: '10px 20px', 
                    backgroundColor: '#4CAF50', 
                    color: 'white', 
                    textDecoration: 'none', 
                    borderRadius: '8px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    border: 'none',
                    fontSize: '14px'
                }}>
                    Generate Schedule
                </Link>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
                <input type="file" onChange={handleChange} accept=".csv, .xlsx" />
                <button type="button" onClick={handleUpload}>Upload</button>
            </div>
        </div>
    );
};

export default UploadSchedule;