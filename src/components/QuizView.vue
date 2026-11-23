<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import type { QuizAnswer } from '../types'

interface QuestionItem {
  id: number
  text: string
  options?: string[] 
}

const router = useRouter()

const isStarted = ref<boolean>(false)
const isLoadingQuestions = ref<boolean>(true)
const isSaving = ref<boolean>(false)
const loadError = ref<string>('')

const questions = ref<QuestionItem[]>([])
const currentStep = ref<number>(0)
const answerText = ref<string>('')
const answers = ref<QuizAnswer[]>([])

const currentQuestion = computed<QuestionItem | undefined>(() => {
  return questions.value[currentStep.value]
})


const isChoiceQuestion = computed<boolean>(() => {
  return Boolean(currentQuestion.value?.options && currentQuestion.value.options.length > 0)
})

const fetchQuestions = async (): Promise<void> => {
  isLoadingQuestions.value = true
  loadError.value = ''
  try {
    const { data } = await api.get<Array<QuestionItem | string>>('/questions')
    questions.value = data.map((item, idx) =>
      typeof item === 'string'
        ? { id: idx + 1, text: item }
        : {
            id: item.id ?? idx + 1,
            text: item.text,
            options: item.options || []
          }
    )
  } catch (err) {
    loadError.value = 'Не удалось загрузить вопросы с сервера. Попробуйте обновить страницу.'
  } finally {
    isLoadingQuestions.value = false
  }
}

onMounted(() => {
  fetchQuestions()
})

const startQuiz = (): void => {
  if (questions.value.length === 0) return
  currentStep.value = 0
  answers.value = []
  answerText.value = ''
  isStarted.value = true
}


const submitAnswer = async (finalAnswer: string): Promise<void> => {
  const q = currentQuestion.value
  if (!q) return

  answers.value.push({
    question: q.text,
    answer: finalAnswer.trim() || 'Ответ не указан'
  })
  answerText.value = ''

  if (currentStep.value < questions.value.length - 1) {
    currentStep.value++
  } else {
    isSaving.value = true
    try {
      const email = localStorage.getItem('user_email')
      await api.post('/quiz', {
        email,
        answers: answers.value
      })
      router.push('/pets')
    } catch (err) {
      alert('Не удалось сохранить результаты опроса на сервере')
    } finally {
      isSaving.value = false
    }
  }
}
</script>

<template>
  <div class="card quiz-card">
    
    <div v-if="!isStarted" class="quiz-intro">
      <h1 class="quiz-title">Пройди опрос</h1>
      <p class="quiz-subtitle">и наш чат-бот поможет подобрать питомца</p>

      <p v-if="loadError" class="error-text">{{ loadError }}</p>

      <button
        v-if="loadError"
        type="button"
        class="btn-primary"
        @click="fetchQuestions"
      >
        Повторить загрузку
      </button>

      <button
        v-else
        type="button"
        class="btn-primary"
        :disabled="isLoadingQuestions || questions.length === 0"
        @click="startQuiz"
      >
        {{ isLoadingQuestions ? 'Загрузка вопросов...' : 'К опросу' }}
      </button>
    </div>

    
    <div v-else-if="currentQuestion" class="quiz-step">
      <p class="step-counter">
        Вопрос {{ currentStep + 1 }} из {{ questions.length }}
      </p>
      <h2 class="question-text">{{ currentQuestion.text }}</h2>

      
      <div v-if="isChoiceQuestion" class="options-grid">
        <button
          v-for="option in currentQuestion.options"
          :key="option"
          type="button"
          class="option-pill-btn"
          :disabled="isSaving"
          @click="submitAnswer(option)"
        >
          {{ isSaving && currentStep === questions.length - 1 ? 'Сохраняем...' : option }}
        </button>
      </div>

      
      <template v-else>
        <textarea
          v-model="answerText"
          class="answer-box"
          rows="4"
          placeholder="Напишите ваш ответ..."
        ></textarea>
        <button
          type="button"
          class="btn-primary"
          :disabled="isSaving"
          @click="submitAnswer(answerText)"
        >
          {{
            isSaving
              ? 'Сохраняем ответы...'
              : currentStep < questions.length - 1
                ? 'Далее'
                : 'Подобрать питомца'
          }}
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.quiz-card {
  text-align: center;
}

.quiz-title {
  font-size: 28px;
  font-weight: 500;
  margin-bottom: 12px;
  color: #1f291c;
}

.quiz-subtitle {
  font-size: 16px;
  color: #4a5547;
  margin-bottom: 32px;
  line-height: 1.4;
}

.step-counter {
  font-size: 13px;
  color: #6b7268;
  margin-bottom: 8px;
}

.question-text {
  font-size: 21px;
  font-weight: 500;
  margin-bottom: 24px;
  color: #1f291c;
  line-height: 1.35;
}


.options-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-pill-btn {
  width: 100%;
  padding: 14px 24px;
  border-radius: 999px;
  border: 1.5px solid #26481c;
  background-color: #ffffff;
  color: #26481c;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-pill-btn:hover:not(:disabled) {
  background-color: #26481c;
  color: #ffffff;
}

.option-pill-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}


.answer-box {
  width: 100%;
  border: 1px solid #e6d7c8;
  border-radius: 16px;
  padding: 16px;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  margin-bottom: 24px;
  color: #1f291c;
}

.answer-box:focus {
  border-color: #26481c;
}

.error-text {
  color: #991b1b;
  font-size: 14px;
  margin-bottom: 16px;
}
</style>
