// CoursePage.jsx
import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Space, Spin, Alert, Button } from 'antd';

export default function CoursePage() {
    const { id } = useParams();
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchCourse() {
            try {
                const response = await fetch(`http://localhost:5000/get_course/${id}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status} ${response.statusText}`);
                }
                const data = await response.json();
                setCourse(data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching course:", error);
                setError(error.message);
                setLoading(false);
            }
        }

        fetchCourse();
    }, [id]);

    if (loading) {
        return <Spin tip="Loading..." />;
    }

    if (error) {
        return <Alert message="Error" description={error} type="error" showIcon />;
    }

    return (
        <div>
            <h1>Course Page</h1>
            <Link to="/user_main" className="btn btn-primary">
                Back to Main Page
            </Link>

            {course && (
                <Space direction="vertical">
                    <Card title={course.profession.profession_name || "Unknown Profession"}>
                        <p>Profession Description:</p>
                        <p>{course.profession.profession_description}</p>
                        <p>Topics:</p>
                        <ul>
                            {course.topics.map((topic, topicIndex) => (
                                <li key={topicIndex}>
                                    <strong>{topic.TopicTitle} </strong>

                                        <Link to={`/theory/${topic.id}`}>
                                            <Button type="primary">Go to Theory</Button>
                                        </Link>

                                </li>
                            ))}
                        </ul>
                    </Card>
                </Space>
            )}

        </div>
    );
}
