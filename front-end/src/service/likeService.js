// const API_URL = 'https://twitter-remake-backend.onrender.com/api';
const API_URL = 'http://localhost:8000/api';

export const addLike = async (tweetId) => {
    const res = await fetch(`${API_URL}/tweets/${tweetId}/like`, {
        method: 'POST'
    });
    if (!res.ok) {
        throw new Error('Failed to like tweet');
    }
    const { cached } = await res.json();
    return cached;
};