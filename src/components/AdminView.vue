<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

type RequestStatus = 'new' | 'contacted' | 'scheduled' | 'rejected'

interface AdoptRequest {
  id: number
  petId: number
  petName: string
  petDescription: string
  petImage: string
  applicantName: string
  contact: string
  contactMethod: string
  status: RequestStatus
  createdAt: string
}

const router = useRouter()

const filterStatus = ref<'all' | RequestStatus>('all')
const requests = ref<AdoptRequest[]>([])

onMounted(async () => {
  try {
    const { data } = await api.get<AdoptRequest[]>('/requests')
    requests.value = data
  } catch (err) {
    console.error('Ошибка загрузки заявок:', err)
  }
})

const filteredRequests = computed<AdoptRequest[]>(() => {
  if (filterStatus.value === 'all') return requests.value
  return requests.value.filter((req) => req.status === filterStatus.value)
})

const stats = computed(() => {
  return {
    total: requests.value.length,
    newCount: requests.value.filter((r) => r.status === 'new').length,
    scheduledCount: requests.value.filter((r) => r.status === 'scheduled').length
  }
})

const statusLabels: Record<RequestStatus, string> = {
  new: 'Новая заявка',
  contacted: 'Связались с кандидатом',
  scheduled: 'Встреча назначена',
  rejected: 'Отклонена'
}

const updateStatus = async (id: number, newStatus: RequestStatus): Promise<void> => {
  try {
    await api.patch(`/requests/${id}`, { status: newStatus })
    const target = requests.value.find((r) => r.id === id)
    if (target) {
      target.status = newStatus
    }
  } catch (err) {
    alert('Ошибка обновления статуса')
  }
}

const deleteRequest = async (id: number): Promise<void> => {
  try {
    await api.delete(`/requests/${id}`)
    requests.value = requests.value.filter((r) => r.id !== id)
  } catch (err) {
    alert('Ошибка удаления заявки')
  }
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
        <span class="header-divider">Панель администратора</span>
      </div>

      <div class="header-right">
        <button class="header-pill-btn" @click="router.push('/profile')">
          В кабинет пользователя
        </button>
        <div class="header-avatar" title="Администратор">А</div>
        <button class="logout-link" @click="logout">Выйти</button>
      </div>
    </header>

    <div class="dashboard-grid">
      
      <aside class="left-sidebar">
        <nav class="side-nav">
          <div class="nav-item disabled">
            <span class="nav-icon">🐾</span>
            <span>Подопечные приюта</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">♡</span>
            <span>Опекуны</span>
          </div>
          <div class="nav-item disabled">
            <span class="nav-icon">📊</span>
            <span>Отчёты фонда</span>
          </div>

          <button class="nav-item active" @click="filterStatus = 'all'">
            <span class="nav-icon">📥</span>
            <span>Заявки «Приютить»</span>
            <span v-if="stats.newCount > 0" class="menu-counter">{{ stats.newCount }}</span>
          </button>
        </nav>
      </aside>

      
      <main class="main-content">
        <div class="page-heading">
          <h1>Заявки на знакомство</h1>
          
        </div>

        
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">Всего заявок</span>
            <strong class="stat-value">{{ stats.total }}</strong>
          </div>
          <div class="stat-card highlight">
            <span class="stat-label">Ожидают звонка</span>
            <strong class="stat-value">{{ stats.newCount }}</strong>
          </div>
          <div class="stat-card">
            <span class="stat-label">Встреча назначена</span>
            <strong class="stat-value">{{ stats.scheduledCount }}</strong>
          </div>
        </div>

        
        <section class="white-panel">
          <div class="panel-header-row">
            <div>
              <h2 class="panel-title">Входящие анкеты ({{ filteredRequests.length }})</h2>
              
            </div>
          </div>

          <div v-if="filteredRequests.length === 0" class="empty-box">
            <p>Заявок в выбранной категории пока нет.</p>
          </div>

          <div v-else class="requests-list">
            <div v-for="req in filteredRequests" :key="req.id" class="request-card">
              
              <div class="req-top">
                <div class="req-pet-info">
                  <img :src="req.petImage" :alt="req.petName" class="req-pet-thumb" />
                  <div>
                    <div class="req-pet-name">Питомец: {{ req.petName }}</div>
                    <div class="req-pet-desc">{{ req.petDescription }}</div>
                  </div>
                </div>

                <span class="req-status-pill" :class="req.status">
                  {{ statusLabels[req.status] }}
                </span>
              </div>

              
              <div class="req-applicant-box">
                <div class="applicant-row">
                  <span class="app-label">Кандидат:</span>
                  <span class="app-val">{{ req.applicantName }}</span>
                </div>
                <div class="applicant-row">
                  <span class="app-label">Контакт:</span>
                  <span class="app-val">{{ req.contact }}</span>
                </div>
                <div class="applicant-row">
                  <span class="app-label">Способ связи:</span>
                  <span class="method-tag">{{ req.contactMethod }}</span>
                </div>
                <div class="applicant-row">
                  <span class="app-label">Дата заявки:</span>
                  <span class="app-date">{{ req.createdAt }}</span>
                </div>
              </div>

              
              <div class="req-actions-bar">
                <div class="status-controls">
                  <label class="select-label">Изменить статус:</label>
                  <select
                    :value="req.status"
                    class="status-select"
                    @change="updateStatus(req.id, ($event.target as HTMLSelectElement).value as RequestStatus)"
                  >
                    <option value="new">Новая заявка</option>
                    <option value="contacted">Связались с кандидатом</option>
                    <option value="scheduled">Встреча назначена</option>
                    <option value="rejected">Отклонена</option>
                  </select>
                </div>

                <button type="button" class="delete-req-btn" @click="deleteRequest(req.id)">
                  Удалить заявку
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>

      
      <aside class="right-sidebar">
        <div class="right-links">
          <span class="right-heading">Фильтр заявок</span>
          <button
            class="right-link"
            :class="{ active: filterStatus === 'all' }"
            @click="filterStatus = 'all'"
          >
            Все заявки ({{ requests.length }})
          </button>
          <button
            class="right-link"
            :class="{ active: filterStatus === 'new' }"
            @click="filterStatus = 'new'"
          >
            Новые ({{ stats.newCount }})
          </button>
          <button
            class="right-link"
            :class="{ active: filterStatus === 'contacted' }"
            @click="filterStatus = 'contacted'"
          >
            Связались
          </button>
          <button
            class="right-link"
            :class="{ active: filterStatus === 'scheduled' }"
            @click="filterStatus = 'scheduled'"
          >
            Встреча назначена
          </button>
          <button
            class="right-link"
            :class="{ active: filterStatus === 'rejected' }"
            @click="filterStatus = 'rejected'"
          >
            Отклонённые
          </button>
        </div>
      </aside>
    </div>
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
flex-shrink: 0;
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
/* Левое меню */
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
.menu-counter {
margin-left: auto;
background-color: #9c4a1a;
color: #ffffff;
font-size: 11px;
font-weight: 600;
padding: 2px 7px;
border-radius: 999px;
}
.nav-icon {
font-size: 15px;
width: 18px;
text-align: center;
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
/* Карточки статистики */
.stats-grid {
display: grid;
grid-template-columns: repeat(3, 1fr);
gap: 14px;
}
.stat-card {
background-color: #ffffff;
border-radius: 16px;
padding: 18px 20px;
display: flex;
flex-direction: column;
gap: 6px;
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}
.stat-card.highlight {
background-color: #fae8dc;
}
.stat-label {
font-size: 12px;
color: #6c7267;
}
.stat-card.highlight .stat-label {
color: #9c4a1a;
}
.stat-value {
font-size: 26px;
font-weight: 600;
color: #1f241d;
}
.stat-card.highlight .stat-value {
color: #9c4a1a;
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
margin-bottom: 4px;
}
.panel-subtitle {
font-size: 13px;
color: #7c8277;
margin-bottom: 20px;
}
.requests-list {
display: flex;
flex-direction: column;
gap: 16px;
}
.request-card {
border: 1px solid #e5e7de;
border-radius: 16px;
padding: 18px;
display: flex;
flex-direction: column;
gap: 14px;
}
.req-top {
display: flex;
justify-content: space-between;
align-items: flex-start;
gap: 12px;
}
.req-pet-info {
display: flex;
align-items: center;
gap: 14px;
}
.req-pet-thumb {
width: 54px;
height: 54px;
border-radius: 12px;
object-fit: cover;
flex-shrink: 0;
}
.req-pet-name {
font-size: 16px;
font-weight: 600;
color: #1f241d;
}
.req-pet-desc {
font-size: 13px;
color: #6c7267;
margin-top: 2px;
}
.req-status-pill {
padding: 5px 12px;
border-radius: 999px;
font-size: 12px;
font-weight: 500;
white-space: nowrap;
}
.req-status-pill.new {
background-color: #fae8dc;
color: #9c4a1a;
}
.req-status-pill.contacted {
background-color: #eef0e8;
color: #4a5046;
}
.req-status-pill.scheduled {
background-color: #eaf2e8;
color: #26481c;
}
.req-status-pill.rejected {
background-color: #fee2e2;
color: #991b1b;
}
.req-applicant-box {
background-color: #f6f7f2;
border-radius: 12px;
padding: 14px 16px;
display: grid;
grid-template-columns: 1fr 1fr;
gap: 10px 16px;
}
.applicant-row {
display: flex;
flex-direction: column;
gap: 2px;
}
.app-label {
font-size: 11px;
color: #8c9287;
}
.app-val {
font-size: 14px;
font-weight: 500;
color: #1f241d;
word-break: break-all;
}
.method-tag {
display: inline-block;
width: fit-content;
padding: 2px 10px;
border-radius: 999px;
border: 1px solid #26481c;
background-color: #ffffff;
color: #26481c;
font-size: 12px;
font-weight: 500;
}
.app-date {
font-size: 13px;
color: #555b50;
}
.req-actions-bar {
display: flex;
justify-content: space-between;
align-items: center;
gap: 12px;
padding-top: 4px;
}
.status-controls {
display: flex;
align-items: center;
gap: 10px;
}
.select-label {
font-size: 13px;
color: #6c7267;
}
.status-select {
padding: 7px 14px;
border-radius: 999px;
border: 1px solid #d5d8cd;
background-color: #ffffff;
font-size: 13px;
color: #1f241d;
outline: none;
cursor: pointer;
}
.status-select:focus {
border-color: #26481c;
}
.delete-req-btn {
background: none;
border: none;
color: #8c9287;
font-size: 12px;
text-decoration: underline;
cursor: pointer;
}
.delete-req-btn:hover {
color: #991b1b;
}
.empty-box {
padding: 28px;
text-align: center;
background: #f6f7f2;
border-radius: 12px;
color: #6c7267;
font-size: 14px;
}
/* Правый столбец */
.right-links {
position: sticky;
top: 24px;
display: flex;
flex-direction: column;
gap: 10px;
padding-top: 68px;
}
.right-heading {
font-size: 12px;
font-weight: 600;
color: #8c9287;
text-transform: uppercase;
letter-spacing: 0.04em;
margin-bottom: 4px;
}
.right-link {
background: none;
border: none;
text-align: left;
font-size: 13px;
color: #7c8277;
cursor: pointer;
padding: 3px 0;
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
.stats-grid {
grid-template-columns: 1fr;
gap: 10px;
}
.white-panel {
padding: 18px 14px;
}
.req-top,
.req-actions-bar {
flex-direction: column;
align-items: flex-start;
}
.req-applicant-box {
grid-template-columns: 1fr;
}
}
</style>