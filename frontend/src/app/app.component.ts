import { Component, inject, signal, WritableSignal } from '@angular/core'
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms'
import { AppService } from './app.service'
import { Response } from './models/response'
import { collection, collectionData, CollectionReference, Firestore, orderBy, query } from '@angular/fire/firestore'
import { AsyncPipe, DatePipe } from '@angular/common'
import { Observable } from 'rxjs'
import { GeneratedImage } from './models/generated-image'

@Component({
	selector: 'app-root',
	imports: [ReactiveFormsModule, AsyncPipe, DatePipe],
	templateUrl: './app.component.html'
})
export class AppComponent {
	appService: AppService = inject(AppService)
	store: Firestore = inject(Firestore)
	generatedImages: Observable<GeneratedImage[]>

	loading: WritableSignal<boolean> = signal(false)
	generatedImageUrl: WritableSignal<string> = signal('')
	form: FormGroup = new FormGroup({
		prompt: new FormControl('')
	})

	constructor() {
		const generatedImagesCollection: CollectionReference = collection(this.store, 'generated-images')
		const imagesQuery = query(generatedImagesCollection, orderBy('timestamp', 'desc'))
		this.generatedImages = collectionData(imagesQuery) as Observable<GeneratedImage[]>
	}

	/**
	 * Handles the form submission event.
	 * 
	 * This method sets the loading state to true, sends a request to generate an image
	 * based on the provided prompt, and then updates the loading state and the generated
	 * image URL based on the response.
	 */
	async onSubmit() {
		this.loading.set(true)
		await this.appService.generateImage(this.form.value.prompt).then((response: Response) => {
			this.generatedImageUrl.set(response.filename)
			this.loading.set(false)
		}).catch(() => {
			this.loading.set(false)
		})
	}
}
