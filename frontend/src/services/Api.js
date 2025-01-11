import axios from 'axios';

export const Api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  withCredentials: true,
})

export const getRobotControlWsData = async () => {
  const response = await Api.post('/control/startSession');
  return response.data;
}

export const getSettings = async () => {
  const response = await Api.get('/settings');
  return response.data;
}