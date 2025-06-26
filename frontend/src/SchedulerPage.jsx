import { useState } from 'react';
import { uploadFile } from './api/api';
import { generateRoundRobin, downloadBlob } from './api/api';

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
        try {
            const formData = new FormData();
            formData.append('file', file);

            // console.log('Uplaoding file:', file);
            // uploadFile('http://localhost:5001/api/admin/upload_round_robin', formData);

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
            <button type="button" onClick={handleUpload}>Upload</button>
        </div>
    );
};

export default UploadSchedule;