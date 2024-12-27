import { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5000'); // Replace with your Flask backend URL

export const useSocket = () => {
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Handle connect event
        socket.on('connect', () => {
            setIsConnected(true);
            console.log('Connected to server:', socket.id);
        });

        // Handle disconnection
        socket.on('disconnect', () => {
            setIsConnected(false);
            console.log('Disconnected from server');
        });

        return () => {
            socket.off('connect');
            socket.off('disconnect');
        };
    }, []);

    // Send the username to the server
    const sendUsername = (username) => {
        socket.emit('set_username', { username });
    };

    return { socket, isConnected, sendUsername };
};
