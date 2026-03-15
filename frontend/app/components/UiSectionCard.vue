<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <section class="surface min-w-0 overflow-hidden p-6">
    <div class="mb-4 flex items-start justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold text-ink-900">{{ title }}</h2>
        <p v-if="subtitle" class="mt-1 text-sm text-ink-500">{{ subtitle }}</p>
      </div>
      <slot name="action" />
    </div>

    <slot />
  </section>
</template>
