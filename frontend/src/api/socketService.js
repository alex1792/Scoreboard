import { useEffect } from 'react';
import { io } from 'socket.io-client';
import { PROD_BASE_URL, DEV_BASE_URL } from '../config/urls';

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

        // 修復 WebSocket URL 配置
        const socketUrl = process.env.NODE_ENV === 'production' 
            ? `${PROD_BASE_URL}`  
            : `${DEV_BASE_URL}`;  

        console.log('🔗 MatchesPage connecting to WebSocket:', `${socketUrl}/scoreboard`);

        // 修復：直接連接到正確的namespace
        socketRef.current = io(`${socketUrl}/scoreboard`, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 3000,
            path: '/socket.io/'
        });

        socketRef.current.on('connect', () => {
            console.log('✅ MatchesPage WebSocket connected! Socket ID:', socketRef.current.id);
        });

        socketRef.current.on('match_update', (data) => {
            console.log('📡 MatchesPage received match update:', data);
            console.log('Match status:', data.status);
            console.log('Match scores:', { score1: data.score1, score2: data.score2 });
            
            setMatches(prev => {
                if (!Array.isArray(prev)) {
                    console.error('setMatches received non-array:', prev);
                    return prev;
                }
                
                const updated = prev.map(m => {
                    if (m.id === data.id) {
                        const merged = { ...m, ...data };
                        console.log('Updating match:', m.id);
                        console.log('Before:', { 
                            score1: m.score1, 
                            score2: m.score2, 
                            player1_score: m.player1_score, 
                            player2_score: m.player2_score 
                        });
                        console.log('After:', { 
                            score1: merged.score1, 
                            score2: merged.score2, 
                            player1_score: merged.player1_score, 
                            player2_score: merged.player2_score 
                        });
                        return merged;
                    }
                    return m;
                });
                
                console.log('Updated matches list length:', updated.length);
                return updated;
            });

            // animating effect
            if (setAnimatingMatchId) {
                setAnimatingMatchId(data.id);
                setTimeout(() => setAnimatingMatchId(null), 1000);
            }
        });

        socketRef.current.on('match_delete', (data) => {
            console.log('️ Match Deleted:', data);
            
            setMatches(prev => {
                if (!Array.isArray(prev)) {
                    console.error('setMatches received non-array:', prev);
                    return prev;
                }
                
                return prev.filter(m => m.id !== data.id);
            });
        });

        socketRef.current.on('connect_error', (err) => {
            console.error('❌ MatchesPage WebSocket connection error:', err.message);
        });

        socketRef.current.on('disconnect', (reason) => {
            console.log(' MatchesPage WebSocket disconnected:', reason);
        });

        // remove function
        return () => {
            if (socketRef.current) {
                console.log('🧹 Cleaning up MatchesPage WebSocket connection');
                socketRef.current.disconnect();
            }
        };
    }, []); // 移除依賴項
}
