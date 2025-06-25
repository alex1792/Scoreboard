import { useEffect } from 'react';
import io from 'socket.io-client';

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

        socketRef.current.on('match_delete', (data) => {
            console.log('Match Deleted:', data);
            
            // Remove the deleted match from the state
            setMatches(prev => 
                prev.filter(m => m.id !== data.id)
            );
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
