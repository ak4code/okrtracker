<script setup lang="ts">
import type { OkrItem } from '~/composables/useOkrApi'
import { formatOkrProgressScaleValue } from '~/composables/useProgressDisplay'

defineProps<{
  okr: OkrItem
}>()
</script>

<template>
  <NuxtLink
    :to="`/okrs/${okr.id}`"
    class="block block-radius border border-ink-200 bg-white p-4 transition-all hover:border-ink-300 hover:shadow-sm"
  >
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <p class="text-xs text-ink-400">{{ okr.quarter }}</p>
        <h3 class="mt-1 text-sm font-medium text-ink-900">{{ okr.title }}</h3>
      </div>
      <UiStatusBadge :status="okr.status" size="sm" />
    </div>

    <div class="mt-2 text-xs text-ink-500">
      {{ okr.owner }} · {{ okr.team }}
    </div>

    <div class="mt-3">
      <UiProgressBar :value="okr.progress" :scale-value="okr.progress" compact />
    </div>

    <div class="mt-2 flex items-center justify-between text-xs text-ink-500">
      <span>{{ okr.keyResultsCount }} ключевых результатов</span>
      <span>{{ formatOkrProgressScaleValue(okr.progress) }}</span>
    </div>
  </NuxtLink>
</template>
