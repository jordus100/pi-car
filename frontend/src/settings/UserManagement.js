import React, {useEffect, useState} from "react";
import {addUser, deleteUser, getAllUsers} from "../services/Api";
import {getSftpSettings} from "../services/Api";

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [newUser, setNewUser] = useState({ name: '', email: '' });
  const [message, setMessage] = useState('')

  async function getUsers() {
    try {
      const users = await getAllUsers()
      setUsers(users)
    }
    catch (e) {
      console.error(e)
    }
  }

  const handleAddUser = async () => {
    setMessage('')
    if (newUser.name && newUser.password) {
      try {
        await addUser(newUser.name, newUser.password)
        await getUsers()
      } catch (e) {
        if (e.response) {
          setMessage(e.response.data.message);
        } else {
          setMessage('Failed to add user ' + newUser.name)
        }
      }
    }
  };

  const handleDeleteUser = async (id) => {
    if (window.confirm(`Are you sure you want to delete user ${users.find(user => { return user.id === id }).username}?`)) {
      try {
        await deleteUser(id)
        await getUsers()
      } catch(e) {
        if (e.response) {
        setMessage(e.response.data.message);
        } else {
        setMessage('Failed to delete user')
        }
      }
    }
  };

  useEffect(() => {
    getUsers()
  }, []);

  return (
    <section className="user-management">
      <h2>User Management</h2>
      <div className="simple-form">
        <input
          type="text"
          placeholder="Name"
          value={newUser.name}
          onChange={(e) => setNewUser({...newUser, name: e.target.value})}
        />
        <input
          type="text"
          placeholder="Password"
          value={newUser.password}
          onChange={(e) => setNewUser({...newUser, password: e.target.value})}
          required
          minLength={8}
        />
        <button onClick={handleAddUser}>Add User</button>
        <p>{message}</p>
      </div>
      <table className="user-table">
        <thead>
        <tr>
          <th>Name</th>
          <th>Actions</th>
        </tr>
        </thead>
        <tbody>
        {users.map(user => (
          <tr key={user.id}>
            <td>{user.username}</td>
            <td>
              <button onClick={() => handleDeleteUser(user.id)}>Delete</button>
            </td>
          </tr>
        ))}
        </tbody>
      </table>
    </section>
  )
}