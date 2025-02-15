import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core'
import { provideRouter } from '@angular/router'
import { routes } from './app.routes';
import { getApp, initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { getFirestore, provideFirestore } from '@angular/fire/firestore'

export const appConfig: ApplicationConfig = {
	providers: [
		provideZoneChangeDetection({ eventCoalescing: true }),
		provideRouter(routes),
		provideFirebaseApp(
			() => initializeApp({
				projectId: "gcp-project-image-generator",
				appId: "1:1006167454203:web:d1eff2ef29a663708b9b5e",
				storageBucket: "gcp-project-image-generator.firebasestorage.app",
				apiKey: "AIzaSyCeBldsAd4PZIu3wyJl0z0kw-kmzEty-hg",
				authDomain: "gcp-project-image-generator.firebaseapp.com",
				messagingSenderId: "1006167454203",
			})
		),
		provideFirestore(() => getFirestore(
			getApp(), "gcp-project-image-generator"
		))
	]
}
