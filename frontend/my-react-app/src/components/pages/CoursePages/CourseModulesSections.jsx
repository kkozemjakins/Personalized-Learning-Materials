import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Button } from 'antd';
import axios from 'axios';

const { Panel } = Card;

const CourseModulesSections = () => {
  const { courseId } = useParams();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/get_course_modules/${courseId}`);
        setModules(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching modules:', error);
        setLoading(false);
      }
    };

    fetchModules();
  }, [courseId]);

  if (loading) {
    return <p>Loading...</p>;
  }

  if (!modules || modules.length === 0) {
    return <p>No modules found.</p>;
  }

  return (
    <div>
      {modules.map((module, index) => (
        <Card key={index} title={`${index + 1}. ${module.title}`}>
          {module.sections.map((section, sectionIndex) => (
            <Link
              key={sectionIndex}
              to={`/course_topics/${courseId}/${module.id}/${section.id}`}
              style={{ display: 'block', marginBottom: '10px' }}
            >
              <Button type="primary">{`${sectionIndex + 1}. ${section.title}`}</Button>
            </Link>
          ))}
        </Card>
      ))}
    </div>
  );
};

export default CourseModulesSections;
