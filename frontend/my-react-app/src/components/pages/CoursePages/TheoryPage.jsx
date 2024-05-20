import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Space, Spin, Alert, Button } from 'antd';

export default function TheoryPage() {
    const { id } = useParams();
    const [theoryData, setTheoryData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchTheoryData() {
            try {
                const response = await fetch(`http://localhost:5000/get_theory/${id}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status} ${response.statusText}`);
                }
                const data = await response.json();
                setTheoryData(data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching theory data:", error);
                setError(error.message);
                setLoading(false);
            }
        }

        fetchTheoryData();
    }, [id]);

    if (loading) {
        return <Spin tip="Loading..." />;
    }

    if (error) {
        return <Alert message="Error" description={error} type="error" showIcon />;
    }

    return (
        <div>
            <h1>Theory Page</h1>

            {theoryData && (
                <Space direction="vertical">
                    <Card title={theoryData.title}>
                        <p>{theoryData.description}</p>
                        <p>Links:</p>
                        <ul>
                            {theoryData.links.map((link, index) => (
                                <li key={index}>
                                    <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
                                </li>
                            ))}
                        </ul>
                    </Card>
                    <Space>
                        {theoryData.task_ids && theoryData.task_ids.map((taskId, index) => (
                            <Button key={index} type="primary" href={`/task/${taskId}`}>
                                <Link to={`/task/${taskId}`}>Task {index + 1}</Link>
                            </Button>
                        ))}
                    </Space>
                </Space>
            )}
        </div>
    );
}
