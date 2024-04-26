import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchData, renderListItems } from "./Functions/apiUtils";
import { Collapse, Card, Button } from 'antd';

const { Panel } = Collapse;

export default function LandingPage() {
  const [professions, setProfessions] = useState([]);

  useEffect(() => {
    fetchData("http://localhost:5000/get_prof", setProfessions, "Professions");
  }, []);

  const renderProfItem = (prof) => (
    <Panel header={prof.profession_name} key={prof.id}>
      <p>{prof.profession_description}</p>
      <Link to={`/profession/${prof.id}`}>
        <Button type="primary">View Details</Button>
      </Link>
    </Panel>
  );

  return (
    <div>
      <div>
        <div className="container h-100">
          <div className="row h-100">
            <div className="col-12">
              <h1>Welcome!</h1>
              <p>
                <Link to="/login" className="btn btn-success">
                  Login
                </Link>{" "}
                |{" "}
                <Link to="/register" className="btn btn-success">
                  Register
                </Link>
              </p>

              {/* Display Professions */}
              <h2>Professions List</h2>
              <Collapse>
                {professions.map((prof) => renderProfItem(prof))}
              </Collapse>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
