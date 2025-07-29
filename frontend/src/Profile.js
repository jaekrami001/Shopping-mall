import React from 'react';

const Profile = ({ user }) => {
  return (
    <div className="profile">
      <h2>Profile</h2>
      <p>
        <strong>Username:</strong> {user.username}
      </p>
    </div>
  );
};

export default Profile;
