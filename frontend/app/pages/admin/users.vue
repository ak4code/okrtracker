<script setup lang="ts">
definePageMeta({
  title: 'Пользователи',
})

const { users } = useMockData()
</script>

<template>
  <div class="space-y-6">
    <UiSectionCard title="Пользователи и роли" subtitle="Учет ролей, команд и уровня доступа.">
      <div class="block-radius overflow-hidden border border-ink-200">
        <table class="min-w-full bg-white text-sm">
          <thead class="bg-ink-50 text-left text-xs uppercase tracking-[0.2em] text-ink-400">
            <tr>
              <th class="px-4 py-3">Пользователь</th>
              <th class="px-4 py-3">Роль</th>
              <th class="px-4 py-3">Команда</th>
              <th class="px-4 py-3">Статус</th>
              <th class="px-4 py-3">Доступ</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-ink-100 text-ink-600">
            <tr v-for="user in users" :key="user.name">
              <td class="px-4 py-4 font-medium text-ink-900">{{ user.name }}</td>
              <td class="px-4 py-4">{{ user.role }}</td>
              <td class="px-4 py-4">{{ user.team }}</td>
              <td class="px-4 py-4">{{ user.status }}</td>
              <td class="px-4 py-4">{{ user.access }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </UiSectionCard>

    <UiSectionCard title="Нет доступа" subtitle="Состояние для недостаточных прав.">
      <div class="block-radius border border-amber-200 bg-amber-100/60 p-5">
        <p class="font-semibold text-amber-500">Недостаточно прав для редактирования системных шаблонов OKR.</p>
        <p class="mt-2 text-sm text-ink-600">Пользователь может просматривать раздел, но изменение доступно только администраторам.</p>
      </div>
    </UiSectionCard>
  </div>
</template>
