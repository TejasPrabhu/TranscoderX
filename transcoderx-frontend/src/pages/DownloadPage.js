import React, { useState } from 'react';
import axios from 'axios';
import { Button, Form } from 'react-bootstrap';
import { token } from './LoginPage';

function DownloadPage() {
	const [fid, setFid] = useState('');

	const handleDownload = async (event) => {
		event.preventDefault();

		try {
			const gatewayUrl = process.env.GATEWAY_URL;
			const downloadUrl = `http://trancoderx.site/api/download?fid=${fid}`;
			// const url = `${gatewayUrl}/download?fid=${fid}`;
			const response = await axios.get(downloadUrl, {
				responseType: 'blob', // important
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});

			// Create a new blob object with mime-type explicitly set, otherwise only Chrome works
			const url = window.URL.createObjectURL(
				new Blob([response.data], { type: 'audio/mpeg' })
			);
			const link = document.createElement('a');
			link.href = url;
			link.setAttribute('download', `${fid}.mp3`); // or any other extension
			document.body.appendChild(link);
			link.click();
		} catch (err) {
			console.error('Failed to download', err);
		}
	};

	return (
		<div>
			<h2>Download File</h2>
			<Form onSubmit={handleDownload}>
				<Form.Group>
					<Form.Label>Enter File ID:</Form.Label>
					<Form.Control
						type='text'
						value={fid}
						onChange={(e) => setFid(e.target.value)}
						required
					/>
				</Form.Group>
				<Button
					variant='primary'
					type='submit'
				>
					Download
				</Button>
			</Form>
		</div>
	);
}

export default DownloadPage;
