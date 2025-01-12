import React, {useState} from "react";
import {changePassword} from "../services/Api";

export default function ChangePassword() {
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [message, setMessage] = useState('');
  const [oldPass, setOldPass] = useState('');
  const [newPass, setNewPass] = useState('');
  function onPasswordChangeSubmit(e) {
    e.preventDefault();
    changePassword(oldPass, newPass)
      .then(() => setMessage('Password changed successfully'))
      .catch((e) => {
        if (e.response) {
          setMessage(e.response.data.message);
        } else {
          setMessage('Failed to change password')
        }
      });
  }
  return (
    <section className="password-section">
      <button className="toggle-btn" onClick={() => { setShowPasswordForm(!showPasswordForm); }}>
        {showPasswordForm ? 'Close Password Form' : 'Change Password'}
      </button>
      {showPasswordForm && (
        <>
        <form className="password-form" onSubmit={onPasswordChangeSubmit}>
          <input value={oldPass} onChange={(e) => setOldPass(e.target.value)} type="password" placeholder="Current Password" required/>
          <input value={newPass} onChange={(e) => setNewPass(e.target.value)} type="password" placeholder="New Password" required minLength={8}/>
          <button type="submit">Submit</button>
        </form>
        <p>{message}</p>
        </>
      )}
    </section>
  )
}