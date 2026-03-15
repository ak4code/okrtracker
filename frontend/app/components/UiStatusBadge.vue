<script setup lang="ts">
import { AlertCircle, Archive, CheckCircle2, FileText, TrendingUp, XCircle } from 'lucide-vue-next'
import { getOkrStatusLabel } from '~/composables/useStatusDisplay'

type UiStatus = 'draft' | 'on track' | 'at risk' | 'completed' | 'active' | 'off track' | 'archived'

const props = defineProps<{
  status: UiStatus
  size?: 'sm' | 'md'
}>()

const config = computed(() => {
  const map: Record<UiStatus, { label: string, className: string, icon: unknown }> = {
    draft: { label: getOkrStatusLabel('draft'), className: 'bg-ink-100 text-ink-600', icon: FileText },
    active: { label: getOkrStatusLabel('active'), className: 'bg-sky-100 text-sky-500', icon: TrendingUp },
    'on track': { label: getOkrStatusLabel('on track'), className: 'bg-mint-100 text-mint-500', icon: CheckCircle2 },
    'at risk': { label: getOkrStatusLabel('at risk'), className: 'bg-amber-100 text-amber-500', icon: AlertCircle },
    'off track': { label: getOkrStatusLabel('off track'), className: 'bg-rose-100 text-rose-500', icon: XCircle },
    completed: { label: getOkrStatusLabel('completed'), className: 'bg-mint-100 text-mint-500', icon: CheckCircle2 },
    archived: { label: getOkrStatusLabel('archived'), className: 'bg-ink-100 text-ink-500', icon: Archive },
  }

  return map[props.status]
})
</script>

<template>
  <span
    class="inline-flex items-center rounded-full font-medium"
    :class="[config.className, size === 'sm' ? 'gap-1 px-2 py-0.5 text-xs' : 'gap-1.5 px-2.5 py-1 text-sm']"
  >
    <component :is="config.icon" :class="size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5'" />
    {{ config.label }}
  </span>
</template>
