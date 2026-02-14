import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api'

export const useNokAuditsStore = defineStore('nokAudits', () => {
    // State
    const audits = ref([])
    const lines = ref([])
    const categories = ref([])
    const solvers = ref([])
    const loading = ref(false)
    const error = ref(null)

    // Computed - Statistiky
    const stats = computed(() => {
        const today = new Date()
        today.setHours(0, 0, 0, 0)

        return {
            total: audits.value.length,
            open: audits.value.filter(a => a.neshoda_status === 'open').length,
            assigned: audits.value.filter(a => a.neshoda_status === 'assigned').length,
            inProgress: audits.value.filter(a => a.neshoda_status === 'in_progress').length,
            resolved: audits.value.filter(a => a.neshoda_status === 'resolved').length,
            closed: audits.value.filter(a => a.neshoda_status === 'closed').length,
            overdue: audits.value.filter(a => {
                if (!a.termin || a.neshoda_status === 'resolved' || a.neshoda_status === 'closed') {
                    return false
                }
                const termin = new Date(a.termin)
                return termin < today
            }).length,
        }
    })

    // Computed - Skupiny podle linky
    const auditsByLine = computed(() => {
        const grouped = {}
        audits.value.forEach(audit => {
            if (!grouped[audit.line_name]) {
                grouped[audit.line_name] = []
            }
            grouped[audit.line_name].push(audit)
        })
        return grouped
    })

    // Computed - Skupiny podle kategorie
    const auditsByCategory = computed(() => {
        const grouped = {}
        audits.value.forEach(audit => {
            if (!grouped[audit.category_name]) {
                grouped[audit.category_name] = []
            }
            grouped[audit.category_name].push(audit)
        })
        return grouped
    })

    // Actions
    async function fetchAudits(filters = {}) {
        loading.value = true
        error.value = null

        try {
            const params = {}
            if (filters.line_id) params.line_id = filters.line_id
            if (filters.category_id) params.category_id = filters.category_id
            if (filters.date_from) params.date_from = filters.date_from
            if (filters.date_to) params.date_to = filters.date_to

            const { data } = await api.get('/answers/nok-list', { params })
            audits.value = data
        } catch (err) {
            error.value = err.message
            console.error('Error fetching NOK audits:', err)
        } finally {
            loading.value = false
        }
    }

    async function fetchLines() {
        try {
            const { data } = await api.get('/lines/')
            lines.value = data
        } catch (err) {
            console.error('Error fetching lines:', err)
        }
    }

    async function fetchCategories() {
        try {
            const { data } = await api.get('/checklist/categories')
            categories.value = data
        } catch (err) {
            console.error('Error fetching categories:', err)
        }
    }

    async function fetchSolvers() {
        try {
            const { data } = await api.get('/neshody/solvers')
            solvers.value = data
        } catch (err) {
            console.error('Error fetching solvers:', err)
        }
    }

    async function assignSolver(neshodaId, solverData) {
        try {
            await api.post(`/neshody/${neshodaId}/assign-solver`, solverData)
            // Reload audits after assignment
            await fetchAudits()
            return { success: true }
        } catch (err) {
            console.error('Error assigning solver:', err)
            return { success: false, error: err.message }
        }
    }

    async function initialize() {
        await Promise.all([
            fetchAudits(),
            fetchLines(),
            fetchCategories(),
            fetchSolvers(),
        ])
    }

    function getAuditById(id) {
        return audits.value.find(a => a.id === id)
    }

    function getSolverName(solverId) {
        const solver = solvers.value.find(s => s.id === solverId)
        return solver ? solver.jmeno : 'Neznámý'
    }

    return {
        // State
        audits,
        lines,
        categories,
        solvers,
        loading,
        error,

        // Computed
        stats,
        auditsByLine,
        auditsByCategory,

        // Actions
        fetchAudits,
        fetchLines,
        fetchCategories,
        fetchSolvers,
        assignSolver,
        initialize,
        getAuditById,
        getSolverName,
    }
})