import { useEffect } from 'react';
import io from 'socket.io-client';
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
            ? `${PROD_BASE_URL}`  // 移除 /scoreboard，使用根路徑
            : `${DEV_BASE_URL}`;  // 移除 /scoreboard，使用根路徑

        socketRef.current = io(socketUrl, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 3000,
            path: '/socket.io/'  // 明確指定 Socket.IO 路徑
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
