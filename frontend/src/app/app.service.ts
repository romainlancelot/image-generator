import { Injectable } from "@angular/core"
import { Response } from "./models/response"
import { environment } from "../environments/environment"


@Injectable({ providedIn: "root" })
export class AppService {
	/**
	 * Generates an image based on the provided prompt by making a POST request to the generate URL.
	 * 
	 * @param {string} prompt - The prompt to generate the image from.
	 * @throws {Error} - Throws an error if the network response is not ok.
	 * @returns {Promise<Response>} - A promise that resolves to the response containing the generated image data.
	 */
	async generateImage(prompt: string): Promise<Response> {
		const response = await fetch(environment.GENERATE_URL, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ prompt }),
		})
		if (!response.ok) {
			throw new Error("Failed to generate image.")
		}
		const data: Response = await response.json()
		return data
	}
}
