import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchData } from "./Functions/apiUtils";
import { Collapse, Button, List } from 'antd';

const { Panel } = Collapse;

export default function LandingPage() {
  const [professions, setProfessions] = useState([]);

  useEffect(() => {
    fetchData("http://localhost:5000/get_prof", setProfessions, "professions");
  }, []);

  const renderDescription = (description) => {
    return (
      <List
        itemLayout="vertical"
        dataSource={Object.entries(description)}
        renderItem={([key, value]) => (
          <List.Item>
            <List.Item.Meta
              title={<h4>{key.replace(/_/g, " ")}</h4>}
            />
            <p>{value}</p>
          </List.Item>
        )}
      />
    );
  };

  const renderSectionContent = (content) => {
    return (
      <List
        itemLayout="vertical"
        dataSource={Object.entries(content)}
        renderItem={([key, value]) => {
          if (typeof value === 'object' && value !== null) {
            return (
              <List.Item>
                <Collapse>
                  <Panel header={key.replace(/_/g, " ")} key={key}>
                    {renderSectionContent(value)}
                  </Panel>
                </Collapse>
              </List.Item>
            );
          } else {
            return (
              <List.Item>
                <List.Item.Meta
                  title={<h4>{key.replace(/_/g, " ")}</h4>}
                />
                <p>{value}</p>
              </List.Item>
            );
          }
        }}
      />
    );
  };

  const renderProfItem = (prof) => (
    <Panel header={prof.profession_name} key={prof.id}>
      <Collapse>
        {prof.profession_description && (
          <Panel header="Introduction" key="intro">
            {renderDescription(prof.profession_description)}
          </Panel>
        )}
      </Collapse>
      <Collapse>
        {prof.sections.map((section, index) => (
          <Panel header={section.subsection_name} key={index}>
            {renderSectionContent(section.subsection_content)}
          </Panel>
        ))}
      </Collapse>
      <Link to={`/profession_test/${prof.id}`}>
        <Button type="primary">View Details</Button>
      </Link>
    </Panel>
  );

  return (
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
