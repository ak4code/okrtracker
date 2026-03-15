import type { OkrStatus } from '~/composables/useOkrApi'

export type DisplayStatus = OkrStatus | 'active' | 'off track' | 'archived'

export const getOkrStatusLabel = (status: DisplayStatus) => {
  const map: Record<DisplayStatus, string> = {
    draft: 'Черновик',
    active: 'Активный',
    'on track': 'По плану',
    'at risk': 'Есть риск',
    'off track': 'Отстаёт',
    completed: 'Завершён',
    archived: 'Архив',
  }

  return map[status]
}
