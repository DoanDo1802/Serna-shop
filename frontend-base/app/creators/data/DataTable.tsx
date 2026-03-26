'use client'

import { useEffect, useState } from 'react'
import { ChevronUp, ChevronDown, Search, Download, RefreshCw, Loader2, Bot, Send, Sparkles, X, Trash2, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  exportKalodata,
  getSavedKalodata,
  agentSuggestFilters,
  deleteKalodataCreators,
  sendBatchTikTokDM,
  getProducts,
  type KalodataCreator,
  type KalodataExportParams,
  type AgentSuggestResponse,
  type Product,
} from '@/lib/api'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Checkbox } from '@/components/ui/checkbox'
import { useToast } from '@/hooks/use-toast'

interface DataRow {
  id?: string
  period: string
  name: string
  followers: number
  revenue_livestream: number
  revenue_video: number
  kalodata_url: string
  tiktok_url: string
  age_range: string
  gender: string
  engagement_rate: number
}

interface CrawlConfigState {
  start_date: string
  end_date: string
  revenue_min: string
  revenue_max: string
  age_range: string
  page_size: string
  enrich: boolean
  deduplicate: boolean
  // Kalodata advanced filters
  cateIds: string[]
  content_type: string
  revenue_trend: string
  creator_type: string
  followers: string
  engagement_rate: string
  creator_content: string[]
  mcn_status: string
  creator_debut: string
  unit_price: string
  follower_gender: string
}

const AGE_RANGE_OPTIONS = ['18-24', '25-34', '35-44', '45-54', '55+']

const CATEGORY_OPTIONS = [
  { value: '600001', label: 'Đồ gia dụng' },
  { value: '601152', label: 'Trang phục nữ & đồ lót' },
  { value: '601450', label: 'Chăm sóc sắc đẹp & cá nhân' },
  { value: '605248', label: 'Phụ kiện thời trang' },
  { value: '824584', label: 'Hành lý & túi xách' },
]

const REVENUE_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: '<2500000', label: '< 2.5M' },
  { value: '2500000-25000000', label: '2.5M – 25M' },
  { value: '25000000-250000000', label: '25M – 250M' },
  { value: '>250000000', label: '> 250M' },
]

const CONTENT_TYPE_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: 'VIDEO', label: 'Video' },
  { value: 'LIVE', label: 'Livestream' },
]

const CREATOR_TYPE_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: 'BELONGED_TO_SELLER', label: 'Seller operated' },
  { value: 'INDEPENDENT', label: 'Independent' },
]

const FOLLOWERS_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: '<50000', label: '< 50K' },
  { value: '50000-500000', label: '50K – 500K' },
  { value: '500000-1000000', label: '500K – 1M' },
  { value: '>1000000', label: '> 1M' },
]

const ENGAGEMENT_RATE_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: '0-8', label: '0% – 8%' },
  { value: '8-20', label: '8% – 20%' },
  { value: '>20', label: '> 20%' },
]

const CONTACT_OPTIONS = [
  { value: 'EMAIL', label: 'Email' },
  { value: 'ZALO', label: 'Zalo' },
  { value: 'FACEBOOK', label: 'Facebook' },
  { value: 'INSTAGRAM', label: 'Instagram' },
  { value: 'YOUTUBE', label: 'YouTube' },
  { value: 'WHATSAPP', label: 'WhatsApp' },
  { value: 'TWITTER', label: 'Twitter' },
]

const MCN_STATUS_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: 'SIGNED', label: 'Có MCN' },
  { value: 'NOT_SIGNED', label: 'Không có MCN' },
]

const CREATOR_DEBUT_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: '<4', label: 'Trong 3 ngày' },
  { value: '<8', label: 'Trong 7 ngày' },
  { value: '<31', label: 'Trong 30 ngày' },
  { value: '>30', label: 'Quá 30 ngày' },
]

const UNIT_PRICE_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: '<200000', label: '< 200K' },
  { value: '200000-10000000', label: '200K – 10M' },
  { value: '10000000-100000000', label: '10M – 100M' },
  { value: '>100000000', label: '> 100M' },
]

const FOLLOWER_GENDER_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: '1', label: 'Chủ yếu Nam' },
  { value: '2', label: 'Chủ yếu Nữ' },
]

function getDefaultDateRange() {
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

function mapRows(rows: KalodataCreator[]): DataRow[] {
  return rows.map((row, index) => ({
    ...row,
    id: `${index + 1}`,
  }))
}

function formatUpdatedAt(value?: string | null) {
  if (!value) return ''

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(date)
}

export function DataTable() {
  const defaultDateRange = getDefaultDateRange()
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [searchTerm, setSearchTerm] = useState('')
  const [data, setData] = useState<DataRow[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingStoredData, setLoadingStoredData] = useState(true)
  const [configOpen, setConfigOpen] = useState(false)
  const [updatedAt, setUpdatedAt] = useState<string | null>(null)
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set())
  const [deleting, setDeleting] = useState(false)
  const [sendingDM, setSendingDM] = useState(false)
  const [dmDialogOpen, setDmDialogOpen] = useState(false)
  const [dmMessage, setDmMessage] = useState('')
  const [crawlConfig, setCrawlConfig] = useState<CrawlConfigState>({
    start_date: defaultDateRange.start_date,
    end_date: defaultDateRange.end_date,
    revenue_min: '50000000',
    revenue_max: '100000000',
    age_range: '25-34',
    page_size: '20',
    enrich: true,
    deduplicate: true,
    cateIds: [],
    content_type: '',
    revenue_trend: '',
    creator_type: '',
    followers: '',
    engagement_rate: '',
    creator_content: [],
    mcn_status: '',
    creator_debut: '',
    unit_price: '',
    follower_gender: '',
  })
  // Agent mode state
  const [agentMode, setAgentMode] = useState(false)
  const [agentLoading, setAgentLoading] = useState(false)
  const [agentDescription, setAgentDescription] = useState('')
  const [agentPrice, setAgentPrice] = useState('')
  const [agentResult, setAgentResult] = useState<AgentSuggestResponse | null>(null)
  
  // Products for quick select
  const [products, setProducts] = useState<Product[]>([])
  const [loadingProducts, setLoadingProducts] = useState(false)

  // Load products when agent mode opens
  useEffect(() => {
    if (agentMode && products.length === 0) {
      loadProducts()
    }
  }, [agentMode])

  const loadProducts = async () => {
    setLoadingProducts(true)
    try {
      const result = await getProducts()
      if (result.success) {
        setProducts(result.products)
      }
    } catch (error) {
      console.error('Error loading products:', error)
    } finally {
      setLoadingProducts(false)
    }
  }

  const handleSelectProduct = (product: Product) => {
    setAgentDescription(product.description)
    setAgentPrice(product.price.toString())
  }

  const { toast } = useToast()

  useEffect(() => {
    const loadStoredData = async () => {
      try {
        const result = await getSavedKalodata()
        setData(mapRows(result.data ?? []))
        setUpdatedAt(result.updated_at ?? null)
      } catch (error) {
        console.error('Load stored data error:', error)
        toast({
          title: 'Không thể tải dữ liệu đã lưu',
          description: error instanceof Error ? error.message : 'Vui lòng kiểm tra backend.',
          variant: 'destructive',
        })
      } finally {
        setLoadingStoredData(false)
      }
    }

    void loadStoredData()
  }, [toast])

  const updateConfig = <K extends keyof CrawlConfigState>(key: K, value: CrawlConfigState[K]) => {
    setCrawlConfig((current) => ({
      ...current,
      [key]: value,
    }))
  }

  const handleCrawlData = async () => {
    const pageSize = Number(crawlConfig.page_size)
    const revenueMin = Number(crawlConfig.revenue_min)
    const revenueMax = Number(crawlConfig.revenue_max)

    if (!Number.isFinite(pageSize) || pageSize < 5) {
      toast({
        title: 'Cấu hình chưa hợp lệ',
        description: 'Số lượng tải về tối thiểu là 5.',
        variant: 'destructive',
      })
      return
    }

    if (!Number.isFinite(revenueMin) || !Number.isFinite(revenueMax) || revenueMin > revenueMax) {
      toast({
        title: 'Cấu hình chưa hợp lệ',
        description: 'Khoảng doanh thu không hợp lệ.',
        variant: 'destructive',
      })
      return
    }

    // Build Kalodata advanced filters (chỉ gửi filter đã chọn)
    const filters: Record<string, string | string[]> = {}
    if (crawlConfig.cateIds.length > 0) filters['cateIds'] = crawlConfig.cateIds
    if (crawlConfig.content_type) filters['creator.filter.content_type'] = crawlConfig.content_type
    if (crawlConfig.revenue_trend) filters['global.filter.revenue_trend'] = crawlConfig.revenue_trend
    if (crawlConfig.creator_type) filters['creator.filter.creator_type'] = crawlConfig.creator_type
    if (crawlConfig.followers) filters['creator.filter.followers'] = crawlConfig.followers
    if (crawlConfig.engagement_rate) filters['creator.filter.video_engagement_rate'] = crawlConfig.engagement_rate
    if (crawlConfig.creator_content.length > 0) filters['creator.filter.creator_content'] = crawlConfig.creator_content
    if (crawlConfig.mcn_status) filters['creator.filter.mcn_status'] = crawlConfig.mcn_status
    if (crawlConfig.creator_debut) filters['creator.filter.ad.creator_debut'] = crawlConfig.creator_debut
    if (crawlConfig.unit_price) filters['creator.filter.unit_price'] = crawlConfig.unit_price
    if (crawlConfig.follower_gender) filters['creator.filter.follower_gender'] = crawlConfig.follower_gender

    const payload: KalodataExportParams = {
      start_date: crawlConfig.start_date || undefined,
      end_date: crawlConfig.end_date || undefined,
      revenue_min: revenueMin,
      revenue_max: revenueMax,
      age_range: crawlConfig.age_range,
      page_size: pageSize,
      enrich: crawlConfig.enrich,
      deduplicate: crawlConfig.deduplicate,
      filters: Object.keys(filters).length > 0 ? filters : undefined,
    }

    setLoading(true)
    try {
      toast({
        title: "Đang crawl dữ liệu...",
        description: "Quá trình này có thể mất vài phút. Vui lòng đợi.",
      })

      const result = await exportKalodata(payload)

      if (result.success && result.data) {
        setData(mapRows(result.data))
        setUpdatedAt(result.updated_at ?? null)
        setConfigOpen(false)

        const newCount = result.new_count ?? 0
        const duplicateCount = result.duplicate_count ?? 0
        
        toast({
          title: newCount > 0 ? 'Thành công!' : 'Crawl hoàn tất',
          description:
            newCount > 0
              ? `Đã thêm ${newCount} KOL mới, bỏ qua ${duplicateCount} bản trùng. Tổng đang lưu ${result.count} KOL.`
              : duplicateCount > 0
                ? `Không có KOL mới. Đã bỏ qua ${duplicateCount} bản trùng. Tổng đang lưu ${result.count} KOL.`
                : `Đã lưu ${result.count} KOL.`,
        })
      } else {
        throw new Error(result.error || 'Không thể crawl dữ liệu')
      }
    } catch (error) {
      console.error('Crawl error:', error)
      toast({
        title: "Lỗi",
        description: error instanceof Error ? error.message : "Không thể crawl dữ liệu. Vui lòng kiểm tra backend.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSelected = async () => {
    if (selectedRows.size === 0) {
      toast({
        title: "Chưa chọn KOL nào",
        description: "Vui lòng chọn ít nhất một KOL để xóa",
        variant: "destructive",
      })
      return
    }

    const namesToDelete = Array.from(selectedRows)
    setDeleting(true)
    try {
      const result = await deleteKalodataCreators(namesToDelete)
      if (result.success) {
        setData(prev => prev.filter(row => !selectedRows.has(row.name)))
        setSelectedRows(new Set())
        toast({
          title: "Đã xóa thành công",
          description: `Đã xóa ${result.deleted_count} KOL`,
        })
      } else {
        throw new Error(result.error || 'Không thể xóa KOL')
      }
    } catch (error) {
      console.error('Delete error:', error)
      toast({
        title: "Lỗi",
        description: error instanceof Error ? error.message : "Không thể xóa KOL",
        variant: "destructive",
      })
    } finally {
      setDeleting(false)
    }
  }

  const handleSendDM = () => {
    if (selectedRows.size === 0) {
      toast({
        title: "Chưa chọn KOL nào",
        description: "Vui lòng chọn ít nhất một KOL để gửi tin nhắn",
        variant: "destructive",
      })
      return
    }
    setDmDialogOpen(true)
  }

  const handleSendDMConfirm = async () => {
    if (!dmMessage.trim()) {
      toast({
        title: "Chưa nhập tin nhắn",
        description: "Vui lòng nhập nội dung tin nhắn",
        variant: "destructive",
      })
      return
    }

    const selectedKOLs = data.filter(row => selectedRows.has(row.name))
    const users = selectedKOLs.map(kol => ({
      profile_url: kol.tiktok_url,
      message: dmMessage,
    })).filter(u => u.profile_url) // Chỉ gửi cho KOL có TikTok URL

    if (users.length === 0) {
      toast({
        title: "Không có TikTok URL",
        description: "Các KOL đã chọn không có link TikTok",
        variant: "destructive",
      })
      return
    }

    setSendingDM(true)
    try {
      const result = await sendBatchTikTokDM(users)
      if (result.success) {
        const successCount = result.results.filter((r: any) => r.success).length
        const failCount = result.results.length - successCount
        
        toast({
          title: "Đã gửi tin nhắn",
          description: `Thành công: ${successCount}, Thất bại: ${failCount}`,
        })
        setDmDialogOpen(false)
        setDmMessage('')
        setSelectedRows(new Set())
      } else {
        throw new Error(result.error || 'Không thể gửi tin nhắn')
      }
    } catch (error) {
      console.error('Send DM error:', error)
      toast({
        title: "Lỗi",
        description: error instanceof Error ? error.message : "Không thể gửi tin nhắn",
        variant: "destructive",
      })
    } finally {
      setSendingDM(false)
    }
  }

  const handleExportData = () => {
    if (data.length === 0) {
      toast({
        title: "Không có dữ liệu",
        description: "Vui lòng crawl dữ liệu trước khi xuất",
        variant: "destructive",
      })
      return
    }

    // Export to CSV
    const headers = [
      'Phạm vi thời gian',
      'Tên nhà sáng tạo',
      'Lượng theo dõi',
      'Doanh số livestream',
      'Doanh số video',
      'Link Kalodata',
      'Link TikTok',
      'Độ tuổi người theo dõi',
      'Giới tính người theo dõi',
      'Tỷ lệ tương tác'
    ]
    
    const csvContent = [
      headers.join(','),
      ...data.map(row => [
        row.period,
        row.name,
        row.followers,
        row.revenue_livestream,
        row.revenue_video,
        row.kalodata_url,
        row.tiktok_url,
        row.age_range,
        row.gender,
        row.engagement_rate
      ].join(','))
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `kol_data_${new Date().toISOString().split('T')[0]}.csv`
    link.click()

    toast({
      title: "Đã xuất dữ liệu",
      description: `Đã xuất ${data.length} KOL ra file CSV`,
    })
  }

  const toggleRowSelection = (name: string) => {
    setSelectedRows(prev => {
      const next = new Set(prev)
      if (next.has(name)) {
        next.delete(name)
      } else {
        next.add(name)
      }
      return next
    })
  }

  const toggleAllRows = () => {
    if (selectedRows.size === sortedData.length) {
      setSelectedRows(new Set())
    } else {
      setSelectedRows(new Set(sortedData.map(row => row.name)))
    }
  }

  const handleAgentSuggest = async () => {
    if (!agentDescription.trim()) {
      toast({ title: 'Vui lòng nhập mô tả sản phẩm', variant: 'destructive' })
      return
    }
    setAgentLoading(true)
    setAgentResult(null)
    try {
      const result = await agentSuggestFilters({
        description: agentDescription,
        price: agentPrice || undefined,
      })
      setAgentResult(result)
    } catch (error) {
      toast({
        title: 'Lỗi Agent',
        description: error instanceof Error ? error.message : 'Không thể kết nối Agent',
        variant: 'destructive',
      })
    } finally {
      setAgentLoading(false)
    }
  }

  const applyAgentFilters = () => {
    if (!agentResult?.filters) return
    const f = agentResult.filters
    setCrawlConfig((prev) => ({
      ...prev,
      cateIds: Array.isArray(f['cateIds']) ? f['cateIds'] : prev.cateIds,
      content_type: typeof f['content_type'] === 'string' ? f['content_type'] : prev.content_type,
      revenue_trend: typeof f['revenue_trend'] === 'string' ? f['revenue_trend'] : prev.revenue_trend,
      creator_type: typeof f['creator_type'] === 'string' ? f['creator_type'] : prev.creator_type,
      followers: typeof f['followers'] === 'string' ? f['followers'] : prev.followers,
      engagement_rate: typeof f['engagement_rate'] === 'string' ? f['engagement_rate'] : prev.engagement_rate,
      creator_content: Array.isArray(f['creator_content']) ? f['creator_content'] : prev.creator_content,
      mcn_status: typeof f['mcn_status'] === 'string' ? f['mcn_status'] : prev.mcn_status,
      creator_debut: typeof f['creator_debut'] === 'string' ? f['creator_debut'] : prev.creator_debut,
      unit_price: typeof f['unit_price'] === 'string' ? f['unit_price'] : prev.unit_price,
      follower_gender: typeof f['follower_gender'] === 'string' ? f['follower_gender'] : prev.follower_gender,
      age_range: typeof f['age_range'] === 'string' ? f['age_range'] : prev.age_range,
    }))
    setAgentMode(false)
    setConfigOpen(true)
    toast({ title: 'Đã áp dụng filter từ Agent', description: 'Mở popup crawl để kiểm tra và bắt đầu crawl.' })
  }

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const SortIcon = ({ column }: { column: string }) => {
    if (sortColumn !== column) return <ChevronUp className="w-4 h-4 opacity-30" />
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    )
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      notation: 'compact',
    }).format(value)
  }

  // Filter data based on search
  const filteredData = data.filter(row =>
    row.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Sort data
  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortColumn) return 0
    
    const aValue = a[sortColumn as keyof DataRow]
    const bValue = b[sortColumn as keyof DataRow]
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
    }
    
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue)
    }
    
    return 0
  })

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* Header */}
      <div className="px-8 py-6 border-b border-border">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-3xl font-bold text-foreground">Dữ liệu creator</h2>
            <p className="text-muted-foreground text-sm mt-1">
              {loadingStoredData
                ? 'Đang tải dữ liệu đã lưu...'
                : data.length > 0
                  ? `Đang hiển thị ${sortedData.length} / ${data.length} KOL đã lưu`
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
              onClick={() => setConfigOpen(true)}
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
              onClick={() => setAgentMode(!agentMode)}
              variant={agentMode ? 'default' : 'outline'}
              className="gap-2 font-medium"
            >
              <Bot className="w-4 h-4" />
              {agentMode ? 'Tắt Agent' : 'Agent Mode'}
            </Button>
            <Button
              size="sm"
              onClick={handleExportData}
              disabled={data.length === 0}
              variant="outline"
              className="gap-2 font-medium"
            >
              <Download className="w-4 h-4" />
              Xuất CSV
            </Button>
            {selectedRows.size > 0 && (
              <>
                <Button
                  size="sm"
                  onClick={handleSendDM}
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
                      Gửi tin nhắn ({selectedRows.size})
                    </>
                  )}
                </Button>
                <Button
                  size="sm"
                  onClick={handleDeleteSelected}
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
                      Xóa đã chọn ({selectedRows.size})
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
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground text-sm"
          />
        </div>
      </div>

      {/* Agent Mode Panel */}
      <Dialog open={agentMode} onOpenChange={setAgentMode}>
        <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary/10 ring-1 ring-primary/20">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div>
                <DialogTitle>AI Agent - Gợi ý filter</DialogTitle>
                <DialogDescription>
                  Mô tả sản phẩm để Agent gợi ý filter Kalodata phù hợp nhất
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          <div className="space-y-5">
            {/* Quick Select Products */}
            {products.length > 0 && (
              <div className="space-y-3 p-4 rounded-lg bg-muted/30 border border-border">
                <Label className="text-sm font-medium flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Chọn nhanh sản phẩm
                </Label>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                  {products.map((product) => (
                    <button
                      key={product.id}
                      onClick={() => handleSelectProduct(product)}
                      className="flex flex-col items-start gap-2 p-3 rounded-lg border border-border bg-background hover:border-primary hover:bg-accent/50 transition-all text-left"
                    >
                      {product.image && (
                        <div className="w-full aspect-square rounded-md overflow-hidden bg-muted">
                          <img src={product.image} alt={product.name} className="w-full h-full object-cover" />
                        </div>
                      )}
                      <div className="w-full">
                        <p className="text-xs font-medium line-clamp-2">{product.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(product.price)}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="grid gap-5 lg:grid-cols-[1fr,340px]">
              {/* Left: Description */}
              <div className="space-y-2">
                <Label htmlFor="agent-desc" className="text-sm font-medium">
                  Mô tả sản phẩm <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="agent-desc"
                  placeholder="Ví dụ: Son môi dưỡng ẩm cao cấp, phù hợp cho phụ nữ 20-35 tuổi, phong cách Hàn Quốc, giá tầm trung..."
                  value={agentDescription}
                  onChange={(e) => setAgentDescription(e.target.value)}
                  className="min-h-[140px] resize-none text-sm"
                />
              </div>

              {/* Right: Price */}
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="agent-price" className="text-sm font-medium">Giá bán (VND)</Label>
                  <Input
                    id="agent-price"
                    type="text"
                    placeholder="150000"
                    value={agentPrice}
                    onChange={(e) => setAgentPrice(e.target.value)}
                    className="text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Action Button */}
            <div className="flex items-center gap-3">
              <Button 
                onClick={handleAgentSuggest} 
                disabled={agentLoading || !agentDescription.trim()} 
                className="gap-2"
                size="default"
              >
                {agentLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Đang phân tích...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Gợi ý filter
                  </>
                )}
              </Button>
              {agentResult && (
                <span className="text-xs text-muted-foreground">✓ Đã phân tích xong</span>
              )}
            </div>

            {/* Agent Result */}
            {agentResult && (
              <div className="space-y-4 pt-4 border-t border-border">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-primary/10">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                  <span className="text-sm font-semibold text-foreground">Kết quả phân tích</span>
                </div>
                
                {agentResult.explanation && (
                  <div className="rounded-xl bg-muted/50 border border-border/50 p-4">
                    <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
                      {agentResult.explanation}
                    </p>
                  </div>
                )}
                
                {agentResult.filters && Object.keys(agentResult.filters).length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Filter được đề xuất</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(agentResult.filters).map(([key, value]) => (
                        <div key={key} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20 text-xs font-medium text-primary">
                          <span className="opacity-70">{key}:</span>
                          <span>{Array.isArray(value) ? value.join(', ') : value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {agentResult.error && (
                  <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3">
                    <p className="text-sm text-destructive">{agentResult.error}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setAgentMode(false)} disabled={agentLoading}>
              Đóng
            </Button>
            {agentResult?.filters && Object.keys(agentResult.filters).length > 0 && (
              <Button type="button" onClick={applyAgentFilters} className="gap-2">
                <Sparkles className="w-4 h-4" />
                Áp dụng filter và mở Crawl
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Table */}      {/* Table */}
      <div className="flex-1 overflow-x-auto px-8">
        {loadingStoredData ? (
          <div className="flex flex-col items-center justify-center h-full py-20 text-center">
            <Loader2 className="w-10 h-10 animate-spin text-muted-foreground/60 mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">Đang tải dữ liệu</h3>
            <p className="text-muted-foreground">Vui lòng đợi trong giây lát...</p>
          </div>
        ) : sortedData.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-20">
            <div className="text-center">
              <RefreshCw className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">
                {data.length === 0 ? 'Chưa có dữ liệu' : 'Không tìm thấy kết quả'}
              </h3>
              <p className="text-muted-foreground mb-6">
                {data.length === 0 
                  ? 'Nhấn nút "Crawl dữ liệu" để lấy dữ liệu KOL từ Kalodata'
                  : 'Thử tìm kiếm với từ khóa khác'}
              </p>
              {data.length === 0 && (
                <Button onClick={() => setConfigOpen(true)} disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      Đang crawl...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Crawl dữ liệu ngay
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap w-12">
                  <Checkbox
                    checked={sortedData.length > 0 && selectedRows.size === sortedData.length}
                    onCheckedChange={toggleAllRows}
                  />
                </th>
                <th className="text-left py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  <button
                    type="button"
                    onClick={() => handleSort('period')}
                    className="flex items-center gap-2 hover:text-foreground/80 transition-colors"
                  >
                    Thời gian <SortIcon column="period" />
                  </button>
                </th>
                <th className="text-left py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  <button
                    type="button"
                    onClick={() => handleSort('name')}
                    className="flex items-center gap-2 hover:text-foreground/80 transition-colors"
                  >
                    Tên NST <SortIcon column="name" />
                  </button>
                </th>
                <th className="text-right py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  <button
                    type="button"
                    onClick={() => handleSort('followers')}
                    className="flex items-center justify-end gap-2 hover:text-foreground/80 transition-colors w-full"
                  >
                    Followers <SortIcon column="followers" />
                  </button>
                </th>
                <th className="text-right py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  <button
                    type="button"
                    onClick={() => handleSort('revenue_livestream')}
                    className="flex items-center justify-end gap-2 hover:text-foreground/80 transition-colors w-full"
                  >
                    DS Livestream <SortIcon column="revenue_livestream" />
                  </button>
                </th>
                <th className="text-right py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  <button
                    type="button"
                    onClick={() => handleSort('revenue_video')}
                    className="flex items-center justify-end gap-2 hover:text-foreground/80 transition-colors w-full"
                  >
                    DS Video <SortIcon column="revenue_video" />
                  </button>
                </th>
                <th className="text-left py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  Độ tuổi người theo dõi
                </th>
                <th className="text-left py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  Giới tính
                </th>
                <th className="text-right py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  <button
                    type="button"
                    onClick={() => handleSort('engagement_rate')}
                    className="flex items-center justify-end gap-2 hover:text-foreground/80 transition-colors w-full"
                  >
                    Tỷ lệ tương tác <SortIcon column="engagement_rate" />
                  </button>
                </th>
                <th className="text-left py-4 px-2 font-semibold text-foreground text-xs uppercase whitespace-nowrap">
                  Link TikTok
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => toggleRowSelection(row.name)}
                  className="border-b border-border hover:bg-card/50 transition-colors cursor-pointer"
                >
                  <td className="py-3 px-2" onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedRows.has(row.name)}
                      onCheckedChange={() => toggleRowSelection(row.name)}
                    />
                  </td>
                  <td className="py-3 px-2 text-foreground text-sm whitespace-nowrap">{row.period}</td>
                  <td className="py-3 px-2 text-foreground font-medium text-sm" onClick={(e) => e.stopPropagation()}>
                    {row.kalodata_url ? (
                      <a 
                        href={row.kalodata_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="hover:text-primary hover:underline"
                      >
                        {row.name}
                      </a>
                    ) : (
                      row.name
                    )}
                  </td>
                  <td className="py-3 px-2 text-right text-foreground text-sm whitespace-nowrap">
                    {row.followers.toLocaleString('vi-VN')}
                  </td>
                  <td className="py-3 px-2 text-right text-foreground text-sm whitespace-nowrap">
                    {formatCurrency(row.revenue_livestream)}
                  </td>
                  <td className="py-3 px-2 text-right text-foreground text-sm whitespace-nowrap">
                    {formatCurrency(row.revenue_video)}
                  </td>
                  <td className="py-3 px-2 text-sm text-muted-foreground">{row.age_range}</td>
                  <td className="py-3 px-2 text-sm text-muted-foreground">{row.gender}</td>
                  <td className="py-3 px-2 text-right text-foreground text-sm">
                    {row.engagement_rate ? `${row.engagement_rate.toFixed(2)}%` : '-'}
                  </td>
                  <td className="py-3 px-2 text-sm" onClick={(e) => e.stopPropagation()}>
                    {row.tiktok_url ? (
                      <a 
                        href={row.tiktok_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-white-500 hover:underline"
                      >
                        TikTok
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Dialog gửi tin nhắn */}
      <Dialog open={dmDialogOpen} onOpenChange={setDmDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Gửi tin nhắn TikTok</DialogTitle>
            <DialogDescription>
              Gửi tin nhắn đến {selectedRows.size} KOL đã chọn
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="dm-message">Nội dung tin nhắn</Label>
              <Textarea
                id="dm-message"
                placeholder="Nhập nội dung tin nhắn..."
                value={dmMessage}
                onChange={(e) => setDmMessage(e.target.value)}
                className="min-h-[120px] max-h-[300px] !h-[120px] resize-none overflow-y-auto overflow-x-hidden [field-sizing:initial] [overflow-wrap:anywhere] whitespace-pre-wrap"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Lưu ý: Chỉ gửi đến các KOL có link TikTok. Quá trình này có thể mất vài phút.
            </p>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDmDialogOpen(false)} disabled={sendingDM}>
              Hủy
            </Button>
            <Button type="button" onClick={handleSendDMConfirm} disabled={sendingDM} className="gap-2">
              {sendingDM ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Đang gửi...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Gửi tin nhắn
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={configOpen} onOpenChange={setConfigOpen}>
        <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Cấu hình crawl dữ liệu</DialogTitle>
          </DialogHeader>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="start-date">Từ ngày</Label>
              <Input
                id="start-date"
                type="date"
                value={crawlConfig.start_date}
                onChange={(event) => updateConfig('start_date', event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end-date">Đến ngày</Label>
              <Input
                id="end-date"
                type="date"
                value={crawlConfig.end_date}
                onChange={(event) => updateConfig('end_date', event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="revenue-min">Doanh thu tối thiểu</Label>
              <Input
                id="revenue-min"
                type="number"
                min="0"
                step="1000000"
                value={crawlConfig.revenue_min}
                onChange={(event) => updateConfig('revenue_min', event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="revenue-max">Doanh thu tối đa</Label>
              <Input
                id="revenue-max"
                type="number"
                min="0"
                step="1000000"
                value={crawlConfig.revenue_max}
                onChange={(event) => updateConfig('revenue_max', event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="page-size">Số lượng tải về</Label>
              <Input
                id="page-size"
                type="number"
                min="5"
                step="1"
                value={crawlConfig.page_size}
                onChange={(event) => updateConfig('page_size', event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label>Độ tuổi follower</Label>
              <Select
                value={crawlConfig.age_range}
                onValueChange={(value) => updateConfig('age_range', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Chọn độ tuổi" />
                </SelectTrigger>
                <SelectContent>
                  {AGE_RANGE_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Bộ lọc nâng cao Kalodata */}
          <div className="space-y-3">
            <p className="text-sm font-medium text-foreground">Bộ lọc nâng cao</p>

            {/* Ngành hàng - multi-select */}
            <div className="space-y-2">
              <Label>Ngành hàng</Label>
              <div className="flex flex-wrap gap-3">
                {CATEGORY_OPTIONS.map((cat) => (
                  <label key={cat.value} className="flex items-center gap-1.5 text-sm">
                    <Checkbox
                      checked={crawlConfig.cateIds.includes(cat.value)}
                      onCheckedChange={(checked) => {
                        const next = checked
                          ? [...crawlConfig.cateIds, cat.value]
                          : crawlConfig.cateIds.filter((id) => id !== cat.value)
                        updateConfig('cateIds', next)
                      }}
                    />
                    {cat.label}
                  </label>
                ))}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {/* Nguồn doanh thu */}
              <div className="space-y-2">
                <Label>Nguồn doanh thu</Label>
                <Select value={crawlConfig.content_type} onValueChange={(v) => updateConfig('content_type', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {CONTENT_TYPE_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Loại tài khoản */}
              <div className="space-y-2">
                <Label>Loại tài khoản</Label>
                <Select value={crawlConfig.creator_type} onValueChange={(v) => updateConfig('creator_type', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {CREATOR_TYPE_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Followers */}
              <div className="space-y-2">
                <Label>Followers</Label>
                <Select value={crawlConfig.followers} onValueChange={(v) => updateConfig('followers', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {FOLLOWERS_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Tỷ lệ tương tác */}
              <div className="space-y-2">
                <Label>Tỷ lệ tương tác</Label>
                <Select value={crawlConfig.engagement_rate} onValueChange={(v) => updateConfig('engagement_rate', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {ENGAGEMENT_RATE_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* MCN */}
              <div className="space-y-2">
                <Label>MCN</Label>
                <Select value={crawlConfig.mcn_status} onValueChange={(v) => updateConfig('mcn_status', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {MCN_STATUS_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Thời gian debut */}
              <div className="space-y-2">
                <Label>Thời gian debut</Label>
                <Select value={crawlConfig.creator_debut} onValueChange={(v) => updateConfig('creator_debut', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {CREATOR_DEBUT_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Giá trung bình */}
              <div className="space-y-2">
                <Label>Giá trung bình</Label>
                <Select value={crawlConfig.unit_price} onValueChange={(v) => updateConfig('unit_price', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {UNIT_PRICE_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Giới tính follower */}
              <div className="space-y-2">
                <Label>Giới tính follower</Label>
                <Select value={crawlConfig.follower_gender} onValueChange={(v) => updateConfig('follower_gender', v === '__all__' ? '' : v)}>
                  <SelectTrigger className="w-full"><SelectValue placeholder="Tất cả" /></SelectTrigger>
                  <SelectContent>
                    {FOLLOWER_GENDER_OPTIONS.map((o) => (
                      <SelectItem key={o.value || '__all__'} value={o.value || '__all__'}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Liên hệ creator - multi-select */}
            <div className="space-y-2">
              <Label>Liên hệ creator</Label>
              <div className="flex flex-wrap gap-3">
                {CONTACT_OPTIONS.map((c) => (
                  <label key={c.value} className="flex items-center gap-1.5 text-sm">
                    <Checkbox
                      checked={crawlConfig.creator_content.includes(c.value)}
                      onCheckedChange={(checked) => {
                        const next = checked
                          ? [...crawlConfig.creator_content, c.value]
                          : crawlConfig.creator_content.filter((v) => v !== c.value)
                        updateConfig('creator_content', next)
                      }}
                    />
                    {c.label}
                  </label>
                ))}
              </div>
            </div>

            {/* Xu hướng doanh thu */}
            <div className="flex items-center gap-2">
              <Checkbox
                checked={crawlConfig.revenue_trend === 'GROWING'}
                onCheckedChange={(checked) => updateConfig('revenue_trend', checked ? 'GROWING' : '')}
              />
              <Label className="cursor-pointer">Chỉ hiển thị creator có doanh thu đang tăng</Label>
            </div>
          </div>

          <div className="space-y-4 rounded-lg border border-border bg-card p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <Label htmlFor="enrich-switch">Lấy thêm follower stats</Label>
                <p className="text-xs text-muted-foreground mt-1">
                  Bật để lấy thêm độ tuổi, giới tính và tỷ lệ tương tác.
                </p>
              </div>
              <Switch
                id="enrich-switch"
                checked={crawlConfig.enrich}
                onCheckedChange={(checked) => updateConfig('enrich', checked)}
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <Label htmlFor="deduplicate-switch">Lọc trùng với dữ liệu đã lưu</Label>
                <p className="text-xs text-muted-foreground mt-1">
                  Giữ lại dữ liệu cũ, chỉ thêm KOL mới vào danh sách đã lưu trên backend.
                </p>
              </div>
              <Switch
                id="deduplicate-switch"
                checked={crawlConfig.deduplicate}
                onCheckedChange={(checked) => updateConfig('deduplicate', checked)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setConfigOpen(false)} disabled={loading}>
              Đóng
            </Button>
            <Button type="button" onClick={handleCrawlData} disabled={loading} className="gap-2">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Đang crawl...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  Bắt đầu crawl
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
