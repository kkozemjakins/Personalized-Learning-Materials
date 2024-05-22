// CoursePage.jsx
/*import React, { useState, useEffect } from "react";
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
*/
// CoursePage.jsx
import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from "react-router-dom";
import { Layout, Card, Row, Col, Typography, Image, Collapse, Spin, Button } from 'antd';
import { getSessionCookie } from "../Functions/authUtils";
import { StarOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Content } = Layout;
const { Text } = Typography;
const { Panel } = Collapse;

const CoursePage = () => {
    const { courseId } = useParams();
    const userId = getSessionCookie("user_id"); // Get user ID from session cookie
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCourseData = async () => {
            try {
                const response = await axios.get(`http://localhost:5000/get_course/${courseId}`);
                setCourse(response.data);  
                setLoading(false);
            } catch (error) {
                console.error('Error fetching course data:', error);
                setLoading(false);
            }
        };

        fetchCourseData();
    }, [courseId]);

    if (loading) {
        return <Spin />;
    }

    if (!course) {
        return <Text>No course found.</Text>;
    }

    const { profession, modules } = course;

    return (
        <Content style={{ padding: '24px' }}>
            <Card title={profession.profession_name}>
                <Row gutter={16}>
                    <Col span={8}>
                        <Image width={200} src="https://via.placeholder.com/200" alt="Course cover" />
                    </Col>
                    <Col span={16}>
                        <Text strong>{profession.profession_name}</Text>
                        <Text type="secondary"><br />{profession.profession_description}</Text>
                        <br />
                        <Text type="secondary">
                            <StarOutlined /> - (- ratings)
                        </Text>
                        <Text type="secondary">- learners enrolled</Text>
                    </Col>
                </Row>
                <br />
                <Collapse accordion defaultActiveKey="0">
                    {modules.sort((a, b) => a.ModuleOrder - b.ModuleOrder).map((module, index) => (
                        <Panel header={module.ModuleTitle} key={index}>
                            {module.sections.map((section, sectionIndex) => (
                                <Collapse key={sectionIndex} accordion>
                                    <Panel header={section.SectionTitle} key={sectionIndex}>
                                        {section.topics.map((topic, topicIndex) => (
                                            <Card key={topicIndex} title={topic.TopicTitle}>
                                                {topic.theory.map((item, index) => (
                                                    <div key={index}>
                                                        <p>{item.TheoryContent}</p>
                                                        {/* Render other properties if needed */}
                                                    </div>
                                                ))}
                                            </Card>
                                        ))}
                                    </Panel>
                                </Collapse>
                            ))}
                        </Panel>
                    ))}
                </Collapse>
                <br />
                <Button type="primary" onClick={() => navigate(`/course_modules/${courseId}`)}>View Modules</Button>
            </Card>
        </Content>
    );
};

export default CoursePage;
