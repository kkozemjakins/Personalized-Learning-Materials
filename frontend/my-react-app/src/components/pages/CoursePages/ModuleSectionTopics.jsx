// ModuleSectionTopics.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Collapse } from 'antd';
import axios from 'axios';

const { Panel } = Collapse;

const ModuleSectionTopics = () => {
  const { courseId, moduleId, sectionId } = useParams();
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/get_section_topics/${courseId}/${moduleId}/${sectionId}`);
        setTopics(response.data.topics);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching topics:', error);
        setLoading(false);
      }
    };

    fetchTopics();
  }, [courseId, moduleId, sectionId]);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Topics</h1>
      <Collapse accordion>
        {topics.map((topic, index) => (
          <Panel header={topic.TopicTitle} key={index}>
            <Card>
              <h2>Theory:</h2>
              {topic.theory.map((item, idx) => (
                <p key={idx}>{item.TheoryContent}</p>
              ))}
              <h2>Tasks:</h2>
              {topic.tasks.map((task, idx) => (
                <p key={idx}>{task.PracticalTask}</p>
              ))}
            </Card>
          </Panel>
        ))}
      </Collapse>
    </div>
  );
};

export default ModuleSectionTopics;
