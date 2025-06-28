import { useEffect } from 'react';

// ================================================================================
// ================================================================================
// ===================== Fetch Match Info from backend ============================
// ================================================================================
// ================================================================================

export function useFetchMatchInfo(setMatches) {
    useEffect(() => {
        fetch('http://localhost:5001/api/matches')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                // console.log('Fetched matches:', data.data);
                setMatches(data.data);
                }
            })
            .catch(err => console.error('Failed to fetch match-info update:', err));
    }, [setMatches]);
};

// ================================================================================
// ================================================================================
// =========================== Get Umpire's Match  ================================
// ================================================================================
// ================================================================================

export function useFetchUmpireMatchId(currentUser, setMyMatchId) {
    useEffect(() => {
    if (currentUser?.role === 'umpire') {
      // console.log('currentUser.id: ', currentUser.id);
      fetch(`http://localhost:5001/api/matches/umpire/${currentUser.id}`)
        .then(res => res.json())
        .then(result => {
          if (result.status === 'success' && result.data?.id) {
            setMyMatchId(result.data.id);
          }
        })
    }
  }, [currentUser]);
};

// ================================================================================
// ================================================================================
// ========================= Assign Match to Umpire  ==============================
// ================================================================================
// ================================================================================

export async function assignUmpire(matchId) {
    const umpireId = prompt('Please insert Umpire User ID:');
    if (!umpireId || umpireId.trim() === '') return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(
            `http://localhost:5001/api/matches/${matchId}/umpire`,
            {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ umpire_id: umpireId })
            }
        );

        if(!response.ok) {
            console.log('failed to assign umpire...');
        }
    } catch (err) {
        console.error('Fetch error:', err);
    }
};


// ================================================================================
// ================================================================================
// ========================= Delete Match  ========================================
// ================================================================================
// ================================================================================

export async function deleteMatch(matchId) {
    // if (!confirm('Are you sure you want to delete this match?')) return;
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(
            `http://localhost:5001/api/matches/${matchId}`,
            {
                method: 'DELETE',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            }
        );

        if(!response.ok) {
            console.log('Failed to delete match...');
            return false;
        }
        
        // Return true to indicate successful deletion
        // This can be used to update the UI immediately if needed
        return true;
    } catch (err) {
        console.error('Fetch error:', err);
        return false;
    }
};

// ================================================================================
// ================================================================================
// ========================= Create Match  ========================================
// ================================================================================
// ================================================================================

export async function createMatch(matchData) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:5001/api/matches/create_match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(matchData)
        });

        if(!response.ok) {
            throw new Error('Create match failed');
        }

        return await response.json();
    } catch (err) {
        console.error('Fetch error:', err);
        throw err;
    }
}

// ================================================================================
// ================================================================================
// ================== Handle Submit in Updating User Role  ========================
// ================================================================================
// ================================================================================
export const updateUserRole = async (userId, newRole) => {
  try {
    const response = await fetch(`http://localhost:5001/api/admin/users`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        user_id: userId,
        new_role: newRole
      })
    });

    if (!response.ok) {
      throw new Error('Failed to update user role');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating user role:', error);
    throw error;
  }
};


// ================================================================================
// ================================================================================
// ========================= uplaod file  =========================================
// ================================================================================
// ================================================================================

export async function uploadFile(url, formData) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if(response.ok) {
            alert('Schedule uploaded successfully!');
        } else {
            alert('Failed to upload schedule. Please try again.');
        }
    } catch (err) {
        console.error('Error uploading schedule:', err);
        alert('An error occurred while uploading the schedule.');
    }
};

// ================================================================================
// ================================================================================
// ========================= download file  =======================================
// ================================================================================
// ================================================================================

export async function generateRoundRobin(formData) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:5001/api/admin/upload_round_robin', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (response.ok) {
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                throw new Error(errorData.message);
            } else {
                // 返回 blob 數據，讓調用者決定如何處理
                return await response.blob();
            }
        } else {
            const errorData = await response.json();
            throw new Error(errorData.message);
        }
    } catch (err) {
        console.error('Error generating round robin schedule:', err);
        throw err;
    }
};

export function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};

// ================================================================================
// ================================================================================
// ========================= fetch user info  =====================================
// ================================================================================
// ================================================================================

export async function fetchUsers() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:5001/api/admin/users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            return data.data; // return user data
        } else {
            throw new Error(data.message || 'Failed to fetch users');
        }
    } catch (err) {
        console.error("Failed to fetch users:", err);
        throw err; // rethrow error
    }
}