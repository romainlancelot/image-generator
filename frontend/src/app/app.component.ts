import { Component, inject, signal, WritableSignal } from '@angular/core'
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms'
import { AppService } from './app.service'
import { Response } from './models/response'

@Component({
	selector: 'app-root',
	imports: [ReactiveFormsModule],
	templateUrl: './app.component.html'
})
export class AppComponent {
	loading: WritableSignal<boolean> = signal(false)
	imageUrl: WritableSignal<string> = signal('')
	form: FormGroup = new FormGroup({
		prompt: new FormControl('')
	})
	appService: AppService = inject(AppService)

	async onSubmit() {
		this.loading.set(true)
		const response: Response = await this.appService.generateImage(this.form.value.prompt)
		this.loading.set(false)
		this.imageUrl.set(response.filename)
	}
}
