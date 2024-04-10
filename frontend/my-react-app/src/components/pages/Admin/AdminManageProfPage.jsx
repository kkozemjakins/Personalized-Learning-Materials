// AdminManageProfPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchData, renderListItems, updateUserData, UpdateForm } from "../Functions/apiUtils";

const AdminManageProfPage = () => {
  const [professions, setProfessions] = useState([]);
  const [selectedProfession, setSelectedProfession] = useState(null);
  const [formData, setFormData] = useState({});

  const fields = [
    { name: 'profession_name', label: 'Profession Name', required: true },
    { name: 'profession_description', label: 'Description' },
  ];

  useEffect(() => {
    fetchData("http://localhost:5000/get_prof", setProfessions, "professions");
  }, []);

  const renderProfItem = (prof) => (
    <div key={prof.id}>
      <p>(Profession Name: {prof.profession_name}) (Description: {prof.profession_description})</p>
      <button onClick={() => handleDeleteProf(prof.id)}>Delete Profession</button>
      <button onClick={() => handleUpdateProf(prof)}>Modify Profession</button>
    </div>
  );

  const handleDeleteProf = async (profId) => {
    try {
      const response = await fetch(`http://localhost:5000/delete_prof/${profId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        fetchData("http://localhost:5000/get_prof", setProfessions, "professions");
      } else {
        console.error('Error deleting profession:', response.statusText);
      }
    } catch (error) {
      console.error('Error deleting profession:', error);
    }
  };

  const handleUpdateProf = (prof) => {
    setSelectedProfession(prof);
    setFormData({
      profession_name: prof.profession_name,
      profession_description: prof.profession_description,
    });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();

    try {
      if (!selectedProfession) {
        console.error('No profession selected for update.');
        return;
      }

      const profId = selectedProfession.id;
      const isUpdated = await updateUserData(profId, formData, "professions");

      if (isUpdated) {
        fetchData("http://localhost:5000/get_prof", setProfessions, "professions");
        setSelectedProfession(null);
        setFormData({});
      } else {
        console.error('Error updating profession.');
      }
    } catch (error) {
      console.error('Error updating profession:', error);
    }
  };

  return (
    <div>
      <div className="container h-100">
        <div className="row h-100">
          <div className="col-12">
            <h1>Welcome to Users and Professions Manage</h1>
            <p>
              <Link to="/login" className="btn btn-success">Login</Link> | <Link to="/register" className="btn btn-success">register</Link>
            </p>
            <p>
              <Link to="/admin_users" className="btn btn-success">Manage Users</Link>
              <Link to="/admin_prof" className="btn btn-success">Manage professions </Link>
              <Link to="/admin_test" className="btn btn-success">Manage tests </Link>
            </p>

            {/* Display Professions */}
            <h2>Professions List</h2>
            {renderListItems(professions, renderProfItem)}

            {/* Modify Profession Form */}
            {selectedProfession && (
              <div>
                <h2>Modify Profession: {selectedProfession.profession_name}</h2>
                <UpdateForm formData={formData} fields={fields} onChange={setFormData} onSubmit={handleFormSubmit} />
              </div>
            )}

            {/* Add New Profession Form */}
            <h2>Add New Profession</h2>
            <form method="post" action="http://localhost:5000/add_prof">
              <label>Profession Name:</label>
              <input type="text" name="profession_name" required />
              <label>Description:</label>
              <input type="text" name="profession_description" />
              <button type="submit">Add Profession</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminManageProfPage;
