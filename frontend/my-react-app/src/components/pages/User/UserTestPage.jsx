import React, { useState, useEffect } from "react";
import { useParams, useLocation } from "react-router";
import { useUserRoleAccess } from "../Functions/apiUtils";
import { getSessionCookie } from "../Functions/authUtils";
import { Form, Button, Radio, List, Typography, Alert, Spin } from 'antd';

const { Title, Paragraph } = Typography;

export default function UserTestPage() {
  const { id } = useParams();
  const [userId, setUserId] = useState("");
  const [profession, setProfession] = useState(null);
  const [testQuestions, setTestQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [mark, setMark] = useState(null);
  const [correctAnswersCount, setCorrectAnswersCount] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();
  const userData = location.state || {};
  const { email, id: userIdFromLocation, role } = userData;
  const checkUserRoleAccess = useUserRoleAccess(0);

  useEffect(() => {
    const userIdFromStorage = getSessionCookie("user_id");
    if (userIdFromStorage) {
      setUserId(userIdFromStorage);
    }
  
    if (!profession || testQuestions.length === 0) {
      Promise.all([
        fetch(`http://localhost:5000/get_prof/${id}`).then((response) =>
          response.json()
        ),
        fetch(
          `http://localhost:5000/get_test_questions_by_profession/${id}`
        ).then((response) => response.json()),
      ])
        .then(([professionData, testQuestionsData]) => {
          setProfession(professionData.profession);
          setTestQuestions(testQuestionsData);
          setLoading(false);
        })
        .catch((error) => {
          setError("Error fetching data. Please try again later.");
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [id]);

  const handleAnswerChange = (questionIndex, selectedAnswer) => {
    setAnswers({
      ...answers,
      [questionIndex]: selectedAnswer,
    });
  };

  const handleSubmit = () => {
    let correctAnswers = 0;
  
    testQuestions.forEach((question, index) => {
      if (answers[index] === question.correct_answer) {
        correctAnswers++;
      }
    });
  
    const calculatedMark = Math.round((correctAnswers / testQuestions.length) * 100);
  
    // Submit test results to ProfTestMarks
    const testData = {
      profession_id: id,
      user_id: userId,
      mark: calculatedMark,
      correct_answers_amount: correctAnswers,
      incorrect_answers_amount: testQuestions.length - correctAnswers,
    };
  
    fetch("http://localhost:5000/submit_test_results", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(testData),
    })
      .then((response) => response.json())
      .then((testResultsResponse) => {
        console.log("Test results submitted:", testResultsResponse);
        setMark(calculatedMark);
        setCorrectAnswersCount(correctAnswers);
  
        // Once test results are submitted, save user answers to ProfTestUserResults
        const userAnswersData = testQuestions.map((question, index) => ({
          profession_id: id,
          user_id: userId,
          user_marks_id: testResultsResponse.user_marks_id,
          questions_id: question.question_id,
          user_answer: answers[index] || "", // If user didn't answer, save an empty string
        }));
  
        fetch("http://localhost:5000/save_user_answers", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userAnswersData),
        })
          .then((response) => response.json())
          .then((userAnswersResponse) => {
            console.log("User answers saved:", userAnswersResponse);
            setSubmitted(true);
          })
          .catch((error) => {
            console.error("Error saving user answers:", error);
          });
      })
      .catch((error) => {
        console.error("Error submitting test results:", error);
      });
  };

  if (loading) {
    return <Spin tip="Loading..." />;
  }

  if (error) {
    return <Alert message={error} type="error" />;
  }

  return (
    <div style={{ padding: '20px' }}>
      <Title level={2}>User Test Page</Title>
      <p>User ID: {userId}</p>
      {profession && (
        <div>
          <Title level={3}>Profession Details</Title>
          <Paragraph>
            <strong>Profession ID:</strong> {profession.id}
          </Paragraph>
          <Paragraph>
            <strong>Profession Name:</strong> {profession.profession_name}
          </Paragraph>
          <Paragraph>
            <strong>Description:</strong> {profession.profession_description}
          </Paragraph>
        </div>
      )}

      <Title level={3}>Test Questions</Title>
      <Form onFinish={handleSubmit}>
        <List
          itemLayout="vertical"
          dataSource={testQuestions}
          renderItem={(question, index) => (
            <List.Item key={index}>
              <Title level={4}>
                {index + 1}. {question.question} (Level: {question.question_level})
              </Title>
              <Form.Item name={`question${index}`}>
                <Radio.Group
                  onChange={(e) => handleAnswerChange(index, e.target.value)}
                  value={answers[index]}
                  disabled={submitted}
                >
                  {Object.values(question).slice(0, 4).map((option, optionIndex) => (
                    <Radio key={optionIndex} value={option}>
                      <span
                        style={{
                          color:
                            submitted && option === question.correct_answer
                              ? "green"
                              : submitted && answers[index] !== option
                              ? "red"
                              : "inherit",
                        }}
                      >
                        {option}
                      </span>
                      {submitted && answers[index] !== option && option === question.correct_answer && (
                        <span style={{ color: "green" }}> ✓</span>
                      )}
                      {submitted && answers[index] === option && option !== question.correct_answer && (
                        <span style={{ color: "red" }}> x</span>
                      )}
                    </Radio>
                  ))}
                </Radio.Group>
              </Form.Item>
            </List.Item>
          )}
        />
        <Form.Item>
          <Button type="primary" htmlType="submit" disabled={submitted}>
            Submit
          </Button>
        </Form.Item>
      </Form>

      {mark !== null && (
        <div>
          <Title level={3}>Test Result</Title>
          <Paragraph>
            <strong>Mark:</strong> {mark}%
          </Paragraph>
          <Paragraph>
            <strong>Correct Answers:</strong> {correctAnswersCount}/{testQuestions.length}
          </Paragraph>
        </div>
      )}
    </div>
  );
}
