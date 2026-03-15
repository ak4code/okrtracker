import { formatDateOnly, formatDateTimeFull } from '~/composables/useDateFormat'

export type OkrStatus =
  | 'draft'
  | 'on track'
  | 'at risk'
  | 'completed'

export interface QuarterItem {
  id: number
  name: string
  year: number
  quarter: number
  startDate: string
  startDateRaw: string
  endDate: string
  endDateRaw: string
  isActive: boolean
}

export interface CheckInItem {
  id: string
  author: string
  date: string
  dateRaw: string
  value: number
  note: string
  keyResultId?: string
  keyResultTitle?: string
  metricType?: 'number' | 'percent' | 'currency' | 'boolean'
  unit?: string
}

export interface KeyResultItem {
  id: string
  title: string
  description: string
  value: number
  owner: string
  metricType: 'number' | 'percent' | 'currency' | 'boolean'
  start: number
  current: number
  target: number
  unit: string
  status: OkrStatus
  progress: number
  lastCheckIn: string
  lastCheckInRaw?: string
  history: CheckInItem[]
}

export interface CommentItem {
  id: string
  author: string
  text: string
  createdAt: string
  createdAtRaw: string
}

export interface ChangeLogItem {
  id: string
  entityType: string
  entityLabel: string
  entityName: string
  action: string
  author: string
  details: string[]
  createdAt: string
  createdAtRaw: string
}

export interface OkrItem {
  id: string
  title: string
  description: string
  ownerId: number
  owner: string
  ownerRole: string
  teamId: number
  team: string
  periodId: number
  quarter: string
  status: OkrStatus
  progress: number
  priority: 'Low' | 'Medium' | 'High'
  risks: string[]
  keyResults: KeyResultItem[]
  keyResultsCount: number
  completedKeyResultsCount: number
  comments: number
  commentsList: CommentItem[]
  changeLogs: ChangeLogItem[]
  updatedAt: string
  updatedAtRaw: string
}

export interface OkrCreateKeyResultPayload {
  title: string
  description: string
  metric_type: 'number' | 'percent' | 'currency' | 'boolean'
  start_value: string
  current_value: string
  target_value: string
  status: 'draft' | 'on_track' | 'at_risk' | 'completed'
}

export interface OkrCreatePayload {
  title: string
  description: string
  owner_id: number
  team_id: number
  period_id: number
  status: 'draft' | 'on_track' | 'at_risk' | 'completed'
  key_results: OkrCreateKeyResultPayload[]
}

export interface OkrUpdatePayload {
  title: string
  description: string
  owner_id: number
  team_id: number
  period_id: number
  status: 'draft' | 'on_track' | 'at_risk' | 'completed'
}

export interface KeyResultUpdatePayload {
  title: string
  description: string
  value: string
  metric_type: 'number' | 'percent' | 'currency' | 'boolean'
  start_value: string
  current_value: string
  target_value: string
  status: 'draft' | 'on_track' | 'at_risk' | 'completed'
}

export interface KeyResultCreatePayload {
  title: string
  description: string
  metric_type: 'number' | 'percent' | 'currency' | 'boolean'
  start_value: string
  current_value: string
  target_value: string
  status: 'draft' | 'on_track' | 'at_risk' | 'completed'
}

export interface CheckInCreatePayload {
  new_value: string
  comment: string
}

export interface CheckInUpdatePayload {
  new_value: string
  comment: string
}

export interface CommentCreatePayload {
  text: string
}

interface QuarterResponse {
  id: number
  name: string
  year: number
  quarter: number
  start_date: string
  end_date: string
  is_active: boolean
}

interface QuarterCreatePayload {
  year: number
  quarter: number
  start_date: string
  end_date: string
  is_active: boolean
}

interface OkrListResponse {
  id: number
  title: string
  description: string
  owner: string
  team: string
  quarter: string
  status: string
  progress: string
  updated_at: string
  key_results_count: number
  completed_key_results_count: number
  comments_count: number
}

interface CheckInResponse {
  id: number
  author: string
  date: string
  value: string
  note: string
}

interface KeyResultResponse {
  id: number
  title: string
  description: string
  value: string
  owner: string
  metric_type: 'number' | 'percent' | 'currency' | 'boolean'
  start: string
  current: string
  target: string
  unit: string
  status: string
  progress: string
  last_check_in: string | null
  history: CheckInResponse[]
}

interface CommentResponse {
  id: number
  author: string
  text: string
  created_at: string
  updated_at: string
}

interface ChangeLogResponse {
  id: number
  entity_type: string
  entity_id: number
  entity_label: string
  entity_name: string
  action: string
  author: string
  payload: Record<string, unknown>
  details: string[]
  created_at: string
}

interface OkrDetailResponse {
  id: number
  title: string
  description: string
  owner_id: number
  owner: string
  team_id: number
  team: string
  period_id: number
  quarter: string
  status: string
  progress: string
  updated_at: string
  key_results: KeyResultResponse[]
  comments: CommentResponse[]
  change_logs: ChangeLogResponse[]
}

const statusMap: Record<string, OkrStatus> = {
  draft: 'draft',
  on_track: 'on track',
  at_risk: 'at risk',
  completed: 'completed',
}

const actionLabelMap: Record<string, string> = {
  created: 'Создание',
  updated: 'Изменение',
  deleted: 'Удаление',
}

const normalizeStatus = (status: string): OkrStatus => statusMap[status] || 'draft'
const toNumber = (value: string | number) => Number(value)

const transformCheckIn = (item: CheckInResponse): CheckInItem => ({
  id: String(item.id),
  author: item.author,
  date: formatDateTimeFull(item.date),
  dateRaw: item.date,
  value: toNumber(item.value),
  note: item.note,
})

const transformKeyResult = (item: KeyResultResponse): KeyResultItem => ({
  id: String(item.id),
  title: item.title,
  description: item.description,
  value: toNumber(item.value),
  owner: item.owner,
  metricType: item.metric_type,
  start: toNumber(item.start),
  current: toNumber(item.current),
  target: toNumber(item.target),
  unit: item.unit,
  status: normalizeStatus(item.status),
  progress: toNumber(item.progress),
  lastCheckIn: item.last_check_in ? formatDateTimeFull(item.last_check_in) : 'Нет обновлений',
  lastCheckInRaw: item.last_check_in || undefined,
  history: item.history.map(transformCheckIn),
})

const createBaseOkr = (item: OkrListResponse | OkrDetailResponse) => ({
  id: String(item.id),
  title: item.title,
  description: item.description,
  ownerId: 'owner_id' in item ? item.owner_id : 0,
  owner: item.owner,
  ownerRole: '',
  teamId: 'team_id' in item ? item.team_id : 0,
  team: item.team,
  periodId: 'period_id' in item ? item.period_id : 0,
  quarter: item.quarter,
  status: normalizeStatus(item.status),
  progress: toNumber(item.progress),
  priority: 'Medium' as const,
  risks: [],
  updatedAt: formatDateTimeFull(item.updated_at),
  updatedAtRaw: item.updated_at,
})

const transformQuarter = (item: QuarterResponse): QuarterItem => ({
  id: item.id,
  name: item.name,
  year: item.year,
  quarter: item.quarter,
  startDate: formatDateOnly(item.start_date),
  startDateRaw: item.start_date,
  endDate: formatDateOnly(item.end_date),
  endDateRaw: item.end_date,
  isActive: item.is_active,
})

const transformOkrDetail = (item: OkrDetailResponse): OkrItem => ({
  ...createBaseOkr(item),
  keyResults: item.key_results.map(transformKeyResult),
  keyResultsCount: item.key_results.length,
  completedKeyResultsCount: item.key_results.filter((keyResult) => keyResult.status === 'completed').length,
  comments: item.comments.length,
  commentsList: item.comments.map((comment) => ({
    id: String(comment.id),
    author: comment.author,
    text: comment.text,
    createdAt: formatDateTimeFull(comment.created_at),
    createdAtRaw: comment.created_at,
  })),
  changeLogs: item.change_logs.map((log) => ({
    id: String(log.id),
    entityType: log.entity_type,
    entityLabel: log.entity_label,
    entityName: log.entity_name,
    action: actionLabelMap[log.action] || log.action,
    author: log.author,
    details: log.details || [],
    createdAt: formatDateTimeFull(log.created_at),
    createdAtRaw: log.created_at,
  })),
})

export const useOkrApi = () => {
  const auth = useAuth()

  const fetchQuarters = async (): Promise<QuarterItem[]> => {
    const quarters = await auth.apiFetch<QuarterResponse[]>('/okr/quarters/', {
      method: 'GET',
    })

    return quarters.map(transformQuarter)
  }

  const createQuarter = async (payload: QuarterCreatePayload): Promise<QuarterItem> => {
    const item = await auth.apiFetch<QuarterResponse>('/okr/quarters/', {
      method: 'POST',
      body: payload,
    })

    return transformQuarter(item)
  }

  const updateQuarter = async (
    quarterId: number,
    payload: QuarterCreatePayload,
  ): Promise<QuarterItem> => {
    const item = await auth.apiFetch<QuarterResponse>(`/okr/quarters/${quarterId}/`, {
      method: 'PATCH',
      body: payload,
    })

    return transformQuarter(item)
  }

  const fetchOkrs = async (params: { quarter?: string } = {}): Promise<OkrItem[]> => {
    const searchParams = new URLSearchParams()
    if (params.quarter) {
      searchParams.set('quarter', params.quarter)
    }

    const suffix = searchParams.toString() ? `?${searchParams.toString()}` : ''
    const okrs = await auth.apiFetch<OkrListResponse[]>(`/okr/okrs/${suffix}`, {
      method: 'GET',
    })

    return okrs.map((item) => ({
      ...createBaseOkr(item),
      keyResults: [],
      keyResultsCount: item.key_results_count,
      completedKeyResultsCount: item.completed_key_results_count,
      comments: item.comments_count,
      commentsList: [],
      changeLogs: [],
    }))
  }

  const fetchOkr = async (id: string | number): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/okrs/${id}/`, {
      method: 'GET',
    })

    return transformOkrDetail(item)
  }

  const createOkr = async (payload: OkrCreatePayload): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>('/okr/okrs/', {
      method: 'POST',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  const updateOkr = async (id: string | number, payload: OkrUpdatePayload): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/okrs/${id}/`, {
      method: 'PATCH',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  const createKeyResult = async (
    okrId: string | number,
    payload: KeyResultCreatePayload,
  ): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/okrs/${okrId}/key-results/`, {
      method: 'POST',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  const updateKeyResult = async (id: string | number, payload: KeyResultUpdatePayload): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/key-results/${id}/`, {
      method: 'PATCH',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  const createCheckIn = async (keyResultId: string | number, payload: CheckInCreatePayload): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/key-results/${keyResultId}/check-ins/`, {
      method: 'POST',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  const updateCheckIn = async (checkInId: string | number, payload: CheckInUpdatePayload): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/check-ins/${checkInId}/`, {
      method: 'PATCH',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  const deleteCheckIn = async (checkInId: string | number): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/check-ins/${checkInId}/`, {
      method: 'DELETE',
    })

    return transformOkrDetail(item)
  }

  const createComment = async (okrId: string | number, payload: CommentCreatePayload): Promise<OkrItem> => {
    const item = await auth.apiFetch<OkrDetailResponse>(`/okr/okrs/${okrId}/comments/`, {
      method: 'POST',
      body: payload,
    })

    return transformOkrDetail(item)
  }

  return {
    createComment,
    createCheckIn,
    createKeyResult,
    createOkr,
    deleteCheckIn,
    fetchOkr,
    fetchOkrs,
    fetchQuarters,
    updateCheckIn,
    updateKeyResult,
    updateOkr,
    createQuarter,
    updateQuarter,
  }
}
