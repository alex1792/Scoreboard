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

        console.log('🔗 嘗試連接WebSocket到:', socketUrl);
        console.log('🌍 當前環境:', process.env.NODE_ENV);

        // 修復：直接連接到正確的namespace
        socketRef.current = io(`${socketUrl}/scoreboard`, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 3000,
            path: '/socket.io/'
        });

        socketRef.current.on('connect', () => {
            console.log('✅ WebSocket 已連接！Socket ID:', socketRef.current.id);
            console.log('Namespace:', socketRef.current.nsp);
        });

        socketRef.current.on('match_update', (data) => {
            console.log('📡 收到比賽更新:', data);
            
            setMatches(prev => {
                const updated = prev.map(m => m.id === data.id ? { ...m, ...data } : m);
                console.log('🔄 更新比賽列表:', updated);
                return updated;
            });

            // animating effect
            setAnimatingMatchId(true);
            setTimeout(() => setAnimatingMatchId(false), 200);
        });

        socketRef.current.on('match_delete', (data) => {
            console.log('🗑️ Match Deleted:', data);
            
            setMatches(prev => 
                prev.filter(m => m.id !== data.id)
            );
        });

        socketRef.current.on('connect_error', (err) => {
            console.error('❌ WebSocket 連接錯誤:', err.message);
            console.error('錯誤詳情:', err);
        });

        socketRef.current.on('disconnect', (reason) => {
            console.log('🔌 WebSocket 斷開連接:', reason);
        });

        // remove function
        return () => {
            if (socketRef.current) {
                console.log('🧹 清理WebSocket連接');
                socketRef.current.disconnect();
            }
        };
    }, [setMatches, setAnimatingMatchId]);
}
