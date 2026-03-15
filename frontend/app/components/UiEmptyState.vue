<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>

<template>
  <div class="block-radius flex min-h-52 flex-col items-center justify-center border border-ink-200 bg-white px-6 py-10 text-center">
    <div class="h-12 w-12 rounded-full bg-ink-100" />
    <h3 class="mt-4 text-lg font-semibold text-ink-900">{{ title }}</h3>
    <p class="mt-2 max-w-sm text-sm text-ink-500">{{ description }}</p>
  </div>
</template>
