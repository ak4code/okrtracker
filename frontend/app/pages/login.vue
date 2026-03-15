<script setup lang="ts">
import { Lock, LogIn } from 'lucide-vue-next'

definePageMeta({
  layout: false,
  title: 'Авторизация',
})

const auth = useAuth()
const form = reactive({
  email: '',
  password: '',
})
const errorMessage = ref('')

const submit = async () => {
  errorMessage.value = ''

  try {
    await auth.login({
      email: form.email,
      password: form.password,
    })
    await navigateTo('/')
  }
  catch (error: any) {
    errorMessage.value = error?.data?.detail || 'Не удалось выполнить вход. Проверьте email и пароль.'
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-sky-100 via-white to-violet-100 p-4">
    <div class="w-full max-w-md">
      <div class="mb-8 text-center">
        <div class="mb-4 inline-flex h-16 w-16 items-center justify-center block-radius bg-gradient-to-br from-sky-500 to-violet-600 text-2xl font-semibold text-white">
          O
        </div>
        <h1 class="text-3xl font-semibold text-ink-900">OKR Tracker</h1>
        <p class="mt-2 text-ink-500">Войдите в систему управления целями</p>
      </div>

      <div class="block-radius bg-white p-8 shadow-lg">
        <form class="space-y-6" @submit.prevent="submit">
          <div>
            <label class="mb-2 block text-sm text-ink-700">Email</label>
            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="admin@example.com"
              class="input-base pl-4"
            >
          </div>
          <div>
            <label class="mb-2 block text-sm text-ink-700">Пароль</label>
            <input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              placeholder="Введите пароль"
              class="input-base pl-4"
            >
          </div>
          <div v-if="errorMessage" class="rounded-sm border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
            {{ errorMessage }}
          </div>
          <button
            type="submit"
            class="btn btn-accent btn-lg w-full"
            :disabled="auth.isLoading.value"
          >
            <LogIn class="h-4 w-4" />
            {{ auth.isLoading.value ? 'Входим...' : 'Войти' }}
          </button>
        </form>

        <div class="mt-6 border-t border-ink-200 pt-6">
          <button type="button" class="btn btn-secondary btn-lg w-full text-ink-400">
            <Lock class="h-4 w-4" />
            Корпоративный вход будет добавлен позже
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
