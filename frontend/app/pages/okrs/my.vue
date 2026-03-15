<script setup lang="ts">
definePageMeta({
  title: 'Мои OKR',
})

const { okrs } = useMockData()
</script>

<template>
  <div class="grid gap-6 xl:grid-cols-2">
    <OkrSummaryCard v-for="okr in okrs.slice(0, 2)" :key="okr.id" :okr="okr" />
    <UiSectionCard title="Пустое состояние" subtitle="Если у сотрудника еще нет назначенных целей.">
      <UiEmptyState title="У вас пока нет OKR" description="Создайте первую цель или запросите привязку к команде у администратора." />
    </UiSectionCard>
  </div>
</template>
