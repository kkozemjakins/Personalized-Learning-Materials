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

    const renderDescription = (description) => {
        if (!description || typeof description !== 'object') return null;

        return Object.entries(description).map(([key, value]) => (
            <div key={key}>
                <Typography.Title level={4}>{key.replace(/_/g, " ")}</Typography.Title>
                {typeof value === 'object' && value !== null ? (
                    renderDescription(value)
                ) : (
                    <Typography.Paragraph>{value}</Typography.Paragraph>
                )}
            </div>
        ));
    };

    return (
        <Content style={{ padding: '24px' }}>
            <Card title={profession.profession_name}>
                <Row gutter={16}>
                    <Col span={8}>
                        <Image width={200} src="https://via.placeholder.com/200" alt="Course cover" />
                    </Col>
                    <Col span={16}>
                        <Text strong>{profession.profession_name}</Text>
                        <Text type="secondary"><br />{renderDescription(profession.profession_description)}</Text>
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
