'use client'

import { useState, useEffect } from 'react'
import { syncKOLData, getKOLRanking, type KOL } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { RefreshCw, TrendingUp, ExternalLink, Video } from 'lucide-react'
import { DashboardShell } from '@/components/dashboard-shell'

export default function KOLManagementPage() {
  const [kols, setKols] = useState<KOL[]>([])
  const [ranking, setRanking] = useState<KOL[]>([])
  const [loading, setLoading] = useState(false)
  const [sheetUrl, setSheetUrl] = useState('https://docs.google.com/spreadsheets/d/1o6qMdV7bQ7ADDG8llRD1oy58iwfaa3mhFRR3DtsmutE/edit')
  const [activeTab, setActiveTab] = useState('management')

  const loadKOLData = async (fetchStats = false) => {
    setLoading(true)
    try {
      const result = await syncKOLData(sheetUrl, 'KOL_management', fetchStats)
      if (result.success && result.kols) {
        setKols(result.kols)
      }
    } catch (error) {
      console.error('Error loading KOL data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadRanking = async () => {
    setLoading(true)
    try {
      const result = await getKOLRanking(sheetUrl, 'KOL_management')
      if (result.success && result.ranking) {
        setRanking(result.ranking)
        
        // Hiển thị thông báo nếu có KOL không có stats
        const kolsWithoutStats = result.ranking.filter(k => 
          !k.total_stats || k.total_stats.total_engagement === 0
        )
        
        if (kolsWithoutStats.length > 0) {
          console.warn(`⚠️ ${kolsWithoutStats.length} KOL không có stats hoặc chưa đăng video`)
        }
      } else {
        throw new Error(result.error || 'Không thể tải bảng xếp hạng')
      }
    } catch (error) {
      console.error('Error loading ranking:', error)
      alert(`Lỗi: ${error instanceof Error ? error.message : 'Không thể tải bảng xếp hạng'}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadKOLData(false)
  }, [])

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num.toString()
  }

  return (
    <DashboardShell>
      <div className="flex-1 flex flex-col bg-background">
        {/* Header */}
        <div className="px-8 py-6 border-b border-border">
          <div className="flex items-center justify-between gap-4 mb-6">
            <div>
              <h2 className="text-3xl font-bold text-foreground">Quản lý KOL</h2>
              <p className="text-muted-foreground text-sm mt-1">
                Theo dõi và đánh giá hiệu suất KOL
              </p>
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Google Sheet URL"
                value={sheetUrl}
                onChange={(e) => setSheetUrl(e.target.value)}
                className="w-96"
              />
              <Button onClick={() => loadKOLData(false)} disabled={loading}>
                <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Đồng bộ
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="management">Quản lý KOL</TabsTrigger>
              <TabsTrigger value="ranking">Bảng xếp hạng</TabsTrigger>
            </TabsList>

            <TabsContent value="management" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Danh sách KOL</CardTitle>
              <CardDescription>
                Theo dõi trạng thái đăng bài của các KOL
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>TikTok Account</TableHead>
                    <TableHead>Sản phẩm</TableHead>
                    <TableHead>Số bài đăng</TableHead>
                    <TableHead>Trạng thái</TableHead>
                    <TableHead>Link bài đăng</TableHead>
                    <TableHead>Hành động</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {kols.map((kol, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="font-medium">
                        <a
                          href={kol.tiktok_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 hover:underline"
                        >
                          {kol.tiktok_account}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </TableCell>
                      <TableCell>{kol.product || '-'}</TableCell>
                      <TableCell>
                        <Badge variant={kol.post_count > 0 ? 'default' : 'secondary'}>
                          {kol.post_count} video
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {kol.post_count === 0 ? (
                          <Badge variant="destructive">Chưa đăng</Badge>
                        ) : (
                          <Badge variant="success">Đã đăng</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {kol.post_links.length > 0 ? (
                          <div className="flex flex-col gap-1">
                            {kol.post_links.map((link, i) => (
                              <a
                                key={i}
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                              >
                                <Video className="h-3 w-3" />
                                Video {i + 1}
                              </a>
                            ))}
                          </div>
                        ) : (
                          <span className="text-muted-foreground text-sm">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            // TODO: Xem chi tiết stats
                          }}
                        >
                          Chi tiết
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
            </TabsContent>

            <TabsContent value="ranking" className="space-y-4 mt-6">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-semibold">Bảng xếp hạng KOL</h2>
                  <p className="text-sm text-muted-foreground">
                  </p>
                </div>
                <Button onClick={loadRanking} disabled={loading}>
                  <TrendingUp className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  {loading ? 'Đang tải...' : 'Tải bảng xếp hạng'}
                </Button>
              </div>

              {ranking.length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center py-12">
                    <TrendingUp className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
                    <p className="text-muted-foreground">
                      Click "Tải bảng xếp hạng" để xem thống kê
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Quá trình này có thể mất vài phút để lấy stats từ TikTok
                    </p>
                  </CardContent>
                </Card>
              ) : (

              <Card>
                <CardContent className="pt-6">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">Hạng</TableHead>
                        <TableHead>TikTok Account</TableHead>
                        <TableHead>Sản phẩm</TableHead>
                        <TableHead className="text-right">KOL Score</TableHead>
                        <TableHead className="text-right">Videos</TableHead>
                        <TableHead className="text-right">Lượt xem</TableHead>
                        <TableHead className="text-right">Likes</TableHead>
                        <TableHead className="text-right">Tổng Engagement</TableHead>
                        <TableHead className="text-right">Avg ER (%)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {ranking.map((kol) => (
                        <TableRow key={kol.rank}>
                          <TableCell className="font-bold">
                            {kol.rank === 1 && '🥇'}
                            {kol.rank === 2 && '🥈'}
                            {kol.rank === 3 && '🥉'}
                            {kol.rank! > 3 && `#${kol.rank}`}
                          </TableCell>
                          <TableCell className="font-medium">
                            <a
                              href={kol.tiktok_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:underline"
                            >
                              {kol.tiktok_account}
                            </a>
                          </TableCell>
                          <TableCell>{kol.product || '-'}</TableCell>
                          <TableCell className="text-right">
                            <Badge variant="default" className="font-mono font-bold">
                              {kol.kol_score?.toFixed(2) || '0.00'}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <Badge variant="outline">
                              {kol.total_scored_videos || 0}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            {formatNumber(kol.total_stats?.views || 0)}
                          </TableCell>
                          <TableCell className="text-right">
                            {formatNumber(kol.total_stats?.likes || 0)}
                          </TableCell>
                          <TableCell className="text-right font-bold">
                            {formatNumber(kol.total_stats?.total_engagement || 0)}
                          </TableCell>
                          <TableCell className="text-right">
                            <Badge variant="outline">
                              {kol.total_stats?.avg_engagement_rate?.toFixed(2) || '0.00'}%
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
    </DashboardShell>
  )
}
