// UserTestResultsPage.jsx
import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useUserRoleAccess } from "../Functions/apiUtils";

// Arrow icons for indicating collapse/expand state
const arrowDown = "\u25BC";
const arrowUp = "\u25B2";

export default function UserTestResultsPage() {
    const checkUserRoleAccess = useUserRoleAccess(0);
    const [userEmail, setUserEmail] = useState("");
    const [userId, setUserId] = useState("");
    const [userRole, setUserRole] = useState("");
    const [userAnswers, setUserAnswers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [collapsedTests, setCollapsedTests] = useState({});
    
    // Define a ref to track previous userId
    const previousUserId = useRef(null);

    useEffect(() => {
        // Fetch user information from session storage or state
        const userEmailFromStorage = sessionStorage.getItem("user_email");
        const userIdFromStorage = sessionStorage.getItem("user_id");
        const userRoleFromStorage = sessionStorage.getItem("user_role");

        setUserEmail(userEmailFromStorage);
        setUserId(userIdFromStorage);
        setUserRole(userRoleFromStorage);

        if (!checkUserRoleAccess() || !userId) {
            setLoading(false);
            return;
        }

        // Fetch user answers from the backend API only if userId has changed
        if (userId !== previousUserId.current) {
            setLoading(true);
            fetch(`http://localhost:5000/user_answers/${userId}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Failed to fetch user answers");
                    }
                    return response.json();
                })
                .then((data) => {
                    setUserAnswers(data.userAnswers);
                    setLoading(false);
                })
                .catch((error) => {
                    setError(error);
                    setLoading(false);
                });
            previousUserId.current = userId; // Update previousUserId ref
        }
    }, [userId, checkUserRoleAccess]);

    useEffect(() => {
        // Set all tests to be collapsed by default
        const initialCollapsedState = {};
        userAnswers.forEach(mark_info => {
            initialCollapsedState[mark_info.prof_test_results_marks_id] = true;
        });
        setCollapsedTests(initialCollapsedState);
    }, [userAnswers]);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    // Group user answers by prof_test_id
    const groupedUserAnswers = {};
    userAnswers.forEach((mark_info) => {
        if (!groupedUserAnswers[mark_info.prof_test_results_marks_id]) {
            groupedUserAnswers[mark_info.prof_test_results_marks_id] = [];
        }
        groupedUserAnswers[mark_info.prof_test_results_marks_id].push(mark_info);
    });

    // Toggle collapse state for a test
    const toggleCollapse = (testId) => {
        setCollapsedTests((prevState) => ({
            ...prevState,
            [testId]: !prevState[testId],
        }));
    };

    // Function to delete all marks and answers
    const deleteAllMarksAndAnswers = () => {
        fetch(`http://localhost:5000/delete_all_test_results`, {
            method: "DELETE",
        })
        .then(response => response.json())
        .then(data => {
            // Handle success
            console.log(data.message);
            // Update userAnswers state to clear the data
            setUserAnswers([]);
        })
        .catch(error => {
            // Handle error
            console.error("Error deleting marks and answers:", error);
        });
    };

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                        <h1>Welcome to this User</h1>
                        <p>User Email: {userEmail}</p>
                        <p>User ID: {userId}</p>
                        <p>User Role: {userRole}</p>

                        <p>
                            <Link to="/logout" className="btn btn-success">Logout</Link> 
                            | <Link to="/user_main" className="btn btn-success">Main</Link> 
                        </p>

                        {/* Button to delete all marks and answers */}
                        <button className="btn btn-danger" onClick={deleteAllMarksAndAnswers}>
                            Delete All Marks and Answers
                        </button>

                        {/* Display user answers grouped by prof_test_id */}
                        {Object.entries(groupedUserAnswers).map(([testId, answers]) => (
                            <div key={testId}>
                                <h2 onClick={() => toggleCollapse(testId)}>
                                    {collapsedTests[testId] ? arrowDown : arrowUp}
                                    &nbsp;Test ID: {testId}
                                </h2>
                                {!collapsedTests[testId] && (
                                    <ul>
                                        {answers.map((answer, index) => (
                                            <li key={answer.id}>
                                                <ul>
                                                    <li>
                                                        id of result:{answer.prof_test_results_marks_id}
                                                    </li>
                                                    <li>
                                                        Question: <i>{answer.question_text} </i> Level: {answer.question_level}
                                                    </li>
                                                    <li>User Answer: {answer.user_answer}</li>
                                                    <li>
                                                        <span style={{ color: answer.correct_incorrect === 1 ? "green" : "red" }}>
                                                            Correct/Incorrect: {answer.correct_incorrect === 1 ? "Correct" : "Incorrect"}
                                                        </span>
                                                    </li>
                                                    {index === answers.length - 1 && (
                                                        <div>
                                                            <p>Comment on Result:</p> {answer.comment_on_result}
                                                        </div>
                                                    )}
                                                </ul>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
