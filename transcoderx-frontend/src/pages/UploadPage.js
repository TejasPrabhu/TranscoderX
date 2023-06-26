import React, { useState } from 'react';
import axios from 'axios';
import { Button, Form } from 'react-bootstrap';
import { token } from './LoginPage';

function UploadPage() {
	const [file, setFile] = useState(null);

	const handleSubmit = async (event) => {
		event.preventDefault();

		let formData = new FormData();
		formData.append('file', file);

		try {
			const gatewayUrl = process.env.GATEWAY_URL;
			const url = 'http://trancoderx.site/api/upload';
			// const url = `${gatewayUrl}/upload`
			const response = await axios.post(url, formData, {
				headers: {
					'Content-Type': 'multipart/form-data',
					Authorization: `Bearer ${token}`,
				},
			});

			console.log(response);
			console.log('Upload successful');
		} catch (err) {
			console.error('Failed to upload', err);
		}
	};

	return (
		<div>
			<h2>Upload File</h2>
			<Form onSubmit={handleSubmit}>
				<Form.Group>
					<Form.Label>Select file:</Form.Label>
					<Form.Control
						type='file'
						onChange={(e) => setFile(e.target.files[0])}
						required
					/>
				</Form.Group>
				<Button
					variant='primary'
					type='submit'
				>
					Upload
				</Button>
			</Form>
		</div>
	);
}

export default UploadPage;
