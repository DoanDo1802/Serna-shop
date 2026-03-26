import { DashboardShell } from '@/components/dashboard-shell'
import { PagePlaceholder } from '@/components/page-placeholder'

export default function CreatorsPage() {
  return (
    <DashboardShell>
      <PagePlaceholder
        title="Nhà sáng tạo"
        description="Hãy chọn mục Dữ liệu trong sidebar để xem danh sách creator."
      />
    </DashboardShell>
  )
}