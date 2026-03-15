<script setup lang="ts">
import { AlertTriangle, CheckCircle2, Clock, TrendingUp } from 'lucide-vue-next'

defineProps<{
  label: string
  value: string
  hint: string
  tone: string
}>()

const tones: Record<string, { box: string, icon: unknown }> = {
  sky: { box: 'text-sky-500', icon: TrendingUp },
  mint: { box: 'text-mint-500', icon: CheckCircle2 },
  amber: { box: 'text-amber-500', icon: AlertTriangle },
  rose: { box: 'text-violet-500', icon: Clock },
}
</script>

<template>
  <article class="surface min-w-0 p-6">
    <div class="mb-2 flex items-center justify-between">
      <span class="text-sm text-ink-500">{{ label }}</span>
      <component :is="(tones[tone] || tones.sky).icon" class="h-5 w-5" :class="(tones[tone] || tones.sky).box" />
    </div>
    <p class="text-3xl font-semibold text-ink-900">{{ value }}</p>
    <p class="mt-1 text-xs text-ink-500">{{ hint }}</p>
  </article>
</template>
