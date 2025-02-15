import { Timestamp } from "@angular/fire/firestore"

export interface GeneratedImage {
    image: string
    prompt: string
    timestamp: Timestamp
}