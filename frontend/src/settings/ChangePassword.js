import React, {useState} from "react";

export default function ChangePassword() {
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  return (
    <section className="password-section">
      <button className="toggle-btn" onClick={() => setShowPasswordForm(!showPasswordForm)}>
        {showPasswordForm ? 'Close Password Form' : 'Change Password'}
      </button>
      {showPasswordForm && (
        <form className="password-form">
          <input type="password" placeholder="Current Password" required/>
          <input type="password" placeholder="New Password" required/>
          <input type="password" placeholder="Confirm New Password" required/>
          <button type="submit">Submit</button>
        </form>
      )}
    </section>
  )
}