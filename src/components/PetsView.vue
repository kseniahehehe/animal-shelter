<script setup lang="ts">
import { ref, computed, onMounted, type CSSProperties } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import type { Pet } from '../types'

const router = useRouter()

const pets = ref<Pet[]>([])
const currentIndex = ref<number>(0)
const favoritesCount = ref<number>(0)
const isLoading = ref<boolean>(true)

const currentPet = computed<Pet | undefined>(() => pets.value[currentIndex.value])

onMounted(async () => {
  try {
    isLoading.value = true
    const email = localStorage.getItem('user_email')
    const [petsRes, favsRes] = await Promise.all([
      api.get<Pet[]>('/pets', { params: { email } }),
      api.get<Pet[]>('/favorites', { params: { email } })
    ])
    pets.value = petsRes.data
    favoritesCount.value = favsRes.data.length
  } catch (err) {
    console.error('Ошибка загрузки питомцев:', err)
  } finally {
    isLoading.value = false
  }
})

const nextPet = (): void => {
  if (pets.value.length === 0) return
  currentIndex.value = (currentIndex.value + 1) % pets.value.length
}

const skipPet = (): void => {
  nextPet()
}

const addToFavorites = async (): Promise<void> => {
  const pet = currentPet.value
  if (!pet) return

  try {
    const email = localStorage.getItem('user_email')
    await api.post('/favorites', { email, pet_id: pet.id })
    favoritesCount.value++
  } catch (err) {
    console.error('Ошибка добавления в избранное:', err)
  }

  nextPet()
}

const goToFavorites = (): void => {
  router.push('/favorites')
}

// Свайпы для мобильных экранов
const touchStartX = ref<number>(0)
const swipeOffsetX = ref<number>(0)
const isSwiping = ref<boolean>(false)
const SWIPE_THRESHOLD = 90

const onTouchStart = (e: TouchEvent): void => {
  const touch = e.touches[0]
  if (!touch) return
  touchStartX.value = touch.clientX
  isSwiping.value = true
}

const onTouchMove = (e: TouchEvent): void => {
  if (!isSwiping.value) return
  const touch = e.touches[0]
  if (!touch) return
  swipeOffsetX.value = touch.clientX - touchStartX.value
}

const onTouchEnd = (): void => {
  if (!isSwiping.value) return
  isSwiping.value = false

  if (swipeOffsetX.value > SWIPE_THRESHOLD) {
    addToFavorites()
  } else if (swipeOffsetX.value < -SWIPE_THRESHOLD) {
    skipPet()
  }

  swipeOffsetX.value = 0
}

const cardSwipeStyle = computed<CSSProperties>(() => {
  const rotate = swipeOffsetX.value * 0.04
  return {
    transform: `translateX(${swipeOffsetX.value}px) rotate(${rotate}deg)`,
    transition: isSwiping.value ? 'none' : 'transform 0.25s ease'
  }
})
</script>


<template>
  <div class="pets-wrapper" v-if="currentPet">
    <div class="top-bar">
      <button class="fav-link-btn" @click="router.push('/profile')">
        Личный кабинет
      </button>
      <button class="fav-link-btn" @click="goToFavorites">
        Избранное ({{ favoritesCount }}) →
      </button>
    </div>

    <div
      class="pet-card"
      :style="cardSwipeStyle"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      <div class="photo-box">
        <img :src="currentPet.image" :alt="currentPet.name" class="pet-photo" />

        <div v-if="swipeOffsetX > 35" class="swipe-stamp stamp-like">
          В избранное
        </div>
        <div v-if="swipeOffsetX < -35" class="swipe-stamp stamp-skip">
          Пропустить
        </div>

        <div class="guardians-badge">
          <span class="dots">•••</span> {{ currentPet.guardians }}
        </div>
      </div>

      <div class="pet-info">
        <h2 class="pet-name">{{ currentPet.name }}, {{ currentPet.age }}</h2>
        <p class="pet-desc">{{ currentPet.description }}</p>
      </div>
    </div>

    <p class="mobile-swipe-hint">
      ← Свайп влево — пропустить • Вправо — в избранное →
    </p>

    <div class="pet-actions">
      <button class="btn-primary" @click="skipPet">Пропустить</button>
      <button class="btn-primary" @click="addToFavorites">В избранное</button>
    </div>
  </div>
</template>

<style scoped>
.pets-wrapper {
  width: 100%;
  max-width: 540px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  overflow-x: hidden;
}

.top-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.fav-link-btn {
  padding: 8px 18px;
  border-radius: 999px;
  border: 1px solid #26481c;
  background: #ffffff;
  color: #26481c;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.fav-link-btn:hover {
  background: #26481c;
  color: #ffffff;
}

.pet-card {
  width: 100%;
  background: #ffffff;
  border: 1.5px solid #2b4c24;
  border-radius: 20px;
  padding: 12px;
  box-shadow: 0 10px 30px rgba(43, 76, 36, 0.05);
  touch-action: pan-y;
  user-select: none;
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
  pointer-events: none;
}

.swipe-stamp {
  position: absolute;
  top: 16px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  z-index: 2;
}

.stamp-like {
  left: 16px;
  background-color: #26481c;
}

.stamp-skip {
  right: 16px;
  background-color: #6b7268;
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

.pet-actions {
  display: flex;
  gap: 20px;
  width: 100%;
}

.mobile-swipe-hint {
  display: none;
  font-size: 13px;
  color: #6b7268;
  text-align: center;
}

@media (max-width: 600px) {
  .photo-box {
    height: 250px;
  }

  .pet-actions {
    display: none;
  }

  .mobile-swipe-hint {
    display: block;
  }
}
</style>
