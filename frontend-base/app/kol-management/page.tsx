'use client'

import { useState, useEffect } from 'react'
import {
  syncKOLData,
  getKOLRanking,
  getGenericSheetData,
  getApprovedKOLs,
  getProcessedBookings,
  getRejectionHistory,
  approveKOL,
  rejectKOL,
  deleteApprovedKOL,
  sendKOLNotification,
  syncKOLVideos,
  updateKOLRanking,
  type KOL
} from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { RefreshCw, TrendingUp, ExternalLink, Video, Check, X, Eye, UserPlus, UserMinus, AlertCircle, Send, Heart, MessageCircle, Share2 } from 'lucide-react'
import { DashboardShell } from '@/components/dashboard-shell'

export default function KOLManagementPage() {
  const [kols, setKols] = useState<KOL[]>([])
  const [ranking, setRanking] = useState<KOL[]>([])
  const [bookings, setBookings] = useState<any[]>([])
  const [processedBookingIds, setProcessedBookingIds] = useState<string[]>([])
  const [rejectionHistory, setRejectionHistory] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(false)
  const [sheetUrl, setSheetUrl] = useState('https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit')
  const [activeTab, setActiveTab] = useState('bookings')

  // State cho Modal chi tiết
  const [selectedKOL, setSelectedKOL] = useState<any>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)

  const loadApprovedKols = async () => {
    setLoading(true)
    try {
      // Tự động đồng bộ video từ Sheet trước khi lấy danh sách
      await syncKOLVideos()
      const result = await getApprovedKOLs()
      if (result.success && result.kols) {
        setKols(result.kols)
      }
    } catch (error) {
      console.error('Error loading approved KOLs:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadProcessedBookings = async () => {
    try {
      const result = await getProcessedBookings()
      if (result.success) {
        setProcessedBookingIds(result.ids)
      }
    } catch (error) {
      console.error('Error loading processed bookings:', error)
    }
  }

  const loadRejectionHistory = async () => {
    try {
      const result = await getRejectionHistory()
      if (result.success) {
        setRejectionHistory(result.history)
      }
    } catch (error) {
      console.error('Error loading rejection history:', error)
    }
  }

  const loadRanking = async () => {
    setLoading(true)
    try {
      const result = await getKOLRanking()
      if (result.success && result.ranking) {
        setRanking(result.ranking)
      }
    } catch (error) {
      console.error('Error loading ranking:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadBookings = async () => {
    setLoading(true)
    try {
      const result = await getGenericSheetData(sheetUrl, 'Đk_Booking')
      if (result.success && result.data) {
        setBookings(result.data)
      }
      await loadProcessedBookings()
      await loadRejectionHistory()
    } catch (error) {
      console.error('Error loading bookings:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadBookings()
    loadApprovedKols()
    loadRanking()
    loadProcessedBookings()
    loadRejectionHistory()
  }, [])

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  const formatTikTokLink = (link: string) => {
    if (!link || link === '#' || link === '-' || link === '') return '#'
    // If already a full URL
    if (link.startsWith('http')) return link

    // If it's a domain already like www.tiktok.com or tiktok.com/something
    if (link.includes('tiktok.com')) {
      return `https://${link.startsWith('www.') ? '' : 'www.'}${link}`
    }

    // Handle @user or just user
    if (link.startsWith('@')) return `https://www.tiktok.com/${link}`
    return `https://www.tiktok.com/@${link}`
  }

  // Helper để lấy giá trị từ record theo từ khóa trong key (phòng hờ sai lệch header)
  const getRowValue = (row: any, keyword: string, exclude?: string) => {
    const key = Object.keys(row).find(k => {
      const lower = k.toLowerCase()
      const match = lower.includes(keyword.toLowerCase())
      const skip = exclude && lower.includes(exclude.toLowerCase())
      return match && !skip
    })
    return key ? row[key] : null
  }

  // Mapper cho cột Đăng ký Booking
  const mapBookingData = (row: any) => {
    // Ưu tiên cột "Link" và "Tiktok", loại trừ cột "ID" để tránh nhầm lẫn
    const rawLink = getRowValue(row, 'Link', 'ID') || getRowValue(row, 'Tiktok', 'ID') || '#'
    const rawId = getRowValue(row, 'ID Tiktok') || getRowValue(row, 'TikTok ID') || '-'

    return {
      timestamp: row['Dấu thời gian'] || getRowValue(row, 'Timestamp') || '-',
      product_choice: getRowValue(row, 'lựa chọn hợp tác') || getRowValue(row, 'Sản phẩm', 'MIỄN PHÍ') || '-',
      tiktok_id: rawId,
      tiktok_link: formatTikTokLink(String(rawLink)),
      email: getRowValue(row, 'Email') || '-',
      phone: getRowValue(row, 'Số điện thoại') || '-',
      address: getRowValue(row, 'Địa chỉ nhận sản phẩm') || getRowValue(row, 'Địa chỉ') || '-',
      is_free: getRowValue(row, 'KHÔNG tính phí') || '-',
      need_ads: getRowValue(row, 'hỗ trợ chạy ads') || '-'
    }
  }

  const handleApprove = async (row: any) => {
    const b = mapBookingData(row)
    const kolData: KOL = {
      tiktok_account: String(b.tiktok_id),
      tiktok_link: b.tiktok_link,
      product: b.product_choice,
      post_links: [],
      post_count: 0,
      registration_info: b
    }

    try {
      setLoading(true)
      const result = await approveKOL(kolData, b.timestamp)
      if (result.success) {
        setProcessedBookingIds(prev => [...prev, b.timestamp])
        await loadApprovedKols()
      }
    } catch (error) {
      console.error('Error approving KOL:', error)
      alert('Lỗi khi duyệt KOL')
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async (row: any) => {
    const b = mapBookingData(row)
    try {
      setLoading(true)
      const result = await rejectKOL(b.timestamp, String(b.tiktok_id))
      if (result.success) {
        setProcessedBookingIds(prev => [...prev, b.timestamp])
        await loadRejectionHistory()
      }
    } catch (error) {
      console.error('Error rejecting KOL:', error)
      alert('Lỗi khi từ chối KOL')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteApproved = async (tiktokAccount: string) => {
    if (!confirm(`Bạn có chắc muốn xóa ${tiktokAccount} khỏi danh sách quản lý?`)) return

    try {
      setLoading(true)
      const result = await deleteApprovedKOL(tiktokAccount)
      if (result.success) {
        await loadApprovedKols()
      }
    } catch (error) {
      console.error('Error deleting approved KOL:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSendNotification = async (kol: KOL) => {
    if (!kol.registration_info?.email) {
      alert('KOL này không có email đăng ký')
      return
    }

    try {
      setLoading(true)
      const result = await sendKOLNotification(
        kol.registration_info.email,
        kol.booking_code || 'N/A',
        kol.tiktok_account
      )
      if (result.success) {
        alert(`Đã gửi thông báo thành công cho ${kol.tiktok_account}`)
      }
    } catch (error) {
      console.error('Error sending notification:', error)
      alert('Lỗi khi gửi thông báo email')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateRanking = async () => {
    try {
      setLoading(true)
      const result = await updateKOLRanking()
      if (result.success) {
        alert(`Đã cập nhật xếp hạng cho ${result.count} KOL thành công!`)
        await loadRanking()
      }
    } catch (error) {
      console.error('Error updating ranking:', error)
      alert('Lỗi khi cập nhật xếp hạng')
    } finally {
      setLoading(false)
    }
  }

  const showDetail = (kol: any) => {
    setSelectedKOL(kol)
    setIsDetailOpen(true)
  }

  // Lọc bỏ những booking đã xử lý
  const pendingBookings = bookings.filter(b => !processedBookingIds.includes(b['Dấu thời gian']))

  return (
    <DashboardShell>
      <div className="flex-1 flex flex-col bg-background">
        {/* Header */}
        <div className="px-8 py-6 border-b border-border">
          <div className="flex items-center justify-between gap-4 mb-6">
            <div>
              <h2 className="text-3xl font-bold text-foreground">Quản lý KOL</h2>
              <p className="text-muted-foreground text-sm mt-1">
                Duyệt đăng ký và theo dõi hiệu suất KOL chuyên nghiệp
              </p>
            </div>
            <div className="flex gap-2 text-muted-foreground text-xs items-center opacity-0 group-hover:opacity-100 transition-opacity">
              {/* URL đã được cố định */}
            </div>
            <div className="flex gap-2">
              <Button onClick={() => {
                if (activeTab === 'bookings') loadBookings()
                else if (activeTab === 'management') loadApprovedKols()
                else loadRanking()
              }} disabled={loading}>
                <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Tải lại
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="bookings">Đăng ký mới ({pendingBookings.length})</TabsTrigger>
              <TabsTrigger value="management">Đang quản lý ({kols.length})</TabsTrigger>
              <TabsTrigger value="ranking">Bảng xếp hạng</TabsTrigger>
            </TabsList>

            <TabsContent value="bookings" className="space-y-4 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Danh sách đăng ký chờ duyệt</CardTitle>
                  <CardDescription>Chọn Duyệt để thêm vào danh sách quản lý hoặc Từ chối để bỏ qua</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[120px]">Thời gian</TableHead>
                        <TableHead>TikTok ID</TableHead>
                        <TableHead>Sản phẩm</TableHead>
                        <TableHead>Liên hệ</TableHead>
                        <TableHead className="text-center">Hành động</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {pendingBookings.map((row, idx) => {
                        const b = mapBookingData(row)
                        const rejectCount = rejectionHistory[String(b.tiktok_id)] || 0

                        return (
                          <TableRow key={idx}>
                            <TableCell className="text-[10px] text-muted-foreground whitespace-nowrap">
                              {b.timestamp}
                            </TableCell>
                            <TableCell className="font-medium">
                              <div className="flex flex-col gap-1">
                                <a href={b.tiktok_link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-1">
                                  {b.tiktok_id}
                                  <ExternalLink className="h-3 w-3" />
                                </a>
                                {rejectCount > 0 && (
                                  <Badge variant="destructive" className="w-fit text-[9px] h-4 px-1 flex items-center gap-0.5">
                                    <AlertCircle className="h-2.5 w-2.5" />
                                    Bị từ chối {rejectCount} lần
                                  </Badge>
                                )}
                              </div>
                            </TableCell>
                            <TableCell className="text-xs max-w-[150px] truncate">{b.product_choice}</TableCell>
                            <TableCell>
                              <div className="text-[10px] space-y-0.5">
                                <div className="font-medium text-foreground">{b.phone}</div>
                                <div className="text-muted-foreground">{b.email}</div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center justify-center gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-8 w-8 p-0 text-green-600 hover:text-green-700 hover:bg-green-50"
                                  onClick={() => handleApprove(row)}
                                  title="Duyệt"
                                >
                                  <Check className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleReject(row)}
                                  title="Từ chối"
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                                  onClick={() => showDetail({ registration_info: b, tiktok_account: String(b.tiktok_id), tiktok_link: b.tiktok_link })}
                                  title="Xem chi tiết"
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        )
                      })}
                      {pendingBookings.length === 0 && !loading && (
                        <TableRow>
                          <TableCell colSpan={5} className="text-center py-12 text-muted-foreground italic">
                            Không có đăng ký mới nào cần xử lý
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="management" className="space-y-4 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Danh sách KOL Active</CardTitle>
                  <CardDescription>Quản lý hiệu suất và video của các KOL đã được duyệt</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>TikTok Account</TableHead>
                        <TableHead>Trạng thái Video</TableHead>
                        <TableHead>Link bài đăng</TableHead>
                        <TableHead className="text-right">Hành động</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {kols.map((kol, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="font-medium">
                            <div className="flex flex-col gap-1">
                              <a href={formatTikTokLink(kol.tiktok_link)} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:underline text-blue-600">
                                {kol.tiktok_account}
                                <ExternalLink className="h-3 w-3" />
                              </a>
                              {kol.booking_code && (
                                <Badge variant="secondary" className="w-fit text-[9px] h-4 px-1 bg-blue-50 text-blue-700 border-blue-200">
                                  {kol.booking_code}
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            {(kol.post_count || 0) === 0 ? (
                              <Badge variant="destructive" className="text-[10px]">Chưa đăng bài</Badge>
                            ) : (
                              <Badge className="bg-green-500 hover:bg-green-600 text-[10px]">
                                Đã đăng {kol.post_count} video
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            {kol.post_links && kol.post_links.length > 0 ? (
                              <div className="flex flex-wrap gap-1">
                                {kol.post_links.map((link, i) => (
                                  <a key={i} href={link} target="_blank" rel="noopener noreferrer" className="text-[10px] bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded hover:bg-blue-100 flex items-center gap-1">
                                    <Video className="h-2.5 w-2.5" />
                                    V{i + 1}
                                  </a>
                                ))}
                              </div>
                            ) : <span className="text-muted-foreground text-[10px] italic">Đang chờ video...</span>}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-7 px-2 text-[10px] text-blue-600 border-blue-200 hover:bg-blue-50"
                                onClick={() => handleSendNotification(kol)}
                                disabled={loading}
                              >
                                <Send className={`h-3 w-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
                                Gửi mail
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-7 px-2 text-[10px]"
                                onClick={() => showDetail(kol)}
                              >
                                <Eye className="h-3 w-3 mr-1" />
                                Chi tiết
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-7 w-7 p-0 text-red-500"
                                onClick={() => handleDeleteApproved(kol.tiktok_account)}
                              >
                                <UserMinus className="h-3.5 w-3.5" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      {kols.length === 0 && !loading && (
                        <TableRow>
                          <TableCell colSpan={4} className="text-center py-12 text-muted-foreground">
                            Chưa có KOL nào được duyệt. Hãy kiểm tra tab Đăng ký mới.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="ranking" className="space-y-4 mt-6">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-semibold">Bảng xếp hạng hiệu quả</h2>
                  <p className="text-sm text-muted-foreground">Phân tích dựa trên KOL đã được duyệt</p>
                </div>
                <Button onClick={handleUpdateRanking} disabled={loading}>
                  <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  Cập nhật bảng xếp hạng
                </Button>
              </div>

              {ranking.length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center py-12">
                    <TrendingUp className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                    <p className="text-muted-foreground">Nhấn cập nhật để lấy dữ liệu xếp hạng</p>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-16">Hạng</TableHead>
                          <TableHead>KOL / Booking</TableHead>
                          <TableHead className="text-right">Video / Age</TableHead>
                          <TableHead className="text-right">Chỉ số (Thích/Cmt/Share)</TableHead>
                          <TableHead className="text-right">KOL Score</TableHead>
                          <TableHead className="text-right">Lượt xem</TableHead>
                          <TableHead className="text-right">Avg ER</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {ranking.map((kol, idx) => (
                          <TableRow key={idx}>
                            <TableCell className="font-bold">
                              {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}
                            </TableCell>
                            <TableCell className="font-medium text-xs">
                              <div className="flex flex-col">
                                <span className="font-bold">{kol.tiktok_account}</span>
                                <span className="text-[10px] text-muted-foreground">{kol.booking_code}</span>
                                <span className="text-[10px] text-muted-foreground truncate max-w-[120px]">{kol.product}</span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex flex-col items-end gap-0.5">
                                <span className="text-[10px] font-bold text-muted-foreground">{kol.total_videos || 0} videos</span>
                                {kol.scored_videos?.map((v, vIdx) => (
                                  <span key={vIdx} className="text-[9px] px-1 bg-slate-100 rounded text-slate-600">
                                    video age {Math.round(v.age_in_days)}d
                                  </span>
                                ))}
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex flex-col items-end text-[10px] text-muted-foreground">
                                <span className="flex items-center gap-1 font-mono">
                                  {formatNumber(kol.total_likes || 0)} <Heart className="w-2 h-2 text-rose-400" />
                                </span>
                                <span className="flex items-center gap-1 font-mono">
                                  {formatNumber(kol.total_comments || 0)} <MessageCircle className="w-2 h-2 text-blue-400" />
                                </span>
                                <span className="flex items-center gap-1 font-mono">
                                  {formatNumber(kol.total_shares || 0)} <Share2 className="w-2 h-2 text-green-400" />
                                </span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <Badge variant="secondary" className="font-mono font-bold text-[10px] bg-purple-50 text-purple-700 border-purple-100">
                                {kol.kol_score?.toFixed(2) || '0.00'}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right text-xs font-bold text-blue-600">
                              {formatNumber(kol.total_views || 0)}
                            </TableCell>
                            <TableCell className="text-right">
                              <Badge variant="outline" className="text-[10px] font-mono text-green-600 border-green-200">
                                {kol.avg_engagement_rate || 0}%
                              </Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Modal chi tiết KOL */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              Thông tin chi tiết KOL: {selectedKOL?.tiktok_account}
            </DialogTitle>
            <DialogDescription>
              Toàn bộ thông tin đăng ký tại Tab Booking
            </DialogDescription>
          </DialogHeader>

          {selectedKOL?.registration_info && (
            <div className="grid grid-cols-2 gap-4 mt-4">
              {selectedKOL.booking_code && (
                <div className="col-span-2 mb-2 p-2 bg-blue-50 border border-blue-100 rounded-md flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-700">MÃ BOOKING:</span>
                  <Badge className="bg-blue-600">{selectedKOL.booking_code}</Badge>
                </div>
              )}
              <div className="space-y-3">
                <DetailItem label="Thời gian đăng ký" value={selectedKOL.registration_info.timestamp} />
                <DetailItem label="TikTok ID" value={String(selectedKOL.registration_info.tiktok_id)} />
                <DetailItem label="Sản phẩm hợp tác" value={selectedKOL.registration_info.product_choice} />
                <DetailItem label="Email" value={selectedKOL.registration_info.email} />
              </div>
              <div className="space-y-3">
                <DetailItem label="Số điện thoại" value={selectedKOL.registration_info.phone} />
                <DetailItem label="Địa chỉ nhận hàng" value={selectedKOL.registration_info.address} />
                <DetailItem label="Hợp tác miễn phí" value={selectedKOL.registration_info.is_free} />
                <DetailItem label="Cần hỗ trợ Ads" value={selectedKOL.registration_info.need_ads} />
              </div>
              <div className="col-span-2 pt-2">
                <a
                  href={formatTikTokLink(selectedKOL.tiktok_link)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full inline-flex items-center justify-center gap-2 bg-black text-white py-2 rounded-md hover:bg-black/90 transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  Ghé thăm kênh TikTok
                </a>
              </div>
            </div>
          )}
          {!selectedKOL?.registration_info && (
            <div className="py-10 text-center text-muted-foreground italic">
              KOL này dường như được thêm thủ công hoặc không có thông tin đăng ký gốc.
            </div>
          )}
        </DialogContent>
      </Dialog>
    </DashboardShell>
  )
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</span>
      <span className="text-sm font-medium border-l-2 border-primary/20 pl-2 py-1 bg-muted/30 rounded-r-sm">{value}</span>
    </div>
  )
}
