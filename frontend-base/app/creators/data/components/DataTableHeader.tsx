import { Search, Download, RefreshCw, Loader2, Bot, Trash2, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface DataTableHeaderProps {
  dataLength: number
  filteredLength: number
  updatedAt: string | null
  loading: boolean
  loadingStoredData: boolean
  searchTerm: string
  selectedRowsCount: number
  agentMode: boolean
  deleting: boolean
  sendingDM: boolean
  onSearchChange: (value: string) => void
  onCrawlClick: () => void
  onAgentModeToggle: () => void
  onExport: () => void
  onSendDM: () => void
  onDeleteSelected: () => void
  formatUpdatedAt: (value?: string | null) => string
}

export function DataTableHeader({
  dataLength,
  filteredLength,
  updatedAt,
  loading,
  loadingStoredData,
  searchTerm,
  selectedRowsCount,
  agentMode,
  deleting,
  sendingDM,
  onSearchChange,
  onCrawlClick,
  onAgentModeToggle,
  onExport,
  onSendDM,
  onDeleteSelected,
  formatUpdatedAt,
}: DataTableHeaderProps) {
  return (
    <div className="px-8 py-6 border-b border-border">
      <div className="flex items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Dữ liệu creator</h2>
          <p className="text-muted-foreground text-sm mt-1">
            {loadingStoredData
              ? 'Đang tải dữ liệu đã lưu...'
              : dataLength > 0
                ? `Đang hiển thị ${filteredLength} / ${dataLength} KOL đã lưu`
                : 'Nhấn "Crawl dữ liệu" để bắt đầu'}
          </p>
          {updatedAt && (
            <p className="text-xs text-muted-foreground mt-1">
              Cập nhật gần nhất: {formatUpdatedAt(updatedAt)}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={onCrawlClick}
            disabled={loading}
            className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground border-0 font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Đang crawl...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                Crawl dữ liệu
              </>
            )}
          </Button>
          <Button
            size="sm"
            onClick={onAgentModeToggle}
            variant={agentMode ? 'default' : 'outline'}
            className="gap-2 font-medium"
          >
            <Bot className="w-4 h-4" />
            {agentMode ? 'Tắt Agent' : 'Agent Mode'}
          </Button>
          <Button
            size="sm"
            onClick={onExport}
            disabled={dataLength === 0}
            variant="outline"
            className="gap-2 font-medium"
          >
            <Download className="w-4 h-4" />
            Xuất CSV
          </Button>
          {selectedRowsCount > 0 && (
            <>
              <Button
                size="sm"
                onClick={onSendDM}
                disabled={sendingDM}
                variant="default"
                className="gap-2 font-medium"
              >
                {sendingDM ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Đang gửi...
                  </>
                ) : (
                  <>
                    <MessageSquare className="w-4 h-4" />
                    Gửi tin nhắn ({selectedRowsCount})
                  </>
                )}
              </Button>
              <Button
                size="sm"
                onClick={onDeleteSelected}
                disabled={deleting}
                variant="destructive"
                className="gap-2 font-medium"
              >
                {deleting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Đang xóa...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    Xóa đã chọn ({selectedRowsCount})
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center gap-3 bg-card px-4 py-2 rounded-lg border border-border hover:border-border/70 transition-colors">
        <Search className="w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Tìm kiếm theo tên..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground text-sm"
        />
      </div>
    </div>
  )
}
