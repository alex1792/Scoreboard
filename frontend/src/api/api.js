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
}

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
}

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
// ================== Handle Submit in Updating User Role  ========================
// ================================================================================
// ================================================================================
export async function updateUserRole(username, role) {
    // e.preventDefault();
    const response = await fetch('http://localhost:5001/api/admin/users', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
            username: username,
            role: role
        })
    });

    if(!response.ok) {
        throw new Error('Update failed');
    }

    return await response.json();
};



// const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       // request information for updating user role
//       const requestInfo = {
//         url: 'http://localhost:5001/api/admin/upate_user_role',
//         method: 'PUT',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
//         },
//         body: JSON.stringify({ 
//           username,
//           role 
//         }),
//       };

//       const response = await fetch(requestInfo.url, requestInfo);
//       if (!response.ok) throw new Error('Update failed');

//       const result = await response.json();
//       // console.log('Update successful:', result);
//     } catch (err) {
//       console.error(err);
//     }
//   };