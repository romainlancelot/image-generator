import { Component } from '@angular/core'
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms'

@Component({
	selector: 'app-root',
	imports: [ReactiveFormsModule],
	templateUrl: './app.component.html'
})
export class AppComponent {
	form: FormGroup = new FormGroup({
		prompt: new FormControl('')
	})

	onSubmit() {
	}
}
