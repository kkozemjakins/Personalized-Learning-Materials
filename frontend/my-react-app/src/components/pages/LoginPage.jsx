//LoginPage.jsx

import React, { useState } from "react";
import { Button, Checkbox, Form, Input } from 'antd';
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { setSessionCookie } from "./Functions/authUtils";

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const logInUserFirebase = () => {
      axios.post('http://localhost:5000/login', {
          email: email,
          password: password
      })
      .then(function (response) {
          console.log(response);
          const { user_id, is_admin } = response.data;
    
          // Store user ID in session
          setSessionCookie("user_id", user_id);
          console.log(user_id);
    
          if (is_admin) {
              navigate("/admin_main");
          } else {
              navigate("/user_main");
          }
      })
      .catch(function (error) {
          console.log(error, 'error');
          alert("Login failed");
      });
    }
  

    const logInUserGoogle = () => {
        window.location.href = "http://localhost:5000/google/signup"; // Redirect to Google signup
    }

    return (
        <Form
            layout="vertical"
            name="basic"
            initialValues={{
                remember: true,
            }}
            wrapperCol={{
                span: 8,
            }}
        >
            <Form.Item
                label="Email"
                name="email"
                rules={[
                    {
                        type: 'email',
                        required: true,
                        message: 'Please input your email!',
                    },
                ]}
            >
                <Input value={email} onChange={(e) => setEmail(e.target.value)} />
            </Form.Item>

            <Form.Item
                label="Password"
                name="password"
                rules={[
                    {
                        required: true,
                        message: 'Please input your password!',
                    },
                ]}
            >
                <Input.Password value={password} onChange={(e) => setPassword(e.target.value)} />
            </Form.Item>

            <Form.Item
                name="remember"
                valuePropName="checked"
            >
                <Checkbox>Remember me</Checkbox>
            </Form.Item>

            <Form.Item>
                <Button type="primary" onClick={logInUserFirebase}>
                    Login
                </Button>
                <Button type="danger" onClick={logInUserGoogle} style={{marginLeft: '10px', backgroundColor: '#ECECEC', borderColor: '#ECECEC'}}>
                    Sign In with Google
                </Button>
                <p style={{marginTop: '10px'}}>Don't have an account? <a href="/register" className="link-danger">Register</a></p>
            </Form.Item>
        </Form>
    );
}
