import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Button } from 'antd';
import axios from 'axios';

const CourseModulesSections = () => {
  const { courseId } = useParams();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/get_course_modules/${courseId}`);
        const sortedModules = response.data.sort((a, b) => a.order - b.order);
        setModules(sortedModules); // Sort modules by ModuleOrder before setting state
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

  const isPreviousModuleCompleted = (moduleIndex) => {
    if (moduleIndex === 0) return true; // The first module is available from the beginning
    return modules[moduleIndex - 1].completion; // Check if the previous module is completed
  };

  const isPreviousSectionCompleted = (moduleIndex, sectionIndex) => {
    if (sectionIndex === 0) {
      return isPreviousModuleCompleted(moduleIndex); // Check if the previous module is completed
    }
    return modules[moduleIndex].sections[sectionIndex - 1].completion; // Check if the previous section is completed
  };

  return (
    <div>
      {modules.map((module, moduleIndex) => (
        <Card
          key={moduleIndex}
          title={`${moduleIndex + 1}. ${module.title}`}
          style={{ marginBottom: '20px' }}
        >
          {module.sections.map((section, sectionIndex) => (
            <Link
              key={sectionIndex}
              to={`/course_topics/${courseId}/${module.id}/${section.id}`}
              style={{ display: 'block', marginBottom: '10px' }}
            >
              <Button
                type="primary"
                disabled={!isPreviousSectionCompleted(moduleIndex, sectionIndex)}
              >
                {`${sectionIndex + 1}. ${section.title}`}
              </Button>
            </Link>
          ))}
        </Card>
      ))}
    </div>
  );
};

export default CourseModulesSections;
