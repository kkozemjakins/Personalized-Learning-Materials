// UserMainPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useUserRoleAccess } from "../Functions/apiUtils";

export default function UserMainPage() {
    const checkUserRoleAccess = useUserRoleAccess(0);
    const [professions, setProfessions] = useState([]);
    const [tests, setTests] = useState([]);
    const [userEmail, setUserEmail] = useState("");
    const [userId, setUserId] = useState("");
    const [userRole, setUserRole] = useState("");

    useEffect(() => {
        // Fetch user information from session storage or state
        const userEmailFromStorage = sessionStorage.getItem("user_email");
        const userIdFromStorage = sessionStorage.getItem("user_id");
        const userRoleFromStorage = sessionStorage.getItem("user_role");

        setUserEmail(userEmailFromStorage);
        setUserId(userIdFromStorage);
        setUserRole(userRoleFromStorage);

        if (!checkUserRoleAccess()) {
            return;
        }

        fetch("http://localhost:5000/get_prof")
            .then((response) => response.json())
            .then((data) => {
                if (data.professions) {
                    setProfessions(data.professions);
                }
            })
            .catch((error) => console.error("Error fetching professions:", error));

        // Fetch all tests
        fetch("http://localhost:5000/get_test")
            .then((response) => response.json())
            .then((data) => {
                if (data.profTest) {
                    setTests(data.profTest);
                }
            })
            .catch((error) => console.error("Error fetching tests:", error));
    }, []); // Empty dependency array to run the effect only once on component mount

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                    <p><Link to="/logout" className="btn btn-success">Logout</Link> 
                    | <Link to="/user_test_results" className="btn btn-success">Test results</Link> 
                    | <Link to="/user_courses" className="btn btn-success">Your courses</Link> </p>
                  
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
