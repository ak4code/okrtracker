<script setup lang="ts">
import type { OkrItem } from '~/composables/useOkrApi'
import { formatOkrProgressScaleValue } from '~/composables/useProgressDisplay'

defineProps<{
  items: OkrItem[]
}>()
</script>

<template>
  <div class="block-radius overflow-hidden border border-ink-200">
    <div class="overflow-x-auto">
      <table class="min-w-full bg-white">
        <thead class="bg-ink-50 text-left text-xs uppercase tracking-[0.2em] text-ink-400">
          <tr>
            <th class="px-4 py-3 font-medium">Цель</th>
            <th class="px-4 py-3 font-medium">Владелец</th>
            <th class="px-4 py-3 font-medium">Команда</th>
            <th class="px-4 py-3 font-medium">Квартал</th>
            <th class="px-4 py-3 font-medium">Статус</th>
            <th class="px-4 py-3 font-medium">Прогресс</th>
            <th class="px-4 py-3 font-medium">Обновлено</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-ink-100 text-sm text-ink-600">
          <tr v-for="okr in items" :key="okr.id" class="hover:bg-ink-50/60">
            <td class="px-4 py-4">
              <NuxtLink :to="`/okrs/${okr.id}`" class="font-semibold text-ink-900 hover:text-sky-500">
                {{ okr.title }}
              </NuxtLink>
              <p class="mt-1 text-xs text-ink-400 line-clamp-1">{{ okr.description }}</p>
            </td>
            <td class="px-4 py-4">{{ okr.owner }}</td>
            <td class="px-4 py-4">{{ okr.team }}</td>
            <td class="px-4 py-4">{{ okr.quarter }}</td>
            <td class="px-4 py-4"><UiStatusBadge :status="okr.status" size="sm" /></td>
            <td class="px-4 py-4">
              <div class="min-w-28 space-y-2">
                <div class="flex items-center justify-between gap-3 text-xs text-ink-500">
                  <span>{{ formatOkrProgressScaleValue(okr.progress) }}</span>
                </div>
                <UiProgressBar :value="okr.progress" :scale-value="okr.progress" :show-value="false" compact />
              </div>
            </td>
            <td class="px-4 py-4">{{ okr.updatedAt }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
