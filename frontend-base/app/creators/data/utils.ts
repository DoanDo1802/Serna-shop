import type { KalodataCreator } from '@/lib/api'
import type { DataRow } from './types'

export function getDefaultDateRange() {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  const startDate = new Date(today)
  startDate.setDate(today.getDate() - 30)

  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: yesterday.toISOString().split('T')[0],
  }
}

export function mapRows(rows: KalodataCreator[]): DataRow[] {
  return rows.map((row, index) => ({
    ...row,
    id: `${index + 1}`,
  }))
}

export function formatUpdatedAt(value?: string | null) {
  if (!value) return ''

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date)
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    notation: 'compact',
  }).format(value)
}
