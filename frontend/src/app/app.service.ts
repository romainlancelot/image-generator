import { Injectable } from '@angular/core';
import { Response } from './models/response';

@Injectable({ providedIn: 'root' })
export class AppService {
	private readonly generateUrl: string | undefined = process.env['GENERATE_URL']
	private readonly bucketName: string | undefined = process.env['BUCKET_NAME']
	private readonly bucketImagesPath: string | undefined = process.env['BUCKET_IMAGES_PATH']

	constructor() { }

	async generateImage(prompt: string): Promise<Response> {
		if (this.generateUrl === undefined || this.bucketName === undefined || this.bucketImagesPath === undefined) {
			throw new Error('Environment variables not correctly set')
		}
		const response = await fetch(this.generateUrl, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ prompt }),
		});
		if (!response.ok) {
			throw new Error('Network response was not ok')
		}
		const data: Response = await response.json()
		data.filename = `https://storage.cloud.google.com/${this.bucketName}/${this.bucketImagesPath}/${data.filename}`
		return data
	}
}
