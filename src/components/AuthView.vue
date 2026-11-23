<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const mode = ref<'register' | 'login'>('register')
const isSubmitting = ref<boolean>(false)

const formData = ref({
  name: '',
  email: '',
  password: ''
})

const handleSubmit = async (): Promise<void> => {
  isSubmitting.value = true
  try {
    const endpoint = mode.value === 'register' ? '/register' : '/login'
    const payload =
      mode.value === 'register'
        ? { name: formData.value.name, email: formData.value.email, password: formData.value.password }
        : { email: formData.value.email, password: formData.value.password }

    const { data } = await api.post(endpoint, payload)

    localStorage.setItem('user_token', data.token)
    localStorage.setItem('user_email', data.email)

    if (data.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/profile')
    }
  } catch (err: any) {
    alert(err.response?.data?.error || 'Ошибка авторизации. Проверьте данные.')
  } finally {
    isSubmitting.value = false
  }
}
</script>


<template>
  <div class="card auth-card">
    <div class="tabs">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: mode === 'register' }"
        @click="mode = 'register'"
      >
        Регистрация
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: mode === 'login' }"
        @click="mode = 'login'"
      >
        Авторизация
      </button>
    </div>

    <form class="auth-form" @submit.prevent="handleSubmit">
      <input
        v-if="mode === 'register'"
        v-model="formData.name"
        class="input-pill"
        placeholder="Имя"
        required
      />
      <input
        v-model="formData.email"
        class="input-pill"
        type="email"
        :placeholder="mode === 'register' ? 'Email' : 'Email'"
        required
      />
      <input
        v-model="formData.password"
        class="input-pill"
        type="password"
        placeholder="Пароль"
        required
      />

      <button type="submit" class="btn-primary submit-btn">
        {{ mode === 'register' ? 'Зарегистрироваться' : 'Войти' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border-radius: 999px;
  font-size: 16px;
  cursor: pointer;
  border: 1px solid #26481c;
  background-color: #ffffff;
  color: #26481c;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background-color: #26481c;
  color: #ffffff;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.input-pill {
  width: 100%;
  padding: 12px 20px;
  border-radius: 999px;
  border: 1px solid #e6d7c8;
  font-size: 15px;
  outline: none;
  color: #26481c;
}

.input-pill:focus {
  border-color: #26481c;
}

.submit-btn {
  margin-top: 10px;
}

@media (max-width: 600px) {
  .tabs {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
