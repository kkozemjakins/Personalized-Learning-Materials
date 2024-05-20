// UserCoursePage.jsx
import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getSessionCookie } from "../Functions/authUtils";
import { Card, Space, Spin, Alert, Button } from 'antd';

export default function UserCoursePage() {
    const userId = getSessionCookie("user_id"); // Get user ID from session cookie
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        async function fetchUserCourses() {
            try {
                const response = await fetch(`http://localhost:5000/get_user_course/${userId}`);

                if (!response.ok) {
                    throw new Error(`Error: ${response.status} ${response.statusText}`);
                }
                const data = await response.json();
                setCourses(data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching user courses:", error);
                setError(error.message);
                setLoading(false);
            }
        }

        fetchUserCourses();
    }, [userId]);

    if (loading) {
        return <Spin tip="Loading..." />;
    }

    if (error) {
        return <Alert message="Error" description={error} type="error" showIcon />;
    }

    return (
        <div>
            <h1>User Course Page</h1>
            <Link to="/user_main" className="btn btn-primary">
                Back to Main Page
            </Link>

            <p></p>
            <Space direction="vertical" size={16}>
                {courses.map((course, index) => (
                    <Card
                        key={index}
                        title={course.profession.profession_name || "Unknown Profession"}
                        style={{ width: 300 }}
                        extra={
                            <Button type="primary" onClick={() => navigate(`/course/${course.id}`)}>
                                Go To Course
                            </Button>
                        }
                    >
                        <p>Topics:</p>
                        <ul>
                            {course.topics.map((topic, topicIndex) => (
                                <li key={topicIndex}>{topic.TopicTitle}</li>
                            ))}
                        </ul>
                    </Card>
                ))}
            </Space>
        </div>
    );
}
