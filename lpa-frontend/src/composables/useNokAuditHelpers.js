import { computed } from 'vue'

export function useNokAuditHelpers() {
    const formatDate = (dateString) => {
        if (!dateString) return '-'
        const date = new Date(dateString)
        return date.toLocaleDateString('cs-CZ')
    }

    const formatDateTime = (dateString) => {
        if (!dateString) return '-'
        const date = new Date(dateString)
        return date.toLocaleString('cs-CZ')
    }

    const getStatusText = (status) => {
        const statusMap = {
            open: 'Otevřené',
            assigned: 'Přiřazené',
            in_progress: 'V řešení',
            resolved: 'Vyřešené',
            closed: 'Uzavřené',
        }
        return statusMap[status] || status
    }

    const getStatusBadgeClass = (status) => {
        const classMap = {
            open: 'bg-red-100 text-red-800',
            assigned: 'bg-orange-100 text-orange-800',
            in_progress: 'bg-blue-100 text-blue-800',
            resolved: 'bg-green-100 text-green-800',
            closed: 'bg-gray-100 text-gray-800',
        }
        return classMap[status] || 'bg-gray-100 text-gray-800'
    }

    const isOverdue = (termin, status) => {
        if (!termin || status === 'resolved' || status === 'closed') return false
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        const deadline = new Date(termin)
        return deadline < today
    }

    const getOverdueClass = (termin, status) => {
        return isOverdue(termin, status) ? 'bg-red-50 border-l-4 border-red-500' : ''
    }

    const truncate = (text, length = 60) => {
        if (!text) return ''
        return text.length > length ? text.substring(0, length) + '...' : text
    }

    const getImageUrl = (path) => {
        if (!path) return ''
        const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
        return `${baseUrl}/${path}`
    }

    const exportToCSV = (data, filename = 'export.csv') => {
        if (!data || data.length === 0) {
            console.warn('No data to export')
            return
        }

        const headers = Object.keys(data[0])
        const csvContent = [
            headers.join(';'),
            ...data.map(row =>
                headers.map(header => `"${row[header] || ''}"`).join(';')
            )
        ].join('\n')

        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', filename)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    return {
        formatDate,
        formatDateTime,
        getStatusText,
        getStatusBadgeClass,
        isOverdue,
        getOverdueClass,
        truncate,
        getImageUrl,
        exportToCSV,
    }
}