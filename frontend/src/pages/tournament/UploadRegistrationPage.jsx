import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { uploadRegistrationFile, fetchInfoFromBackend } from '../../api/api';
import '../../styles/pages/tournament/UploadRegistrationPage.css';

const UploadRegistrationPage = () => {
  const { tournamentId } = useParams();
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [tournament, setTournament] = useState(null);

  // 取得錦標賽資料
  useEffect(() => {
    const fetchTournament = async () => {
      try {
        const data = await fetchInfoFromBackend(`http://localhost:5001/api/tournaments/${tournamentId}`);
        if (data.status === 'success') {
          setTournament(data.data);
        }
      } catch (error) {
        console.error('Error fetching tournament:', error);
      }
    };
    fetchTournament();
  }, [tournamentId]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (
        selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        selectedFile.type === 'application/vnd.ms-excel'
      ) {
        setFile(selectedFile);
        setMessage('');
      } else {
        setMessage('Please select a valid Excel file (.xlsx or .xls)');
        setMessageType('error');
        setFile(null);
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload');
      setMessageType('error');
      return;
    }
    setUploading(true);
    setMessage('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('tournament_id', tournamentId);
      const response = await uploadRegistrationFile(formData, tournamentId);
      if (response.status === 'success') {
        setMessage(`Successfully uploaded ${response.data?.count || 0} registrations!`);
        setMessageType('success');
        setFile(null);
        setTimeout(() => {
          navigate(`/tournaments/${tournamentId}/check-registration`);
        }, 2000);
      } else {
        setMessage(response.message || 'Upload failed');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Network error, please try again');
      setMessageType('error');
    } finally {
      setUploading(false);
    }
  };

  // 動態產生範例資料
  const generateExampleRows = () => {
    if (!tournament || !tournament.events) return [];
    const rows = [];
    tournament.events.forEach(event => {
      event.groups.forEach(group => {
        if (event.category === 'MS' || event.category === 'WS') {
          // 單打
          rows.push({
            firstName: 'Player1 Frist Name',
            lastName: 'Player1 Last Name',
            email: 'player1@example.com',
            event: event.name,
            group: group.name,
            partnerFirstName: '',
            partnerLastName: ''
          });
        } else {
          // 雙打
          rows.push({
            firstName: 'Player1 Frist Name',
            lastName: 'Player1 Last Name',
            email: 'player1@example.com',
            event: event.name,
            group: group.name,
            partnerFirstName: 'Player2 Frist Name',
            partnerLastName: 'Player2 Last Name'
          });
        }
      });
    });
    return rows;
  };

  return (
    <div className="upload-registration-container">
      <div className="upload-header">
        <h1>Upload Tournament Registrations</h1>
        <p>Upload an Excel file to bulk import registrations for this tournament.</p>
      </div>

      <div className="instructions">
        <h3>File Format Instructions</h3>
        <div className="instruction-content">
          <p>Your Excel file should contain the following columns:</p>
          <ul>
            <li><strong>First Name</strong> - Player's first name</li>
            <li><strong>Last Name</strong> - Player's last name</li>
            <li><strong>Email</strong> - Player's email address</li>
            <li><strong>Event</strong> - Event name (see below)</li>
            <li><strong>Group</strong> - Group name (see below)</li>
            <li><strong>Partner First Name</strong> - Partner's first name (for doubles only)</li>
            <li><strong>Partner Last Name</strong> - Partner's last name (for doubles only)</li>
          </ul>
          {tournament && (
            <div className="tournament-info">
              <div className="tournament-header">
                <h4>Available Events and Groups for "{tournament.name}":</h4>
              </div>
              <div className="events-list">
                {tournament.events.map(event => (
                  <div key={event.id} className="event-item">
                    <div className="event-name">{event.name}</div>
                    <div className="event-details">
                      <div className="event-detail">
                        <span>Groups:</span>
                        <span>{event.groups.map(group => group.name).join(', ')}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="example-section">
            <h4>Example:</h4>
            <div className="example-table">
              <table>
                <thead>
                  <tr>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Email</th>
                    <th>Event</th>
                    <th>Group</th>
                    <th>Partner First Name</th>
                    <th>Partner Last Name</th>
                  </tr>
                </thead>
                <tbody>
                  {generateExampleRows().length > 0 ? (
                    generateExampleRows().map((row, idx) => (
                      <tr key={idx}>
                        <td>{row.firstName}</td>
                        <td>{row.lastName}</td>
                        <td>{row.email}</td>
                        <td>{row.event}</td>
                        <td>{row.group}</td>
                        <td>{row.partnerFirstName}</td>
                        <td>{row.partnerLastName}</td>
                      </tr>
                    ))
                  ) : (
                    <>
                      <tr>
                        <td>John</td>
                        <td>Lin</td>
                        <td>john@example.com</td>
                        <td>Men's Single</td>
                        <td>A</td>
                        <td></td>
                        <td></td>
                      </tr>
                      <tr>
                        <td>Jane</td>
                        <td>Liu</td>
                        <td>jane@example.com</td>
                        <td>Women's Doubles</td>
                        <td>B</td>
                        <td>Mary</td>
                        <td>Hsu</td>
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <div className="upload-section">
        <div className="file-upload-area">
          <h3>Select Excel File</h3>
          <form onSubmit={handleUpload}>
            <div className="file-input-container">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".xlsx,.xls"
                className="file-input"
                id="registration-file"
              />
              <label htmlFor="registration-file" className="file-label">
                <div className="upload-icon">
                  <img src="/upload-arrow-icon.png" alt="Upload" className="upload-icon-img" />
                </div>
                <span>Choose Excel file</span>
                <small>Supports .xlsx and .csv files</small>
              </label>
            </div>
            {file && (
              <div className="file-info">
                <p>Selected file: <strong>{file.name}</strong></p>
                <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
              </div>
            )}
            <button
              type="submit"
              className="upload-btn"
              disabled={!file || uploading}
            >
              {uploading ? 'Uploading...' : 'Upload Registrations'}
            </button>
          </form>
        </div>
        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}
      </div>

      
    </div>
  );
};

export default UploadRegistrationPage;