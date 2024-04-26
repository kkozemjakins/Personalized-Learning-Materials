// UserCoursePage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useUserRoleAccess } from "../Functions/apiUtils";
import { getUserInfo } from "../Functions/authUtils";

export default function UserCoursePage() {
    const [userJsons, setUserJsons] = useState([]);
    const { userEmail, userId, userRole } = getUserInfo();

    useEffect(() => {
        fetchUserJsons();
    }, []);

    const fetchUserJsons = () => {
        console.log(userId)
        // Define your getUserId function to get the user ID
        fetch(`http://localhost:5000/get_user_json/${userId}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.user_jsons) {
                    setUserJsons(data.user_jsons);
                }
            })
            .catch((error) => console.error("Error fetching user JSONs:", error));
    };

    return (
        <div>
            <h1>User Course Page</h1>
            <Link to="/user_main" className="btn btn-primary">
                Back to Main Page
            </Link>
            <hr />
            {userJsons.map((json, index) => (
                <div key={index} className="card my-3">
                    <div className="card-header">
                        <h3>Course Outline {index + 1}</h3>
                    </div>
                    <div className="card-body">
                        <p>
                            <strong>Comment on Results:</strong> {json.comment_on_results}
                        </p>
                        <Link to={`/user_tasks`} className="btn btn-info">
                                        Details
                        </Link>
                        {/* You can add more details from the JSON file here */}
                    </div>
                </div>
            ))}
        </div>
    );
}
