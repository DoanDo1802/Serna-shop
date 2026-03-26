'use client'

import { useState, useEffect } from 'react'
import { Plus, Pencil, Trash2, Search, Package, ImageIcon, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { DashboardShell } from '@/components/dashboard-shell'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  type Product as ProductType,
} from '@/lib/api'

type Product = ProductType

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(true)
  const [viewingProduct, setViewingProduct] = useState<Product | null>(null)
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    specifications: '',
    price: '',
    status: 'in_stock' as 'in_stock' | 'out_of_stock',
    image: '',
  })

  const { toast } = useToast()

  // Load products from backend
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const result = await getProducts()
        if (result.success) {
          setProducts(result.products)
        }
      } catch (error) {
        console.error('Load products error:', error)
        toast({
          title: 'Không thể tải dữ liệu',
          description: error instanceof Error ? error.message : 'Vui lòng kiểm tra backend.',
          variant: 'destructive',
        })
      } finally {
        setLoadingData(false)
      }
    }

    void loadProducts()
  }, [toast])

  const handleOpenDialog = (product?: Product) => {
    if (product) {
      setEditingProduct(product)
      setFormData({
        name: product.name,
        description: product.description,
        specifications: product.specifications,
        price: product.price.toString(),
        status: product.status,
        image: product.image || '',
      })
    } else {
      setEditingProduct(null)
      setFormData({
        name: '',
        description: '',
        specifications: '',
        price: '',
        status: 'in_stock',
        image: '',
      })
    }
    setDialogOpen(true)
  }

  const handleSaveProduct = async () => {
    if (!formData.name || !formData.price) {
      toast({
        title: 'Thiếu thông tin',
        description: 'Vui lòng nhập tên và giá sản phẩm',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      const productData = {
        name: formData.name,
        description: formData.description,
        specifications: formData.specifications,
        price: parseFloat(formData.price),
        status: formData.status,
        image: formData.image || undefined,
      }

      if (editingProduct) {
        // Update existing product
        const result = await updateProduct(editingProduct.id, productData)
        if (result.success) {
          setProducts(prev => prev.map(p => p.id === editingProduct.id ? result.product : p))
          toast({
            title: 'Đã cập nhật',
            description: 'Sản phẩm đã được cập nhật thành công',
          })
        } else {
          throw new Error(result.error || 'Không thể cập nhật sản phẩm')
        }
      } else {
        // Add new product
        const result = await createProduct(productData)
        if (result.success) {
          setProducts(prev => [result.product, ...prev])
          toast({
            title: 'Đã thêm',
            description: 'Sản phẩm mới đã được thêm thành công',
          })
        } else {
          throw new Error(result.error || 'Không thể thêm sản phẩm')
        }
      }
      setDialogOpen(false)
    } catch (error) {
      console.error('Save product error:', error)
      toast({
        title: 'Lỗi',
        description: error instanceof Error ? error.message : 'Không thể lưu sản phẩm',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteProduct = async (id: string) => {
    try {
      const result = await deleteProduct(id)
      if (result.success) {
        setProducts(prev => prev.filter(p => p.id !== id))
        toast({
          title: 'Đã xóa',
          description: 'Sản phẩm đã được xóa',
        })
      } else {
        throw new Error(result.error || 'Không thể xóa sản phẩm')
      }
    } catch (error) {
      console.error('Delete product error:', error)
      toast({
        title: 'Lỗi',
        description: error instanceof Error ? error.message : 'Không thể xóa sản phẩm',
        variant: 'destructive',
      })
    }
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = () => {
      setFormData(prev => ({ ...prev, image: reader.result as string }))
    }
    reader.readAsDataURL(file)
  }

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(value)
  }

  return (
    <DashboardShell>
      <div className="flex-1 flex flex-col bg-background">
      {/* Header */}
      <div className="px-8 py-6 border-b border-border">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-3xl font-bold text-foreground">Quản lý sản phẩm</h2>
            <p className="text-muted-foreground text-sm mt-1">
              {products.length > 0
                ? `Đang hiển thị ${filteredProducts.length} / ${products.length} sản phẩm`
                : 'Chưa có sản phẩm nào'}
            </p>
          </div>
          <Button onClick={() => handleOpenDialog()} className="gap-2">
            <Plus className="w-4 h-4" />
            Thêm sản phẩm
          </Button>
        </div>

        {/* Search */}
        <div className="flex items-center gap-3 bg-card px-4 py-2 rounded-lg border border-border hover:border-border/70 transition-colors">
          <Search className="w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Tìm kiếm sản phẩm..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground text-sm"
          />
        </div>
      </div>

      {/* Products Grid */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {loadingData ? (
          <div className="flex flex-col items-center justify-center h-full py-20">
            <Loader2 className="w-10 h-10 animate-spin text-muted-foreground/60 mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">Đang tải dữ liệu</h3>
            <p className="text-muted-foreground">Vui lòng đợi trong giây lát...</p>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-20">
            <Package className="w-16 h-16 text-muted-foreground/30 mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">
              {products.length === 0 ? 'Chưa có sản phẩm' : 'Không tìm thấy sản phẩm'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {products.length === 0
                ? 'Nhấn nút "Thêm sản phẩm" để bắt đầu'
                : 'Thử tìm kiếm với từ khóa khác'}
            </p>
            {products.length === 0 && (
              <Button onClick={() => handleOpenDialog()} className="gap-2">
                <Plus className="w-4 h-4" />
                Thêm sản phẩm đầu tiên
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-card border border-border rounded-xl overflow-hidden hover:shadow-lg transition-all group"
              >
                {/* Image */}
                <div className="aspect-square bg-muted relative overflow-hidden">
                  {product.image ? (
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <ImageIcon className="w-16 h-16 text-muted-foreground/30" />
                    </div>
                  )}
                  <div className="absolute top-2 right-2">
                    <Badge variant={product.status === 'in_stock' ? 'default' : 'secondary'}>
                      {product.status === 'in_stock' ? 'Còn hàng' : 'Hết hàng'}
                    </Badge>
                  </div>
                </div>

                {/* Content */}
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="font-semibold text-foreground line-clamp-1">{product.name}</h3>
                    <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                      {product.description}
                    </p>
                    {product.specifications && (
                      <div className="mt-2 pt-2 border-t border-border">
                        <p className="text-xs text-muted-foreground font-medium mb-1">Thông số:</p>
                        <p className="text-xs text-muted-foreground line-clamp-2 whitespace-pre-wrap">
                          {product.specifications}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-border">
                    <span className="text-lg font-bold text-foreground">
                      {formatCurrency(product.price)}
                    </span>
                    <div className="flex gap-1 transition-opacity">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setViewingProduct(product)}
                        className="h-8 w-8 p-0"
                        title="Xem chi tiết"
                      >
                        <Package className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleOpenDialog(product)}
                        className="h-8 w-8 p-0"
                        title="Chỉnh sửa"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeleteProduct(product.id)}
                        className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingProduct ? 'Chỉnh sửa sản phẩm' : 'Thêm sản phẩm mới'}</DialogTitle>
            <DialogDescription>
              {editingProduct ? 'Cập nhật thông tin sản phẩm' : 'Nhập thông tin sản phẩm mới'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                Tên sản phẩm <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                placeholder="Nhập tên sản phẩm"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Mô tả</Label>
              <Textarea
                id="description"
                placeholder="Mô tả chi tiết về sản phẩm"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="min-h-[80px] resize-none"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="specifications">Thông số kỹ thuật</Label>
              <Textarea
                id="specifications"
                placeholder="Ví dụ:&#10;• Kích thước: 15 x 10 cm&#10;• Trọng lượng: 200g&#10;• Chất liệu: Cotton 100%&#10;• Xuất xứ: Việt Nam"
                value={formData.specifications}
                onChange={(e) => setFormData(prev => ({ ...prev, specifications: e.target.value }))}
                className="min-h-[120px] resize-none text-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="price">
                  Giá (VND) <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="price"
                  type="number"
                  placeholder="150000"
                  value={formData.price}
                  onChange={(e) => setFormData(prev => ({ ...prev, price: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Trạng thái</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value: 'in_stock' | 'out_of_stock') =>
                    setFormData(prev => ({ ...prev, status: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="in_stock">Còn hàng</SelectItem>
                    <SelectItem value="out_of_stock">Hết hàng</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Hình ảnh sản phẩm</Label>
              <div className="space-y-3">
                {formData.image && (
                  <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-border">
                    <img
                      src={formData.image}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <label className="flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-dashed border-border bg-background/50 text-sm cursor-pointer hover:border-primary/50 hover:bg-accent/50 transition-all">
                  <ImageIcon className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">
                    {formData.image ? 'Thay đổi ảnh' : 'Chọn ảnh sản phẩm'}
                  </span>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                </label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} disabled={loading}>
              Hủy
            </Button>
            <Button type="button" onClick={handleSaveProduct} disabled={loading} className="gap-2">
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Đang lưu...
                </>
              ) : (
                <>
                  {editingProduct ? 'Cập nhật' : 'Thêm sản phẩm'}
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Product Detail Dialog */}
      <Dialog open={!!viewingProduct} onOpenChange={() => setViewingProduct(null)}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Chi tiết sản phẩm</DialogTitle>
          </DialogHeader>

          {viewingProduct && (
            <div className="space-y-6">
              {/* Image */}
              {viewingProduct.image && (
                <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-border">
                  <img
                    src={viewingProduct.image}
                    alt={viewingProduct.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Info */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-2xl font-bold text-foreground">{viewingProduct.name}</h3>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-2xl font-bold text-foreground">
                      {formatCurrency(viewingProduct.price)}
                    </span>
                    <Badge variant={viewingProduct.status === 'in_stock' ? 'default' : 'secondary'}>
                      {viewingProduct.status === 'in_stock' ? 'Còn hàng' : 'Hết hàng'}
                    </Badge>
                  </div>
                </div>

                {viewingProduct.description && (
                  <div>
                    <h4 className="text-sm font-semibold text-foreground mb-2">Mô tả</h4>
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                      {viewingProduct.description}
                    </p>
                  </div>
                )}

                {viewingProduct.specifications && (
                  <div>
                    <h4 className="text-sm font-semibold text-foreground mb-2">Thông số kỹ thuật</h4>
                    <div className="rounded-lg bg-muted/50 border border-border p-4">
                      <pre className="text-sm text-foreground whitespace-pre-wrap font-sans leading-relaxed">
                        {viewingProduct.specifications}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setViewingProduct(null)}>
              Đóng
            </Button>
            <Button type="button" onClick={() => {
              setViewingProduct(null)
              handleOpenDialog(viewingProduct!)
            }} className="gap-2">
              <Pencil className="w-4 h-4" />
              Chỉnh sửa
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </DashboardShell>
  )
}
