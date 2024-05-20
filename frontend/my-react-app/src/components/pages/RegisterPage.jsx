import React, { useState } from 'react';
import { Button, Checkbox, Form, Input } from 'antd';
import axios from 'axios';
import { useNavigate } from "react-router-dom";

const RegisterPage = () => {
    const [form] = Form.useForm();
    const navigate = useNavigate();

    const registerUser = (values) => {
        axios.post('http://localhost:5000/signup', values)
        .then(function (response) {
            console.log(response);
            navigate("/");
        })
        .catch(function (error) {
            console.log(error, 'error');
            if (error.response && error.response.status === 401) {
                alert("Invalid credentials");
            } else if (error.response) {
                alert(`An error occurred. Status: ${error.response.status}`);
            } else {
                alert("An error occurred.");
            }
        });
    };

    const onFinish = (values) => {
        registerUser(values);
    };

    const googleSignUp = () => {
        window.location.href = "http://localhost:5000/google/signup";
    };

    const facebookSignUp = () => {
        window.location.href = "http://localhost:5000/facebook/signup";
    };
  
    return (
        <Form
            form={form}
            layout="vertical"
            name="basic"
            initialValues={{
                remember: true,
            }}
            onFinish={onFinish}
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
                <Input />
            </Form.Item>

            <Form.Item
                label="Username"
                name="username"
                rules={[
                    {
                        required: true,
                        message: 'Please input your username!',
                    },
                    {
                        pattern: /^[a-zA-Z0-9_]+$/,
                        message: 'Username can only contain letters, numbers, and underscores!',
                    },
                ]}
            >
                <Input />
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
                <Input.Password />
            </Form.Item>

            <Form.Item
                name="remember"
                valuePropName="checked">
                <Checkbox>Remember me</Checkbox>
            </Form.Item>

            <Form.Item>
                <Button type="primary" htmlType="submit">
                    Sign Up
                </Button>
                <Button type="danger" onClick={googleSignUp} style={{marginLeft: '10px', backgroundColor: '#ECECEC', borderColor: '#ECECEC'}}>
                    Sign Up with Google
                </Button>
                <Button type="primary" onClick={facebookSignUp} style={{marginLeft: '10px', backgroundColor: '#3b5998', borderColor: '#3b5998'}}>
                    Sign Up with Facebook
                </Button>
            </Form.Item>
            <Form.Item>
                <p >Login to your account <a href="/login" className="link-danger">Login</a></p>
            </Form.Item>
        </Form>
        
    );
}

export default RegisterPage;
  