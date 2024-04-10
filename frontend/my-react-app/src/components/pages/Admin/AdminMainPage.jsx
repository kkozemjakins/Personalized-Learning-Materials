import React, { } from "react";
 
import {Link} from 'react-router-dom';
 
export default function AdminMainPage(){
 
  return (
    <div>
        <div className="container h-100">
            <div className="row h-100">
                <div className="col-12">
                    <h1>Welcome to this Admin</h1>
                    <p><Link to="/login" className="btn btn-success">Login</Link> | <Link to="/register" className="btn btn-success">register</Link> </p>
                    <p><Link to="/admin_users" className="btn btn-success">Manage Users</Link> | <Link to="/admin_prof" className="btn btn-success">Manage professions</Link></p>
                </div>
            </div>
        </div>
    </div>
  );
}