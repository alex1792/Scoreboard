import { useState } from 'react';

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

        try {
            const response = await fetch('http://localhost:5001/api/admin/upload_match_schedule', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData,
            });

            // console.log('token: ', localStorage.getItem('access_token'));

            if(response.ok) {
                alert('Schedule uploaded successfully!');
            } else {
                alert('Failed to upload schedule. Please try again.');
            }
        } catch (error) {
            console.error('Error uploading schedule:', error);
            alert('An error occurred while uploading the schedule.');
        }
    };

    return (
        <div>
            <input type="file" onChange={handleChange} accept=".csv, .xlsx" />
            <button type="button" onClick={handleUpload}>Upload</button>
        </div>
    );
};

export default UploadSchedule;