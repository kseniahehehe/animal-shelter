export interface Pet {
  id: number
  name: string
  age: string
  description: string
  guardians: string
  image: string
  ai_reason?: string
}

export interface QuizAnswer {
  question: string
  answer: string
}

export interface ProfileData {
  firstName: string
  lastName: string
  email: string
  birthDate: string
  lifestyle: string
  avatar: string
}
