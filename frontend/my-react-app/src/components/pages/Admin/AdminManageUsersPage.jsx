// AdminManageUsersPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchData, renderListItemsWithAction, updateUserData, UpdateForm} from "../Functions/apiUtils";

export default function AdminManageUsersPage() {

  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({});

  const fields = [
    { name: 'email', label: 'Email', required: true },
    { name: 'role_id', label: 'Role ID', type: 'number' },
    
  ];  

  useEffect(() => {
    fetchData("http://localhost:5000/get_users", setUsers, "users");
  }, []);

  const renderUserItem = (user, handleDeleteUser, handleUpdateUser) => (
    <div key={user.id}>
      <p>(User email: {user.email}) (Role ID: {user.role_id})</p>
      <button onClick={() => handleDeleteUser(user.id)}>Delete User</button>
      <button onClick={() => handleUpdateUser(user)}>Modify User</button>
    </div>
  );
  

  const handleDeleteUser = async (userId) => {
    try {
      const response = await fetch(`http://localhost:5000/delete_user/${userId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update the state or re-fetch the user list after successful deletion
        fetchData("http://localhost:5000/get_users", setUsers, "users");
      } else {
        console.error('Error deleting user:', response.statusText);
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  const handleUpdateUser = (user) => {
    setSelectedUser(user);
    setFormData({
      email: user.email,
      role_id: user.role_id,
    });
  };


  const handleFormSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior

    try {
      if (!selectedUser) {
        console.error('No user selected for update.');
        return;
      }

      const userId = selectedUser.id;
      const isUpdated = await updateUserData(userId, formData);

      if (isUpdated) {
        fetchData("http://localhost:5000/get_users", setUsers, "users");
        setSelectedUser(null);
        setFormData({}); // Clear form data after update
      } else {
        console.error('Error updating user.');
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };
  
  

  return (
    <div>
      <div className="container h-100">
        <div className="row h-100">
          <div className="col-12">
            <h1>Welcome to Users Manage</h1>
            <p>
              <Link to="/login" className="btn btn-success">Login</Link> | <Link to="/register" className="btn btn-success">register</Link>
            </p>
            <p>
              <Link to="/admin_users" className="btn btn-success">Manage Users</Link>
              <Link to="/admin_prof" className="btn btn-success">Manage professions </Link>
              <Link to="/admin_test" className="btn btn-success">Manage tests </Link>
            </p>

          {/* Display Users */}
          <h2>Users List</h2>
          {renderListItemsWithAction(users, renderUserItem, handleDeleteUser, handleUpdateUser)}

            {/* Modify User Form */}
            {selectedUser && (
              <div>
                <h2>Modify User: {selectedUser.email}</h2>
                <UpdateForm formData={formData} fields={fields} onChange={setFormData} onSubmit={handleFormSubmit} />
              </div>
            )}

            {/* Add New User Form (example, modify as needed) */}
            <h2>Add New User</h2>
            <form method="post" action="http://localhost:5000/add_user">
              <label>Email:</label>
              <input type="text" name="email" required />
              <label>Password:</label>
              <input type="password" name="password" required />
              <label>Role ID:</label>
              <input type="number" name="role_id" />
              <button type="submit">Add User</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
