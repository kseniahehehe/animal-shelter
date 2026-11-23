<script setup lang="ts">
import { ref, watch } from 'vue'
import api from '../api'
import type { Pet } from '../types'

const props = defineProps<{
  pet: Pet | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const name = ref<string>('')
const contact = ref<string>('')
const contactMethod = ref<string>('Звонок')
const agreed = ref<boolean>(false)
const isSubmitted = ref<boolean>(false)
const isSending = ref<boolean>(false)

const methods = ['Звонок', 'WhatsApp', 'Telegram', 'MAX', 'Почта']

watch(() => props.pet, () => {
  name.value = ''
  contact.value = ''
  contactMethod.value = 'Звонок'
  isSubmitted.value = false
  agreed.value = false
})

const submitForm = async (): Promise<void> => {
  if (!agreed.value || !props.pet) return
  isSending.value = true

  try {
    await api.post('/requests', {
      pet_id: props.pet.id,
      applicant_name: name.value,
      contact: contact.value,
      contact_method: contactMethod.value
    })
    isSubmitted.value = true
  } catch (err) {
    alert('Не удалось отправить заявку. Попробуйте позже.')
  } finally {
    isSending.value = false
  }
}

const closeModal = (): void => {
  isSubmitted.value = false
  emit('close')
}
</script>



<template>
  <div v-if="pet" class="modal-backdrop" @click.self="closeModal">
    <div class="modal-card">
      <button type="button" class="close-btn" @click="closeModal" aria-label="Закрыть">
        ✕
      </button>

      
      <div v-if="isSubmitted" class="success-view">
        <div class="success-icon">✓</div>
        <h2 class="modal-title">Заявка отправлена!</h2>
        <p class="modal-subtitle">
          Спасибо, {{ name }}! Сотрудник приюта скоро свяжется с вами через
          <strong>{{ contactMethod }}</strong> по контакту <strong>{{ contact }}</strong>,
          чтобы рассказать о питомце «{{ pet.name }}» и договориться о встрече.
        </p>
        <button type="button" class="submit-btn" @click="closeModal">
          Отлично
        </button>
      </div>

      
      <template v-else>
        <h2 class="modal-title">Заявка на знакомство</h2>
        <p class="modal-subtitle">
          {{ pet.name }}, {{ pet.description }}. Оставьте контакт: сотрудник приюта
          свяжется с вами, расскажет о подопечном и договорится о встрече.
        </p>

        <form class="adopt-form" @submit.prevent="submitForm">
          <div class="field-group">
            <label>Имя</label>
            <input v-model="name" type="text" required />
          </div>

          <div class="field-group">
            <label>Телефон или почта</label>
            <input v-model="contact" type="text" required />
            <span class="field-hint">Например, +7 916 123-45-67 или anna@mail.ru</span>
          </div>

          <div class="field-group">
            <label>Как с вами связаться</label>
            <div class="methods-row">
              <button
                v-for="m in methods"
                :key="m"
                type="button"
                class="method-pill"
                :class="{ active: contactMethod === m }"
                @click="contactMethod = m"
              >
                {{ m }}
              </button>
            </div>
          </div>

          <label class="checkbox-row">
            <input v-model="agreed" type="checkbox" required />
            <span>Согласен на обработку персональных данных *</span>
          </label>

          <button type="submit" class="submit-btn" :disabled="!agreed">
            Отправить заявку
          </button>
        </form>
      </template>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(25, 30, 22, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  z-index: 1000;
}

.modal-card {
  position: relative;
  width: 100%;
  max-width: 520px;
  background-color: #ffffff;
  border-radius: 28px;
  padding: 36px 36px 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.18);
  color: #1f241d;
  max-height: 92vh;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid #e5e7de;
  background-color: #ffffff;
  color: #6c7267;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.close-btn:hover {
  border-color: #1f241d;
  color: #1f241d;
}

.modal-title {
  font-size: 26px;
  font-weight: 600;
  color: #1f241d;
  margin-bottom: 10px;
  padding-right: 32px;
}

.modal-subtitle {
  font-size: 14px;
  color: #555b50;
  line-height: 1.45;
  margin-bottom: 22px;
}

.adopt-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-group label {
  font-size: 13px;
  color: #4a5046;
}

.field-group input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1.5px solid #dcdfd6;
  font-size: 15px;
  color: #1f241d;
  outline: none;
  transition: border-color 0.15s ease;
}

.field-group input:focus {
  border-color: #26481c;
}

.field-hint {
  font-size: 12px;
  color: #8c9287;
}

.methods-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.method-pill {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid #dcdfd6;
  background-color: #ffffff;
  color: #1f241d;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.method-pill:hover {
  border-color: #26481c;
}

.method-pill.active {
  border: 1.5px solid #26481c;
  font-weight: 500;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #4a5046;
  cursor: pointer;
  margin-top: 2px;
}

.checkbox-row input[type='checkbox'] {
  width: 18px;
  height: 18px;
  accent-color: #26481c;
  cursor: pointer;
  flex-shrink: 0;
}

.submit-btn {
  margin-top: 6px;
  width: 100%;
  padding: 14px 24px;
  border-radius: 999px;
  border: none;
  background-color: #26481c;
  color: #ffffff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background-color: #1d3815;
}

.submit-btn:disabled {
  background-color: #9ba596;
  cursor: not-allowed;
}

.success-view {
  text-align: center;
  padding: 12px 0;
}

.success-view .modal-title {
  padding-right: 0;
}

.success-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background-color: #eaf2e8;
  color: #26481c;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

@media (max-width: 600px) {
  .modal-card {
    padding: 28px 20px 24px;
    border-radius: 22px;
  }

  .modal-title {
    font-size: 22px;
  }
}
</style>
