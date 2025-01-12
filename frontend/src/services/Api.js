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

export const changePassword = async(oldPass, newPass) => {
  const response = await Api.post('/change_password', { "old_password": oldPass, "new_password": newPass });
  return response.data;
}

export const getAllUsers = async () => {
  const response = await Api.get('/users');
  return response.data;
}

export const addUser = async (name, pass) => {
  const res = await Api.post('/add_user', {'username': name, 'password': pass})
  return res.data
}

export const deleteUser = async (id) => {
  const res = await Api.delete(`/users/${id}`)
  return res.data
}

export const turnOffRobot = async () => {
  const res = await Api.post('/shutdown')
  return res.data
}

export const joinZerotierNetwork = async (networkId) => {
  const res = await Api.post('/zerotier', {networkId})
  return res.data
}

export const getSftpSettings = async () => {
  const res = await Api.get('/sftp')
  return res.data
}

export const saveSftpSettings = async (username, password, port, host) => {
  const res = await Api.post('/sftp', {username, password, port, host})
  return res.data
}

export const getIpData = async () => {
  const res = await Api.get('/ip')
  return res.data
}