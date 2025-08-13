import { useState } from 'react';
import { uploadFile } from '../../api/api';
import { generateRoundRobin, downloadBlob } from '../../api/api';

const UploadSchedule = () => {
    const [file, setFile] = useState(null);
    const [totalCourt, setTotalCourt] = useState(null);

    const handleChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if(!file) {
            alert('Please select a file to upload.');
            return;
        }
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('total_court', totalCourt);

            const blob = await generateRoundRobin(formData);
            downloadBlob(blob, 'round_robin_schedule.xlsx');
            alert('Schedule generated successfully!');
        } catch (err) {
            alert('Error generating schedule. Please try again.');
            console.error('Error generating schedule:', err);
        }
        
    };

    return (
        <div>
            <h2>Upload the round robin</h2>
            <input type="file" onChange={handleChange} accept=".csv, .xlsx" />
            <select
                value={totalCourt}
                onChange={(e) => setTotalCourt(e.target.value)}
            >
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
                <option value="6">6</option>
                <option value="7">7</option>
                <option value="8">8</option>
                <option value="9">9</option>
                <option value="10">10</option>
            </select>
            <button type="button" onClick={handleUpload}>Upload</button>
        </div>
    );
};

export default UploadSchedule;