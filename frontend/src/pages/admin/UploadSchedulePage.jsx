import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // 加入 useNavigate

const UploadSchedulePage = () => {
  const { tournamentId } = useParams(); // 從 URL 獲取 tournamentId
  const navigate = useNavigate(); // 加入這行
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    // 不需要再 append tournament_id，因為在 URL 中

    try {
        const token = localStorage.getItem('access_token');
      
        const response = await fetch(`http://localhost:5001/api/admin/tournament/${tournamentId}/upload-schedule`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      const data = await response.json();
      setResult(data);
      
      // 只有在成功時才 redirect
      if (data.status === 'success') {
        navigate(`/tournaments/${tournamentId}/schedule`);
      }
    } catch (error) {
      setResult({ status: 'error', message: 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-schedule-page">
      <h2>Upload my custom schedule</h2>
      <p>Tournament ID: {tournamentId}</p>
      
      <div className="upload-section">
        <input
          type="file"
          accept=".xlsx,.xls"  // 允許更多 Excel 格式
          onChange={handleFileChange}
        />
        <button 
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? 'Uploading...' : 'Upload Schedule'}
        </button>
      </div>

      {result && (
        <div className={`result ${result.status}`}>
          <p>{result.message}</p>
          {result.details && (
            <pre>{JSON.stringify(result.details, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadSchedulePage;