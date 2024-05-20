// apiUtils.js
import { useNavigate } from "react-router-dom";
export const fetchData = async (url, setData, dataKey) => {
  try {
    const response = await fetch(url);
    const data = await response.json();

    if (Array.isArray(data[dataKey])) {
      setData(data[dataKey]);
    }
  } catch (error) {
    console.error(`Error fetching data from ${url}:`, error);
  }
};

export const renderListItems = (items, renderFunction) => (
  <ul>
    {Array.isArray(items) ? items.map((item) => (
      <li key={item.id}>{renderFunction(item)}</li>
    )) : null}
  </ul>
);

export const renderListItemsWithAction = (items, renderFunction, handleDelete, handleModify) => (
  <ul>
    {Array.isArray(items) ? items.map((item) => (
      <li key={item.id}>
        {renderFunction(item, handleDelete, handleModify)}
      </li>
    )) : null}
  </ul>
);

export const updateUserData = async (userId, updatedUserData, setData, dataKey) => {
  try {
    const response = await fetch(`http://localhost:5000/update_user/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedUserData),
    });

    if (response.ok) {
      fetchData(`http://localhost:5000/get_${dataKey}`, setData, dataKey);
      return true; // Successful update
    } else {
      console.error(`Error updating ${dataKey}:`, response.statusText);
      return false;
    }
  } catch (error) {
    console.error(`Error updating ${dataKey}:`, error);
    return false;
  }
};

export const updateTestData = async (questionId, updatedQuestionData, setData, dataKey) => {
  try {
    const response = await fetch(`http://localhost:5000/update_test_questions/${questionId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedQuestionData),
    });

    if (response.ok) {
      fetchData(`http://localhost:5000/get_${dataKey}`, setData, dataKey);
      return true; // Successful update
    } else {
      console.error(`Error updating ${dataKey}:`, response.statusText);
      return false;
    }
  } catch (error) {
    console.error(`Error updating ${dataKey}:`, error);
    return false;
  }
};

export const UpdateForm = ({ formData, fields, onChange, onSubmit }) => (
  <form onSubmit={onSubmit}>
    {fields.map((field) => (
      <div key={field.name}>
        <label>{field.label}:</label>
        <input
          type={field.type || 'text'}
          name={field.name}
          value={formData[field.name] || ''}
          onChange={(e) => onChange({ ...formData, [field.name]: e.target.value })}
          required={field.required || false}
        />
      </div>
    ))}
    <button type="submit">Update</button>
  </form>
);

export default UpdateForm;


export const useUserRoleAccess = (requiredUserRole) => {
  const navigate = useNavigate();

  const checkUserRoleAccess = () => {
      const isLoggedIn = sessionStorage.getItem("user_id");
      const userRole = sessionStorage.getItem("user_role");

      if (!isLoggedIn) {
          navigate("/login");
          return false;
      }

      if (parseInt(userRole) !== requiredUserRole) {
          navigate("/login"); // Redirect to login if user role does not match
          return false;
      }

      return true;
  };

  return checkUserRoleAccess;
};