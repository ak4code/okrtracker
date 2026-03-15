<script setup lang="ts">
import { Pencil, Trash2 } from 'lucide-vue-next'
import type { CheckInItem } from '~/composables/useOkrApi'

defineProps<{
  history: CheckInItem[]
}>()

const emit = defineEmits<{
  edit: [item: CheckInItem]
  delete: [item: CheckInItem]
}>()
</script>

<template>
  <div class="space-y-2.5">
    <div
      v-for="item in history"
      :key="item.id"
      class="block-radius border border-ink-200 bg-white px-3 py-3"
    >
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
            <p class="text-sm font-medium text-ink-900">{{ item.author }}</p>
            <p class="text-xs text-ink-400">{{ item.date }}</p>
          </div>
          <p
            v-if="item.keyResultTitle"
            class="mt-1 text-[11px] uppercase tracking-[0.14em] text-ink-400"
          >
            {{ item.keyResultTitle }}
          </p>
        </div>
        <div class="flex items-center gap-1.5">
          <div class="rounded-full bg-sky-100 px-2.5 py-1 text-xs font-medium text-sky-500">{{ item.value }}</div>
          <button class="btn btn-secondary btn-sm !min-h-8 px-2.5" @click="emit('edit', item)">
            <Pencil class="h-3.5 w-3.5" />
          </button>
          <button class="btn btn-danger btn-sm !min-h-8 px-2.5" @click="emit('delete', item)">
            <Trash2 class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
      <p v-if="item.note" class="mt-2 text-sm leading-5 text-ink-600">{{ item.note }}</p>
    </div>
  </div>
</template>
