<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import AdoptModal from './AdoptModal.vue'
import type { Pet } from '../types'

const router = useRouter()

const favorites = ref<Pet[]>([])
const selectedPetForAdopt = ref<Pet | null>(null)

onMounted(async () => {
  try {
    const email = localStorage.getItem('user_email')
    const { data } = await api.get<Pet[]>('/favorites', { params: { email } })
    favorites.value = data
  } catch (err) {
    console.error('Ошибка загрузки избранного:', err)
  }
})

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

const goBackToPets = (): void => {
  router.push('/pets')
}

const goToProfile = (): void => {
  router.push('/profile')
}
</script>


<template>
  <div class="favorites-wrapper">
    <div class="header-bar">
      <div class="nav-buttons-group">
        <button class="back-btn" @click="goBackToPets">← К подбору</button>
        <button class="back-btn" @click="goToProfile">Личный кабинет</button>
      </div>
      <span class="counter">Избранное: {{ favorites.length }}</span>
    </div>

    <div v-if="favorites.length === 0" class="card empty-state">
      <p>Вы пока никого не добавили в избранное.</p>
      <button class="btn-primary back-action" @click="goBackToPets">
        Подобрать питомца
      </button>
    </div>

    <div v-else class="favorites-list">
      <div v-for="pet in favorites" :key="pet.id" class="pet-card">
        <div class="photo-box">
          <img :src="pet.image" :alt="pet.name" class="pet-photo" />
          <div class="guardians-badge">
            <span class="dots">•••</span> {{ pet.guardians }}
          </div>
        </div>

        <div class="pet-info">
          <div class="pet-header-row">
            <div>
              <h2 class="pet-name">{{ pet.name }}, {{ pet.age }}</h2>
              <p class="pet-desc">{{ pet.description }}</p>
            </div>
            <button class="remove-btn" @click="removeFromFavorites(pet.id)">
              Убрать
            </button>
          </div>

          <div class="pet-action-buttons">
            <button type="button" class="adopt-btn" @click="handleAdopt(pet)">
              Познакомиться
            </button>
            <button type="button" class="sponsor-btn" @click="handleSponsor(pet)">
              Стать опекуном
            </button>
          </div>
        </div>
      </div>
    </div>
  <AdoptModal :pet="selectedPetForAdopt" @close="selectedPetForAdopt = null" />
  </div>
</template>

<style scoped>
.favorites-wrapper {
  width: 100%;
  max-width: 540px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 48px 16px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.nav-buttons-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.back-btn {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #26481c;
  background: #ffffff;
  color: #26481c;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #26481c;
  color: #ffffff;
}

.counter {
  font-size: 15px;
  font-weight: 500;
  color: #26481c;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pet-card {
  width: 100%;
  background: #ffffff;
  border: 1.5px solid #2b4c24;
  border-radius: 20px;
  padding: 12px;
  box-shadow: 0 10px 30px rgba(43, 76, 36, 0.05);
}

.photo-box {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 14px;
  overflow: hidden;
}

.pet-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.guardians-badge {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: #ffffff;
  color: #1f291c;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.dots {
  color: #26481c;
  margin-right: 4px;
}

.pet-info {
  padding: 14px 8px 6px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pet-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.pet-action-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
}

.adopt-btn {
  flex: 1;
  padding: 11px 16px;
  border-radius: 999px;
  border: 1.5px solid #26481c;
  background-color: #26481c;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.adopt-btn:hover {
  background-color: #1d3815;
  border-color: #1d3815;
}

.sponsor-btn {
  flex: 1;
  padding: 11px 16px;
  border-radius: 999px;
  border: 1.5px solid #26481c;
  background-color: #ffffff;
  color: #26481c;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.sponsor-btn:hover {
  background-color: #f2f5f0;
}

.pet-name {
  font-size: 20px;
  font-weight: 600;
  color: #1f291c;
  margin-bottom: 4px;
}

.pet-desc {
  font-size: 14px;
  color: #6b7268;
}

.remove-btn {
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: transparent;
  color: #6b7268;
  font-size: 13px;
  cursor: pointer;
}

.remove-btn:hover {
  border-color: #991b1b;
  color: #991b1b;
}

.empty-state {
  text-align: center;
  color: #6b7268;
}

.back-action {
  margin-top: 20px;
}

@media (max-width: 600px) {
  .photo-box {
    height: 220px;
  }
  .pet-action-buttons { flex-direction: column; gap: 8px; }
  .favorites-wrapper{
    padding: 32px 12px;
  }
}
</style>
