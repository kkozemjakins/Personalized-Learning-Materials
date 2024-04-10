import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchData, renderListItems } from "./Functions/apiUtils";
 
export default function LandingPage(){
  const [professions, setProfessions] = useState([]);

  useEffect(() => {
    fetchData("http://localhost:5000/get_prof", setProfessions, "professions");
  }, []);

  const renderProfItem = (prof) => (
    `(Profession Name: ${prof.profession_name}) (Description: ${prof.profession_description})`
  );

 
  return (
    <div>
        <div className="container h-100">
            <div className="row h-100">
                <div className="col-12">
                    <h1>Welcome to this React Application</h1>
                    <p><Link to="/login" className="btn btn-success">Login</Link> | <Link to="/register" className="btn btn-success">register</Link> </p>
                  
                    {/* Display Professions */}
                    <h2>Professions List</h2>
                    {renderListItems(professions, renderProfItem)}
                </div>
            </div>
        </div>
    </div>
  );
}