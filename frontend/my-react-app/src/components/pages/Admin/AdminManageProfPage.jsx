import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Table, Button, Form, Input } from 'antd';

const AdminManageProfPage = () => {
  const [professions, setProfessions] = useState([]);
  const [selectedProfession, setSelectedProfession] = useState(null);
  const [formData, setFormData] = useState({});
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchProfessions();
  }, []);

  const fetchProfessions = async () => {
    try {
      const response = await fetch("http://localhost:5000/get_prof");
      if (response.ok) {
        const data = await response.json();
        setProfessions(data.professions);
      } else {
        console.error('Failed to fetch professions:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching professions:', error);
    }
  };

  const handleDeleteProf = async (profId) => {
    try {
      const response = await fetch(`http://localhost:5000/delete_prof/${profId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        fetchProfessions();
      } else {
        console.error('Error deleting profession:', response.statusText);
      }
    } catch (error) {
      console.error('Error deleting profession:', error);
    }
  };

  const handleEditProf = (prof) => {
    setSelectedProfession(prof);
    setIsEditing(true);
    setFormData({
      profession_name: prof.profession_name,
      profession_description: prof.profession_description,
    });
  };

  const handleAddEditProfSubmit = async (values) => {
    try {
      let url = "http://localhost:5000/add_prof";
      let method = "POST";
      if (isEditing) {
        url = `http://localhost:5000/update_prof/${selectedProfession.id}`;
        method = "PUT";
      }

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        fetchProfessions();
        setSelectedProfession(null);
        setIsEditing(false);
        setFormData({});
      } else {
        console.error('Error adding/editing profession:', response.statusText);
      }
    } catch (error) {
      console.error('Error adding/editing profession:', error);
    }
  };

  const columns = [
    { title: 'Profession Name', dataIndex: 'profession_name', key: 'profession_name' },
    { title: 'Description', dataIndex: 'profession_description', key: 'profession_description' },
    {
      title: 'Action',
      key: 'action',
      render: (text, record) => (
        <span>
          <Button onClick={() => handleEditProf(record)}>Edit</Button>
          <Button onClick={() => handleDeleteProf(record.id)}>Delete</Button>
        </span>
      ),
    },
  ];

  return (
    <div>
      <h1>Welcome to Users and Professions Manage</h1>
      <p>
        <Link to="/login" className="btn btn-success">Login</Link> | <Link to="/register" className="btn btn-success">Register</Link>
      </p>
      <p>
        <Link to="/admin_users" className="btn btn-success">Manage Users</Link>
        <Link to="/admin_prof" className="btn btn-success">Manage professions </Link>
        <Link to="/admin_test" className="btn btn-success">Manage tests </Link>
      </p>

      <h2>Professions List</h2>
      <Table dataSource={professions} columns={columns} />

      <h2>{isEditing ? 'Edit Profession' : 'Add New Profession'}</h2>
      <Form
        initialValues={formData}
        onFinish={handleAddEditProfSubmit}
        onValuesChange={(changedValues, allValues) => setFormData(allValues)}
      >
        <Form.Item
          label="Profession Name"
          name="profession_name"
          rules={[{ required: true, message: 'Please input the profession name!' }]}
        >
          <Input />
        </Form.Item>
        {isEditing && (
          <Form.Item
            label="Description"
            name="profession_description"
            
            rules={[{ required: true, message: 'Please input the profession description!' }]}
          >
            <Input />
          </Form.Item>
        )}
        <Form.Item>
          <Button type="primary" htmlType="submit">{isEditing ? 'Update' : 'Add'}</Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default AdminManageProfPage;
