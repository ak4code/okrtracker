<script setup lang="ts">
const props = defineProps<{
  value: number
  compact?: boolean
  showValue?: boolean
  scaleValue?: number
}>()

const clamped = computed(() => Math.max(0, Math.min(props.value, 1)))
const widthPercent = computed(() => clamped.value * 100)
const displayValue = computed(() => `${Math.round(clamped.value * 100)}%`)
const barClass = computed(() => {
  const effectiveScaleValue = typeof props.scaleValue === 'number' ? props.scaleValue : props.value

  if (effectiveScaleValue >= 1) {
    return 'bg-mint-500'
  }

  if (effectiveScaleValue >= 0.7) {
    return 'bg-amber-500'
  }

  if (effectiveScaleValue >= 0.3) {
    return 'bg-sky-500'
  }

  return 'bg-ink-400'
})
</script>

<template>
  <div :class="compact ? 'space-y-2' : 'space-y-3'">
    <div :class="compact ? 'h-1.5' : 'h-2'" class="rounded-full bg-ink-100 overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-300"
        :class="barClass"
        :style="{ width: `${widthPercent}%` }"
      />
    </div>
    <p v-if="showValue !== false" class="text-xs text-ink-500">{{ displayValue }}</p>
  </div>
</template>
