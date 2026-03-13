import axios from 'axios';

// The backend server will be running on port 5000 (default for Flask)
const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getConfigs = async () => {
    try {
        const response = await api.get('/config');
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export const optimizeRoute = async (network, algorithm, startNode, endNode) => {
    try {
        const response = await api.post('/optimize', {
            network,
            algorithm,
            start_node: startNode,
            end_node: endNode,
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

export default api;
