import axios from 'axios';

const API_BASE = '/api';

export async function analyzeCode(code, language, filename = 'untitled') {
    const response = await axios.post(`${API_BASE}/analyze`, {
        code,
        language,
        filename,
    });
    return response.data;
}

export async function getHistory() {
    const response = await axios.get(`${API_BASE}/history`);
    return response.data;
}
