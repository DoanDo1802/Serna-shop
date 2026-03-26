export interface DataRow {
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

export interface CrawlConfigState {
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
