// UserMainPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useUserRoleAccess,fetchData, } from "../Functions/apiUtils";
import { getUserInfo } from "../Functions/authUtils";

export default function UserMainPage() {

    const [professions, setProfessions] = useState([]);
    const { userEmail, userId, userRole } = getUserInfo();
    const checkUserRoleAccess = useUserRoleAccess(0);

    useEffect(() => {
        if (!checkUserRoleAccess()) {
            return;
        }

        fetchData("http://localhost:5000/get_prof", setProfessions, "Professions");
    }, []); 

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                        <p>
                            <Link to="/logout" className="btn btn-success">Logout</Link> 
                            | <Link to="/user_test_results" className="btn btn-success">Test results</Link> 
                            | <Link to="/user_courses" className="btn btn-success">Your courses</Link>
                        </p>
                      
                        <h1>Welcome to this User</h1>
                        <p>User Email: {userEmail}</p>
                        <p>User ID: {userId}</p>
                        <p>User Role: {userRole}</p>
                        {/* Display Professions */}
                        <h2>Professions List</h2>
                        <ul>
                            {professions.map((prof) => (
                                <li key={prof.id}>
                                    (Profession ID: {prof.id}) (Profession Name: {prof.profession_name}) (Description: {prof.profession_description})
                                    <Link to={`/profession_test/${prof.id}`} className="btn btn-info">
                                        Details
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
