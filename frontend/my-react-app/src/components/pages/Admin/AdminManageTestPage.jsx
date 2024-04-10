// AdminManageTestPage.jsx
import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchData, renderListItemsWithAction, updateTestData, UpdateForm } from "../Functions/apiUtils";

export default function AdminManageTestPage() {

  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [formData, setFormData] = useState({});
  const [questions, setQuestions] = useState([]);

  const fields = [
    { name: 'question', label: 'Question', required: true },
    { name: 'level_of_question', label: 'Level of Question' },
    { name: 'correct_answer', label: 'Correct Answer', required: true },
    { name: 'answer_variant1', label: 'Answer Variant 1' },
    { name: 'answer_variant2', label: 'Answer Variant 2' },
    { name: 'answer_variant3', label: 'Answer Variant 3' },
    { name: 'answer_variant4', label: 'Answer Variant 4' },
  ];

  useEffect(() => {
    fetchData("http://localhost:5000/get_test_questions", setQuestions, "profTestCreatedQuestions");
    fetchData("http://localhost:5000/get_test", setTests, "profTest");
  }, []);

  const renderQuestionItem = (question, handleDeleteQuestion, handleUpdateQuestion) => (
    <div key={question.id}>
      <p>Question: {question.question}</p> 
      <p>Question Level: {question.level_of_question}</p> 
      <p>Correct Answer: {question.correct_answer}</p>
      <p>Answer Variant 1: {question.answer_variant1}</p>
      <p>Answer Variant 2: {question.answer_variant2}</p>
      <p>Answer Variant 3: {question.answer_variant3}</p>
      <p>Answer Variant 4: {question.answer_variant4}</p>
      <button onClick={() => handleDeleteQuestion(question.id)}>Delete Question</button>
      <button onClick={() => handleUpdateQuestion(question)}>Modify Question</button>
    </div>
  );


const handleDeleteQuestion = async (questionId) => {
    try {
      const response = await fetch(`http://localhost:5000/delete_test_questions/${questionId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (response.ok) {
        fetchData("http://localhost:5000/get_test_questions", setQuestions, "profTestGeneratedQuestions");
      } else {
        console.error('Error deleting question:', response.statusText);
      }
    } catch (error) {
      console.error('Error deleting question:', error);
    }
  };
  

  const handleUpdateQuestion = (question) => {
    setSelectedTest(question);
    setFormData({
      question: question.question,
      level_of_question: question.level_of_question,
      correct_answer: question.correct_answer,
      answer_variant1: question.answer_variant1,
      answer_variant2: question.answer_variant2,
      answer_variant3: question.answer_variant3,
    });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();

    try {
      if (!selectedTest) {
        console.error('No question selected for update.');
        return;
      }

      const questionId = selectedTest.id;
      const isUpdated = await updateTestData(questionId, formData);

      if (isUpdated) {
        fetchData("http://localhost:5000/get_test_questions", setQuestions, "profTestGeneratedQuestions");
        setSelectedTest(null);
        setFormData({});
      } else {
        console.error('Error updating question.');
      }
    } catch (error) {
      console.error('Error updating question:', error);
    }
  };

  return (
    <div>
      <div className="container h-100">
        <div className="row h-100">
          <div className="col-12">
            <h1>Welcome to Test Questions Management</h1>
            <p>
              <Link to="/admin_users" className="btn btn-success">Manage Users</Link>
              <Link to="/admin_prof" className="btn btn-success">Manage professions </Link>
              <Link to="/admin_test" className="btn btn-success">Manage tests </Link>
            </p>

            {/* Display Test Questions */}
            <h2>Test Questions List</h2>
            {renderListItemsWithAction(questions, renderQuestionItem, handleDeleteQuestion, handleUpdateQuestion)}

            {/* Modify Question Form */}
            {selectedTest && (
              <div>
                <h2>Modify Question: {selectedTest.question}</h2>
                <UpdateForm formData={formData} fields={fields} onChange={setFormData} onSubmit={handleFormSubmit} />
              </div>
            )}

            {/* Add New Question Form */}
            <h2>Add New Question</h2>
            <form method="post" action="http://localhost:5000/add_test_questions">
              {fields.map((field) => (
                <div key={field.name}>
                  <label>{field.label}:</label>
                  <input
                    type={field.type || 'text'}
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                    required={field.required || false}
                  />
                </div>
              ))}
              <button type="submit">Add Question</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
