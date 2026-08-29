export const getRiskColor = (risk) => {
  const colors = {
    CRITICAL: '#ef4444',
    HIGH: '#f59e0b',
    MEDIUM: '#3b82f6',
    LOW: '#22c55e',
  }
  return colors[risk] || '#64748b'
}

export const getRiskBgColor = (risk) => {
  const colors = {
    CRITICAL: '#fee2e2',
    HIGH: '#fef3c7',
    MEDIUM: '#dbeafe',
    LOW: '#dcfce7',
  }
  return colors[risk] || '#f1f5f9'
}

export const getSIFStatusColor = (status) => {
  const colors = {
    YES: '#22c55e',
    NO: '#3b82f6',
    UNCERTAIN: '#f59e0b',
  }
  return colors[status] || '#64748b'
}

export const getSIFStatusBgColor = (status) => {
  const colors = {
    YES: '#dcfce7',
    NO: '#e0e7ff',
    UNCERTAIN: '#fef3c7',
  }
  return colors[status] || '#f1f5f9'
}

export const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const truncateText = (text, length = 100) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

export const capitalize = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}
