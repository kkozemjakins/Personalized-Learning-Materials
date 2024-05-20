import React, { useState, useEffect } from 'react';
import { Collapse, Divider, Table } from 'antd';
import { fetchData } from '../Functions/apiUtils';
import { getSessionCookie } from '../Functions/authUtils';

const { Panel } = Collapse;

export default function UserTestResultPage() {
  const [testResults, setTestResults] = useState([]);
  const userId = getSessionCookie('user_id');

  useEffect(() => {
    fetchData(`http://localhost:5000/user_answers/${userId}`, setTestResults, 'userAnswers');
  }, [userId]);

  const renderCollapseItems = () => {
    const collapseItems = {};
    testResults.forEach((result) => {
      const { prof_test_results_marks_id, question_text, user_answer, correct_answer, correct_incorrect, profession_name, mark } = result;
      if (!collapseItems[prof_test_results_marks_id]) {
        collapseItems[prof_test_results_marks_id] = [];
      }
      collapseItems[prof_test_results_marks_id].push({
        question_text,
        user_answer,
        correct_answer,
        correct_incorrect,
        profession_name,
        mark
      });
    });

    return Object.keys(collapseItems).map((key) => (
      <Panel header={`Test Result - ${collapseItems[key][0].profession_name} | Score: ${collapseItems[key][0].mark}/100`} key={key}>
        <Table
          dataSource={collapseItems[key]}
          columns={[
            { title: 'Question', dataIndex: 'question_text', key: 'question_text' },
            { title: 'User Answer', dataIndex: 'user_answer', key: 'user_answer' },
            { title: 'Correct Answer', dataIndex: 'correct_answer', key: 'correct_answer' },
            { title: 'Correct/Incorrect', dataIndex: 'correct_incorrect', key: 'correct_incorrect' },
          ]}
          pagination={false}
        />
      </Panel>
    ));
  };

  return (
    <div>
      <h1>User Test Results</h1>
      
      <Collapse>
      
        {renderCollapseItems()}
          
      </Collapse>
      
    </div>
  );
}
