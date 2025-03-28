import React, { useState } from 'react';
import './SignUp.css'; // Assuming a separate CSS file

const SignUp = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError("Passwords do not match!");
            return;
        }

        // Reset error before proceeding
        setError('');
        
        const userData = { email, password };

        try {
            const response = await fetch('http://localhost:8000/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();
            console.log(data);

            if (response.ok) {
                alert("Sign-up successful!");
            } else {
                alert("Sign-up failed.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };

    return (
        <>
        <div className="login-logo">
        <img src="/KSU Logo.png" alt="KSU Logo" style={{ width: '100px', height: 'auto' }} />
          <h1>The Nest Exchange</h1>
          </div>
        <div className="sign-up-container">
            <h2>Sign up</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder= "Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <button type="submit">Sign up</button>
            </form>
        </div>\
        </>
    );
};

export default SignUp;