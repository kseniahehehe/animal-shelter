<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import AdoptModal from './AdoptModal.vue'
import type { Pet, QuizAnswer } from '../types'

interface ExtendedProfileData {
  firstName: string
  lastName: string
  birthDate: string
  workField: string
  hobbies: string
  about: string
  avatar: string
}

interface ContactItem {
  id: number
  type: 'email' | 'phone'
  value: string
  subtitle: string
  status: 'verified' | 'pending'
  isPrimary?: boolean
  notice?: string
}

const router = useRouter()

const activeSection = ref<'personal' | 'contacts' | 'quiz' | 'favorites'>('personal')
const hasChanges = ref<boolean>(false)
const saveSuccess = ref<boolean>(false)

const profileData = ref<ExtendedProfileData>({
  firstName: '',
  lastName: '',
  birthDate: '',
  workField: '',
  hobbies: '',
  about: '',
  avatar: ''
})

const contacts = ref<ContactItem[]>([])
const addingType = ref<'email' | 'phone' | null>(null)
const newContactValue = ref<string>('')

const quizResults = ref<QuizAnswer[]>([])
const favorites = ref<Pet[]>([])
const selectedPetForAdopt = ref<Pet | null>(null)

onMounted(async () => {
  try {
    const email = localStorage.getItem('user_email')
    const { data } = await api.get('/profile', { params: { email } })

    profileData.value = data.profile
    contacts.value = data.contacts || []
    quizResults.value = data.quizResults || []
    favorites.value = data.favorites || []
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err)
  }
})

const avatarLetter = computed<string>(() => {
  return (profileData.value.firstName?.charAt(0) || 'П').toUpperCase()
})

const markChanged = (): void => {
  hasChanges.value = true
  saveSuccess.value = false
}

const handleAvatarUpload = (event: Event): void => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e: ProgressEvent<FileReader>) => {
    const result = e.target?.result
    if (typeof result === 'string') {
      profileData.value.avatar = result
      markChanged()
    }
  }
  reader.readAsDataURL(file)
}

const saveProfile = async (): Promise<void> => {
  try {
    const email = localStorage.getItem('user_email')
    await api.put('/profile', {
      email,
      profile: profileData.value,
      contacts: contacts.value
    })
    hasChanges.value = false
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 2500)
  } catch (err) {
    alert('Ошибка при сохранении профиля')
  }
}

const openAddContact = (type: 'email' | 'phone'): void => {
  addingType.value = type
  newContactValue.value = ''
}

const confirmAddContact = (): void => {
  const val = newContactValue.value.trim()
  if (!val || !addingType.value) return

  contacts.value.push({
    id: Date.now(),
    type: addingType.value,
    value: val,
    subtitle: addingType.value === 'email' ? 'Почта' : 'Телефон',
    status: 'pending'
  })
  addingType.value = null
  newContactValue.value = ''
  markChanged()
}

const removeContact = (id: number): void => {
  contacts.value = contacts.value.filter((c) => c.id !== id)
  markChanged()
}

const removeFromFavorites = async (id: number): Promise<void> => {
  try {
    const email = localStorage.getItem('user_email')
    await api.delete(`/favorites/${id}`, { params: { email } })
    favorites.value = favorites.value.filter((pet) => pet.id !== id)
  } catch (err) {
    console.error('Ошибка удаления из избранного:', err)
  }
}

const handleAdopt = (pet: Pet): void => {
  selectedPetForAdopt.value = pet
}

const handleSponsor = (pet: Pet): void => {
  alert(`Вы оформили заявку на опекунство над питомцем «${pet.name}»!`)
}

const scrollToSection = (section: 'personal' | 'contacts' | 'quiz' | 'favorites'): void => {
  activeSection.value = section
  const el = document.getElementById(`section-${section}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const goToQuiz = (): void => {
  router.push('/quiz')
}

const goToPets = (): void => {
  router.push('/pets')
}

const logout = (): void => {
  localStorage.removeItem('user_token')
  localStorage.removeItem('user_email')
  router.push('/auth')
}
</script>


<template>
  <div class="dashboard-page">
    <header class="top-header">
      <div class="header-left">
        <span class="brand-logo">🐾 Ника</span>
        <span class="header-divider">Личный кабинет</span>
      </div>

      <div class="header-right">
        
        
        <div class="header-avatar" @click="scrollToSection('personal')">
          <img v-if="profileData.avatar" :src="profileData.avatar" alt="Avatar" />
          <span v-else>{{ avatarLetter }}</span>
        </div>
        <button class="logout-link" @click="logout">Выйти</button>
      </div>
    </header>

    <div class="dashboard-grid">
      <aside class="left-sidebar">
        <nav class="side-nav">
          <div class="nav-item disabled">
            <span class="nav-icon">⊞</span>
            <span>Обзор</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">♡</span>
            <span>Пожертвования</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">🐾</span>
            <span>Мои подопечные</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">↻</span>
            <span>Регулярная помощь</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">⚑</span>
            <span>Мои сборы</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">💬</span>
            <span>Обращения</span>
          </div>

          <button class="nav-item active" @click="scrollToSection('personal')">
            <span class="nav-icon">👤</span>
            <span>Профиль и настройки</span>
          </button>
        </nav>
      </aside>

      <main class="main-content">
        <div class="page-heading">
          <h1>Профиль и настройки</h1>
          <p>
            Личные данные, способы входа и анкета опекуна. Данные сохраняются в вашем профиле.
          </p>
        </div>

        <section id="section-personal" class="white-panel">
          <h2 class="panel-title">Личные данные</h2>
          <p class="panel-subtitle">
            Расскажите немного о себе — это поможет приюту лучше узнать будущего опекуна.
          </p>

          <div class="avatar-upload-row">
            <div class="big-avatar">
              <img v-if="profileData.avatar" :src="profileData.avatar" alt="Фото" />
              <span v-else>{{ avatarLetter }}</span>
            </div>
            <div class="upload-controls">
              <label class="upload-btn">
                Загрузить фотографию
                <input type="file" accept="image/*" hidden @change="handleAvatarUpload" />
              </label>
              <span class="upload-hint">JPG, PNG или WEBP, до 10 МБ.</span>
            </div>
          </div>

          <form class="profile-form" @submit.prevent="saveProfile">
            <div class="form-grid">
              <div class="form-group">
                <label>Имя *</label>
                <input v-model="profileData.firstName" type="text" required @input="markChanged" />
              </div>

              <div class="form-group">
                <label>Фамилия *</label>
                <input
                  v-model="profileData.lastName"
                  type="text"
                  placeholder="Введите фамилию"
                  @input="markChanged"
                />
              </div>

              <div class="form-group">
                <label>Дата рождения</label>
                <input v-model="profileData.birthDate" type="date" @input="markChanged" />
              </div>

              <div class="form-group">
                <label>Сфера работы</label>
                <input
                  v-model="profileData.workField"
                  type="text"
                  placeholder="Например: IT, медицина, образование"
                  @input="markChanged"
                />
              </div>

              <div class="form-group full-width">
                <label>Хобби</label>
                <input
                  v-model="profileData.hobbies"
                  type="text"
                  placeholder="Например: бег, чтение, походы на природу"
                  @input="markChanged"
                />
              </div>

              <div class="form-group full-width">
                <label>О себе</label>
                <textarea
                  v-model="profileData.about"
                  rows="3"
                  placeholder="Расскажите о своем образе жизни и отношении к животным..."
                  @input="markChanged"
                ></textarea>
              </div>
            </div>

            <div class="panel-save-bar">
              <span class="changes-status">
                {{ saveSuccess ? '✓ Изменения сохранены' : hasChanges ? 'Есть несохранённые изменения' : 'Изменений нет' }}
              </span>
              <button
                type="submit"
                class="save-pill-btn"
                :class="{ ready: hasChanges }"
              >
                Сохранить
              </button>
            </div>
          </form>
        </section>

        <section id="section-contacts" class="white-panel">
          <h2 class="panel-title">Почта и телефоны</h2>
          <p class="panel-subtitle">
            Входить можно по любому подтверждённому контакту, письма и чеки приходят на основную почту.
            Если вы помогали фонду с другой почты или телефона, добавьте их: найденная история появится в кабинете.
          </p>

          <div class="contacts-list">
            <div v-for="item in contacts" :key="item.id" class="contact-block">
              <div class="contact-row">
                <div class="contact-left">
                  <div class="contact-icon-box">
                    <span v-if="item.type === 'email'">✉</span>
                    <span v-else>📱</span>
                  </div>
                  <div class="contact-details">
                    <div class="contact-value">{{ item.value }}</div>
                    <div class="contact-sub">{{ item.subtitle }}</div>
                  </div>
                </div>

                <div class="contact-right">
                  <span v-if="item.status === 'verified'" class="status-badge verified">
                    ✓ Подтверждён
                  </span>
                  <span v-else class="status-badge pending">
                    🕒 На проверке
                  </span>

                  <button
                    v-if="!item.isPrimary"
                    type="button"
                    class="delete-contact-btn"
                    @click="removeContact(item.id)"
                  >
                    Удалить
                  </button>
                </div>
              </div>

              <div v-if="item.notice" class="contact-notice-box">
                <span class="notice-icon">🕒</span>
                <p>{{ item.notice }}</p>
              </div>
            </div>
          </div>

          <div v-if="addingType" class="add-contact-form">
            <input
              v-model="newContactValue"
              :type="addingType === 'email' ? 'email' : 'tel'"
              :placeholder="addingType === 'email' ? 'Введите новую почту' : '+7 999 000-00-00'"
            />
            <div class="add-contact-actions">
              <button type="button" class="btn-green-sm" @click="confirmAddContact">Добавить</button>
              <button type="button" class="outline-pill-btn" @click="addingType = null">Отмена</button>
            </div>
          </div>

          <div class="contacts-footer-buttons">
            <button type="button" class="outline-pill-btn" @click="openAddContact('email')">
              + Добавить почту
            </button>
            <button type="button" class="outline-pill-btn" @click="openAddContact('phone')">
              + Добавить телефон
            </button>
          </div>
        </section>

        <section id="section-quiz" class="white-panel">
          <div class="panel-header-row">
            <div>
              <h2 class="panel-title">Результаты опроса</h2>
              <p class="panel-subtitle">Ваши ответы для подбора питомца</p>
            </div>
            <button class="btn-green-sm" @click="goToQuiz">
              {{ quizResults.length > 0 ? 'Перепройти опрос' : 'Пройти опрос' }}
            </button>
          </div>

          <div v-if="quizResults.length === 0" class="empty-box">
            <p>Вы еще не проходили опрос для подбора питомца.</p>
          </div>

          <div v-else class="quiz-results-list">
            <div v-for="(item, idx) in quizResults" :key="idx" class="quiz-result-item">
              <span class="q-title">{{ idx + 1 }}. {{ item.question }}</span>
              <span class="q-answer">{{ item.answer }}</span>
            </div>
          </div>
        </section>

        <section id="section-favorites" class="white-panel">
          <div class="panel-header-row">
            <div>
              <h2 class="panel-title">Избранные питомцы ({{ favorites.length }})</h2>
              <p class="panel-subtitle">Сохраненные анкеты животных</p>
            </div>
            <button class="outline-pill-btn" @click="goToPets">
              Выбрать питомцев →
            </button>
          </div>

          <div v-if="favorites.length === 0" class="empty-box">
            <p>В избранном пока нет ни одного питомца.</p>
          </div>

          <div v-else class="fav-cards-grid">
            <div v-for="pet in favorites" :key="pet.id" class="fav-pet-card">
              <img :src="pet.image" :alt="pet.name" class="fav-pet-img" />
              <div class="fav-pet-body">
                <h3>{{ pet.name }}, {{ pet.age }}</h3>
                <p>{{ pet.description }}</p>
                <span class="guardians-tag">{{ pet.guardians }}</span>

                
                <div class="pet-card-actions">
                  <button type="button" class="adopt-btn" @click="handleAdopt(pet)">
                    Познакомиться
                  </button>
                  <button type="button" class="sponsor-btn" @click="handleSponsor(pet)">
                    Стать опекуном
                  </button>
                </div>

                <button type="button" class="remove-pet-btn" @click="removeFromFavorites(pet.id)">
                  Убрать из избранного
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>

      <aside class="right-sidebar">
        <div class="right-links">
          <button
            class="right-link"
            :class="{ active: activeSection === 'personal' }"
            @click="scrollToSection('personal')"
          >
            Личные данные
          </button>
          <button
            class="right-link"
            :class="{ active: activeSection === 'contacts' }"
            @click="scrollToSection('contacts')"
          >
            Почта и телефон
          </button>
          <button
            class="right-link"
            :class="{ active: activeSection === 'quiz' }"
            @click="scrollToSection('quiz')"
          >
            Результаты опроса
          </button>
          <button
            class="right-link"
            :class="{ active: activeSection === 'favorites' }"
            @click="scrollToSection('favorites')"
          >
            Избранные питомцы
          </button>
        </div>
      </aside>
    </div>
    <AdoptModal :pet="selectedPetForAdopt" @close="selectedPetForAdopt = null" />
  </div>
</template>


<style scoped>
.dashboard-page {
  width: 100%;
  max-width: 100vw;
  min-height: 100vh;
  background-color: #f6f7f2;
  color: #1f241d;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  box-sizing: border-box;
}

.top-header {
  width: 100%;
  height: 64px;
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e8eae1;
  background-color: #f6f7f2;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-logo {
  font-weight: 700;
  font-size: 18px;
  color: #26481c;
}

.header-divider {
  font-size: 14px;
  color: #6c7267;
  padding-left: 14px;
  border-left: 1px solid #d5d8cd;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-pill-btn {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid #d5d8cd;
  background: #ffffff;
  font-size: 13px;
  color: #1f241d;
  cursor: pointer;
}

.header-pill-btn:hover {
  border-color: #26481c;
}

.header-badge {
  padding: 6px 12px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid #e5e7de;
  font-size: 13px;
  cursor: pointer;
}

.header-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background-color: #26481c;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
}

.header-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logout-link {
  background: none;
  border: none;
  color: #6c7267;
  font-size: 13px;
  cursor: pointer;
  margin-left: 4px;
}

.logout-link:hover {
  color: #991b1b;
}

.dashboard-grid {
  max-width: 1240px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
  display: grid;
  grid-template-columns: 230px minmax(0, 1fr) 190px;
  gap: 36px;
  align-items: start;
}

.left-sidebar,
.main-content,
.right-sidebar {
  min-width: 0;
  width: 100%;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.side-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 16px;
  border: none;
  background: transparent;
  border-radius: 12px;
  font-size: 14px;
  color: #4a5046;
  text-align: left;
  width: 100%;
}

.nav-item.disabled {
  cursor: default;
  user-select: none;
  opacity: 0.85;
}

.nav-item.active {
  background-color: #fae8dc;
  color: #9c4a1a;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
}

.nav-icon {
  font-size: 15px;
  width: 18px;
  text-align: center;
}

.page-heading {
  margin-bottom: 4px;
}

.page-heading h1 {
  font-size: 30px;
  font-weight: 600;
  color: #1f241d;
  margin-bottom: 6px;
}

.page-heading p {
  font-size: 14px;
  color: #6c7267;
  line-height: 1.45;
}

.white-panel {
  width: 100%;
  background-color: #ffffff;
  border-radius: 20px;
  padding: 28px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
}

.panel-title {
  font-size: 19px;
  font-weight: 600;
  color: #1f241d;
  margin-bottom: 6px;
}

.panel-subtitle {
  font-size: 13px;
  color: #7c8277;
  margin-bottom: 22px;
  line-height: 1.45;
}

.panel-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 16px;
}

.panel-header-row .panel-subtitle {
  margin-bottom: 0;
}

.avatar-upload-row {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 24px;
}

.big-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: #eff1eb;
  color: #4a5046;
  font-size: 22px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.big-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-controls {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.upload-btn {
  display: inline-block;
  width: fit-content;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #d5d8cd;
  background: #ffffff;
  font-size: 13px;
  font-weight: 500;
  color: #1f241d;
  cursor: pointer;
}

.upload-btn:hover {
  border-color: #26481c;
}

.upload-hint {
  font-size: 12px;
  color: #8c9287;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 12px;
  color: #6c7267;
}

.form-group input,
.form-group textarea {
  width: 100%;
  max-width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #dcdfd6;
  font-size: 14px;
  font-family: inherit;
  color: #1f241d;
  background-color: #ffffff;
  outline: none;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #26481c;
}

.panel-save-bar {
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid #eef0e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.changes-status {
  font-size: 13px;
  color: #8c9287;
}

.save-pill-btn {
  padding: 10px 26px;
  border-radius: 999px;
  border: none;
  background-color: #9ba596;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-pill-btn.ready,
.save-pill-btn:hover {
  background-color: #26481c;
}

.contacts-list {
  display: flex;
  flex-direction: column;
}

.contact-block {
  padding: 16px 0;
  border-top: 1px solid #eef0e8;
}

.contact-block:first-child {
  border-top: none;
  padding-top: 4px;
}

.contact-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.contact-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.contact-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background-color: #f6f7f2;
  color: #6c7267;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}

.contact-details {
  min-width: 0;
}

.contact-value {
  font-size: 14px;
  font-weight: 500;
  color: #1f241d;
  word-break: break-all;
}

.contact-sub {
  font-size: 12px;
  color: #8c9287;
  margin-top: 2px;
}

.contact-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.status-badge {
  font-size: 12px;
  font-weight: 500;
}

.status-badge.verified {
  color: #3d6b35;
}

.status-badge.pending {
  color: #7c8277;
}

.delete-contact-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #6c7267;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
}

.delete-contact-btn:hover {
  color: #991b1b;
}

.contact-notice-box {
  margin-top: 14px;
  margin-left: 52px;
  background-color: #f5f4ee;
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 12px;
  color: #555b50;
  line-height: 1.45;
}

.notice-icon {
  flex-shrink: 0;
  font-size: 14px;
}

.add-contact-form {
  margin-top: 16px;
  padding: 14px;
  background-color: #f6f7f2;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.add-contact-form input {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #dcdfd6;
  font-size: 14px;
  outline: none;
}

.add-contact-actions {
  display: flex;
  gap: 8px;
}

.contacts-footer-buttons {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eef0e8;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.outline-pill-btn {
  padding: 9px 18px;
  border-radius: 999px;
  border: 1px solid #d5d8cd;
  background: #ffffff;
  color: #1f241d;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.2s ease;
}

.outline-pill-btn:hover {
  border-color: #26481c;
}

.btn-green-sm {
  padding: 9px 18px;
  border-radius: 999px;
  border: none;
  background-color: #26481c;
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.btn-green-sm:hover {
  background-color: #1d3815;
}

.quiz-results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quiz-result-item {
  background-color: #f6f7f2;
  padding: 14px 16px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.q-title {
  font-size: 13px;
  color: #6c7267;
}

.q-answer {
  font-size: 15px;
  font-weight: 500;
  color: #1f241d;
}

.fav-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.fav-pet-card {
  border: 1px solid #e5e7de;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.fav-pet-img {
  width: 100%;
  height: 170px;
  object-fit: cover;
}

.fav-pet-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.fav-pet-body h3 {
  font-size: 16px;
  font-weight: 600;
}

.fav-pet-body p {
  font-size: 13px;
  color: #6c7267;
}

.guardians-tag {
  font-size: 12px;
  color: #26481c;
  font-weight: 500;
}
.pet-card-actions {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.adopt-btn {
  width: 100%;
  padding: 9px 14px;
  border-radius: 999px;
  border: 1.5px solid #26481c;
  background-color: #26481c;
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.adopt-btn:hover {
  background-color: #1d3815;
  border-color: #1d3815;
}

.sponsor-btn {
  width: 100%;
  padding: 9px 14px;
  border-radius: 999px;
  border: 1.5px solid #26481c;
  background-color: #ffffff;
  color: #26481c;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.sponsor-btn:hover {
  background-color: #f2f5f0;
}
.remove-pet-btn {
  margin-top: 4px;
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid #dcdfd6;
  background: transparent;
  color: #6c7267;
  font-size: 12px;
  cursor: pointer;
}

.remove-pet-btn:hover {
  border-color: #991b1b;
  color: #991b1b;
}

.empty-box {
  padding: 20px;
  text-align: center;
  background: #f6f7f2;
  border-radius: 12px;
  color: #6c7267;
  font-size: 14px;
}

.right-links {
  position: sticky;
  top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 68px;
}

.right-link {
  background: none;
  border: none;
  text-align: left;
  font-size: 13px;
  color: #7c8277;
  cursor: pointer;
  padding: 2px 0;
  transition: color 0.15s ease;
}

.right-link.active,
.right-link:hover {
  color: #1f241d;
  font-weight: 600;
}

@media (max-width: 960px) {
  .dashboard-grid {
grid-template-columns: minmax(0, 1fr);
gap: 16px;
padding: 16px;
}
.right-sidebar {
display: none;
}
.side-nav {
flex-direction: column;
gap: 6px;
}
.nav-item {
background-color: #ffffff;
border: 1px solid #e5e7de;
padding: 10px 14px;
font-size: 13px;
}
.nav-item.active {
border-color: #fae8dc;
margin-top: 0;
}
}
@media (max-width: 600px) {
.top-header {
padding: 10px 14px;
height: auto;
gap: 8px;
}
.header-divider,
.header-pill-btn {
display: none;
}
.dashboard-grid {
padding: 14px 12px;
}
.page-heading h1 {
font-size: 22px;
}
.white-panel {
padding: 18px 14px;
border-radius: 16px;
}
.form-grid {
grid-template-columns: 1fr;
gap: 12px;
}
.contact-notice-box {
margin-left: 0;
}
.contacts-footer-buttons,
.panel-header-row {
flex-direction: column;
align-items: stretch;
}
.outline-pill-btn,
.btn-green-sm {
width: 100%;
text-align: center;
}
.fav-cards-grid {
grid-template-columns: 1fr;
}
}
</style>
