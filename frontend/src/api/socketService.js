import { useEffect } from 'react';
import io from 'socket.io-client';

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
// =========================== Match Info Listener  ===============================
// ================================================================================
// ================================================================================
export function useMatchInfoListener(socketRef, { setMatches, setAnimatingMatchId }) {
    useEffect(() => {
        // if there exist connection, disconnect
        if (socketRef.current) {
            socketRef.current.disconnect();
        }

        // establish new connection
        socketRef.current = io('http://localhost:5001/scoreboard', {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 3000
        });

        socketRef.current.on('connect', () => {
        // console.log('WebSocket 已連接！Socket ID:', socketRef.current.id);
        });

        socketRef.current.on('match_update', (data) => {
            console.log('Receive Match Info Update:', data);
            
            setMatches(prev =>
                prev.map(m => m.id === data.id ? { ...m, ...data } : m)
            );

            // animating effect
            setAnimatingMatchId(true);
            setTimeout(() => setAnimatingMatchId(false), 200);
        });

        socketRef.current.on('connect_error', (err) => {
        // console.error('連接錯誤:', err.message);
        });

        // remove function
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };
    }, [setMatches, setAnimatingMatchId]);
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