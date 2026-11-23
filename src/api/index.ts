import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'

// ПЕРЕКЛЮЧАТЕЛЬ РЕЖИМА:
// true  = автономная проверка без Flask (все работает в браузере)
// false = боевой режим для сборки (npm run build) и работы с реальным Flask
const USE_MOCK = false

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('user_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- ВРЕМЕННЫЙ ИМИТАТОР БЭКЕНДА ДЛЯ ПРОВЕРКИ В БРАУЗЕРЕ ---
if (USE_MOCK) {
  const mockPets = [
    {
      id: 1,
      name: 'Люпин',
      age: '1 год',
      description: 'Мальчик, центр «Мокрый нос», Брёхово',
      guardians: '3 из 5 опекунов',
      image: 'https://unsplash.com',
      ai_reason: 'Спокойный и дружелюбный, отлично подойдет для проживания в квартире.'
    },
    {
      id: 2,
      name: 'Рекс',
      age: '2 года',
      description: 'Мальчик, приют «Счастливый хвост»',
      guardians: '2 из 5 опекунов',
      image: 'https://unsplash.com',
      ai_reason: 'Любит активные прогулки и легко находит общий язык с людьми.'
    },
    {
      id: 3,
      name: 'Белла',
      age: '8 месяцев',
      description: 'Девочка, приют «Дом для друга»',
      guardians: '4 из 5 опекунов',
      image: 'https://unsplash.com',
      ai_reason: 'Ласковая и не требует сложного ухода, подойдет даже новичкам.'
    }
  ]

  const mockQuestions = [
  {
    "id": 1,
    "text": "Кого вы хотите завести?",
    "options": ["Собаку", "Кошку"]
  },
  {
    "id": 2,
    "text": "Где вы живете?",
    "options": ["В квартире", "В частном доме"]
  },
  {
    "id": 3,
    "text": "Расскажите подробнее о вашем образе жизни и опыте общения с животными"
  }
]


  api.defaults.adapter = async (config: InternalAxiosRequestConfig): Promise<AxiosResponse> => {
    // Имитация небольшой задержки сети (300 мс), чтобы увидеть анимацию загрузки
    await new Promise((resolve) => setTimeout(resolve, 300))

    const url = config.url || ''
    const method = (config.method || 'get').toLowerCase()
    const body = config.data ? JSON.parse(config.data) : {}

    const reply = (data: any, status = 200): AxiosResponse => ({
      data,
      status,
      statusText: 'OK',
      headers: {},
      config
    })

        // 1. Вход и регистрация
    if (url === '/register' || url === '/login') {
      const email = body.email || 'user@mail.ru'
      const isAdmin = email === 'admin@fond-nika.ru'

      // При новой регистрации полностью сбрасываем данные прошлой сессии
      if (url === '/register' || !localStorage.getItem('mock_profile')) {
        localStorage.removeItem('mock_fav_ids')
        localStorage.removeItem('mock_quiz')

        localStorage.setItem(
          'mock_profile',
          JSON.stringify({
            firstName: body.name || 'Пользователь',
            lastName: '',
            birthDate: '',
            workField: '',
            hobbies: '',
            about: '',
            avatar: ''
          })
        )
        localStorage.setItem(
          'mock_contacts',
          JSON.stringify([
            {
              id: 1,
              type: 'email',
              value: email,
              subtitle: 'Почта, основная: письма, чеки и вход',
              status: 'verified',
              isPrimary: true
            }
          ])
        )
      }

      return reply({
        token: 'mock-token-123',
        email,
        role: isAdmin ? 'admin' : 'user'
      })
    }


    // 2. Профиль пользователя
    if (url === '/profile' && method === 'get') {
      const favIds: number[] = JSON.parse(localStorage.getItem('mock_fav_ids') || '[]')
      return reply({
        profile: JSON.parse(localStorage.getItem('mock_profile') || '{}'),
        contacts: JSON.parse(localStorage.getItem('mock_contacts') || '[]'),
        quizResults: JSON.parse(localStorage.getItem('mock_quiz') || '[]'),
        favorites: mockPets.filter((p) => favIds.includes(p.id))
      })
    }

    if (url === '/profile' && method === 'put') {
      localStorage.setItem('mock_profile', JSON.stringify(body.profile))
      localStorage.setItem('mock_contacts', JSON.stringify(body.contacts))
      return reply({ status: 'saved' })
    }

    // 3. Вопросы и сохранение опроса
    if (url === '/questions' && method === 'get') {
      return reply(mockQuestions)
    }

    if (url === '/quiz' && method === 'post') {
      localStorage.setItem('mock_quiz', JSON.stringify(body.answers || []))
      return reply({ status: 'ok' })
    }

    // 4. Животные
    if (url === '/pets' && method === 'get') {
      return reply(mockPets)
    }

    // 5. Избранное
    if (url === '/favorites' && method === 'get') {
      const favIds: number[] = JSON.parse(localStorage.getItem('mock_fav_ids') || '[]')
      return reply(mockPets.filter((p) => favIds.includes(p.id)))
    }

    if (url === '/favorites' && method === 'post') {
      const favIds: number[] = JSON.parse(localStorage.getItem('mock_fav_ids') || '[]')
      if (!favIds.includes(body.pet_id)) {
        favIds.push(body.pet_id)
        localStorage.setItem('mock_fav_ids', JSON.stringify(favIds))
      }
      return reply({ status: 'added' })
    }

    if (url.startsWith('/favorites/') && method === 'delete') {
      const id = Number(url.split('/').pop())
      const favIds: number[] = JSON.parse(localStorage.getItem('mock_fav_ids') || '[]')
      localStorage.setItem('mock_fav_ids', JSON.stringify(favIds.filter((fid) => fid !== id)))
      return reply({ status: 'deleted' })
    }

    // 6. Заявки для администратора
    if (url === '/requests' && method === 'get') {
      return reply(JSON.parse(localStorage.getItem('mock_requests') || '[]'))
    }

    if (url === '/requests' && method === 'post') {
      const pet = mockPets.find((p) => p.id === body.pet_id)
      const list = JSON.parse(localStorage.getItem('mock_requests') || '[]')
      list.unshift({
        id: Date.now(),
        petId: body.pet_id,
        petName: pet?.name || 'Питомец',
        petDescription: pet?.description || '',
        petImage: pet?.image || '',
        applicantName: body.applicant_name,
        contact: body.contact,
        contactMethod: body.contact_method,
        status: 'new',
        createdAt: new Date().toLocaleString('ru-RU')
      })
      localStorage.setItem('mock_requests', JSON.stringify(list))
      return reply({ status: 'created' })
    }

    if (url.startsWith('/requests/') && method === 'patch') {
      const id = Number(url.split('/').pop())
      const list = JSON.parse(localStorage.getItem('mock_requests') || '[]')
      const item = list.find((r: any) => r.id === id)
      if (item) item.status = body.status
      localStorage.setItem('mock_requests', JSON.stringify(list))
      return reply({ status: 'updated' })
    }

    if (url.startsWith('/requests/') && method === 'delete') {
      const id = Number(url.split('/').pop())
      const list = JSON.parse(localStorage.getItem('mock_requests') || '[]')
      localStorage.setItem('mock_requests', JSON.stringify(list.filter((r: any) => r.id !== id)))
      return reply({ status: 'deleted' })
    }

    return reply({}, 404)
  }
}

export default api
