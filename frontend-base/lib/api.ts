// API client cho backend KOL Data

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface KalodataExportParams {
  start_date?: string;
  end_date?: string;
  revenue_min?: number;
  revenue_max?: number;
  age_range?: string;
  page_size?: number;
  enrich?: boolean; // Có lấy thêm dữ liệu follower không
  deduplicate?: boolean;
  filters?: Record<string, string | string[]>; // Kalodata advanced filters
}

export interface AgentSuggestParams {
  description: string;
  price?: string;
  image?: string; // base64
  image_url?: string;
}

export interface AgentSuggestResponse {
  success: boolean;
  explanation?: string;
  filters?: Record<string, string | string[]>;
  raw?: string;
  error?: string;
}

export interface KalodataCreator {
  period: string;
  name: string;
  followers: number;
  revenue_livestream: number;
  revenue_video: number;
  kalodata_url: string;
  tiktok_url: string;
  age_range: string;
  gender: string;
  engagement_rate: number;
}

export interface KalodataApiResponse {
  success: boolean;
  data: KalodataCreator[];
  count: number;
  new_records?: KalodataCreator[];
  new_count?: number;
  duplicate_count?: number;
  updated_at?: string | null;
  last_crawl?: {
    file_path?: string;
    ran_at?: string;
    params?: KalodataExportParams;
    deduplicate?: boolean;
    new_count?: number;
    duplicate_count?: number;
    stored_count?: number;
  } | null;
  error?: string;
}

export interface TikTokVideo {
  id: string;
  title: string;
  thumbnail: string;
  url: string;
}

async function parseApiResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
  const text = await response.text();
  let payload: unknown = null;

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    if (payload && typeof payload === 'object' && 'error' in payload) {
      throw new Error(String((payload as { error: string }).error));
    }

    if (typeof payload === 'string' && payload.trim()) {
      throw new Error(payload);
    }

    throw new Error(fallbackMessage);
  }

  return payload as T;
}

// Kalodata APIs
export async function exportKalodata(params: KalodataExportParams): Promise<KalodataApiResponse> {
  const response = await fetch(`${API_BASE_URL}/api/kalodata/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  return parseApiResponse<KalodataApiResponse>(response, 'Failed to export Kalodata');
}

export async function getSavedKalodata(): Promise<KalodataApiResponse> {
  const response = await fetch(`${API_BASE_URL}/api/kalodata/data`, {
    cache: 'no-store',
  });

  return parseApiResponse<KalodataApiResponse>(response, 'Failed to load saved Kalodata data');
}

export async function deleteKalodataCreators(names: string[]): Promise<{ success: boolean; deleted_count: number; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/kalodata/delete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ names }),
  });

  return parseApiResponse<{ success: boolean; deleted_count: number; error?: string }>(response, 'Failed to delete creators');
}

export async function uploadToSheets(excelPath: string, sheetUrl: string, sheetName = 'Sheet1') {
  const response = await fetch(`${API_BASE_URL}/api/kalodata/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      excel_path: excelPath,
      google_sheet_url: sheetUrl,
      sheet_name: sheetName,
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to upload to Google Sheets');
  }
  
  return response.json();
}

// TikTok APIs
export async function getTikTokVideos(profileUrl: string) {
  const response = await fetch(`${API_BASE_URL}/api/tiktok/videos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_url: profileUrl }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get TikTok videos');
  }
  
  return response.json();
}

export async function getTikTokUserId(profileUrl: string) {
  const response = await fetch(`${API_BASE_URL}/api/tiktok/userid`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_url: profileUrl }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to get TikTok user ID');
  }
  
  return response.json();
}

export async function sendTikTokDM(profileUrl: string, message: string) {
  const response = await fetch(`${API_BASE_URL}/api/tiktok/send-dm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_url: profileUrl, message }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to send TikTok DM');
  }
  
  return response.json();
}

export async function sendBatchTikTokDM(users: Array<{ profile_url: string; message: string }>) {
  const response = await fetch(`${API_BASE_URL}/api/tiktok/batch-dm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ users }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to send batch TikTok DM');
  }
  
  return response.json();
}

// Agent APIs
export async function agentSuggestFilters(params: AgentSuggestParams): Promise<AgentSuggestResponse> {
  const response = await fetch(`${API_BASE_URL}/api/agent/suggest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  return parseApiResponse<AgentSuggestResponse>(response, 'Failed to get agent suggestions');
}

// Health check
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}

// ============= PRODUCT APIs =============

export interface Product {
  id: string
  name: string
  description: string
  specifications: string
  price: number
  status: 'in_stock' | 'out_of_stock'
  image?: string
  createdAt: string
  updatedAt?: string
}

export interface ProductsResponse {
  success: boolean
  products: Product[]
  count: number
  updated_at?: string
  error?: string
}

export async function getProducts(): Promise<ProductsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/products`, {
    cache: 'no-store',
  });
  return parseApiResponse<ProductsResponse>(response, 'Failed to load products');
}

export async function getProduct(id: string): Promise<{ success: boolean; product: Product; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/products/${id}`, {
    cache: 'no-store',
  });
  return parseApiResponse(response, 'Failed to load product');
}

export async function createProduct(product: Omit<Product, 'id' | 'createdAt'>): Promise<{ success: boolean; product: Product; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(product),
  });
  return parseApiResponse(response, 'Failed to create product');
}

export async function updateProduct(id: string, product: Omit<Product, 'id' | 'createdAt'>): Promise<{ success: boolean; product: Product; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(product),
  });
  return parseApiResponse(response, 'Failed to update product');
}

export async function deleteProduct(id: string): Promise<{ success: boolean; message?: string; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/products/${id}`, {
    method: 'DELETE',
  });
  return parseApiResponse(response, 'Failed to delete product');
}

export async function batchDeleteProducts(ids: string[]): Promise<{ success: boolean; deleted_count: number; remaining_count: number; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/products/batch-delete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids }),
  });
  return parseApiResponse(response, 'Failed to delete products');
}

// ============= KOL MANAGEMENT APIs =============

export interface VideoStats {
  video_id: string
  video_url: string
  likes: number
  comments: number
  shares: number
  views: number
  engagement_rate: number
  posted_at?: string // ISO timestamp
  days_since_posted?: number // Số ngày kể từ khi đăng
  error?: string
}

export interface TotalStats {
  likes: number
  comments: number
  shares: number
  views: number
  total_engagement: number
  avg_engagement_rate: number
}

export interface KOL {
  tiktok_account: string
  tiktok_link: string
  product?: string
  post_links?: string[]
  post_count: number
  rank?: number
  kol_score?: number
  total_scored_videos?: number
  total_stats?: {
    likes: number
    comments: number
    shares: number
    saves: number
    views: number
    total_engagement: number
    avg_engagement_rate: number
  }
  total_videos?: number
  total_views?: number
  total_likes?: number
  total_comments?: number
  total_shares?: number
  total_engagement?: number
  avg_engagement_rate?: number
  latest_video_age?: number
  scored_videos?: any[]
  registration_info?: any
  booking_code?: string
}

export interface BookingRegistration {
  timestamp: string;
  product: string;
  tiktok_id: string;
  tiktok_link: string;
  email: string;
  phone: string;
  address: string;
  free_sample: string;
  ads_support: string;
  is_booking?: boolean;
}

export interface KOLResponse {
  success: boolean;
  kols?: KOL[];
  bookings?: BookingRegistration[];
  ranking?: KOL[];
  total: number;
  from_cache?: boolean;
  error?: string;
}

export async function syncKOLData(spreadsheetUrl: string, sheetName = 'KOL_management', fetchStats = false): Promise<KOLResponse> {
  const response = await fetch(`${API_BASE_URL}/api/kol/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      spreadsheet_url: spreadsheetUrl,
      sheet_name: sheetName,
      fetch_stats: fetchStats,
    }),
  });
  return parseApiResponse<KOLResponse>(response, 'Failed to sync KOL data');
}

export async function getWorksheets(spreadsheetUrl: string): Promise<{ success: boolean; worksheets: string[]; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/worksheets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      spreadsheet_url: spreadsheetUrl,
    }),
  });
  return parseApiResponse(response, 'Failed to get worksheets');
}

export async function getKOLRanking(): Promise<KOLResponse> {
  const response = await fetch(`${API_BASE_URL}/api/kol/ranking`);
  return parseApiResponse<KOLResponse>(response, 'Failed to get KOL ranking');
}

export async function getGenericSheetData(spreadsheetUrl: string, sheetName: string): Promise<{ success: boolean; data: any[]; error?: string }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/sheet-data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      spreadsheet_url: spreadsheetUrl,
      sheet_name: sheetName,
    }),
  });
  return parseApiResponse(response, 'Failed to get sheet data');
}

export async function getApprovedKOLs(): Promise<{ success: boolean; kols: any[] }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/approved-list`);
  return parseApiResponse(response, 'Failed to get approved KOLs');
}

export async function getProcessedBookings(): Promise<{ success: boolean; ids: string[] }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/processed-bookings`);
  return parseApiResponse(response, 'Failed to get processed bookings');
}

export async function approveKOL(kol: any, bookingId: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kol, booking_id: bookingId }),
  });
  return parseApiResponse(response, 'Failed to approve KOL');
}

export async function getRejectionHistory(): Promise<{ success: boolean; history: Record<string, number> }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/rejection-history`);
  return parseApiResponse(response, 'Failed to get rejection history');
}

export async function rejectKOL(bookingId: string, tiktokId?: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ booking_id: bookingId, tiktok_id: tiktokId }),
  });
  return parseApiResponse(response, 'Failed to reject KOL');
}

export async function deleteApprovedKOL(tiktokAccount: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/delete-approved`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tiktok_account: tiktokAccount }),
  });
  return parseApiResponse(response, 'Failed to delete approved KOL');
}

export async function sendKOLNotification(email: string, bookingCode: string, tiktokAccount: string): Promise<{ success: boolean }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/send-notification`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, booking_code: bookingCode, tiktok_account: tiktokAccount }),
  });
  return parseApiResponse(response, 'Failed to send notification');
}

export async function syncKOLVideos(): Promise<{ success: boolean, updated: number }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/sync-videos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  return parseApiResponse(response, 'Failed to sync videos');
}

export async function updateKOLRanking(): Promise<{ success: boolean, count: number }> {
  const response = await fetch(`${API_BASE_URL}/api/kol/update-ranking`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  return parseApiResponse(response, 'Failed to update ranking');
}
