import axios from 'axios';

// Use the live Render backend URL, but allow local override if needed
const API_BASE = import.meta.env.VITE_API_BASE || 'https://ai-code-reviewer-7711.onrender.com/api';

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
