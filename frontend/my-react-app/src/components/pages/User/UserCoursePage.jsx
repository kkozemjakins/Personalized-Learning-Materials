//UserCoursePage.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import XmlViewer from 'react-xml-viewer'; // Change import to default

const Recommendations = ({ resultId }) => {
  const [recommendations, setRecommendations] = useState('');
  const [userId, setUserId] = useState('');

  useEffect(() => {
    const userIdFromStorage = sessionStorage.getItem("user_id");
    setUserId(userIdFromStorage);

    const fetchRecommendations = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/get_user_xml/${userIdFromStorage}`);
        setRecommendations(response.data.user_xmls);
      } catch (error) {
        console.error('Error fetching XML file:', error);
      }
    };
    fetchRecommendations();
  }, [resultId]);

  return (
    <div>
      <XmlViewer xml={recommendations} />
    </div>
  );
};

export default Recommendations;