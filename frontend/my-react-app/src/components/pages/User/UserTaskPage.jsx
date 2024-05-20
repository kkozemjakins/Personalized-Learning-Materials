// UserTaskPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useUserRoleAccess,fetchData } from "../Functions/apiUtils";


export default function UserTaskPage() {
    const [userJsons, setUserJsons] = useState([]);

    const [userID, setUserId] = useState("");

    useEffect(() => {
        fetchUserJsons();
        const userIdFromStorage = sessionStorage.getItem("user_id");
        setUserId(userIdFromStorage);
    }, []);

    const fetchUserJsons = () => {
        console.log(userID)
        // Define your getUserId function to get the user ID
        fetchData("http://localhost:5000/get_user_json/2ebf1f5a0aa742b88bf2536b1aca7d9c", setUserJsons, "user_jsons");

    };

    return (
        <div>
            <h1>User Task Page</h1>
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
                        <h4>Tasks:</h4>
                        {/* Check if course_outline exists before mapping over its topics */}
                        {json.course_outline?.topics && json.course_outline.topics.map((topic, topicIndex) => (
                            <div key={topicIndex}>
                                <h5>{topic.title}</h5>
                                <ul>
                                    {topic.practical_tasks.task.map((task, taskIndex) => (
                                        <li key={taskIndex}>{task}</li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>
            ))}

        </div>
    );
}
