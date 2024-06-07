import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Button, Typography, List, Spin } from 'antd';
import { getSessionCookie } from "../Functions/authUtils";
import axios from 'axios';

const { Title, Paragraph } = Typography;

const TopicTheoryTask = ({ theory, tasks }) => (
  <div>
    <Title level={2}>Theory:</Title>
    <List
      bordered
      dataSource={theory}
      renderItem={item => (
        <List.Item>
          <Paragraph>{item.TheoryContent}</Paragraph>
        </List.Item>
      )}
    />
    <Title level={2}>Tasks:</Title>
    <List
      bordered
      dataSource={tasks}
      renderItem={item => (
        <List.Item>
          <Paragraph>{item.PracticalTask}</Paragraph>
        </List.Item>
      )}
    />
  </div>
);

const ModuleSectionTopics = () => {
  const { courseId, moduleId, sectionId, topicId } = useParams();
  const [topics, setTopics] = useState(null);
  const userId = getSessionCookie("user_id");
  const [loading, setLoading] = useState(true);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/get_topic_details/${topicId}`);
        setTopics(response.data.topics_theory_tasks);
        setLoading(false);

        const isTopicCompleted = await axios.get(`http://localhost:5000/check_topic_completion/${topicId}/${userId}`);
        setIsCompleted(isTopicCompleted.data.completed);
      } catch (error) {
        console.error('Error fetching topics:', error);
        setLoading(false);
      }
    };

    fetchTopics();
  }, [courseId, moduleId, sectionId, topicId, userId]);

  const handleFinishClick = async () => {
    try {
      const response = await axios.post(`http://localhost:5000/topic_completed/${topicId}/${userId}`);
      console.log('Topic completion saved:', response.data);
      setIsCompleted(true);
    } catch (error) {
      console.error('Error saving topic completion:', error);
    }
  };

  if (loading) {
    return <Spin />;
  }

  if (!topics) {
    return <Paragraph>Topic not found.</Paragraph>;
  }

  return (
    <div>
      <Title level={1}>{topics.TopicTitle}</Title>
      <Card>
        <TopicTheoryTask theory={topics.theory} tasks={topics.tasks} />
        <Button type={isCompleted ? 'default' : 'primary'} disabled={isCompleted} onClick={handleFinishClick}>
          {isCompleted ? 'Completed' : 'Finish'}
        </Button>
      </Card>
    </div>
  );
};

export default ModuleSectionTopics;
