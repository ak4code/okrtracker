<script setup lang="ts">
definePageMeta({
  title: 'OKR команд',
})

import { formatOkrProgressScaleValue } from '~/composables/useProgressDisplay'

const { teams, okrs } = useMockData()
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <article v-for="team in teams" :key="team.name" class="surface p-5">
        <p class="text-sm text-ink-500">{{ team.name }}</p>
        <p class="mt-3 font-display text-4xl font-semibold text-ink-900">{{ formatOkrProgressScaleValue(team.progress) }}</p>
        <div class="mt-3">
          <UiProgressBar :value="team.progress" :scale-value="team.progress" compact />
        </div>
        <p class="mt-2 text-sm text-ink-500">At risk: {{ team.atRisk }} · Overdue: {{ team.overdue }}</p>
      </article>
    </section>

    <UiSectionCard title="OKR команды" subtitle="Квартальный обзор по нескольким командам с проблемными зонами.">
      <div class="grid gap-4 xl:grid-cols-2">
        <OkrSummaryCard v-for="okr in okrs" :key="okr.id" :okr="okr" />
      </div>
    </UiSectionCard>
  </div>
</template>
