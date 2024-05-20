// TaskPage.jsx

import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Card, Space, Spin, Alert, Input, Button } from 'antd';
import { getSessionCookie } from "../Functions/authUtils";

export default function TaskPage() {
    const { id } = useParams();
    const [taskData, setTaskData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [answer, setAnswer] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [submissionError, setSubmissionError] = useState(null);
    const userId = getSessionCookie("user_id"); // Get user ID from session cookie

    useEffect(() => {
        async function fetchTaskData() {
            try {
                const response = await fetch(`http://localhost:5000/get_task/${id}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status} ${response.statusText}`);
                }
                const data = await response.json();
                setTaskData(data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching task data:", error);
                setError(error.message);
                setLoading(false);
            }
        }

        fetchTaskData();
    }, [id]);

    const handleAnswerChange = (e) => {
        setAnswer(e.target.value);
    };

    const handleSubmitAnswer = async () => {
        try {
            setSubmitting(true);
            const response = await fetch(`http://localhost:5000/submit_answer/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userId, answer }), // Include user ID in the request body
            });
            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            // Reset answer input
            setAnswer('');
            setSubmitting(false);
            // Optionally, you can handle successful submission
        } catch (error) {
            console.error("Error submitting answer:", error);
            setSubmissionError(error.message);
            setSubmitting(false);
        }
    };
    

    if (loading) {
        return <Spin tip="Loading..." />;
    }

    if (error) {
        return <Alert message="Error" description={error} type="error" showIcon />;
    }

    return (
        <div>
            <h1>Task Page</h1>

            {taskData && (
                <Space direction="vertical">
                    <Card title={taskData.title}>
                        <p>{taskData.description}</p>
                        {/* Add more task details here */}
                    </Card>
                    <Space>
                        <Input.TextArea 
                            value={answer} 
                            onChange={handleAnswerChange} 
                            placeholder="Your answer" 
                            autoSize={{ minRows: 3, maxRows: 6 }} // Adjust the number of rows
                        />
                        <Button type="primary" onClick={handleSubmitAnswer} loading={submitting}>
                            Submit Answer
                        </Button>
                    </Space>
                    {submissionError && (
                        <Alert message="Error" description={submissionError} type="error" showIcon />
                    )}
                </Space>
            )}
        </div>
    );
}
