export interface RoleItem {
  id: number
  name: string
  code: string
  description: string
}

export interface TeamItem {
  id: number
  name: string
  code: string
  description: string
  membersCount: number
}

export interface UserItem {
  id: number
  email: string
  firstName: string
  lastName: string
  role: string
  primaryTeam: string
  teams: number[]
  isActive: boolean
  isStaff: boolean
}

interface RoleResponse {
  id: number
  name: string
  code: string
  description: string
}

interface RolePayload {
  name: string
  code: string
  description: string
}

interface TeamResponse {
  id: number
  name: string
  code: string
  description: string
  members_count: number
}

interface TeamPayload {
  name: string
  code: string
  description: string
}

interface UserResponse {
  id: number
  email: string
  first_name: string
  last_name: string
  role: string
  primary_team: string
  teams: number[]
  is_active: boolean
  is_staff: boolean
}

interface UserPayload {
  email: string
  first_name: string
  last_name: string
  role_id: number | null
  primary_team_id: number | null
  team_ids: number[]
  is_active: boolean
  is_staff: boolean
  password: string
}

const transformRole = (item: RoleResponse): RoleItem => ({
  id: item.id,
  name: item.name,
  code: item.code,
  description: item.description,
})

const transformTeam = (item: TeamResponse): TeamItem => ({
  id: item.id,
  name: item.name,
  code: item.code,
  description: item.description,
  membersCount: item.members_count,
})

const transformUser = (item: UserResponse): UserItem => ({
  id: item.id,
  email: item.email,
  firstName: item.first_name,
  lastName: item.last_name,
  role: item.role,
  primaryTeam: item.primary_team,
  teams: item.teams,
  isActive: item.is_active,
  isStaff: item.is_staff,
})

export const useCoreApi = () => {
  const auth = useAuth()

  const fetchRoles = async (): Promise<RoleItem[]> => {
    const roles = await auth.apiFetch<RoleResponse[]>('/core/roles/', { method: 'GET' })
    return roles.map(transformRole)
  }

  const createRole = async (payload: RolePayload): Promise<RoleItem> => {
    const role = await auth.apiFetch<RoleResponse>('/core/roles/', { method: 'POST', body: payload })
    return transformRole(role)
  }

  const updateRole = async (roleId: number, payload: RolePayload): Promise<RoleItem> => {
    const role = await auth.apiFetch<RoleResponse>(`/core/roles/${roleId}/`, { method: 'PATCH', body: payload })
    return transformRole(role)
  }

  const fetchTeams = async (): Promise<TeamItem[]> => {
    const teams = await auth.apiFetch<TeamResponse[]>('/core/teams/', { method: 'GET' })
    return teams.map(transformTeam)
  }

  const createTeam = async (payload: TeamPayload): Promise<TeamItem> => {
    const team = await auth.apiFetch<TeamResponse>('/core/teams/', { method: 'POST', body: payload })
    return transformTeam(team)
  }

  const updateTeam = async (teamId: number, payload: TeamPayload): Promise<TeamItem> => {
    const team = await auth.apiFetch<TeamResponse>(`/core/teams/${teamId}/`, { method: 'PATCH', body: payload })
    return transformTeam(team)
  }

  const fetchUsers = async (): Promise<UserItem[]> => {
    const users = await auth.apiFetch<UserResponse[]>('/core/users/', { method: 'GET' })
    return users.map(transformUser)
  }

  const createUser = async (payload: UserPayload): Promise<UserItem> => {
    const user = await auth.apiFetch<UserResponse>('/core/users/', { method: 'POST', body: payload })
    return transformUser(user)
  }

  const updateUser = async (userId: number, payload: UserPayload): Promise<UserItem> => {
    const user = await auth.apiFetch<UserResponse>(`/core/users/${userId}/`, { method: 'PATCH', body: payload })
    return transformUser(user)
  }

  return {
    fetchRoles,
    createRole,
    updateRole,
    fetchTeams,
    createTeam,
    updateTeam,
    fetchUsers,
    createUser,
    updateUser,
  }
}
