//UserMainPage.jsx


import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Collapse, Button } from 'antd';
import { fetchData } from "../Functions/apiUtils";
import { getSessionCookie } from "../Functions/authUtils";

const { Panel } = Collapse;

export default function UserMainPage() {
    const [professions, setProfessions] = useState([]);
    const navigate = useNavigate();
    const userId = getSessionCookie("user_id"); // Get user ID from session cookie

    useEffect(() => {

        
        fetchData("http://localhost:5000/get_prof", setProfessions, "professions");
    }, []);

    const logout = () => {

    };

    const renderProfItem = (prof) => (
        <Panel header={prof.profession_name} key={prof.id}>
          <p>{prof.profession_description}</p>
          <Link to={`/profession_test/${prof.id}`}>
            <Button type="primary">View Details</Button>
          </Link>
        </Panel>
    );

    // Check if user is logged in

    return (
        <div>
            <div className="container h-100">
                <div className="row h-100">
                    <div className="col-12">
                        <p>
                            <button className="btn btn-success" onClick={logout}>Logout</button>
                            | <Link to="/user_test_results" className="btn btn-success">Test results</Link> 
                            | <Link to="/user_courses" className="btn btn-success">Your courses</Link>
                        </p>
                      
                        <h1>Welcome User {userId}!</h1> {/* Display user ID */}
                        {/* Display Professions */}
                        <h2>Professions List</h2>
                        <Collapse>
                            {professions.map((prof) => renderProfItem(prof))}
                        </Collapse>
                    </div>
                </div>
            </div>
        </div>
    );
}
