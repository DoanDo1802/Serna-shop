'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { DashboardShell } from '@/components/dashboard-shell'
import { RefreshCw, CheckCircle2, XCircle, AlertCircle, Edit } from 'lucide-react'

interface CookieStatus {
  exists: boolean
  valid: boolean
  updated_at: string | null
  source: 'auto' | 'env' | null
  account_name: string | null
}

interface CookieStatusResponse {
  kalodata: CookieStatus
  tiktok: CookieStatus
}

export default function SettingsPage() {
  const [status, setStatus] = useState<CookieStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [manualDialogOpen, setManualDialogOpen] = useState(false)
  const [manualPlatform, setManualPlatform] = useState<'kalodata' | 'tiktok'>('tiktok')
  const [manualCookie, setManualCookie] = useState('')
  const [savingManual, setSavingManual] = useState(false)

  const fetchStatus = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:5000/api/cookies/status')
      const data = await response.json()
      
      if (data.success) {
        setStatus(data.status)
      } else {
        setError(data.error || 'Không thể lấy trạng thái cookie')
      }
    } catch (err) {
      setError('Không thể kết nối đến backend')
    } finally {
      setLoading(false)
    }
  }

  const refreshCookie = async (platform: 'kalodata' | 'tiktok' | 'all', force: boolean = false) => {
    try {
      setRefreshing(platform)
      setError(null)
      setSuccess(null)

      const response = await fetch('http://localhost:5000/api/cookies/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ platform, force }),
      })

      const data = await response.json()

      if (data.success) {
        // Build success message with account names
        let successMsg = ''
        if (platform === 'all') {
          const messages = []
          if (data.results.kalodata?.success) {
            const accountName = data.results.kalodata.account_name
            messages.push(`Kalodata${accountName ? ` (${accountName})` : ''}`)
          }
          if (data.results.tiktok?.success) {
            const accountName = data.results.tiktok.account_name
            messages.push(`TikTok${accountName ? ` (@${accountName})` : ''}`)
          }
          successMsg = `✅ Cookie có sẵn: ${messages.join(', ')}`
        } else {
          const result = data.results[platform]
          const accountName = result?.account_name
          if (accountName) {
            successMsg = `✅ Cookie ${platform} có sẵn - Tài khoản: ${platform === 'tiktok' ? '@' : ''}${accountName}`
          } else {
            successMsg = `✅ Cookie ${platform} có sẵn (chưa có tên tài khoản)`
          }
        }
        
        setSuccess(successMsg)
        await fetchStatus()
      } else {
        const errors = Object.entries(data.results || {})
          .filter(([_, result]: any) => !result.success)
          .map(([platform, result]: any) => `${platform}: ${result.error}`)
          .join(', ')
        setError(errors || data.error || 'Không thể kiểm tra cookie')
      }
    } catch (err) {
      setError('Không thể kết nối đến backend')
    } finally {
      setRefreshing(null)
    }
  }

  const saveManualCookie = async () => {
    try {
      setSavingManual(true)
      setError(null)
      setSuccess(null)

      const response = await fetch('http://localhost:5000/api/cookies/manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform: manualPlatform,
          cookie: manualCookie,
        }),
      })

      const data = await response.json()

      if (data.success) {
        setSuccess(`Đã lưu cookie ${manualPlatform} thành công! (${data.cookie_count} cookies)`)
        setManualDialogOpen(false)
        setManualCookie('')
        await fetchStatus()
      } else {
        setError(data.error || 'Không thể lưu cookie')
      }
    } catch (err) {
      setError('Không thể kết nối đến backend')
    } finally {
      setSavingManual(false)
    }
  }

  const openManualDialog = (platform: 'kalodata' | 'tiktok') => {
    setManualPlatform(platform)
    setManualCookie('')
    setManualDialogOpen(true)
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Chưa có'
    try {
      return new Date(dateStr).toLocaleString('vi-VN')
    } catch {
      return 'Không xác định'
    }
  }

  const getStatusBadge = (cookieStatus: CookieStatus) => {
    if (!cookieStatus.exists) {
      return <Badge variant="destructive" className="gap-1"><XCircle className="h-3 w-3" /> Chưa có</Badge>
    }
    if (cookieStatus.valid) {
      return <Badge variant="default" className="gap-1 bg-green-600"><CheckCircle2 className="h-3 w-3" /> Hợp lệ</Badge>
    }
    return <Badge variant="secondary" className="gap-1"><AlertCircle className="h-3 w-3" /> Không hợp lệ</Badge>
  }

  const getSourceBadge = (source: string | null) => {
    if (source === 'auto') {
      return <Badge variant="outline" className="gap-1">🤖 Tự động</Badge>
    }
    if (source === 'env') {
      return <Badge variant="outline" className="gap-1">📝 Thủ công</Badge>
    }
    return <Badge variant="outline">-</Badge>
  }

  if (loading) {
    return (
      <DashboardShell>
        <div className="flex items-center justify-center h-screen">
          <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </DashboardShell>
    )
  }

  return (
    <DashboardShell>
      <div className="flex-1 overflow-auto">
        <div className="p-8 space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Cài Đặt</h1>
            <p className="text-gray-500 mt-2">Quản lý cookie và cấu hình hệ thống</p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="border-green-600 bg-green-50">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-6 md:grid-cols-2">
        {/* Kalodata Cookie */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Kalodata Cookie</span>
              {status && getStatusBadge(status.kalodata)}
            </CardTitle>
            <CardDescription>
              Cookie để truy cập dữ liệu KOL từ Kalodata
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2 text-sm">
              {status?.kalodata.account_name && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">Tài khoản:</span>
                  <span className="font-semibold text-blue-600">
                    {status.kalodata.account_name}
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-500">Nguồn:</span>
                {status && getSourceBadge(status.kalodata.source)}
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Cập nhật lần cuối:</span>
                <span className="font-mono text-xs">
                  {status && formatDate(status.kalodata.updated_at)}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => refreshCookie('kalodata', false)}
                disabled={refreshing !== null}
                className="flex-1"
                variant="outline"
              >
                {refreshing === 'kalodata' ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Đang kiểm tra...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Kiểm tra
                  </>
                )}
              </Button>
            </div>

            <Button
              onClick={() => openManualDialog('kalodata')}
              disabled={refreshing !== null}
              variant="ghost"
              className="w-full"
            >
              <Edit className="mr-2 h-4 w-4" />
              Nhập cookie mới
            </Button>

            <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
              💡 <strong>Kiểm tra:</strong> Xem cookie còn hạn không<br />
              💡 <strong>Nhập mới:</strong> Đổi tài khoản hoặc cập nhật cookie
            </div>
          </CardContent>
        </Card>

        {/* TikTok Cookie */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>TikTok Cookie</span>
              {status && getStatusBadge(status.tiktok)}
            </CardTitle>
            <CardDescription>
              Cookie để truy cập dữ liệu và gửi tin nhắn TikTok
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2 text-sm">
              {status?.tiktok.account_name && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">Tài khoản:</span>
                  <span className="font-semibold text-blue-600">
                    @{status.tiktok.account_name}
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-500">Nguồn:</span>
                {status && getSourceBadge(status.tiktok.source)}
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Cập nhật lần cuối:</span>
                <span className="font-mono text-xs">
                  {status && formatDate(status.tiktok.updated_at)}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => refreshCookie('tiktok', false)}
                disabled={refreshing !== null}
                className="flex-1"
                variant="outline"
              >
                {refreshing === 'tiktok' ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Đang kiểm tra...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Kiểm tra
                  </>
                )}
              </Button>
            </div>

            <Button
              onClick={() => openManualDialog('tiktok')}
              disabled={refreshing !== null}
              variant="ghost"
              className="w-full"
            >
              <Edit className="mr-2 h-4 w-4" />
              Nhập cookie mới
            </Button>

            <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
              💡 <strong>Kiểm tra:</strong> Xem cookie còn hạn không<br />
              💡 <strong>Nhập mới:</strong> Đổi tài khoản hoặc cập nhật cookie
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Thao Tác Nhanh</CardTitle>
          <CardDescription>
            Kiểm tra tất cả cookies cùng lúc
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={() => refreshCookie('all', false)}
            disabled={refreshing !== null}
            size="lg"
            className="w-full"
          >
            {refreshing === 'all' ? (
              <>
                <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                Đang kiểm tra tất cả...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-5 w-5" />
                Kiểm tra tất cả
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Hướng Dẫn</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <h4 className="font-semibold mb-2">🔍 Kiểm Tra Cookie</h4>
            <p className="text-gray-600">
              Khi bạn nhấn "Kiểm tra", hệ thống sẽ:
            </p>
            <ul className="list-disc list-inside text-gray-600 ml-4 mt-2 space-y-1">
              <li>Kiểm tra cookie có tồn tại trong hệ thống không</li>
              <li>Hiển thị tên tài khoản (nếu đã lưu)</li>
              <li>KHÔNG gọi API thật để xác thực</li>
              <li>KHÔNG mở trình duyệt</li>
            </ul>
            <p className="text-gray-600 mt-2 text-xs italic">
              ⚠️ Nếu cookie vẫn dùng được nhưng "Kiểm tra" báo lỗi, đừng lo - cookie vẫn hoạt động bình thường!
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-2">✏️ Nhập Cookie Mới</h4>
            <p className="text-gray-600">
              Dùng khi muốn đổi tài khoản hoặc cookie hết hạn:
            </p>
            <ol className="list-decimal list-inside text-gray-600 ml-4 mt-2 space-y-1">
              <li>Mở TikTok/Kalodata trên trình duyệt thường</li>
              <li>Đăng nhập tài khoản bạn muốn dùng</li>
              <li>Nhấn F12 → Tab Console</li>
              <li>Paste: <code className="bg-gray-200 px-1 rounded">copy(document.cookie)</code></li>
              <li>Click "Nhập cookie mới" → Paste → Lưu</li>
            </ol>
          </div>

          <div>
            <h4 className="font-semibold mb-2">🤖 Nguồn Cookie</h4>
            <ul className="list-disc list-inside text-gray-600 ml-4 space-y-1">
              <li><strong>Tự động:</strong> Cookie được nhập qua form hoặc script</li>
              <li><strong>Thủ công:</strong> Cookie được nhập trực tiếp vào .env</li>
            </ul>
          </div>

          <div className="bg-blue-50 p-4 rounded border border-blue-200">
            <p className="text-blue-800">
              <strong>💡 Lưu ý:</strong> Nếu TikTok block (Maximum attempts), 
              hãy dùng "Nhập cookie mới" thay vì script tự động.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Manual Cookie Input Dialog */}
      <Dialog open={manualDialogOpen} onOpenChange={setManualDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Nhập Cookie Thủ Công - {manualPlatform === 'kalodata' ? 'Kalodata' : 'TikTok'}</DialogTitle>
            <DialogDescription>
              Paste cookie string từ trình duyệt của bạn vào đây
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Cookie String</label>
              <Textarea
                value={manualCookie}
                onChange={(e) => setManualCookie(e.target.value)}
                placeholder="name1=value1; name2=value2; name3=value3; ..."
                rows={8}
                className="font-mono text-xs break-all whitespace-pre-wrap overflow-y-auto resize-none"
                style={{ 
                  wordBreak: 'break-all', 
                  overflowWrap: 'anywhere',
                  maxHeight: '200px'
                }}
              />
              <p className="text-xs text-gray-500 mt-2">
                Số ký tự: {manualCookie.length}
              </p>
            </div>

            <div className="bg-blue-50 p-4 rounded border border-blue-200 text-sm">
              <p className="font-semibold mb-2">📝 Cách lấy cookie:</p>
              <ol className="list-decimal list-inside space-y-1 text-gray-700">
                <li>Mở {manualPlatform === 'kalodata' ? 'Kalodata' : 'TikTok'} trên trình duyệt thường</li>
                <li>Đăng nhập tài khoản của bạn</li>
                <li>Nhấn F12 → Tab Console</li>
                <li>Paste: <code className="bg-gray-200 px-1 rounded">copy(document.cookie)</code></li>
                <li>Nhấn Enter → Cookie đã được copy!</li>
                <li>Paste vào ô trên</li>
              </ol>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setManualDialogOpen(false)}
              disabled={savingManual}
            >
              Hủy
            </Button>
            <Button
              onClick={saveManualCookie}
              disabled={savingManual || manualCookie.length < 50}
            >
              {savingManual ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Đang lưu...
                </>
              ) : (
                'Lưu Cookie'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
        </div>
      </div>
    </DashboardShell>
  )
}
