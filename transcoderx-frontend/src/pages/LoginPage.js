import React, { useState } from 'react';
import axios from 'axios';
import { Button, Form, Container, Alert } from 'react-bootstrap';

let token = null; // <-- JWT is stored here

function LoginPage() {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState('');

	const handleSubmit = async (event) => {
		event.preventDefault();
		setLoading(true);
		setError(''); // reset the error message

		try {
			const gatewayUrl = process.env.GATEWAY_URL;
			const url = 'http://trancoderx.site/api/login';
			// const url = `${gatewayUrl}/login`
			const authString = `${username}:${password}`;
			const response = await axios.post(
				url,
				{},
				{
					headers: {
						Authorization: `Basic ${btoa(authString)}`,
					},
				}
			);

			// If the request is successful, store the JWT token into the memory
			token = response.data;
			console.log(token);
			console.log('Login successful');
			// TODO: Redirect to the next page (e.g., a dashboard)
		} catch (err) {
			// If there's an error, set the error state so it can be displayed
			setError('Failed to login. Please check your credentials.');
			console.error(err);
		} finally {
			setLoading(false);
		}
	};

	return (
		<Container>
			<h2>Login</h2>
			<Form onSubmit={handleSubmit}>
				<Form.Group controlId='formBasicEmail'>
					<Form.Label>Username</Form.Label>
					<Form.Control
						type='text'
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						required
					/>
				</Form.Group>
				<Form.Group controlId='formBasicPassword'>
					<Form.Label>Password</Form.Label>
					<Form.Control
						type='password'
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
				</Form.Group>
				<Button
					variant='primary'
					type='submit'
					disabled={loading}
				>
					{loading ? 'Loading...' : 'Login'}
				</Button>
				{error && <Alert variant='danger'>{error}</Alert>}
			</Form>
		</Container>
	);
}

export { LoginPage, token };
